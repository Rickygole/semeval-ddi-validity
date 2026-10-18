import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_prompts as pr
from ddiood import inputs
from ddiood import rev2_adjudicator as ra
from ddiood import rev2_data as rd
from ddiood import rev2_jobs as rj

A7 = ROOT / "artifacts" / "amend7"


def items_and_sections(inputs_gz):
    base = json.load(gzip.open(inputs_gz, "rt"))
    ood = inputs.ood_as_pairs(base["ood_pairs"])
    old = inputs.ood_as_pairs(base["ood_old_pairs"])
    sets = json.loads((A7 / "primary_sets.json").read_text())
    excluded = set(sets["older_artifacts"]) | set(sets["older_missed_vocabulary_drugs"])
    sheet = rd.read_sheet(ROOT / "results" / "revision" / "post8" / "label_audit_sheet.csv")
    sections = json.loads((A7 / "di_sections.json").read_text())
    return ra.all_items(sheet, ood, old, excluded), sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default=str(ROOT / "artifacts" / "bundle" / "inputs.json.gz"))
    ap.add_argument("--tokenizer-dir", required=True)
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "rev2" / "time_estimates.json"))
    a = ap.parse_args()
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    path = snapshot_download(ra.OLMO, revision=ra.OLMO_REVISION, allow_patterns=["*.json", "merges.txt"],
                             ignore_patterns=["*safetensors*"], local_dir=a.tokenizer_dir)
    tok = AutoTokenizer.from_pretrained(path)
    items, sections = items_and_sections(a.inputs)
    keys = ra.unique_keys(items)
    total, chunked = 0, {}
    for drug, partner in keys:
        chunks = ra.fit_chunks(tok, drug, sections[drug]["text"], partner)
        if len(chunks) > 1:
            chunked[drug] = len(chunks)
        for c in chunks:
            total += ra.n_tokens(tok, pr.chat(tok, ra.build_prompt(drug, c, partner)))
    est = rj.estimates(r2b_tokens=total)
    est["r2b"] = {"n_items": len(items), "n_unique_prompts": len(keys), "tokens": total, "chunked_drugs": chunked,
                  "n_in_both_sets": len({(x["ood_drug"], x["partner"]) for x in items if x["set"] == "audit"} &
                                        {(x["ood_drug"], x["partner"]) for x in items if x["set"] == "random"})}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(est, indent=1))
    print(json.dumps({"notebooks": est["notebooks"], "r2b": est["r2b"]}, indent=1))
    print(json.dumps({k: v for k, v in est["jobs"].items()}, indent=0))


if __name__ == "__main__":
    main()
