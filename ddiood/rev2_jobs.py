import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

from . import amend7_llm as al
from . import rev2_adjudicator as ra
from . import rev2_encoders as re_
from . import rev2_data as rd
from .amend7_jobs import atomic_write, finished

ROOT = Path(__file__).resolve().parents[1]
STORED = ROOT / "results" / "revision" / "preds"
STORED_NAME = {"b2mixed": "b2mixed-biomedbert-s{seed}", "b2sentence": "b2sentence-biomedbert-s{seed}",
               "marker": "b2sentence-biomedbert-s{seed}"}
CODE_FILES = ("rev2_adjudicator.py", "rev2_data.py", "rev2_encoders.py", "rev2_jobs.py", "amend7_llm.py",
              "amend7_prompts.py", "amend7_panel.py", "amend7_data.py", "bert.py", "gpu_jobs.py", "inputs.py", "config.py")
NOTEBOOK_HOURS_CAP = 2.0
ADJUDICATOR = "r2-olmo-adjudication"
MIN_FREE_BYTES = 8 * 10 ** 9


def job(kind, name, group, **kw):
    cfg = {"kind": kind, "name": name, "group": group}
    cfg.update(kw)
    return cfg


def registry():
    J = []
    for family in re_.FAMILIES:
        for seed in re_.SEEDS:
            J.append(job("r2a", f"r2-{family}-biomedbert-s{seed}", "R2a", family=family, seed=seed))
    J.append(job("r2b", ADJUDICATOR, "R2b", model=ra.OLMO, revision=ra.OLMO_REVISION, sample_seed=ra.SAMPLE_SEED))
    return J


NOTEBOOKS = {
    "R2a_b2mixed": lambda j: j["kind"] == "r2a" and j["family"] == "b2mixed",
    "R2a_sentence_marker": lambda j: j["kind"] == "r2a" and j["family"] in ("b2sentence", "marker"),
    "R2b_adjudicator": lambda j: j["kind"] == "r2b",
}


def notebook_jobs():
    reg = registry()
    out = {n: [j["name"] for j in reg if f(j)] for n, f in NOTEBOOKS.items()}
    flat = [x for v in out.values() for x in v]
    if sorted(flat) != sorted(j["name"] for j in reg):
        raise RuntimeError("the notebooks do not cover every job exactly once")
    return out


def code_version():
    h = hashlib.sha256()
    here = Path(__file__).parent
    for p in [here / f for f in sorted(CODE_FILES)]:
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def config_hash(cfg, smoke):
    return hashlib.sha256(json.dumps({**cfg, "smoke": smoke, "code": code_version()}, sort_keys=True).encode()).hexdigest()


def stored_seconds(cfg, preds=STORED):
    f = Path(preds) / (STORED_NAME[cfg["family"]].format(seed=cfg["seed"]) + ".json")
    return json.loads(f.read_text())["seconds"] if f.exists() else None


def estimates(preds=STORED, r2b_tokens=None):
    jobs = {}
    for cfg in registry():
        if cfg["kind"] == "r2a":
            s = stored_seconds(cfg, preds)
            jobs[cfg["name"]] = None if s is None else {"stored_s": s, "low_s": round(s + 60), "high_s": round(1.6 * s + 120)}
        else:
            jobs[cfg["name"]] = None if r2b_tokens is None else {
                "tokens": int(r2b_tokens), "low_s": round(600 + r2b_tokens / 13000.0), "high_s": round(1200 + r2b_tokens / 5000.0)}
    notebooks = {}
    for nb, names in notebook_jobs().items():
        if any(jobs[n] is None for n in names):
            notebooks[nb] = {"jobs": len(names), "low_h": None, "high_h": None}
            continue
        lo = sum(jobs[n]["low_s"] for n in names)
        hi = sum(jobs[n]["high_s"] for n in names)
        notebooks[nb] = {"jobs": len(names), "low_h": round(lo / 3600, 2), "high_h": round(hi / 3600, 2)}
    return {"jobs": jobs, "notebooks": notebooks, "rule": "low = stored seconds + 60; high = 1.6 * stored seconds + 120; "
            "marker uses the b2sentence seconds; the adjudicator is 600 s + tokens / 13000 (low) and 1200 s + tokens / 5000 (high)"}


