import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import audit, config
from ddiood.baselines import _novel_label
from ddiood.inputs import ood_as_pairs, pairs_hash
from ddiood.openfda import LabelStore, section_text

OUT = ROOT / "results" / "revision" / "audit"
PAIRS = ROOT / "results" / "corrected" / "ood_pairs.csv"

H1, H2 = "#" + " ", "##" + " "
GUIDE = "\n".join([
    H1 + 'Two-annotator label audit',
    '',
    'Built by `python scripts/audit_sheet.py`. Scored by `python scripts/audit_kappa.py` once both annotators have finished.',
    '',
    H2 + 'Files',
    '',
    '* `audit_sheet.csv`: the items. Each annotator works on a separate copy, saved as `annotator_1.csv` or `annotator_2.csv` in this folder.',
    '* `answer_key.csv`: the FDA-derived label of each item. Annotators must not open it. Only `scripts/audit_kappa.py` reads it.',
    '* `manifest.json`: sampling settings and SHA-256 hashes of the sheet, the key and the frozen pair file.',
    '',
    H2 + 'Task',
    '',
    "Each row names a novel drug and a partner drug. The row gives the novel drug's Drug Interactions section as stored in the local openFDA snapshot, and an openFDA query link to the full label. Decide whether the label says that taking the two drugs together calls for clinical action. Judge each row on its own, from the label only. Do not add interactions from memory or from other sources. Annotators work independently and do not discuss items.",
    '',
    'Fill in four columns:',
    '',
    '* `annotator`: your initials.',
    '* `interacts`: `yes` if the label states or clearly implies that co-administration changes exposure or effect, or requires avoiding, monitoring or a dose change; `no` if the label does not mention the partner or a class it belongs to in an interaction context, or reports no clinically relevant effect; `unsure` if you cannot decide within a few minutes.',
    '* `basis`: `named` if the partner is named in an interaction statement; `class-level` if only a class is named (for example "strong CYP3A inhibitors") and the label\'s own wording places the partner in it; `none` if nothing in the label connects the two. A partner that was studied and showed no effect is `interacts = no`, `basis = named`.',
    '* `notes`: optional, for example the section or sentence you relied on.',
    '',
    H2 + 'Scoring',
    '',
    "`scripts/audit_kappa.py` reports Cohen's kappa on items where neither annotator chose `unsure` (with the number dropped), kappa with `unsure` as a third category, 95% bootstrap intervals over items, the annotator-by-annotator table, and the agreement of each annotator and of the consensus with the FDA label. Tier C is the set of items on which both annotators chose the same `yes` or `no`. There is no third rater; disagreements are excluded from tier C and counted.",
    '',
])


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-pos", type=int, default=50)
    ap.add_argument("--n-neg", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("annotator_1.csv", "annotator_2.csv"):
        if (out / name).exists():
            raise SystemExit(f"{name} exists; the sheet is frozen once annotation has started")
    rows = audit.read_csv(PAIRS)
    items = audit.sample(rows, a.n_pos, a.n_neg, a.seed)
    store = LabelStore(offline=True)
    di = {}
    for d in sorted({it["ood_drug"] for it in items}):
        di[d] = section_text(_novel_label(store, d), config.HOLDOUT_SECTION)
    missing = sorted(d for d, t in di.items() if not t)
    audit.write_csv(out / "audit_sheet.csv", audit.sheet_rows(items, di), audit.SHEET_FIELDS)
    audit.write_csv(out / "answer_key.csv", audit.key_rows(items), ["item_id", "novel_drug", "partner", "fda_label"])
    (out / "GUIDELINES.md").write_text(GUIDE)
    manifest = {"pairs_file": str(PAIRS.relative_to(ROOT)), "pairs_sha256": sha256(PAIRS),
                "pairs_hash": pairs_hash(ood_as_pairs(rows)), "n_pos": a.n_pos, "n_neg": a.n_neg, "seed": a.seed,
                "sampling": "round robin over novel drugs within each class, drug order and rows shuffled with the seed, "
                            "then the combined list shuffled",
                "n_items": len(items), "n_novel_drugs": len({it["ood_drug"] for it in items}),
                "n_novel_drugs_positive": len({it["ood_drug"] for it in items if it["label"] == "1"}),
                "n_novel_drugs_negative": len({it["ood_drug"] for it in items if it["label"] == "0"}),
                "drugs_without_local_di_section": missing,
                "audit_sheet_sha256": sha256(out / "audit_sheet.csv"), "answer_key_sha256": sha256(out / "answer_key.csv")}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
