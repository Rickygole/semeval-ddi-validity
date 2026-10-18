import argparse
import hashlib
import json
import shutil
import sys
import time
import traceback
from pathlib import Path

import numpy as np

from . import amend7_panel as pn
from . import bert, config, gpu_jobs, inputs
from .amend7_jobs import atomic_write, finished
from .rev2_encoders import FAMILIES, SEEDS, file_sha256
from .rev2_jobs import env_info

GROUP = "R3b"
STORED_NAME = "r2-marker-biomedbert-s{seed}"
INPUT_KEYS = ("sentence", "masked", "swap_vocab", "swap_novel", "swap_pseudo", "names")
SWAP_KINDS = ("vocab", "novel", "pseudo")
CODE_FILES = ("rev3b_jobs.py", "rev2_encoders.py", "rev2_jobs.py", "amend7_panel.py", "bert.py", "gpu_jobs.py", "inputs.py",
              "config.py", "semeval.py")
FROZEN_FILE_SHA256 = {
    "bert.py": "a28bf7183fa44d16f1c0537fc77865e436ef21a38800100bd7e9bd2549e32ccb",
    "gpu_jobs.py": "ab8abe15625ecd3cde973a24a56306bea4e12129ab62ea15a1fcadb13f267a32",
    "inputs.py": "5515e07f76ab997d27ed75b34bd4cbe5dee5c0927006ca7420c9e05cf19e52c6",
    "amend7_panel.py": "df478ca53341e55c3e36b213fc9bdc3a6e54ea04952b9107a46d3f7d4436730e",
    "config.py": "0d8f530f7013048d8f57eb71d4d91ba7ce1c1f2e4ca466f25e428a33df4dcf17",
    "semeval.py": "917650b0ca6a861618881cc3b51ae720ed7ac43220e1f627ffbfff42416c10f1",
    "rev2_encoders.py": "0f4028f32514cd49c41a2054d199f2592ef101fccbb9c822e33c9179586bb13e",
}
EXPECTED_INPUTS_SHA256 = "e187d8878c70e492a81c34612d0e71a43d6b7980d760cf6bb3b4fb66d921d75a"
GAP_LIMIT = 1e-3
MIN_FREE_BYTES = 2 * 10 ** 9
NOTEBOOK_HOURS_CAP = 2.0
TEXTS_PER_SEED = 6 * 2810


def job_name(seed):
    return f"r3b-marker-sentence-s{seed}"


def registry():
    return [{"kind": "r3b", "name": job_name(s), "group": GROUP, "family": "marker", "seed": s,
             "weights_name": STORED_NAME.format(seed=s), "inputs": list(INPUT_KEYS)} for s in SEEDS]


def notebook_jobs():
    return {"R3b_marker_sentence": [c["name"] for c in registry()]}


def code_version():
    h = hashlib.sha256()
    here = Path(__file__).parent
    for f in sorted(CODE_FILES):
        h.update(f.encode())
        h.update((here / f).read_bytes())
    return h.hexdigest()


def config_hash(cfg, smoke):
    return hashlib.sha256(json.dumps({**cfg, "smoke": smoke, "code": code_version()}, sort_keys=True).encode()).hexdigest()


def frozen_hashes(root=None):
    here = Path(root) if root else Path(__file__).parent
    return {f: hashlib.sha256((here / f).read_bytes()).hexdigest() for f in sorted(FROZEN_FILE_SHA256)}


def assert_frozen(root=None):
    got = frozen_hashes(root)
    bad = sorted(f for f in FROZEN_FILE_SHA256 if got[f] != FROZEN_FILE_SHA256[f])
    if bad:
        raise RuntimeError(f"frozen files differ from the recorded sha256: {bad}")


def build_inputs(inp):
    texts, fallback = {}, {}
    texts["sentence"], ok = pn.marker_sentence(inp.test)
    fallback["sentence"] = int(len(ok) - sum(ok))
    texts["masked"] = [inputs.mask_names(t, [p["drug_a"], p["drug_b"]]) for t, p in zip(texts["sentence"], inp.test)]
    fallback["masked"] = fallback["sentence"]
    for kind in SWAP_KINDS:
        texts[f"swap_{kind}"], ok = pn.marker_sentence(inp.swaps[kind])
        fallback[f"swap_{kind}"] = int(len(ok) - sum(ok))
    texts["names"] = pn.marker_names(inp.test)
    fallback["names"] = 0
    return texts, fallback


def inputs_sha256(texts):
    return hashlib.sha256(json.dumps({k: texts[k] for k in INPUT_KEYS}, sort_keys=True).encode()).hexdigest()


def labels_sha256(test):
    return hashlib.sha256(json.dumps([[r["pair_id"], r["sentence_id"], r["label_id"]] for r in test]).encode()).hexdigest()


def estimates():
    low, high = 60 + 20, 120 + 90
    per = {c["name"]: {"low_s": low, "high_s": high} for c in registry()}
    n = len(per)
    return {"jobs": per, "notebooks": {"R3b_marker_sentence": {"jobs": n, "low_h": round(n * low / 3600, 2),
                                                                  "high_h": round(n * high / 3600, 2)}},
            "rule": "per seed, 16,860 inferences of a base-size encoder at 512 tokens maximum: low 20 s of scoring plus 60 s of model load, "
                    "high 90 s of scoring plus 120 s of model load; setup (pip, bundle, corpus clone) is not included"}


