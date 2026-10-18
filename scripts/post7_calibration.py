import argparse
import json

import numpy as np

from post7_common import (BOOT_SEED, ROOT, STATUS, TIERS, ci, cell, comparisons, draws, estimate, ev, f3, require_criteria,
                          scheme_weights, summarize, systems, tost_p, within_design, write)

ROWS = (("H1", "older_clean", "b2mixed"), ("H1-novel", "novel", "b2mixed"), ("H6", "novel", "krag"))
SCHEMES = ("two_way", "one_way_drug", "partner_only")


def scheme_draws(c, scores, scheme, boot, seed):
    D = within_design(c["y"], c["g"], c["q"])
    W1, W2 = scheme_weights(scheme, D["nd"], D["nq"], boot, seed)
    H = np.vstack([comparisons(D, s) for s in scores])
    d, ok = draws(D, H, W1, W2)
    return D, [estimate(D, s) for s in scores], d[:, ok]


def below_chance(r):
    return {"ci95_below_0.5": bool(r["ci95"] and r["ci95"][1] < 0.5), "ci90_below_0.5": bool(r["ci90"] and r["ci90"][1] < 0.5)}


def diff_block(a, b):
    n = min(len(a), len(b))
    d = a[:n] - b[:n]
    out = summarize(None, d)
    out["p_tost"] = tost_p(d + 0.5)
    return out


def kappa_rows(truth, S, boot):
    rows = []
    for hid, cohort, system in ROWS:
        for tier in TIERS:
            c = cell(truth, cohort, tier)
            s, db = S[cohort][system][c["mask"]], S[cohort]["DrugBank lookup"][c["mask"]]
            for scheme in ("two_way", "one_way_drug"):
                _, est, d = scheme_draws(c, [s, db], scheme, boot, BOOT_SEED[cohort])
                kd = (d[0] - 0.5) / (d[1] - 0.5)
                k = (est[0] - 0.5) / (est[1] - 0.5)
                rows.append({"id": hid, "cohort": cohort, "tier": tier, "scheme": scheme, "auroc": est[0], "drugbank": est[1],
                             "kappa": k, "kappa_ci95": [float(np.percentile(kd, 2.5)), float(np.percentile(kd, 97.5))],
                             "kappa_upper95": float(np.percentile(kd, 97.5)), "kappa_ci90": [float(np.percentile(kd, 5)), float(np.percentile(kd, 95))],
                             "n_draws": int(d.shape[1]),
                             "note": "DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5)" if tier == "B" else ""})
    return rows


def one_way_rows(truth, S, boot):
    rows, cache = [], {}
    for tier in TIERS:
        for scheme in SCHEMES:
            for hid, cohort, system in ROWS:
                c = cell(truth, cohort, tier)
                _, est, d = scheme_draws(c, [S[cohort][system][c["mask"]]], scheme, boot, BOOT_SEED[cohort])
                r = summarize(est[0], d[0])
                cache[(hid, tier, scheme)] = d[0]
                rows.append({"id": hid, "tier": tier, "scheme": scheme, "n": int(c["mask"].sum()),
                             "n_drugs": int(len(set(c["g"]))), **r, **below_chance(r),
                             "note": "no preregistered test (estimate only)" if hid == "H1-novel" else ""})
            r = diff_block(cache[("H1", tier, scheme)], cache[("H1-novel", tier, scheme)])
            est = next(x["value"] for x in rows if x["id"] == "H1" and x["tier"] == tier and x["scheme"] == scheme) - \
                next(x["value"] for x in rows if x["id"] == "H1-novel" and x["tier"] == tier and x["scheme"] == scheme)
            r["value"] = est
            rows.append({"id": "H4", "tier": tier, "scheme": scheme, "n": None, "n_drugs": None, **r,
                         "ci95_below_0.5": None, "ci90_below_0.5": None,
                         "note": "Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws"})
    holm = {}
    for tier in TIERS:
        for scheme in SCHEMES:
            ps = {h: next(x["p_tost"] for x in rows if x["id"] == h and x["tier"] == tier and x["scheme"] == scheme)
                  for h in ("H1", "H4", "H6")}
            holm[f"{tier}:{scheme}"] = {"raw": ps, "holm": ev.holm(ps)}
    for x in rows:
        h = holm[f"{x['tier']}:{x['scheme']}"]["holm"]
        x["p_holm_family_H1_H4_H6"] = h.get(x["id"])
        x["equivalent_unadjusted"] = bool(x["p_tost"] is not None and x["p_tost"] < 0.05)
    return rows, holm


def bayes_auc(c, s, n, rng, two_way=False):
    D = within_design(c["y"], c["g"], c["q"])
    H = comparisons(D, s)
    if not two_way:
        U = np.bincount(D["d"], weights=H, minlength=D["nd"])
        N = np.bincount(D["d"], minlength=D["nd"]).astype(float)
        W = rng.gamma(1.0, size=(n, D["nd"]))
        return (W @ U) / (W @ N)
    W1 = rng.gamma(1.0, size=(n, D["nd"]))
    W2 = rng.gamma(1.0, size=(n, D["nq"]))
    out = []
    for k in range(0, n, 500):
        d, _ = draws(D, H, W1[k:k + 500], W2[k:k + 500])
        out.append(d[0])
    return np.concatenate(out)


