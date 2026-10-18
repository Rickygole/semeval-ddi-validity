import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import rev2_jobs as rj

META = json.loads((ROOT / "colab" / "experiments" / "E5_llm_baselines.ipynb").read_text())["metadata"]
PIP = {"R2a": "pip -q install accelerate sentencepiece protobuf", "R2b": "pip -q install bitsandbytes accelerate"}

MOUNT = """import os
from google.colab import drive
drive.mount('/content/drive')
D = '/content/drive/MyDrive/temporal-ood-ddi'
os.makedirs(f'{D}/runs/preds', exist_ok=True)
os.makedirs(f'{D}/weights', exist_ok=True)
print(D)"""

GPU = """import torch
assert torch.cuda.is_available(), 'no GPU: switch the runtime to a GPU and rerun'
print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"""

GPU_R2B = GPU + """
assert torch.cuda.get_device_capability(0)[0] >= 8, 'no native bfloat16: use an L4 or A100 runtime'"""

FLUSH = """from google.colab import drive
drive.flush_and_unmount()"""


def cell(src):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "source": source, "outputs": [], "execution_count": None}


def build(name, jobs):
    pip = PIP[name.split("_")[0]]
    listing = "JOBS = [\n" + ",\n".join(f' "{n}"' for n in jobs) + "\n]"
    setup = (f"!mkdir -p /content/w && cp {{D}}/rev2_bundle.tgz /content/rev2_bundle.tgz && tar xzf /content/rev2_bundle.tgz -C /content/w && cp {{D}}/inputs.json.gz /content/w/\n"
             f"!{pip}\n%cd /content/w")
    run = ("%cd /content/w\n!bash -c \"set -o pipefail; python -m ddiood.rev2_jobs run --workdir /content/w --out {D}/runs "
           "--weights {D}/weights --only {' '.join(JOBS)} "
           f"2>&1 | tee -a {{D}}/runs/r2-{name}.log | (grep --line-buffered -E '^(start|done|skip|FAILED)|Error|Traceback'; true)\"")
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
    if name.startswith("R2a"):
        status += ("\nno_weights = [j for j in done if not os.path.isdir(f'{D}/weights/{j}')]\n"
                   "print('finished without saved weights:', no_weights)\n"
                   "assert not no_weights, no_weights")
    gpu = GPU_R2B if name.startswith("R2b") else GPU
    cells = [cell("!nvidia-smi --query-gpu=name,memory.total --format=csv"), cell(gpu), cell(MOUNT), cell(setup),
             cell(listing), cell(run), cell(status), cell(FLUSH)]
    return {"cells": cells, "metadata": {**META, "colab": {**META["colab"], "name": f"{name}.ipynb"}}, "nbformat": 4,
            "nbformat_minor": 5}


def main():
    out = ROOT / "colab" / "experiments"
    for name, jobs in rj.notebook_jobs().items():
        nb = build(name, jobs)
        (out / f"{name}.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
        print(name, len(jobs), "jobs")


if __name__ == "__main__":
    main()
