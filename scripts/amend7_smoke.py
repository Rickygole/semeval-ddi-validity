import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "colab" / "experiments"
TINY_BASE = "hf-internal-testing/tiny-random-bert"
TINY_LLM = "trl-internal-testing/tiny-Qwen2ForCausalLM-2.5"


def code_cells(name):
    nb = json.loads((NB / f"{name}.ipynb").read_text())
    cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    for i, src in enumerate(cells):
        python = [l for l in src.split("\n") if not l.startswith(("!", "%"))]
        compile("\n".join(python), f"{name} cell {i}", "exec")
    return cells


def interpolate(cmd, ns):
    return re.sub(r"\{([^{}]+)\}", lambda m: str(eval(m.group(1), ns)), cmd)


def run_notebook(name, drive, work, smoke_flags):
    ns = {"D": str(drive)}
    for src in code_cells(name):
        if "drive.mount" in src:
            os.makedirs(f"{drive}/runs/preds", exist_ok=True)
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
                cmd = interpolate(cmd.replace("/content/w", str(work)), ns)
                if "amend7_jobs run" in cmd:
                    cmd = cmd.replace(" 2>&1 |", f" {smoke_flags} 2>&1 |", 1)
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
    ap.add_argument("--notebooks", nargs="+", default=["E7_positive_control_part1", "E7_positive_control_part2", "E8_evidence_reader", "E9_model_panel_part1", "E9_model_panel_part2"])
    a = ap.parse_args()
    sim = Path(a.sim)
    drive = sim / "drive"
    work = sim / "w"
    if sim.exists():
        shutil.rmtree(sim)
    drive.mkdir(parents=True)
    work.mkdir(parents=True)
    shutil.copy(a.bundle, drive / "amend7_bundle.tgz")
    shutil.copy(a.inputs, drive / "inputs.json.gz")
    from transformers import AutoModel, AutoTokenizer
    tiny = sim / "tiny_encoder"
    AutoModel.from_pretrained(TINY_BASE).save_pretrained(tiny)
    AutoTokenizer.from_pretrained(TINY_BASE).save_pretrained(tiny)
    flags = f"--smoke --tiny-encoder {tiny} --tiny-llm {TINY_LLM}"
    (work / "data").mkdir(exist_ok=True)
    os.symlink(ROOT / "data" / "DDICorpus", work / "data" / "DDICorpus")
    for name in a.notebooks:
        ns = run_notebook(name, drive, work, flags)
        jobs = ns["JOBS"]
        done = [j for j in jobs if (drive / "runs" / "preds" / f"{j}.json").exists()]
        print(f"{name}: {len(done)}/{len(jobs)} jobs finished")
        if len(done) != len(jobs):
            raise SystemExit(f"{name}: missing {sorted(set(jobs) - set(done))}")


if __name__ == "__main__":
    main()
