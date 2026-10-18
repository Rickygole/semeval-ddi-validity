import argparse
import json
from collections import Counter

import numpy as np

import rev3_common as rc
import rev2_analyze_a as an
import rev2_m3b as m3b
from amend7_cpu_exp5_dissociation import resolve
from ddiood import amend7_analysis as aa
from ddiood import amend7_data as ad
from ddiood import baselines, config, semeval
from ddiood import evaluate2 as ev
from ddiood.openfda import LabelStore

R2A = rc.ROOT / "results" / "revision" / "rev2_colab" / "r2a.json"
SEED = 42


class NoTruth:
    def cohort(self, name):
        return None


def smoothed(pos, neg):
    return (pos + 1) / (pos + neg + 2)


def lodo_rates(train_idx, rows):
    pos, neg = Counter(), Counter()
    by_anchor, by_partner = {}, {}
    for i in train_idx:
        r = rows[i]
        (pos if r["y"] else neg)[r["drug_b"]] += 1
        by_anchor.setdefault(r["drug_a"], []).append(i)
        by_partner.setdefault(r["drug_b"], []).append(i)
    return pos, neg, by_anchor, by_partner


def lodo_scores(rows, train_idx):
    pos, neg, by_anchor, by_partner = lodo_rates(train_idx, rows)
    score = np.zeros(len(rows))
    for i, r in enumerate(rows):
        A, y = r["drug_a"], r["drug_b"]
        p, n = pos[y], neg[y]
        for j in by_anchor.get(A, ()):
            if rows[j]["drug_b"] == y:
                if rows[j]["y"]:
                    p -= 1
                else:
                    n -= 1
        for j in by_partner.get(A, ()):
            if rows[j]["drug_b"] == y:
                if rows[j]["y"]:
                    p -= 1
                else:
                    n -= 1
        score[i] = smoothed(p, n)
    return score


def plain_scores(rows, train_idx):
    pos, neg = Counter(), Counter()
    for i in train_idx:
        (pos if rows[i]["y"] else neg)[rows[i]["drug_b"]] += 1
    return np.array([smoothed(pos[r["drug_b"]], neg[r["drug_b"]]) for r in rows])


def prior_scores(rows, ctx, lookup):
    secs = list(ctx.vocab_di.items())
    cuis = np.array([c for _, (c, _) in secs])
    cache = {}

    def hits(y):
        if y not in cache:
            cache[y] = np.array([ctx.named(y, di) for _, (_, di) in secs], float)
        return cache[y]
    leave, plain = np.zeros(len(rows)), np.zeros(len(rows))
    for i, r in enumerate(rows):
        h = hits(r["drug_b"])
        cy, cx = lookup[r["drug_b"]]["rxcui"], lookup[r["drug_a"]]["rxcui"]
        m_plain = cuis != cy
        m_leave = m_plain & (cuis != cx)
        plain[i] = h[m_plain].sum() / m_plain.sum()
        leave[i] = h[m_leave].sum() / m_leave.sum()
    return leave, plain


def row_stats(c, s, n):
    y = c["y"]
    sc = an.view(c, s)
    w = an.within(c, s, n)
    d1 = aa.draws(y, [sc], c["g"], np.zeros(len(y), int), n, an.BOOT[c["name"]], "within")[0]
    o = aa.summ(aa.point(y, sc, c["g"], "within"), d1)
    return {"pooled_auroc": float(ev.auroc(y, sc)), "within_drug_auroc": w["value"], "within_ci95_two_way": [w["lo95"], w["hi95"]],
            "within_ci95_anchor_only": [o["lo95"], o["hi95"]], "n_draws_two_way": w["n_draws"], "n_draws_anchor_only": o["n_draws"]}


