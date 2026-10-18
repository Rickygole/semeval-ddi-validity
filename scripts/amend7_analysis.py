import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_analysis as aa
from ddiood import semeval
from ddiood.amend7_pairs import read_csv


def build_truth(corrected, ood_artifacts, amend7):
    ood = read_csv(Path(corrected) / "ood_pairs.csv")
    old = read_csv(Path(corrected) / "ood_old_pairs.csv")
    db_ood = read_csv(Path(ood_artifacts) / "drugbank_validation.csv")
    db_old = read_csv(Path(ood_artifacts) / "drugbank_validation_old.csv")
    sets = json.loads((Path(amend7) / "primary_sets.json").read_text())
    sens = sets["sensitivity_shingle"]
    semeval.download()
    test_y = [int(r["label_id"] != 0) for r in semeval.load_pairs("test")]
    truth = aa.Truth(ood, old, db_ood, db_old, {"novel": sens["novel"], "older_primary": sens["older_primary"]}, test_y)
    scores = {"ood": aa.drugbank_scores(inputs_pairs(ood), db_ood), "oodold": aa.drugbank_scores(inputs_pairs(old), db_old)}
    return truth, scores, sens


def inputs_pairs(rows):
    return [{"ood_drug": r["ood_drug"], "semeval_drug": r["semeval_drug"]} for r in rows]


def run(preds, cpu, corrected, ood_artifacts, amend7, which, n):
    truth, db_scores, sens = build_truth(corrected, ood_artifacts, amend7)
    manifest = json.loads((Path(amend7) / "manifest.json").read_text())
    out = {"bootstrap_draws": n, "seeds": aa.SEEDS}
    if "e7" in which:
        out["e7a"] = aa.e7a_verdict(preds, truth, n)
        out["e7b"] = aa.e7b_verdict(preds, truth, manifest["e7b_rule"], n)
        know = aa.knowledge_arms(preds, truth, cpu, n=n)
        out["knowledge"] = aa.add_kappas(know, truth, db_scores, n)
        drop = {"novel": sens["novel"], "older_primary": sens["older_primary"]}
        out["knowledge_sensitivity_drop_overlap"] = aa.knowledge_arms(preds, truth, cpu, n=n, drop=drop)
        out["arm_differences"] = aa.arm_differences(preds, truth, n)
        decisions = [out["e7a"].get("decision"), out["e7b"].get("decision")]
        verdict = ("pending" if any(str(d).startswith("pending") for d in decisions)
                   else "pass" if decisions == ["pass", "pass"] else "not passing")
        out["e7_summary"] = {"e7a": out["e7a"].get("decision"), "e7b": out["e7b"].get("decision"), "e7": verdict}
    if "e8" in which:
        out["e8_names"] = aa.names_prompts(preds, truth, n)
        out["e8_oracle_rule"] = aa.oracle_rule(preds, truth, cpu, n)
        out["e8_evidence"] = aa.evidence_arms(preds, truth, n)
        out["e8_stem_control"] = aa.stem_control(preds, truth, n)
    if "e9" in which:
        out["e9"] = aa.panel(preds, truth, truth.test_y, n)
    return aa.clean(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--cpu", default=str(ROOT / "artifacts" / "amend7" / "preds_cpu"))
    ap.add_argument("--corrected", default=str(ROOT / "results" / "corrected"))
    ap.add_argument("--ood-artifacts", default=str(ROOT / "artifacts" / "ood"))
    ap.add_argument("--amend7", default=str(ROOT / "artifacts" / "amend7"))
    ap.add_argument("--which", nargs="+", default=["e7", "e8", "e9"])
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run(a.preds, a.cpu, a.corrected, a.ood_artifacts, a.amend7, a.which, a.boot)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("e7_summary",) if k in res}, indent=1))


if __name__ == "__main__":
    main()
