import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import rev3_jobs as rj

META = json.loads((ROOT / "colab" / "experiments" / "E5_llm_baselines.ipynb").read_text())["metadata"]
PIP = "pip -q install bitsandbytes accelerate"

MOUNT = """import os
from google.colab import drive
drive.mount('/content/drive')
D = '/content/drive/MyDrive/temporal-ood-ddi'
os.makedirs(f'{D}/runs/preds', exist_ok=True)
os.makedirs(f'{D}/tac2018', exist_ok=True)
print(D)"""

GPU = """import torch
assert torch.cuda.is_available(), 'no GPU: switch the runtime to a GPU and rerun'
print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))
assert torch.cuda.get_device_capability(0)[0] >= 8, 'no native bfloat16: use an L4 or A100 runtime'"""

FLUSH = """from google.colab import drive
drive.flush_and_unmount()"""


def cell(src):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "source": source, "outputs": [], "execution_count": None}


def build(name, jobs):
    listing = "JOBS = [\n" + ",\n".join(f' "{n}"' for n in jobs) + "\n]"
    setup = (f"!mkdir -p /content/w && cp {{D}}/rev3_bundle.tgz /content/rev3_bundle.tgz && tar xzf /content/rev3_bundle.tgz -C /content/w\n"
             f"!{PIP}\n%cd /content/w")
    check = ("import hashlib, json, sys\n"
             "sys.path.insert(0, '/content/w')\n"
             "from ddiood import rev2_adjudicator as ra, rev3_jobs as rj, rev3_tac as rt\n"
             "assert ra.prompt_sha256() == ra.EXPECTED_PROMPT_SHA256, 'frozen R2b prompt hash differs'\n"
             "assert ra.OLMO_REVISION == rj.PLAN_OLMO_REVISION, 'model revision differs from the plan'\n"
             "dirs = rt.fetch(f'{D}/tac2018')\n"
             "items, sections = rt.build_all(dirs)\n"
             "assert rt.items_sha256(items) == rj.EXPECTED_TAC_ITEMS_SHA256, 'TAC item list differs from the frozen list'\n"
             "print(len(items), 'items', rt.items_sha256(items))")
    run = ("%cd /content/w\n!bash -c \"set -o pipefail; python -m ddiood.rev3_jobs run --tac-dir {D}/tac2018 --out {D}/runs "
           "--only {' '.join(JOBS)} "
           f"2>&1 | tee -a {{D}}/runs/r3-{name}.log | (grep --line-buffered -E '^(start|done|skip|FAILED)|Error|Traceback'; true)\"")
    status = ("import os\n"
              "done = sorted(j for j in JOBS if os.path.exists(f'{D}/runs/preds/{j}.json'))\n"
              "failed = sorted(j for j in JOBS if os.path.exists(f'{D}/runs/preds/{j}.failed.txt'))\n"
              "print(f'{len(done)}/{len(JOBS)} jobs finished')\n"
              "print('missing:', [j for j in JOBS if j not in done])\n"
              "print('failed:', failed)\n"
              "for j in failed:\n"
              "    print(j, open(f'{D}/runs/preds/{j}.failed.txt').read()[-1500:])\n"
              "assert not failed, failed\n"
              "assert len(done) == len(JOBS), [j for j in JOBS if j not in done]")
    cells = [cell("!nvidia-smi --query-gpu=name,memory.total --format=csv"), cell(GPU), cell(MOUNT), cell(setup), cell(listing), cell(check),
             cell(run), cell(status), cell(FLUSH)]
    return {"cells": cells, "metadata": {**META, "colab": {**META["colab"], "name": f"{name}.ipynb"}}, "nbformat": 4, "nbformat_minor": 5}


def main():
    out = ROOT / "colab" / "experiments"
    for name, jobs in rj.notebook_jobs().items():
        (out / f"{name}.ipynb").write_text(json.dumps(build(name, jobs), indent=1) + "\n")
        print(name, len(jobs), "jobs")


if __name__ == "__main__":
    main()