def md(res):
    L = ["# C2: reference rows for the R2a seen cohort", "", f"Status: {rc.STATUS}.", "",
         f"DrugBank release: version {res['drugbank_release']['version']}, exported on {res['drugbank_release']['exported_on']}.", "",
         f"Overlap with SemEval train: {json.dumps(res['overlap'])}", ""]
    for cname, rows in res["cohorts"].items():
        c = rows["meta"]
        L += [f"## Cohort {cname}", "", f"{c['n_pairs']} pairs, {c['n_positive']} positive, {c['n_anchor_drugs']} anchor drugs, {c['n_partner_drugs']} partner drugs, "
              f"{c['n_drugs_both_anchor_and_partner']} drugs act as both anchor and partner.", ""]
        body = []
        for name, r in rows["rows"].items():
            body.append([name, rc.f3(r["pooled_auroc"]), rc.f3(r["within_drug_auroc"]), rc.ci(r["within_ci95_two_way"]), rc.ci(r["within_ci95_anchor_only"])])
        L += rc.table(["row", "pooled AUROC", "within-drug AUROC", "95% two-way", "95% anchor only"], body) + [""]
    L += ["DrugBank: " + json.dumps(res["drugbank_counts"]), "", res["notes"], ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(m3b.DEFAULT_ZIP))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    rows = [ad.Data._train_row(x) for x in ad.read_rows_csv(rc.ROOT / "artifacts" / "amend7" / "train_pairs.csv")]
    semeval.download()
    overlap, outside = an.overlap_summary(rows, an.semeval_pair_index(semeval.load_pairs("train")))
    coh = an.cohorts(NoTruth(), rows, outside)
    coh = {k: v for k, v in coh.items() if k.startswith("seen")}
    table = m3b.load_table(a.drugbank, str(rc.RUNS / "drugbank_table.pkl"))
    store = LabelStore(offline=True)
    ctx = baselines.Context(lookup, store)
    states = [resolve(r["drug_a"], r["drug_b"], table, lookup) for r in rows]
    db = np.array([float(s[0] == "positive") for s in states])
    texts = {}
    sm = np.zeros(len(rows))
    for i, r in enumerate(rows):
        x = r["drug_a"]
        if x not in texts:
            texts[x] = baselines.non_di_text(store.get(lookup[x]["normalized"]))
        sm[i] = float(ctx.named(r["drug_b"], texts[x]))
    leave, plain = prior_scores(rows, ctx, lookup)
    all_idx = list(range(len(rows)))
    out_idx = [i for i in all_idx if outside[i]]
    scores = {"all": {"drugbank_lookup": db, "label_string_match": sm, "partner_prior_label_free_anchor_section_excluded": leave,
                      "partner_prior_with_anchor_section (circular for these pairs)": plain,
                      "partner_rate_leave_one_drug_out": lodo_scores(rows, all_idx),
                      "partner_rate_not_left_out (circular reference)": plain_scores(rows, all_idx)},
              "outside": {"drugbank_lookup": db, "label_string_match": sm, "partner_prior_label_free_anchor_section_excluded": leave,
                          "partner_prior_with_anchor_section (circular for these pairs)": plain,
                          "partner_rate_leave_one_drug_out (from the 4,062 pairs)": lodo_scores(rows, out_idx),
                          "partner_rate_leave_one_drug_out (from all 4,643 pairs)": lodo_scores(rows, all_idx),
                          "partner_rate_not_left_out (circular reference)": plain_scores(rows, out_idx)}}
    cohorts = {}
    for key, cname in (("all", "seen"), ("outside", "seen_not_in_semeval_train")):
        c = coh[cname]
        rr = {name: row_stats(c, s, a.boot) for name, s in scores[key].items()}
        anchors, partners = set(c["g"]), set(c["q"])
        cohorts[cname] = {"meta": {"n_pairs": int(len(c["y"])), "n_positive": int(c["y"].sum()), "n_anchor_drugs": len(anchors),
                                   "n_partner_drugs": len(partners), "n_drugs_both_anchor_and_partner": len(anchors & partners)}, "rows": rr}
    res = {"drugbank_release": m3b.header(a.drugbank), "overlap": overlap, "n_boot": a.boot, "seed": SEED,
           "drugbank_counts": {"listed": int(db.sum()), "unresolvable": int(sum(s[0] == "unresolvable" for s in states)),
                               "one_side_resolved": int(sum(s[1] == 1 for s in states))},
           "r2a_rows": rc.load(R2A),
           "notes": "label_string_match is 0 for every negative by construction (E7 negatives are not named anywhere in the anchor label). "
                    "Rows marked circular include the anchor's own label or the pair's own training label. No comparison with the Novel or Older rows is made."}
    res["cohorts"] = cohorts
    rc.write("c2_seen_reference", res, md(res))
    print(rc.OUT / "c2_seen_reference.md")


if __name__ == "__main__":
    main()
