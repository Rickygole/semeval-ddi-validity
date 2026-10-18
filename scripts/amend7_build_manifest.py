import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_pairs as ap
from ddiood import amend7_prompts as pr
from ddiood import inputs

OUT = ROOT / "artifacts" / "amend7"


def main():
    ood = inputs.ood_as_pairs(ap.read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv"))
    old = inputs.ood_as_pairs(ap.read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv"))
    train = ap.read_rows(OUT / "train_pairs.csv")
    panel = json.loads((OUT / "panel_manifest.json").read_text())
    hub = json.loads((OUT / "hub_candidates.json").read_text())
    audit = json.loads((OUT / "input_audit.json").read_text())
    manifest = {"ood_hash": inputs.pairs_hash(ood), "ood_old_hash": inputs.pairs_hash(old),
                "train_hash": inputs.pairs_hash([{"drug_a": r["drug_a"], "drug_b": r["drug_b"], "y": r["y"]} for r in train]),
                "prompts_sha256": pr.frozen_hash(), "panel_revisions": {k: v["sha"] for k, v in panel.items() if not k.startswith("_")},
                "panel_lowercase": {k: v["do_lower_case"] for k, v in panel.items() if not k.startswith("_")},
                "qwen_revision": panel["_qwen"]["sha"], "external_facts": hub["external_subset"]["facts"],
                "panel_verified_on": panel["_verified_on"], "external_revisions": hub["external_subset"]["revisions"],
                "hub_searched_on": hub["searched_on"], "e7b_rule": audit["e7b_rule"],
                "label_snapshot_ood": audit["labels_snapshot"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps({k: manifest[k] for k in ("ood_hash", "ood_old_hash", "train_hash", "prompts_sha256")}, indent=1))


if __name__ == "__main__":
    main()