def post(d, lo, hi):
    p = float(np.mean((d >= lo) & (d <= hi)))
    verdict = "practically equivalent" if p >= 0.95 else ("practically not equivalent" if p <= 0.05 else "undecided")
    return {"posterior_mean": float(d.mean()), "cri90": [float(np.percentile(d, 5)), float(np.percentile(d, 95))],
            "cri95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], "p_in_rope": p,
            "p_below": float(np.mean(d < (lo + hi) / 2)), "verdict": verdict, "n_draws": int(len(d))}


def bayes_rows(truth, S):
    rows = []
    for model, n, seed, tw in (("Bayesian bootstrap over drugs (primary)", 20000, 11, False),
                               ("two-way Bayesian bootstrap over drugs and partners (secondary)", 4000, 12, True)):
        for tier in TIERS:
            rng = np.random.default_rng(seed)
            dd = {}
            for hid, cohort, system in ROWS:
                c = cell(truth, cohort, tier)
                dd[hid] = bayes_auc(c, S[cohort][system][c["mask"]], n, rng, tw)
                rows.append({"id": hid, "tier": tier, "model": model, **post(dd[hid], 0.40, 0.60)})
            rows.append({"id": "H4", "tier": tier, "model": model, **post(dd["H1"] - dd["H1-novel"], -0.10, 0.10)})
    return rows


def md(res):
    L = ["# Interval calibration, kappa framing and Bayesian equivalence", "", f"Status: {STATUS}.", "",
         "## Primary framing row: H1 kappa against the DrugBank lookup", "",
         "kappa = (AUROC - 0.5) / (AUROC_DrugBank - 0.5), within drug, with paired draws for the model and DrugBank.", "",
         "| id | tier | bootstrap | AUROC | DrugBank | kappa | 95% CI | 95% upper bound | note |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["kappa"]:
        L.append(f"| {r['id']} | {r['tier']} | {r['scheme']} | {f3(r['auroc'])} | {f3(r['drugbank'])} | {f3(r['kappa'])} | "
                 f"{ci(r['kappa_ci95'])} | {f3(r['kappa_upper95'])} | {r['note']} |")
    L += ["", "## 1a. Two-way, one-way drug and partner-only bootstrap", "",
          "The two-way rows are the preregistered intervals recomputed by the same code (they reproduce decisions.md). "
          "The one-way and partner-only rows are sensitivity analyses. A one-way interval that lies below 0.5 means the model is "
          "significantly below chance under that bootstrap (inverted information); it is not support for equivalence.", "",
          "| id | tier | bootstrap | estimate | 90% CI | 95% CI | p_TOST | Holm (H1, H4, H6) | 90% CI below 0.5 | 95% CI below 0.5 | note |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["intervals"]:
        L.append(f"| {r['id']} | {r['tier']} | {r['scheme']} | {f3(r['value'])} | {ci(r['ci90'])} | {ci(r['ci95'])} | "
                 f"{f3(r['p_tost'])} | {f3(r['p_holm_family_H1_H4_H6'])} | {'' if r['ci90_below_0.5'] is None else r['ci90_below_0.5']} | "
                 f"{'' if r['ci95_below_0.5'] is None else r['ci95_below_0.5']} | {r['note']} |")
    L += ["", "## 1c. Bayesian region of practical equivalence", "",
          "Region [0.40, 0.60] for AUROC rows and [-0.10, 0.10] for H4. Primary: Bayesian bootstrap over drugs, Dirichlet(1, ..., 1) "
          "weights (the posterior under a Dirichlet process prior with concentration tending to 0; noninformative, all mass on the "
          "observed drugs, partners fixed). Secondary: independent Dirichlet(1) weights on drugs and on partners. "
          "Rule: posterior probability at least 0.95 is practically equivalent, at most 0.05 practically not equivalent, otherwise undecided. "
          "p_below is P(AUROC < 0.5), or P(difference < 0) for H4.", "",
          "| id | tier | model | posterior mean | 90% CrI | 95% CrI | P(in region) | p_below | verdict |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["bayes"]:
        L.append(f"| {r['id']} | {r['tier']} | {r['model']} | {f3(r['posterior_mean'])} | {ci(r['cri90'])} | {ci(r['cri95'])} | "
                 f"{f3(r['p_in_rope'])} | {f3(r['p_below'])} | {r['verdict']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    crit = require_criteria()
    truth = ev.load_truth()
    S = systems(truth)
    dec = json.loads((ROOT / "results" / "revision" / "eval" / "decisions.json").read_text())
    intervals, holm = one_way_rows(truth, S, a.boot)
    for r in intervals:
        if r["tier"] == "A" and r["scheme"] == "two_way" and r["id"] in dec and a.boot == 1000:
            ref = dec[r["id"]]
            if abs(r["value"] - ref["value"]) > 6e-5 or abs(r["ci90"][0] - ref["interval90"][0]) > 6e-5:
                raise ValueError(f"{r['id']} two-way row does not reproduce decisions.json")
    res = {"status": STATUS, "criteria": {k: crit[k] for k in ("analysis_0_kappa_framing", "analysis_1a_one_way", "analysis_1c_bayes")},
           "kappa": kappa_rows(truth, S, a.boot), "intervals": intervals, "holm": holm, "bayes": bayes_rows(truth, S), "boot": a.boot}
    text = md(res)
    write("calibration", res, text)
    print(text)


if __name__ == "__main__":
    main()
