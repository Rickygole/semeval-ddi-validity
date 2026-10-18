import argparse

import numpy as np

import rev3_common as rc
import rev2_analyze_a as an
from ddiood import amend7_analysis as aa
from ddiood import amend7_data as ad
from ddiood import semeval
from ddiood import evaluate2 as ev

PREDS = rc.ROOT / "runs" / "preds"
R2A = rc.ROOT / "results" / "revision" / "rev2_colab" / "r2a.json"
TRAIN = rc.ROOT / "artifacts" / "amend7" / "train_pairs.csv"
SEED = 42
FORMS = (("names_only", an.COHORT_KEY), ("names_text_b1", an.NAMES_FORM_KEY))


class NoTruth:
    def cohort(self, name):
        return None


def load_context():
    rows = [ad.Data._train_row(x) for x in ad.read_rows_csv(TRAIN)]
    semeval.download()
    sem = semeval.load_pairs("train")
    overlap, outside = an.overlap_summary(rows, an.semeval_pair_index(sem))
    coh = an.cohorts(NoTruth(), rows, outside)
    seen, out = coh["seen"], coh["seen_not_in_semeval_train"]
    inside = ~np.asarray(outside, bool)
    coh3 = {"seen": seen, "seen_not_in_semeval_train": out,
            "seen_in_semeval_train": {"y": seen["y"][inside], "g": seen["g"][inside], "q": seen["q"][inside], "mask": inside, "name": "seen"}}
    return rows, sem, overlap, coh3


def contributing_anchors(c):
    y, g = np.asarray(c["y"]), np.asarray(c["g"])
    return int(sum(1 for d in set(g) if 0 < y[g == d].sum() < (g == d).sum()))


def meta(c):
    anchors, partners = set(c["g"]), set(c["q"])
    return {"n_pairs": int(len(c["y"])), "n_positive": int(np.sum(c["y"])), "n_anchor_drugs": len(anchors), "n_anchor_drugs_with_both_classes": contributing_anchors(c),
            "n_partner_drugs": len(partners), "n_drugs_both_anchor_and_partner": len(anchors & partners)}


def intervals(c, p, n):
    y = c["y"]
    s = an.view(c, p)
    w = an.within(c, p, n)
    d1 = aa.draws(y, [s], c["g"], np.zeros(len(y), int), n, an.BOOT[c["name"]], "within")[0]
    o = aa.summ(aa.point(y, s, c["g"], "within"), d1)
    return {"pooled_auroc": float(ev.auroc(y, s)), "within_drug_auroc": w["value"], "within_ci95_two_way": [w["lo95"], w["hi95"]],
            "within_ci95_anchor_only": [o["lo95"], o["hi95"]], "n_draws_two_way": w["n_draws"], "n_draws_anchor_only": o["n_draws"]}


def family_rows(coh, n, preds=PREDS):
    rows = []
    for family in an.FAMILIES:
        for cname, c in coh.items():
            for form, keymap in FORMS:
                if form == "names_text_b1" and family == "marker":
                    continue
                p, have, per = an.seed_p(preds, family, keymap["seen"])
                if p is None:
                    continue
                per_within = [aa.point(c["y"], an.view(c, x), c["g"], "within") for x in per]
                rows.append({"family": family, "cohort": cname, "input": form, "seeds": have, "complete": sorted(have) == sorted(an.SEEDS),
                             **intervals(c, p, n), "per_seed_within": [float(x) for x in per_within]})
    return rows


def check_against_r2a(rows):
    stored = {(r["family"], r["cohort"], r["input"]): r for r in rc.load(R2A)["dissociation"] if r["cohort"].startswith("seen")}
    out = []
    for r in rows:
        k = (r["family"], r["cohort"], r["input"])
        if k in stored:
            sm = stored[k]["seed_mean"]
            out.append({"family": k[0], "cohort": k[1], "input": k[2],
                        "point_matches": bool(abs(r["within_drug_auroc"] - sm["value"]) < 5e-7),
                        "interval_matches": bool(abs(r["within_ci95_two_way"][0] - sm["lo95"]) < 5e-7 and abs(r["within_ci95_two_way"][1] - sm["hi95"]) < 5e-7)})
    return out


def md(res):
    L = ["# D3: R2a on the seen pairs that are in SemEval train", "", f"Status: {rc.STATUS}.", "",
         f"Overlap: {res['overlap']}", "", "Within-drug AUROC by anchor drug, seed mean over the seeds present, bootstrap seed 42, 1,000 draws. Anchor drugs with one class only do not contribute to the within-drug AUROC; their number is shown.", ""]
    for cname, m in res["cohorts"].items():
        L += [f"## Cohort {cname}", "", f"{m['n_pairs']} pairs, {m['n_positive']} positive, {m['n_anchor_drugs']} anchor drugs ({m['n_anchor_drugs_with_both_classes']} with both classes), "
              f"{m['n_partner_drugs']} partner drugs, {m['n_drugs_both_anchor_and_partner']} drugs act as both anchor and partner.", ""]
        body = [[r["family"], r["input"], ",".join(map(str, r["seeds"])), r["complete"], rc.f3(r["pooled_auroc"]), rc.f3(r["within_drug_auroc"]), rc.ci(r["within_ci95_two_way"]),
                 rc.ci(r["within_ci95_anchor_only"]), ", ".join(f"{x:.3f}" for x in r["per_seed_within"])] for r in res["rows"] if r["cohort"] == cname]
        L += rc.table(["family", "input", "seeds", "complete", "pooled AUROC", "within-drug AUROC", "95% two-way", "95% anchor only", "per-seed within"], body) + [""]
    ok = all(c["point_matches"] and c["interval_matches"] for c in res["r2a_reproduction"])
    L += [f"Existing r2a.json two-way points and intervals reproduced for {len(res['r2a_reproduction'])} rows: {ok}.", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    rows, sem, overlap, coh = load_context()
    out = family_rows(coh, a.boot)
    res = {"overlap": overlap, "cohorts": {k: meta(c) for k, c in coh.items()}, "rows": out, "r2a_reproduction": check_against_r2a(out), "n_boot": a.boot, "seed": SEED}
    rc.write("d3_r2a_overlap", res, md(res))
    print(rc.OUT / "d3_r2a_overlap.md")


if __name__ == "__main__":
    main()
