import datetime
import json
import re
import sys
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_panel as pn
from ddiood.amend7_jobs import QWEN

OUT = ROOT / "artifacts" / "amend7" / "panel_manifest.json"
CASED_SHARE = 0.05


def casing(repo, rev, files):
    if "vocab.txt" not in files:
        return {"vocab_upper_share": None, "wordpiece": False, "do_lower_case": None}
    vocab = open(hf_hub_download(repo, "vocab.txt", revision=rev), encoding="utf8").read().split("\n")
    share = sum(1 for t in vocab if re.match(r"^(##)?[A-Z]", t)) / len(vocab)
    return {"vocab_upper_share": round(share, 4), "wordpiece": True, "do_lower_case": share < CASED_SHARE}


def main():
    api = HfApi()
    out = {}
    for bid, repo in pn.BACKBONES:
        info = api.model_info(repo)
        files = [s.rfilename for s in info.siblings]
        entry = {"id": bid, "sha": info.sha, "gated": info.gated, "private": info.private,
                 "has_safetensors": any(f.endswith(".safetensors") for f in files),
                 "has_pytorch_bin": any(f.endswith(".bin") for f in files)}
        entry.update(casing(repo, info.sha, files))
        out[repo] = entry
        print(repo, info.sha[:10], entry["do_lower_case"], entry["vocab_upper_share"])
    out["_qwen"] = {"repo": QWEN, "sha": api.model_info(QWEN).sha}
    out["_verified_on"] = datetime.date.today().isoformat()
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