def preflight(selected, weights_dir, smoke=False, min_free=MIN_FREE_BYTES):
    weights_dir = Path(weights_dir)
    weights_dir.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(weights_dir).free
    if free < min_free:
        raise RuntimeError(f"only {free / 1e9:.1f} GB free under {weights_dir}, need {min_free / 1e9:.0f} GB")
    if smoke:
        return
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("no GPU: torch.cuda.is_available() is False")
    missing = [c["weights_name"] for c in selected if not (weights_dir / c["weights_name"]).is_dir()]
    if missing:
        raise RuntimeError(f"saved weights missing under {weights_dir}: {missing}")


def load_model(weights, seed, tiny=None):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from .index import device
    if tiny:
        torch.manual_seed(seed)
        model = AutoModelForSequenceClassification.from_pretrained(tiny, num_labels=len(config.LABELS), ignore_mismatched_sizes=True)
        tok = AutoTokenizer.from_pretrained(tiny)
    else:
        model = AutoModelForSequenceClassification.from_pretrained(weights)
        tok = AutoTokenizer.from_pretrained(weights)
    return model.to(device()).eval(), tok


def weight_file(weights):
    files = sorted(Path(weights).glob("*.safetensors")) + sorted(Path(weights).glob("*.bin"))
    if not files:
        raise RuntimeError(f"no weight file under {weights}")
    return files[0]


def read_stored(stored_dir, seed):
    f = Path(stored_dir) / f"{STORED_NAME.format(seed=seed)}.json"
    return json.loads(f.read_text()) if f.exists() else None


def reproduction_checks(ev, stored, n_rows):
    if stored is None:
        raise RuntimeError("the stored R2a prediction file of this seed is missing")
    out = {}
    for mine, theirs in (("sentence", "test_sentence"), ("names", "test_empty")):
        a, b = np.asarray(ev[mine]["p"], float), np.asarray(stored["eval"][theirs]["p"], float)
        if len(a) != len(b):
            raise RuntimeError(f"{mine} has {len(a)} rows, stored {theirs} has {len(b)}")
        gap = float(np.abs(a - b).max())
        out[f"{mine}_vs_{theirs}_max_abs_gap"] = gap
        if gap > GAP_LIMIT:
            raise RuntimeError(f"{mine} does not reproduce stored {theirs}: max gap {gap}")
    return out


def marker_job(inp, cfg, state, weights_dir, stored_dir, smoke, tiny):
    seed = cfg["seed"]
    weights = Path(weights_dir) / cfg["weights_name"]
    if "texts" not in state:
        pn.attach_offsets(inp.test, pn.load_offsets("test"))
        state["texts"], state["fallback"] = build_inputs(inp)
    texts, fallback = state["texts"], state["fallback"]
    stored = read_stored(stored_dir, seed)
    weights_block = {"path": str(weights)}
    if not tiny:
        wf = weight_file(weights)
        got = file_sha256(wf)
        want = stored["weights"]["weight_sha256"] if stored else None
        if got != want:
            raise RuntimeError(f"weight sha256 {got} differs from the stored {want}")
        weights_block.update({"weight_file": wf.name, "weight_sha256": got, "weight_bytes": wf.stat().st_size})
    model, tok = load_model(weights, seed, tiny)
    ev = {}
    for key in INPUT_KEYS:
        p, s = bert.predict(model, tok, texts[key], return_probs=True)
        ev[key] = {"preds": p, "p": [round(x, 6) for x in s]}
    checks = {"skipped": "stand-in model or smoke subsample"} if (tiny or smoke) else reproduction_checks(ev, stored, len(inp.test))
    del model
    extra = {"weights": weights_block, "marker_fallback": fallback, "reproduction": checks,
             "inputs_sha256": inputs_sha256(texts), "test_labels_sha256": labels_sha256(inp.test), "n_rows": len(inp.test),
             "n_swap_rows": {k: len(inp.swaps[k]) for k in SWAP_KINDS}}
    return ev, extra


def run(workdir, out_dir, weights_dir, only=None, smoke=False, tiny_encoder=None, runner=None, inp=None, stored_dir=None):
    out_dir = Path(out_dir)
    (out_dir / "preds").mkdir(parents=True, exist_ok=True)
    selected = [c for c in registry() if not (only and c["name"] not in only)]
    if runner is None:
        preflight(selected, weights_dir, smoke or bool(tiny_encoder))
        if not smoke and not tiny_encoder:
            assert_frozen()
    if inp is None:
        inp = gpu_jobs.Inputs(Path(workdir) / "inputs.json.gz", smoke)
    if not smoke and not tiny_encoder and runner is None:
        texts, _ = build_inputs_for_check(inp)
        if inputs_sha256(texts) != EXPECTED_INPUTS_SHA256:
            raise RuntimeError("the input texts differ from the frozen input list")
    runner = runner or marker_job
    stored_dir = stored_dir or out_dir / "preds"
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
            ev, extra = runner(inp, cfg, state, weights_dir, stored_dir, smoke, tiny_encoder)
            res = {"config": cfg, "config_hash": chash, "smoke": smoke, "code_version": code_version(), "environment": env_info(),
                   "eval": ev, "seconds": round(time.time() - t0, 1), **extra}
            atomic_write(dest, json.dumps(res))
            (out_dir / "preds" / f"{name}.failed.txt").unlink(missing_ok=True)
            print(f"done {name} in {res['seconds']}s", flush=True)
        except Exception:
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


def build_inputs_for_check(inp):
    pn.attach_offsets(inp.test, pn.load_offsets("test"))
    return build_inputs(inp)


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
    sp.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for c in registry():
            print(c["group"], c["name"])
    else:
        failed = run(a.workdir, a.out, a.weights, a.only, a.smoke, a.tiny_encoder)
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
