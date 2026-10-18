import argparse
import os
import shutil
import subprocess
from pathlib import Path

import amend7_smoke as base

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["R2a_b2mixed", "R2a_sentence_marker", "R2b_adjudicator"]


def run_notebook(name, drive, work, flags):
    ns = {"D": str(drive)}
    for src in base.code_cells(name):
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
                cmd = base.interpolate(cmd.replace("/content/rev2_bundle.tgz", str(work.parent / "rev2_bundle.tgz")).replace("/content/w", str(work)), ns)
                if "rev2_jobs run" in cmd:
                    cmd = cmd.replace(" 2>&1 |", f" {flags} 2>&1 |", 1)
                print("RUN:", cmd, flush=True)
                r = subprocess.run(cmd, shell=True, cwd=str(work), env={**os.environ, "PYTHONPATH": str(work)})
                if r.returncode not in (0, 1):
                    raise SystemExit(f"command failed with {r.returncode}: {cmd}")
            else:
                py.append(line.replace("/content/w", str(work)))
        if py:
            exec("\n".join(py), ns)
    return ns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", required=True)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--notebooks", nargs="+", default=NOTEBOOKS)
    a = ap.parse_args()
    sim = Path(a.sim)
    drive = sim / "drive"
    work = sim / "w"
    if sim.exists():
        shutil.rmtree(sim)
    drive.mkdir(parents=True)
    work.mkdir(parents=True)
    shutil.copy(a.bundle, drive / "rev2_bundle.tgz")
    shutil.copy(a.inputs, drive / "inputs.json.gz")
    from transformers import AutoModel, AutoTokenizer
    tiny = sim / "tiny_encoder"
    AutoModel.from_pretrained(base.TINY_BASE).save_pretrained(tiny)
    AutoTokenizer.from_pretrained(base.TINY_BASE).save_pretrained(tiny)
    flags = f"--smoke --tiny-encoder {tiny} --tiny-llm {base.TINY_LLM}"
    (work / "data").mkdir(exist_ok=True)
    os.symlink(ROOT / "data" / "DDICorpus", work / "data" / "DDICorpus")
    for name in a.notebooks:
        ns = run_notebook(name, drive, work, flags)
        jobs = ns["JOBS"]
        done = [j for j in jobs if (drive / "runs" / "preds" / f"{j}.json").exists()]
        failed = [j for j in jobs if (drive / "runs" / "preds" / f"{j}.failed.txt").exists()]
        print(f"{name}: {len(done)}/{len(jobs)} jobs finished, failed {failed}")
        if name.startswith("R2a"):
            missing = [j for j in done if not (drive / "weights" / j).is_dir()]
            print(f"{name}: weights missing for {missing}")
            if missing:
                raise SystemExit(f"{name}: weights missing for {missing}")
        if len(done) != len(jobs):
            raise SystemExit(f"{name}: missing {sorted(set(jobs) - set(done))}")


if __name__ == "__main__":
    main()
