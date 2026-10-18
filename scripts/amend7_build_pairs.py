import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_pairs as ap
from ddiood import config

OUT = ROOT / "artifacts" / "amend7"


def main():
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    cov = json.loads((config.ARTIFACTS / "labels" / "coverage.json").read_text())
    ood = ap.read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv")
    old = ap.read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv")
    rows, counts, audit = ap.build_training_pairs(lookup, cov["vocab_label_found"], ood, old)
    ap.assert_no_leak(rows, lookup, ood, old, audit["excluded_vocab"])
    OUT.mkdir(parents=True, exist_ok=True)
    ap.write_rows(rows, OUT / "train_pairs.csv")
    report = {"counts": counts, "pairs_sha256": ap.rows_hash(rows), "audit": audit,
              "construction": "ddiood.ood.build_pairs with SemEval-vocabulary anchors, partner-matched negatives, "
                              f"at most {ap.MAX_POS_PER_DRUG} positives per anchor, seed {ap.SEED}"}
    (OUT / "train_pairs_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({"counts": counts, "sha": report["pairs_sha256"],
                      "snapshot_train": audit["snapshot_training_labels"]["earliest"],
                      "snapshot_train_latest": audit["snapshot_training_labels"]["latest"]}, indent=1))
    print("excluded vocab", len(audit["excluded_vocab"]))
    print("OOD drugs with an equivalent vocabulary drug", len(audit["ood_drugs_with_equivalent_vocab_drug"]),
          audit["ood_drugs_with_equivalent_vocab_drug"])


if __name__ == "__main__":
    main()
