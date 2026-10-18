import argparse
import json
from pathlib import Path

import numpy as np

from sens_common import ROOT, ci, ev, f3, write
from ddiood import drugbank, semeval

DEFAULT_ZIP = Path.home() / "Downloads" / "drugbank_all_full_database.xml.zip"
EXP5 = ROOT / "results" / "revision" / "amend7" / "cpu" / "exp5_dissociation.json"


def row(name, y, s, groups, boot, seed):
    lo, hi = ev.interval(ev.boot_auroc(y, s, groups, None, boot, seed))
    return {"subset": name, "n": int(len(y)), "n_pos": int(np.sum(y)), "listed": int(np.sum(s)),
            "auroc": ev.auroc(y, s), "ci95": [lo, hi]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(DEFAULT_ZIP))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    table = drugbank.load_interactions(a.drugbank)
    lookup = json.loads((ROOT / "artifacts" / "vocab" / "drug_lookup.json").read_text())
    semeval.download()
    test = semeval.load_pairs("test")
    truth = ev.load_truth()
    y = np.asarray(truth.test_y)
    if [int(r["label_id"] != 0) for r in test] != list(y):
        raise ValueError("SemEval test order differs from the evaluation truth")
    pairs = [{"ood_drug": r["drug_a"], "semeval_drug": r["drug_b"], "label": int(r["label_id"] != 0)} for r in test]
    rows, _ = drugbank.validate(pairs, table, lookup)
    score = np.asarray([1.0 if r["drugbank_label"] == "positive" else 0.0 for r in rows])
    sid = np.asarray([r["sentence_id"] for r in test])
    selfpair = np.asarray([drugbank._norm(r["drug_a"]) == drugbank._norm(r["drug_b"]) for r in test])
    exact_self = np.asarray([r["drug_a"] == r["drug_b"] for r in test])
    res = [row("all pairs, unresolvable counted as not listed", y, score, sid, a.boot, a.seed),
           row("excluding self pairs", y[~selfpair], score[~selfpair], sid[~selfpair], a.boot, a.seed),
           row("self pairs only", y[selfpair], score[selfpair], sid[selfpair], a.boot, a.seed)]
    out = {"status": "sensitivity analysis, post hoc; the amend7 exp5 output is not changed",
           "method": "DrugBank lookup with the preregistered resolution of ddiood.drugbank.validate on the 2,810 SemEval 2013 "
                     "test pairs; score 1 if DrugBank lists the pair; pooled AUROC against the binary SemEval label with a "
                     "bootstrap over sentences; a self pair names the same drug on both sides (case and space normalised)",
           "boot": a.boot, "seed": a.seed, "n_self_pairs": int(selfpair.sum()), "n_self_pairs_exact_string": int(exact_self.sum()),
           "self_pairs_positive": int(y[selfpair].sum()), "self_pairs_listed": int(score[selfpair].sum()), "rows": res}
    if EXP5.exists():
        e5 = {r["subset"]: r for r in json.loads(EXP5.read_text()).get("auroc", [])}
        if e5:
            out["agrees_with_exp5"] = {r["subset"]: (round(r["auroc"], 6) == e5[r["subset"]]["auroc"]) for r in res if r["subset"] in e5}
    md = ["# SemEval self pairs and the DrugBank lookup", "",
          f"{out['n_self_pairs']} of {len(y)} SemEval test pairs name the same drug twice; {out['self_pairs_positive']} of them are "
          f"positive and DrugBank lists {out['self_pairs_listed']}. Sentence bootstrap, {a.boot} draws, seed {a.seed}.", "",
          "Self pairs are negatives the lookup never lists, so they enter as correctly ranked negatives and raise the "
          "all-pairs AUROC; the lookup AUROC on genuine two-drug pairs is the row that excludes them.", "",
          "| subset | n | n_pos | listed | lookup AUROC | 95% CI |", "| --- | --- | --- | --- | --- | --- |"]
    md += [f"| {r['subset']} | {r['n']} | {r['n_pos']} | {r['listed']} | {f3(r['auroc'])} | {ci(r['ci95'])} |" for r in res]
    if out.get("agrees_with_exp5"):
        md += ["", "Agreement with `results/revision/amend7/cpu/exp5_dissociation.json` (AUROC to 4 decimals): " +
               ", ".join(f"{k}: {v}" for k, v in out["agrees_with_exp5"].items()) + "."]
    write("semeval_selfpairs", out, "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
