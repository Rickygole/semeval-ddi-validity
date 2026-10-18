import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import beta

import rev3_common as rc
from ddiood import amend7_analysis as aa
from ddiood import rev3_tac as rt

MIN_DRUGS = 5
MIN_CLUSTER_LABELS = 10
BOOT = 2000
SEED = 42
TAC_ROOT = Path.home() / "rev3-tac-data"
FILES = {"novel": rc.ROOT / "artifacts" / "ood" / "ood_pairs.csv", "older": rc.ROOT / "artifacts" / "ood" / "ood_old_pairs.csv"}
COHORTS = (("novel", "novel", ()), ("older_clean", "older", aa.OLDER_ARTIFACTS), ("older_primary", "older", aa.OLDER_ARTIFACTS + aa.OLDER_MISSED))


def clopper_pearson(k, n, alpha=0.05):
    if not n:
        return None
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def read_pairs(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        lab = r["label"]
        y = int(lab) if lab.isdigit() else (0 if lab == "no_interaction_silver" else 1)
        out.append({"drug": r["ood_drug"], "partner": rt.norm(r["semeval_drug"]), "y": y})
    return out


def cohort_drugs(rows, excluded):
    return {rt.norm(r["drug"]) for r in rows if r["drug"] not in excluded}


def tac_labels(root):
    out = {}
    for s in rt.PRIMARY_SETS:
        out[s] = [x for x in rt.load_set(Path(root) / s) if x["di_text"]]
    return out


def first_word(name):
    return name.split()[0] if name.split() else name


def overlap_counts(cohort_names, tac_names_by_set):
    all_tac = set().union(*tac_names_by_set.values()) if tac_names_by_set else set()
    exact = cohort_names & all_tac
    return {"cohort_drugs": len(cohort_names), "exact_overlap": len(exact),
            "exact_overlap_by_tac_set": {s: len(cohort_names & v) for s, v in tac_names_by_set.items()},
            "first_word_overlap_count_only": len({first_word(n) for n in cohort_names} & {first_word(n) for n in all_tac})}


def agreement(pairs, gold_by_drug, vocab, drugs):
    pos = pos_gold = neg = neg_gold = recalled = gold_total = agree = n = 0
    per_drug = {}
    for d in sorted(drugs):
        mine = [r for r in pairs if rt.norm(r["drug"]) == d]
        gold = {k for k in gold_by_drug.get(d, ()) if k in vocab}
        ours_pos = {r["partner"] for r in mine if r["y"] == 1}
        c = {"n": len(mine), "pos": len(ours_pos), "pos_gold": len(ours_pos & gold), "neg": sum(r["y"] == 0 for r in mine),
             "neg_gold": sum(r["y"] == 0 and r["partner"] in gold for r in mine), "gold": len(gold), "recalled": len(gold & ours_pos),
             "agree": sum((r["y"] == 1) == (r["partner"] in gold) for r in mine)}
        per_drug[d] = c
    return per_drug


def totals(per_drug, names):
    t = {k: sum(per_drug[d][k] for d in names) for k in ("n", "pos", "pos_gold", "neg", "neg_gold", "gold", "recalled", "agree")}
    return t


def rates(t):
    def one(k, n):
        return {"k": int(k), "n": int(n), "value": k / n if n else None, "ci95_clopper_pearson": clopper_pearson(k, n)}
    return {"agreement": one(t["agree"], t["n"]), "precision_of_our_positives": one(t["pos_gold"], t["pos"]),
            "recall_of_tac_gold_by_our_positives": one(t["recalled"], t["gold"]),
            "our_negatives_listed_by_tac_gold": one(t["neg_gold"], t["neg"])}


def cluster_bootstrap(per_drug, n_boot=BOOT, seed=SEED):
    names = sorted(per_drug)
    rng = np.random.RandomState(seed)
    out = {"agreement": [], "precision_of_our_positives": [], "recall_of_tac_gold_by_our_positives": [], "our_negatives_listed_by_tac_gold": []}
    for _ in range(n_boot):
        pick = [names[i] for i in rng.randint(0, len(names), len(names))]
        t = totals(per_drug, pick)
        r = rates(t)
        for k in out:
            out[k].append(np.nan if r[k]["value"] is None else r[k]["value"])
    return {k: rc.pct(v) for k, v in out.items()}


def analyse(tac, cohort_pairs, n_boot=BOOT):
    names_by_set = {s: {rt.norm(x["drug"]) for x in labs} for s, labs in tac.items()}
    gold_by_drug = {}
    for labs in tac.values():
        for x in labs:
            keys = {k for k, v in x["positives"].items() if rt.partner_type(v["code"]) == "substance"}
            gold_by_drug.setdefault(rt.norm(x["drug"]), set()).update(keys)
    res = {"minimum_overlapping_drugs": MIN_DRUGS, "minimum_labels_for_cluster_bootstrap": MIN_CLUSTER_LABELS,
           "match_rule": "TAC label drug and OOD drug equal after lowercase and whitespace collapse (`rev3_tac.norm`); first-word overlap is a count only",
           "tac_labels_with_di_section": {s: len(v) for s, v in names_by_set.items()}, "cohorts": {}}
    ok = False
    for cname, (pairs, drugs_all) in cohort_pairs.items():
        c = overlap_counts(drugs_all, names_by_set)
        c["check_possible"] = c["exact_overlap"] >= MIN_DRUGS
        if c["check_possible"]:
            ok = True
            overlap = drugs_all & set().union(*names_by_set.values())
            vocab = {r["partner"] for rows, _ in cohort_pairs.values() for r in rows}
            per = agreement(pairs, gold_by_drug, vocab, overlap)
            c["pooled"] = rates(totals(per, sorted(per)))
            if len(per) >= MIN_CLUSTER_LABELS:
                c["label_cluster_bootstrap_ci95"] = cluster_bootstrap(per, n_boot)
        res["cohorts"][cname] = c
    res["check_possible"] = ok
    if not ok:
        res["note"] = ("No cohort has at least the minimum number of overlapping drugs under the exact-name rule, so the check is not possible; "
                       "no agreement figure was computed.")
    return res


def md(o):
    L = ["# D7: human-gold check of the label rule against TAC 2018", "", f"Status: {rc.STATUS}.", "",
         f"Match rule: {o['match_rule']}. Minimum: {o['minimum_overlapping_drugs']} overlapping drugs in a cohort. "
         f"TAC labels with a Drug Interactions section: {o['tac_labels_with_di_section']}.", "", f"Check possible: {o['check_possible']}.", ""]
    rows = [[k, c["cohort_drugs"], c["exact_overlap"], c["exact_overlap_by_tac_set"], c["first_word_overlap_count_only"], c["check_possible"]]
            for k, c in o["cohorts"].items()]
    L += rc.table(["cohort", "OOD drugs", "exact overlap", "by TAC set", "first-word overlap (count only)", "check possible"], rows) + [""]
    if o.get("note"):
        L += [o["note"], ""]
    for k, c in o["cohorts"].items():
        if "pooled" in c:
            L += [f"## {k}", ""]
            L += rc.table(["statistic", "k", "n", "value", "Clopper-Pearson 95%", "label-cluster bootstrap 95%"],
                          [[s, r["k"], r["n"], rc.f3(r["value"]), rc.ci(r["ci95_clopper_pearson"]), rc.ci(c.get("label_cluster_bootstrap_ci95", {}).get(s))]
                           for s, r in c["pooled"].items()]) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tac", default=str(TAC_ROOT))
    a = ap.parse_args()
    files = {k: read_pairs(v) for k, v in FILES.items()}
    cohort_pairs = {}
    for cname, key, excl in COHORTS:
        rows = [r for r in files[key] if r["drug"] not in excl]
        cohort_pairs[cname] = (rows, cohort_drugs(files[key], excl))
    o = analyse(tac_labels(a.tac), cohort_pairs)
    rc.write("d7_tac_overlap", o, md(o))
    print(md(o))


if __name__ == "__main__":
    main()
