import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rev3_common as rc

from ddiood import amend7_prompts as pr
from ddiood import rev2_adjudicator as ra
from ddiood import rev3_jobs as rj
from ddiood import rev3_tac as rt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tac-dir", default=str(Path.home() / "rev3-tac-data"))
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ra.OLMO, revision=ra.OLMO_REVISION)
    items, sections = rt.build_all(rt.fetch(a.tac_dir))
    per_set, total, chunked = {}, 0, {}
    for name in sorted({i["set"] for i in items}):
        sub = [i for i in items if i["set"] == name]
        tokens, prompts, nchunk = 0, 0, 0
        for drug, partner in ra.unique_keys(sub):
            chunks = ra.fit_chunks(tok, drug, sections[name][drug]["text"], partner)
            nchunk += len(chunks) > 1
            for c in chunks:
                tokens += ra.n_tokens(tok, pr.chat(tok, ra.build_prompt(drug, c, partner)))
                prompts += 1
        per_set[name] = {"items": len(sub), "prompts_including_chunks": prompts, "prompt_tokens": tokens, "items_with_more_than_one_chunk": nchunk}
        chunked[name] = nchunk
        if name in rt.PRIMARY_SETS + rt.SENSITIVITY_SETS:
            total += tokens
    est = {"per_set": per_set, "total_tokens": total, "items_sha256": rt.items_sha256(items), "estimate": rj.estimates(total),
           "tokenizer": {"repo": ra.OLMO, "revision": ra.OLMO_REVISION}, "notebook_hours_cap": rj.NOTEBOOK_HOURS_CAP}
    rc.write("c4_time_estimate", est, None)
    print(json.dumps(est, indent=1))


if __name__ == "__main__":
    main()
