import argparse
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

from . import amend7_llm as al
from . import rev2_adjudicator as ra
from . import rev3_tac as rt
from .amend7_jobs import atomic_write, finished
from .rev2_jobs import env_info

JOB = "r3-olmo-tac-calibration"
EXPECTED_TAC_ITEMS_SHA256 = "eedca86c5035b2adda86adb9eb9e47418c7dbc88bdad94468b1508801e78952a"
PLAN_OLMO_REVISION = "470b1fba1ae01581f270116362ee4aa1b97f4c84"
CODE_FILES = ("rev3_jobs.py", "rev3_tac.py", "rev2_adjudicator.py", "amend7_llm.py", "amend7_prompts.py")
SMOKE_STEP = 40
NOTEBOOK_HOURS_CAP = 2.0


def registry():
    return [{"kind": "r3", "name": JOB, "group": "R2c", "model": ra.OLMO, "revision": ra.OLMO_REVISION, "sample_seed": rt.SAMPLE_SEED,
             "negative_ratio": rt.NEGATIVE_RATIO}]


def notebook_jobs():
    return {"R2c_tac_calibration": [c["name"] for c in registry()]}


def code_version():
    h = hashlib.sha256()
    here = Path(__file__).parent
    for f in sorted(CODE_FILES):
        h.update(f.encode())
        h.update((here / f).read_bytes())
    return h.hexdigest()


def config_hash(cfg, smoke):
    return hashlib.sha256(json.dumps({**cfg, "smoke": smoke, "code": code_version()}, sort_keys=True).encode()).hexdigest()


def estimates(tokens):
    low, high = round(600 + tokens / 13000.0), round(1200 + tokens / 5000.0)
    return {"tokens": int(tokens), "low_s": low, "high_s": high, "low_h": round(low / 3600, 2), "high_h": round(high / 3600, 2),
            "rule": "600 s + tokens / 13000 (low) and 1200 s + tokens / 5000 (high), the rates of the R2b adjudicator"}


def assert_frozen_r2b():
    if ra.OLMO_REVISION != PLAN_OLMO_REVISION:
        raise RuntimeError("the adjudicator model revision differs from the plan")
    got = ra.prompt_sha256()
    if got != ra.EXPECTED_PROMPT_SHA256:
        raise RuntimeError(f"prompt sha256 {got} differs from the frozen {ra.EXPECTED_PROMPT_SHA256}")


def preflight(smoke):
    assert_frozen_r2b()
    if smoke:
        return
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("no GPU: torch.cuda.is_available() is False")
    if torch.cuda.get_device_capability(0)[0] < 8:
        raise RuntimeError(f"{torch.cuda.get_device_name(0)} has no native bfloat16 support; use an L4 or A100")


def calibration_job(items, sections, state, tiny_llm, smoke):
    if "llm" not in state:
        state["llm"] = ra.load_tiny(tiny_llm) if tiny_llm else ra.load_olmo()
    tok, model = state["llm"]
    out, all_scores, unique = [], [], 0
    for name in sorted({i["set"] for i in items}):
        sub = [i for i in items if i["set"] == name]
        if smoke:
            sub = sub[::SMOKE_STEP]
        log = lambda m, n=name: print(f"{n} {m}", flush=True) if m.endswith("00") else None
        res, scores, n_unique = ra.adjudicate(tok, model, sub, sections[name], log=log)
        out += res
        all_scores += scores
        unique += n_unique
    chunked = sorted({(x["set"], x["ood_drug"]) for x in out if x["n_chunks"] > 1})
    extra = {"model": {"repo": ra.OLMO, "revision": ra.OLMO_REVISION, "license": ra.OLMO_LICENSE, "tiny_stand_in": tiny_llm,
                       "quantization": None if tiny_llm else "bitsandbytes nf4 4-bit, double quantization, bfloat16 compute"},
             "prompt": ra.PROMPT, "prompt_sha256": ra.prompt_sha256(), "chunk_rule": ra.CHUNK_RULE,
             "answer": al.answer_stats(all_scores, ra.NON_ANSWER_MASS), "n_items": len(out), "n_unique_prompts": unique,
             "n_chunked_labels": len(chunked), "tac_sources": rt.SOURCES, "tac_items_sha256": rt.items_sha256(items),
             "r2b_frozen": {"prompt_sha256": ra.EXPECTED_PROMPT_SHA256, "items_sha256": ra.EXPECTED_ITEMS_SHA256}}
    return {"items": out}, extra


def run(tac_dir, out_dir, only=None, smoke=False, tiny_llm=None, runner=None):
    out_dir = Path(out_dir)
    (out_dir / "preds").mkdir(parents=True, exist_ok=True)
    selected = [c for c in registry() if not (only and c["name"] not in only)]
    if runner is None:
        preflight(smoke)
    dirs = rt.fetch(tac_dir)
    items, sections = rt.build_all(dirs)
    got = rt.items_sha256(items)
    if got != EXPECTED_TAC_ITEMS_SHA256:
        raise RuntimeError(f"TAC item list sha256 {got} differs from the frozen {EXPECTED_TAC_ITEMS_SHA256}")
    runner = runner or calibration_job
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
            ev, extra = runner(items, sections, state, tiny_llm, smoke)
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    r = sp.add_parser("run")
    r.add_argument("--tac-dir", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--only", nargs="*")
    r.add_argument("--smoke", action="store_true")
    r.add_argument("--tiny-llm")
    sp.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for c in registry():
            print(c["group"], c["name"])
    else:
        failed = run(a.tac_dir, a.out, a.only, a.smoke, a.tiny_llm)
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