def env_info():
    import importlib
    out = {}
    for pkg in ("torch", "transformers", "bitsandbytes", "accelerate"):
        try:
            out[pkg] = importlib.import_module(pkg).__version__
        except Exception:
            out[pkg] = None
    try:
        import torch
        out["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        out["gpu_capability"] = list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None
    except Exception:
        out["gpu"] = out["gpu_capability"] = None
    return out


def preflight(selected, weights_dir, smoke=False, min_free=MIN_FREE_BYTES):
    weights_dir = Path(weights_dir)
    weights_dir.mkdir(parents=True, exist_ok=True)
    for stale in weights_dir.glob("*.tmp"):
        shutil.rmtree(stale, ignore_errors=True)
    if any(c["kind"] == "r2a" for c in selected):
        free = shutil.disk_usage(weights_dir).free
        if free < min_free:
            raise RuntimeError(f"only {free / 1e9:.1f} GB free under {weights_dir}, need {min_free / 1e9:.0f} GB")
    if smoke:
        return
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("no GPU: torch.cuda.is_available() is False")
    if any(c["kind"] == "r2b" for c in selected) and torch.cuda.get_device_capability(0)[0] < 8:
        raise RuntimeError(f"{torch.cuda.get_device_name(0)} has no native bfloat16 support; use an L4 or A100")


def adjudicator_job(data, cfg, state, tiny_llm):
    sheet_path = data.workdir / "rev2" / "label_audit_sheet.csv"
    sheet = rd.read_sheet(sheet_path)
    if len(sheet) != 255:
        raise RuntimeError(f"the audit sheet has {len(sheet)} rows, expected 255")
    items = ra.all_items(sheet, data.ood_full, data.old_full, data.excluded_older)
    ra.assert_frozen(items)
    if data.smoke:
        items = items[::40]
    if "llm" not in state:
        state["llm"] = ra.load_tiny(tiny_llm) if tiny_llm else ra.load_olmo()
    tok, model = state["llm"]
    log = lambda m: print(f"{cfg['name']} {m}", flush=True) if m.endswith("0") else None
    out, scores, n_unique = ra.adjudicate(tok, model, items, data.sections, log=log)
    audit_keys = {(x["ood_drug"], x["partner"]) for x in out if x["set"] == "audit"}
    random_keys = {(x["ood_drug"], x["partner"]) for x in out if x["set"] == "random"}
    extra = {"model": {"repo": ra.OLMO, "revision": ra.OLMO_REVISION, "license": ra.OLMO_LICENSE,
                       "quantization": None if tiny_llm else "bitsandbytes nf4 4-bit, double quantization, bfloat16 compute",
                       "tiny_stand_in": tiny_llm},
             "prompt": ra.PROMPT, "prompt_sha256": ra.prompt_sha256(), "chunk_rule": ra.CHUNK_RULE,
             "answer": al.answer_stats(scores, ra.NON_ANSWER_MASS),
             "answer_note": "answer.non_answers and answer.n are counted by prompt, chunks included; items carry non_answer per item",
             "n_items": len(out), "n_unique_prompts": n_unique,
             "n_pairs_in_both_sets": len(audit_keys & random_keys),
             "audit_sheet_sha256": hashlib.sha256(sheet_path.read_bytes()).hexdigest(), "sample_seed": ra.SAMPLE_SEED}
    return {"items": out}, extra


def run_job(cfg, data, state, workdir, weights_dir, tiny_encoder, tiny_llm):
    if cfg["kind"] == "r2b":
        return adjudicator_job(data, cfg, state, tiny_llm)
    local = Path(workdir) / "work_local" / cfg["name"]
    ev, extra = re_.encoder_job(data, cfg, local, weights_dir, tiny_encoder)
    hist = local / "work" / "history.json"
    if hist.exists():
        extra["history"] = json.loads(hist.read_text())
    return ev, extra


def run(workdir, out_dir, weights_dir, only=None, smoke=False, tiny_encoder=None, tiny_llm=None, runner=None, data=None):
    out_dir = Path(out_dir)
    (out_dir / "preds").mkdir(parents=True, exist_ok=True)
    Path(weights_dir).mkdir(parents=True, exist_ok=True)
    selected = [c for c in registry() if not (only and c["name"] not in only)]
    if runner is None:
        preflight(selected, weights_dir, smoke)
    if data is None:
        data = rd.Rev2Data(workdir, smoke, need_semeval=any(c["kind"] == "r2a" for c in selected))
    runner = runner or run_job
    state, failed = {}, []
    for cfg in selected:
        name = cfg["name"]
        dest = out_dir / "preds" / f"{name}.json"
        chash = config_hash(cfg, smoke)
        if finished(dest, chash, name):
            print(f"skip {name}", flush=True)
            continue
        t0 = time.time()
        print(f"start {name}", flush=True)
        try:
            ev, extra = runner(cfg, data, state, workdir, weights_dir, tiny_encoder, tiny_llm)
            res = {"config": cfg, "config_hash": chash, "smoke": smoke, "ood_hash": data.ood_hash,
                   "ood_old_hash": data.old_hash, "train_hash": data.manifest["train_hash"],
                   "code_version": code_version(), "environment": env_info(), "eval": ev, "seconds": round(time.time() - t0, 1), **extra}
            atomic_write(dest, json.dumps(res))
            (out_dir / "preds" / f"{name}.failed.txt").unlink(missing_ok=True)
            print(f"done {name} in {res['seconds']}s", flush=True)
        except Exception:
            import traceback
            failed.append(name)
            atomic_write(out_dir / "preds" / f"{name}.failed.txt", traceback.format_exc())
            print(f"FAILED {name}", flush=True)
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
    if failed:
        print(f"{len(failed)} jobs failed: {failed}", flush=True)
    return failed


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    r = sp.add_parser("run")
    r.add_argument("--workdir", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--weights", required=True)
    r.add_argument("--only", nargs="*")
    r.add_argument("--smoke", action="store_true")
    r.add_argument("--tiny-encoder")
    r.add_argument("--tiny-llm")
    sp.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for c in registry():
            print(c["group"], c["name"])
    else:
        failed = run(a.workdir, a.out, a.weights, a.only, a.smoke, a.tiny_encoder, a.tiny_llm)
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
