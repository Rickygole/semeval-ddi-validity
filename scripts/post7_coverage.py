import argparse
import time

import numpy as np
from scipy.stats import norm

from post7_common import (COHORTS, STATUS, TIERS, cell, ci, ev, f3, multinomial_weights, require_criteria,
                          within_design, write)

Z90 = norm.ppf(0.95)
SCHEMES = ("two_way", "one_way_drug", "partner_only")


def scenarios():
    out = []
    for target in (0.45, 0.50, 0.60):
        for sp in (0.0, 1.0):
            for tau in (0.0, 0.5):
                scale = np.sqrt(2 * (sp ** 2 + 1) + tau ** 2)
                out.append({"true_auroc": target, "partner_sd": sp, "slope_sd": tau, "drug_sd": 1.0,
                            "beta": float(norm.ppf(target) * scale)})
    return out


def true_auroc(beta, sp, tau):
    return float(norm.cdf(beta / np.sqrt(2 * (sp ** 2 + 1) + tau ** 2)))


def simulate_scores(rng, y, gd, qd, nd, nq, sc):
    slope = sc["beta"] + sc["slope_sd"] * rng.standard_normal(nd)
    return (slope[gd] * y + sc["partner_sd"] * rng.standard_normal(nq)[qd]
            + sc["drug_sd"] * rng.standard_normal(nd)[gd] + rng.standard_normal(len(y)))


def boot_values(D, H, rng, boot):
    W1 = multinomial_weights(rng, D["nd"], boot)
    W2 = multinomial_weights(rng, D["nq"], boot)
    one1 = np.ones_like(W1)
    one2 = np.ones_like(W2)
    U = np.bincount(D["d"], weights=H, minlength=D["nd"])
    N = np.bincount(D["d"], minlength=D["nd"]).astype(float)
    out = {}
    with np.errstate(invalid="ignore", divide="ignore"):
        M = W1[:, D["d"]] * W2[:, D["qi"]] * W2[:, D["qj"]]
        out["two_way"] = (M @ H) / M.sum(1)
        out["one_way_drug"] = (W1 @ U) / (W1 @ N)
        M = one1[:, D["d"]] * W2[:, D["qi"]] * W2[:, D["qj"]]
        out["partner_only"] = (M @ H) / M.sum(1)
    del one2
    return {k: v[~np.isnan(v)] for k, v in out.items()}


def run_design(y, g, q, sc, reps, boot, rng):
    D = within_design(y, g, q)
    from post7_common import codes
    gd, qd = codes(g), codes(q)
    t = true_auroc(sc["beta"], sc["partner_sd"], sc["slope_sd"])
    est = []
    iv = {k: [] for k in SCHEMES}
    for _ in range(reps):
        s = simulate_scores(rng, np.asarray(y, float), gd, qd, D["nd"], D["nq"], sc)
        H = (s[D["i"]] > s[D["j"]]).astype(float)
        est.append(H.mean())
        b = boot_values(D, H, rng, boot)
        for k in SCHEMES:
            iv[k].append(np.percentile(b[k], [5, 95, 2.5, 97.5]))
    est = np.asarray(est)
    sd = float(est.std(ddof=1))
    res = {"true_auroc": t, "mean_estimate": float(est.mean()), "bias": float(est.mean() - t), "sd_of_estimate": sd,
           "mc_se_coverage90": float(np.sqrt(0.09 / reps)), "schemes": {}}
    for k in SCHEMES:
        a = np.asarray(iv[k])
        hw = float(np.mean(a[:, 1] - a[:, 0]) / 2)
        cov90 = float(np.mean((a[:, 0] <= t) & (t <= a[:, 1])))
        ratio = hw / (Z90 * sd) if sd else None
        if cov90 < 0.87:
            label = "anti-conservative"
        elif 0.87 <= cov90 <= 0.93 and ratio is not None and 0.85 <= ratio <= 1.15:
            label = "calibrated"
        else:
            label = "conservative"
        res["schemes"][k] = {"coverage90": cov90, "coverage95": float(np.mean((a[:, 2] <= t) & (t <= a[:, 3]))),
                             "mean_halfwidth90": hw, "halfwidth90_over_nominal": ratio,
                             "share_90_inside_040_060": float(np.mean((a[:, 0] > 0.40) & (a[:, 1] < 0.60))),
                             "label": label}
    return res


