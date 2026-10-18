import argparse
import hashlib
import json
import sys
import tempfile
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.simplefilter("ignore", RuntimeWarning)

MANIFESTS = (("results/revision/preds_sha256.txt", "results/revision/preds", True),
             ("results/revision/amend7/preds_sha256.txt", "runs/preds", False),
             ("results/revision/amend7/preds_cpu_sha256.txt", "artifacts/amend7/preds_cpu", True),
             ("results/revision/runs_preds_sha256.txt", "runs/preds", False))
PREDS = ROOT / "results" / "revision" / "preds"
REFERENCE = ROOT / "results" / "revision" / "eval" / "decisions.json"
ARCHIVE = ROOT / "docs" / "ARCHIVE_MANIFEST.json"
BASELINES = ROOT / "results" / "corrected" / "baselines.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(manifest, folder, exact):
    listed = {}
    for line in (ROOT / manifest).read_text().splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            listed[name.strip().lstrip("*")] = digest
    problems = []
    for name, digest in sorted(listed.items()):
        path = ROOT / folder / name
        if not path.exists():
            problems.append(f"missing {folder}/{name}")
        elif sha256(path) != digest:
            problems.append(f"hash mismatch {folder}/{name}")
    if exact:
        extra = sorted(p.name for p in (ROOT / folder).glob("*.json") if p.name not in listed)
        problems += [f"unlisted {folder}/{name}" for name in extra]
    return {"manifest": manifest, "folder": folder, "files": len(listed), "problems": problems}


def check_archive():
    out = {"present": ARCHIVE.exists()}
    if not ARCHIVE.exists():
        return out
    m = json.loads(ARCHIVE.read_text())
    out["reference_decisions_sha256_matches_archive"] = sha256(REFERENCE) == m["decisions"]["sha256"]
    for entry in m["prediction_manifests"]:
        out[f"{entry['path']} matches archive"] = sha256(ROOT / entry["path"]) == entry["sha256"]
    want = {Path(e["path"]).name: e["sha256"] for e in m["revision_predictions"]}
    have = {p.name: sha256(p) for p in PREDS.glob("*.json")}
    out["revision_predictions_match_archive"] = want == have
    return out


def recompute(out_dir, boot):
    from ddiood import evaluate2
    found = evaluate2.load_drugbank(allow_missing_drugbank=True)
    drugbank = [tag for tag, rows in found.items() if rows is not None]
    truth = evaluate2.load_truth(allow_missing_drugbank=True)
    start = time.time()
    evaluate2.evaluate(str(PREDS), str(out_dir), truth, boot, evaluate2.load_baselines(BASELINES))
    return Path(out_dir) / "decisions.json", drugbank, round(time.time() - start, 1)


def diff(a, b):
    rows = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            rows.append(key)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--hashes-only", action="store_true")
    a = ap.parse_args(argv)
    report = {"hashes": [check_manifest(*m) for m in MANIFESTS], "archive": check_archive()}
    ok = all(not h["problems"] for h in report["hashes"]) and all(v for k, v in report["archive"].items())
    for h in report["hashes"]:
        status = "OK" if not h["problems"] else "FAIL"
        print(f"[{status}] {h['files']} files in {h['folder']} against {h['manifest']}")
        for p in h["problems"]:
            print(f"       {p}")
    for k, v in report["archive"].items():
        print(f"[{'OK' if v else 'FAIL'}] archive manifest: {k}")
    if not a.hashes_only:
        out_dir = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="ddiood-verify-"))
        produced, drugbank, seconds = recompute(out_dir, a.boot)
        same_bytes = produced.read_bytes() == REFERENCE.read_bytes()
        changed = diff(json.loads(produced.read_text()), json.loads(REFERENCE.read_text()))
        report["decisions"] = {"reference": str(REFERENCE.relative_to(ROOT)), "reference_sha256": sha256(REFERENCE),
                               "recomputed": str(produced), "recomputed_sha256": sha256(produced),
                               "identical_bytes": same_bytes, "differing_hypotheses": changed,
                               "drugbank_files_used": drugbank, "bootstrap_draws": a.boot, "seconds": seconds}
        ok = ok and same_bytes
        print(f"[{'OK' if same_bytes else 'FAIL'}] recomputed decisions.json "
              f"{'is byte-identical to' if same_bytes else 'differs from'} {report['decisions']['reference']}")
        print(f"       reference  {report['decisions']['reference_sha256']}")
        print(f"       recomputed {report['decisions']['recomputed_sha256']}")
        if changed:
            print(f"       differing hypotheses: {', '.join(changed)}")
        print(f"       DrugBank files used: {drugbank or 'none'}; evaluation took {seconds} s")
    print("VERIFY PASSED" if ok else "VERIFY FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
