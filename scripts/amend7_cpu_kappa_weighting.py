import argparse
import json

import numpy as np
from scipy.stats import rankdata

from amend7_cpu_common import (ROOT, ci, cohort_arrays, drugbank_score, ev, f3, fast_within_auroc, paired_draws,
                               seed_mean, stats, write)

DECISIONS = ROOT / "results" / "revision" / "eval" / "decisions.json"


def drug_weighted_auroc(y, s, strata):
    y = np.asarray(y)
    st = stats._codes(strata)
    dense = np.unique(np.asarray(s, float), return_inverse=True)[1].ravel()
    r = rankdata(st.astype(np.int64) * (dense.max() + 1) + dense)
    size = np.bincount(st)
    offset = (np.cumsum(size) - size)[st]
    npos = np.bincount(st, weights=y.astype(float), minlength=len(size))
    nneg = size - npos
    u = np.bincount(st, weights=(r - offset) * y, minlength=len(size)) - npos * (npos + 1) / 2
    ok = (npos > 0) & (nneg > 0)
    return float(np.mean(u[ok] / (npos[ok] * nneg[ok]))) if ok.any() else float("nan")


def draws_with(metric, y, scores, g1, g2, n, seed):
    c1, c2 = stats._codes(g1), stats._codes(g2)
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = stats._expand(rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        strata = c1[idx] * (w1.max() + 1) + r // w2[c2][idx]
        v = [metric(y[idx], s[idx], strata) for s in scores]
        if not any(np.isnan(v)):
            out.append(v)
    return np.asarray(out).T


def interval_block(est, d):
    return {"value": est, "ci90": [float(np.percentile(d, 5)), float(np.percentile(d, 95))],
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], "p_tost": ev.tost_p(d),
            "n_draws": int(len(d))}


def kappa(a, b):
    return (a - 0.5) / (b - 0.5)


def cells(truth):
    b2 = {"novel": seed_mean("b2mixed-biomedbert", "ood_empty")[0], "older": seed_mean("b2mixed-biomedbert", "oodold_empty")[0]}
    krag = seed_mean("krag-hybrid-k5-c400-biomedbert", "ood")[0]
    dbn, dbo = drugbank_score(truth, "ood"), drugbank_score(truth, "oodold")
    nov = cohort_arrays(truth, "novel")
    old = cohort_arrays(truth, "older_clean")
    sens = old["mask"] & truth.sets["oodold"]["sens"]
    so = truth.sets["oodold"]
    sens_arr = {"y": np.asarray(so["y"])[sens], "g": np.asarray(so["g"])[sens], "q": np.asarray(so["partner"])[sens]}
    out = [("H1", "Older-clean", old, b2["older"][old["mask"]], dbo[old["mask"]], 42),
           ("H1-sensitivity", "Older-clean sensitivity", sens_arr, b2["older"][sens], dbo[sens], 42),
           ("H1-novel", "Novel", nov, b2["novel"], dbn, 1042),
           ("H6", "Novel", nov, krag, dbn, 1042)]
    pooled = {"y": np.concatenate([nov["y"], old["y"]]),
              "g": np.concatenate([np.char.add("novel:", nov["g"].astype(str)), np.char.add("older:", old["g"].astype(str))]),
              "q": np.concatenate([nov["q"], old["q"]])}
    out.append(("H1-pooled", "Novel + Older-clean", pooled, np.concatenate([b2["novel"], b2["older"][old["mask"]]]),
                np.concatenate([dbn, dbo[old["mask"]]]), 42))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    truth = ev.load_truth()
    dec = json.loads(DECISIONS.read_text())
    rows = []
    for hid, cohort, c, s, db, seed in cells(truth):
        y, g, q = c["y"], c["g"], c["q"]
        dp = paired_draws(y, [s, db], g, q, a.boot, seed)
        dw = draws_with(drug_weighted_auroc, y, [s, db], g, q, a.boot, seed)
        pw = interval_block(fast_within_auroc(y, s, g), dp[0])
        dbw = fast_within_auroc(y, db, g)
        ref = dec[hid]
        if abs(pw["value"] - ref["value"]) > 1e-3 or abs(pw["ci95"][0] - ref["interval"][0]) > 1e-3:
            raise ValueError(f"{hid}: pair-weighted estimate does not reproduce decisions.json")
        kd = kappa(dp[0], dp[1])
        dww = drug_weighted_auroc(y, s, g)
        dwdb = drug_weighted_auroc(y, db, g)
        rows.append({"id": hid, "cohort": cohort, "n": int(len(y)), "n_drugs": int(len(set(g))),
                     "decision": ref["decision"], "pair_weighted": pw, "drugbank_within": dbw,
                     "kappa": {"value": kappa(pw["value"], dbw), "ci95": [float(np.percentile(kd, 2.5)), float(np.percentile(kd, 97.5))],
                               "margin_0.60": kappa(0.60, dbw), "margin_0.40": kappa(0.40, dbw)},
                     "drug_weighted_sensitivity": {**interval_block(dww, dw[0]), "drugbank": dwdb,
                                                   "kappa": kappa(dww, dwdb)}})
    out = {"status": "Amendment 7 additions, exploratory; kappa and the drug-weighted AUROC are sensitivity and context rows, not preregistered, and change no decision",
           "method": "kappa = (AUROC - 0.5) / (AUROC_DrugBank - 0.5), both within-drug on tier A of the same cohort; its interval uses the same "
                     "two-way draws for the model and the DrugBank lookup. The pair-weighted within-drug AUROC is the preregistered statistic "
                     "(stats.stratified_auroc weights each drug by its positive-negative pair count) and reproduces decisions.json. The "
                     "drug-weighted version averages per-drug AUROCs with equal weight per drug (and per resampled drug copy), over the same "
                     "draws (Novel seed 1042, Older seed 42, pooled seed 42). H4 is a difference between cohorts and has no single kappa; the per-cohort kappas of H1 and H1-novel apply.",
           "rows": rows}
    md = ["# Kappa against the DrugBank ceiling and drug-weighted sensitivity", "",
          "kappa = (AUROC - 0.5) / (AUROC_DrugBank - 0.5), within drug, tier A. Drug-weighted rows are sensitivity analyses, not preregistered.", "",
          "| id | cohort | n | drugs | decision | pair-weighted AUROC | 90% CI | p_tost | DrugBank | kappa | kappa 95% CI | kappa at 0.60 | drug-weighted AUROC | 90% CI | 95% CI | p_tost | kappa (drug-weighted) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        p, d, k = r["pair_weighted"], r["drug_weighted_sensitivity"], r["kappa"]
        md.append(f"| {r['id']} | {r['cohort']} | {r['n']} | {r['n_drugs']} | {r['decision']} | {f3(p['value'])} | {ci(p['ci90'])} | "
                  f"{f3(p['p_tost'])} | {f3(r['drugbank_within'])} | {f3(k['value'])} | {ci(k['ci95'])} | {f3(k['margin_0.60'])} | "
                  f"{f3(d['value'])} | {ci(d['ci90'])} | {ci(d['ci95'])} | {f3(d['p_tost'])} | {f3(d['kappa'])} |")
    md += ["", "H4 compares cohorts and has no single kappa; use the H1 and H1-novel rows."]
    write("kappa_weighting", out, "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
