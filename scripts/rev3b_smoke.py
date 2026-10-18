import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import amend7_smoke as base
from ddiood import config
from ddiood import rev3b_jobs as rj
from ddiood.rev2_encoders import file_sha256

NAME = "R3b_marker_sentence"


def run_notebook(drive, work):
    ns = {"D": str(drive)}
    for src in base.code_cells(NAME):
        if "flush_and_unmount" in src or "torch.cuda" in src:
            print("skipped cell:", src.split("\n")[0])
            continue
        if "drive.mount" in src:
            os.makedirs(f"{drive}/runs/preds", exist_ok=True)
            os.makedirs(f"{drive}/weights", exist_ok=True)
            continue
        py = []
        for line in src.split("\n"):
            if line.startswith("!") or line.startswith("%"):
                if py:
                    exec("\n".join(py), ns)
                    py = []
                cmd = line[1:]
                if line.startswith("%cd"):
                    os.chdir(str(work))
                    continue
                if cmd.startswith("pip") or cmd.startswith("nvidia-smi"):
                    print("skipped:", cmd)
                    continue
                cmd = base.interpolate(cmd.replace("/content/rev3b_bundle.tgz", str(work.parent / "rev3b_bundle.tgz")).replace("/content/w", str(work)), ns)
                if "rev3b_jobs run" in cmd:
                    cmd = cmd.replace(" 2>&1 |", " --smoke 2>&1 |", 1)
                print("RUN:", cmd, flush=True)
                r = subprocess.run(cmd, shell=True, cwd=str(work), env={**os.environ, "PYTHONPATH": str(work)})
                if r.returncode not in (0, 1):
                    raise SystemExit(f"command failed with {r.returncode}: {cmd}")
            else:
                py.append(line.replace("/content/w", str(work)))
        if py:
            exec("\n".join(py), ns)
    return ns


def make_weights(drive, seeds):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    for s in seeds:
        torch.manual_seed(s)
        name = rj.STORED_NAME.format(seed=s)
        dest = drive / "weights" / name
        model = AutoModelForSequenceClassification.from_pretrained(base.TINY_BASE, num_labels=len(config.LABELS), ignore_mismatched_sizes=True)
        model.save_pretrained(dest)
        AutoTokenizer.from_pretrained(base.TINY_BASE).save_pretrained(dest)
        stored = {"weights": {"weight_sha256": file_sha256(rj.weight_file(dest))}, "eval": {}}
        (drive / "runs" / "preds" / f"{name}.json").write_text(json.dumps(stored))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", required=True)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--inputs", required=True)
    a = ap.parse_args()
    sim = Path(a.sim)
    drive, work = sim / "drive", sim / "w"
    if sim.exists():
        shutil.rmtree(sim)
    (drive / "runs" / "preds").mkdir(parents=True)
    (drive / "weights").mkdir()
    work.mkdir(parents=True)
    shutil.copy(a.bundle, drive / "rev3b_bundle.tgz")
    shutil.copy(a.inputs, drive / "inputs.json.gz")
    make_weights(drive, rj.SEEDS)
    (work / "data").mkdir(exist_ok=True)
    os.symlink(ROOT / "data" / "DDICorpus", work / "data" / "DDICorpus")
    ns = run_notebook(drive, work)
    jobs = ns["JOBS"]
    done = [j for j in jobs if (drive / "runs" / "preds" / f"{j}.json").exists()]
    failed = [j for j in jobs if (drive / "runs" / "preds" / f"{j}.failed.txt").exists()]
    print(f"{NAME}: {len(done)}/{len(jobs)} jobs finished, failed {failed}")
    if len(done) != len(jobs):
        raise SystemExit(f"missing {sorted(set(jobs) - set(done))}")
    first = json.loads((drive / "runs" / "preds" / f"{jobs[0]}.json").read_text())
    print({k: len(v["p"]) for k, v in first["eval"].items()}, first["marker_fallback"], first["reproduction"])


if __name__ == "__main__":
    main()
