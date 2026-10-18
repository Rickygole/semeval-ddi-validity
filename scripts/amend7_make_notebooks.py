import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_jobs as aj

META = json.loads((ROOT / "colab" / "experiments" / "E5_llm_baselines.ipynb").read_text())["metadata"]
PIP = {"E7": "pip -q install accelerate", "E8": "pip -q install bitsandbytes accelerate",
       "E9": "pip -q install accelerate sentencepiece protobuf"}

MOUNT = """import os
from google.colab import drive
if os.path.exists('/content/amend7_bundle.tgz'):
    D = '/content'
else:
    drive.mount('/content/drive')
    D = '/content/drive/MyDrive/temporal-ood-ddi'
os.makedirs(f'{D}/runs/preds', exist_ok=True)
print(D)"""


def cell(src):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "source": source, "outputs": [], "execution_count": None}


def build(name, jobs):
    pip = PIP[name.split("_")[0]]
    listing = "JOBS = [\n" + ",\n".join(f' "{n}"' for n in jobs) + "\n]"
    setup = (f"!mkdir -p /content/w && tar xzf {{D}}/amend7_bundle.tgz -C /content/w && cp {{D}}/inputs.json.gz /content/w/\n"
             f"!{pip}\n%cd /content/w\n!python -m ddiood.amend7_jobs merge --inputs inputs.json.gz --delta amend7/delta_amend1.json.gz")
    run = ("%cd /content/w\n!bash -c \"set -o pipefail; python -m ddiood.amend7_jobs run --workdir /content/w --out {D}/runs "
           "--only {' '.join(JOBS)} "
           f"2>&1 | tee -a {{D}}/runs/{name}.log | (grep --line-buffered -E '^(start|done|skip|FAILED)|Error|Traceback'; true)\"")
    status = ("import os, glob\n"
              "done = sorted(j for j in JOBS if os.path.exists(f'{D}/runs/preds/{j}.json'))\n"
              "failed = sorted(j for j in JOBS if os.path.exists(f'{D}/runs/preds/{j}.failed.txt'))\n"
              "print(f'{len(done)}/{len(JOBS)} jobs finished')\n"
              "print('missing:', [j for j in JOBS if j not in done])\n"
              "print('failed:', failed)\n"
              "for j in failed:\n"
              "    print(j, open(f'{D}/runs/preds/{j}.failed.txt').read()[-1500:])\n"
              "assert not failed, failed")
    cells = [cell("!nvidia-smi --query-gpu=name,memory.total --format=csv"), cell(MOUNT), cell(setup), cell(listing),
             cell(run), cell(status)]
    return {"cells": cells, "metadata": {**META, "colab": {**META["colab"], "name": f"{name}.ipynb"}}, "nbformat": 4,
            "nbformat_minor": 5}


def main():
    out = ROOT / "colab" / "experiments"
    for old in out.glob("E[789]_*.ipynb"):
        old.unlink()
    for name, jobs in aj.notebook_jobs().items():
        nb = build(name, jobs)
        (out / f"{name}.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
        print(name, len(jobs), "jobs")


if __name__ == "__main__":
    main()