def md(res):
    L = ["# Coverage of the two-way, one-way drug and partner-only bootstraps", "", f"Status: {STATUS}.", "",
         f"Simulation on the real (label, drug, partner) structure. {res['reps']} replicates per scenario and design, "
         f"{res['boot']} bootstrap draws per replicate, seed {res['seed']}. Score = beta_d y + sigma_p u_partner + v_drug + e, "
         "beta_d = beta + tau z_d; the true within-drug AUROC is Phi(beta / sqrt(2 (sigma_p^2 + 1) + tau^2)). "
         "Ratio = mean 90% half-width / (1.645 x replicate SD); 1 is calibrated. Labels: calibrated if 90% coverage is in [0.87, 0.93] "
         "and the ratio in [0.85, 1.15]; anti-conservative if coverage is below 0.87; otherwise conservative.", "",
         "| design | true AUROC | sigma_p | tau | SD | bootstrap | coverage 90% | coverage 95% | 90% half-width | ratio | 90% inside 0.40 to 0.60 | label |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["rows"]:
        for k, v in r["result"]["schemes"].items():
            L.append(f"| {r['design']} | {f3(r['result']['true_auroc'])} | {r['scenario']['partner_sd']} | {r['scenario']['slope_sd']} | "
                     f"{f3(r['result']['sd_of_estimate'])} | {k} | {f3(v['coverage90'])} | {f3(v['coverage95'])} | "
                     f"{f3(v['mean_halfwidth90'])} | {f3(v['halfwidth90_over_nominal'])} | {f3(v['share_90_inside_040_060'])} | {v['label']} |")
    L += ["", "## Summary by design and bootstrap", "", "| design | bootstrap | coverage 90% range | ratio range | labels | adequate (no anti-conservative scenario) |",
          "| --- | --- | --- | --- | --- | --- |"]
    for s in res["summary"]:
        L.append(f"| {s['design']} | {s['scheme']} | {ci(s['coverage90_range'])} | {ci(s['ratio_range'])} | {s['labels']} | {s['adequate']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    crit = require_criteria()
    t0 = time.time()
    truth = ev.load_truth()
    rng = np.random.default_rng(a.seed)
    rows = []
    for cohort in COHORTS:
        for tier in TIERS:
            c = cell(truth, cohort, tier)
            for sc in scenarios():
                r = run_design(c["y"], c["g"], c["q"], sc, a.reps, a.boot, rng)
                rows.append({"design": f"{cohort} tier {tier}", "n": int(len(c["y"])), "n_drugs": int(len(set(c["g"]))),
                             "scenario": sc, "result": r})
                print(rows[-1]["design"], sc["true_auroc"], sc["partner_sd"], sc["slope_sd"],
                      {k: round(v["coverage90"], 3) for k, v in r["schemes"].items()}, round(time.time() - t0), flush=True)
    summary = []
    for design in dict.fromkeys(r["design"] for r in rows):
        for k in ("two_way", "one_way_drug", "partner_only"):
            v = [r["result"]["schemes"][k] for r in rows if r["design"] == design]
            labels = sorted({x["label"] for x in v})
            summary.append({"design": design, "scheme": k,
                            "coverage90_range": [min(x["coverage90"] for x in v), max(x["coverage90"] for x in v)],
                            "ratio_range": [min(x["halfwidth90_over_nominal"] for x in v), max(x["halfwidth90_over_nominal"] for x in v)],
                            "labels": ", ".join(labels), "adequate": "anti-conservative" not in labels})
    res = {"status": STATUS, "criteria": crit["analysis_1b_coverage"], "reps": a.reps, "boot": a.boot, "seed": a.seed,
           "rows": rows, "summary": summary, "seconds": time.time() - t0}
    text = md(res)
    write("coverage", res, text)
    print(text)


if __name__ == "__main__":
    main()
