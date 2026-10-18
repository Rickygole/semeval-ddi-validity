import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import rev3b_jobs as rj

META = json.loads((ROOT / "colab" / "experiments" / "E5_llm_baselines.ipynb").read_text())["metadata"]
PIP = "pip -q install accelerate sentencepiece protobuf"

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

FLUSH = """from google.colab import drive
drive.flush_and_unmount()"""


def cell(src):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "source": source, "outputs": [], "execution_count": None}


def build(name, jobs):
    listing = "JOBS = [\n" + ",\n".join(f' "{n}"' for n in jobs) + "\n]"
    setup = (f"!mkdir -p /content/w && cp {{D}}/rev3b_bundle.tgz /content/rev3b_bundle.tgz && tar xzf /content/rev3b_bundle.tgz -C /content/w && cp {{D}}/inputs.json.gz /content/w/\n"
             f"!{PIP}\n%cd /content/w")
    check = ("import json, os, sys\n"
             "sys.path.insert(0, '/content/w')\n"
             "from ddiood import amend7_panel as pn, gpu_jobs, rev3b_jobs as rj\n"
             "rj.assert_frozen()\n"
             "inp = gpu_jobs.Inputs('/content/w/inputs.json.gz')\n"
             "pn.attach_offsets(inp.test, pn.load_offsets('test'))\n"
             "texts, fallback = rj.build_inputs(inp)\n"
             "assert rj.inputs_sha256(texts) == rj.EXPECTED_INPUTS_SHA256, 'the input texts differ from the frozen input list'\n"
             "print(len(inp.test), 'test pairs', rj.inputs_sha256(texts), fallback)\n"
             "for c in rj.registry():\n"
             "    w = f\"{D}/weights/{c['weights_name']}\"\n"
             "    assert os.path.isdir(w), f'missing saved weights {w}'\n"
             "    stored = json.load(open(f\"{D}/runs/preds/{c['weights_name']}.json\"))\n"
             "    assert rj.file_sha256(rj.weight_file(w)) == stored['weights']['weight_sha256'], f'weight sha256 differs for {w}'\n"
             "print('weights present and equal to the stored sha256 for', len(rj.registry()), 'seeds')")
    run = ("%cd /content/w\n!bash -c \"set -o pipefail; python -m ddiood.rev3b_jobs run --workdir /content/w --out {D}/runs "
           "--weights {D}/weights --only {' '.join(JOBS)} "
           f"2>&1 | tee -a {{D}}/runs/r3b-{name}.log | (grep --line-buffered -E '^(start|done|skip|FAILED)|Error|Traceback'; true)\"")
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
    cells = [cell("!nvidia-smi --query-gpu=name,memory.total --format=csv"), cell(GPU), cell(MOUNT), cell(setup), cell(listing),
             cell(check), cell(run), cell(status), cell(FLUSH)]
    return {"cells": cells, "metadata": {**META, "colab": {**META["colab"], "name": f"{name}.ipynb"}}, "nbformat": 4, "nbformat_minor": 5}


def main():
    out = ROOT / "colab" / "experiments"
    for name, jobs in rj.notebook_jobs().items():
        (out / f"{name}.ipynb").write_text(json.dumps(build(name, jobs), indent=1) + "\n")
        print(name, len(jobs), "jobs")


if __name__ == "__main__":
    main()
