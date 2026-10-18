import argparse
import time

import numpy as np

from sens_common import ci, ev, f3, write
from amend7_cpu_common import fast_within_auroc, paired_draws

Z90 = 1.6449

SCENARIOS_SHIFT = (
    {"name": "null, no partner effect", "signal": 0.0, "partner_sd": 0.0, "drug_sd": 1.0},
    {"name": "null, partner effect", "signal": 0.0, "partner_sd": 1.0, "drug_sd": 1.0},
    {"name": "signal 0.37, partner effect", "signal": 0.37, "partner_sd": 1.0, "drug_sd": 1.0},
)
SCENARIOS_SLOPE = (
    {"name": "random slopes, null mean, partner effect", "mu": 0.0, "tau": 0.6, "partner_sd": 1.0},
    {"name": "random slopes, mean 0.37, partner effect", "mu": 0.37, "tau": 0.6, "partner_sd": 1.0},
    {"name": "random slopes, null mean, no partner effect", "mu": 0.0, "tau": 0.6, "partner_sd": 0.0},
)


def cohorts(truth):
    out = {}
    for name, tag in (("novel", "ood"), ("older_clean", "oodold")):
        s = truth.sets[tag]
        m = np.ones(len(s["y"]), bool) if tag == "ood" else s["clean"]
        out[name] = (np.asarray(s["y"])[m], np.asarray(s["g"])[m], np.asarray(s["partner"])[m])
    return out


def summarize(est, intervals, truth_value):
    est, iv = np.asarray(est), np.asarray(intervals)
    sd = float(est.std())
    hw90 = float(np.mean(iv[:, 1] - iv[:, 0]) / 2)
    return {"true_value": float(truth_value), "sd_of_estimate": sd, "mean_halfwidth90": hw90,
            "halfwidth90_over_sd": hw90 / sd if sd else None,
            "halfwidth90_over_nominal": hw90 / (Z90 * sd) if sd else None,
            "coverage90": float(np.mean((iv[:, 0] <= truth_value) & (truth_value <= iv[:, 1]))),
            "coverage95": float(np.mean((iv[:, 2] <= truth_value) & (truth_value <= iv[:, 3]))),
            "equivalence_rate_90_in_040_060": float(np.mean((iv[:, 0] > 0.4) & (iv[:, 1] < 0.6)))}


def pct(d):
    return np.percentile(d, [5, 95, 2.5, 97.5])


def run_shift(y, g, q, sc, reps, boot, seed):
    rng = np.random.default_rng(seed)
    uq, qi = np.unique(q, return_inverse=True)
    ug, gi = np.unique(g, return_inverse=True)
    est, iv = [], []
    for _ in range(reps):
        s = (sc["signal"] * y + sc["partner_sd"] * rng.normal(size=len(uq))[qi]
             + sc["drug_sd"] * rng.normal(size=len(ug))[gi] + rng.normal(size=len(y)))
        d = paired_draws(y, [s], g, q, boot, int(rng.integers(1e9)))[0]
        est.append(fast_within_auroc(y, s, g))
        iv.append(pct(d))
    est = np.asarray(est)
    return summarize(est, iv, est.mean())


def run_slope(y, g, q, sc, reps, boot, seed):
    rng = np.random.default_rng(seed)
    uq, qi = np.unique(q, return_inverse=True)
    ug, gi = np.unique(g, return_inverse=True)
    one = np.zeros(len(y), int)
    est, iv2, iv1 = [], [], []
    for _ in range(reps):
        slope = sc["mu"] + sc["tau"] * rng.normal(size=len(ug))
        s = (slope[gi] * y + sc["partner_sd"] * rng.normal(size=len(uq))[qi]
             + rng.normal(size=len(ug))[gi] + rng.normal(size=len(y)))
        bs = int(rng.integers(1e9))
        est.append(fast_within_auroc(y, s, g))
        iv2.append(pct(paired_draws(y, [s], g, q, boot, bs)[0]))
        iv1.append(pct(paired_draws(y, [s], g, one, boot, bs)[0]))
    est = np.asarray(est)
    t = est.mean()
    return {"two_way": summarize(est, iv2, t), "one_way_drug": summarize(est, iv1, t)}


def dropout(y, g, q, n=1000, seed=0):
    ug, gi = np.unique(g, return_inverse=True)
    uq, qi = np.unique(q, return_inverse=True)
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, len(ug), len(ug)), minlength=len(ug))
        w2 = np.bincount(rng.randint(0, len(uq), len(uq)), minlength=len(uq))
        drawn = np.where(w1 > 0)[0]
        k = 0
        for d in drawn:
            m = gi == d
            if w2[qi[m & (y == 1)]].sum() == 0 or w2[qi[m & (y == 0)]].sum() == 0:
                k += 1
        out.append(k / len(drawn))
    return {"mean_fraction_drawn_drugs_without_both_classes": float(np.mean(out)), "max_fraction": float(np.max(out)), "draws": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    t0 = time.time()
    data = cohorts(ev.load_truth())
    out = {"status": "sensitivity analysis, post hoc; simulation of the preregistered two-way cluster bootstrap",
           "method": "scores simulated on the real Novel and Older-clean pair structure (drugs, partners, labels); each "
                     "replicate draws new scores, computes the within-drug AUROC and its two-way cluster bootstrap "
                     "percentile intervals (the resampling of ddiood.stats.two_way_samples with drug-copy strata, as in "
                     "ddiood.evaluate2); the true value is the mean estimate over replicates; coverage is the share of "
                     "replicates whose interval contains it; halfwidth90_over_nominal is the mean 90% half-width divided "
                     "by 1.645 times the replicate SD, so 1 is a calibrated interval",
           "reps": a.reps, "boot": a.boot, "seed": a.seed, "model_shift": {}, "model_slope": {}, "dropout": {}}
    md = ["# Two-way cluster bootstrap coverage", "",
          f"Simulation on the real pair structure. {a.reps} replicates per scenario, {a.boot} bootstrap draws per replicate, seed {a.seed}.", "",
          "Model A: score = signal * y + partner effect + drug effect + noise. Model B: per-drug random slope on y "
          "(mean mu, SD tau) + partner effect + drug effect + noise, with the two-way and the one-way (drugs only) bootstrap.", ""]
    rows = []
    for cname, (y, g, q) in data.items():
        out["model_shift"][cname] = {}
        for i, sc in enumerate(SCENARIOS_SHIFT):
            r = run_shift(y, g, q, sc, a.reps, a.boot, a.seed + i)
            out["model_shift"][cname][sc["name"]] = {"scenario": sc, **r}
            rows.append((cname, "A", sc["name"], "two-way", r))
        out["model_slope"][cname] = {}
        for i, sc in enumerate(SCENARIOS_SLOPE):
            r = run_slope(y, g, q, sc, a.reps, a.boot, a.seed + 10 + i)
            out["model_slope"][cname][sc["name"]] = {"scenario": sc, **r}
            rows.append((cname, "B", sc["name"], "two-way", r["two_way"]))
            rows.append((cname, "B", sc["name"], "one-way drug", r["one_way_drug"]))
        out["dropout"][cname] = dropout(y, g, q)
    two = [r for *_, b, r in rows if b == "two-way"]
    out["summary_two_way"] = {"coverage90_range": [min(r["coverage90"] for r in two), max(r["coverage90"] for r in two)],
                              "coverage95_range": [min(r["coverage95"] for r in two), max(r["coverage95"] for r in two)],
                              "halfwidth90_over_sd_range": [min(r["halfwidth90_over_sd"] for r in two), max(r["halfwidth90_over_sd"] for r in two)],
                              "halfwidth90_over_nominal_range": [min(r["halfwidth90_over_nominal"] for r in two), max(r["halfwidth90_over_nominal"] for r in two)]}
    one = [r for *_, b, r in rows if b == "one-way drug"]
    out["summary_one_way_drug"] = {"coverage90_range": [min(r["coverage90"] for r in one), max(r["coverage90"] for r in one)],
                                   "halfwidth90_over_sd_range": [min(r["halfwidth90_over_sd"] for r in one), max(r["halfwidth90_over_sd"] for r in one)]}
    out["seconds"] = time.time() - t0
    md += ["| cohort | model | scenario | bootstrap | true value | SD | 90% half-width | half-width / SD | coverage 90% | coverage 95% | 90% inside 0.40 to 0.60 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c, m, n, b, r in rows:
        md.append(f"| {c} | {m} | {n} | {b} | {f3(r['true_value'])} | {f3(r['sd_of_estimate'])} | {f3(r['mean_halfwidth90'])} | "
                  f"{f3(r['halfwidth90_over_sd'])} | {f3(r['coverage90'])} | {f3(r['coverage95'])} | {f3(r['equivalence_rate_90_in_040_060'])} |")
    s2 = out["summary_two_way"]
    md += ["", f"Two-way bootstrap over all scenarios: 90% coverage {ci(s2['coverage90_range'])}, 95% coverage {ci(s2['coverage95_range'])}, "
           f"90% half-width {ci(s2['halfwidth90_over_sd_range'])} times the SD of the estimate (a calibrated interval gives 1.645).", ""]
    md += ["Share of drawn drugs that drop out of a bootstrap draw because the partner resampling leaves them one class:", ""]
    for c, d in out["dropout"].items():
        md.append(f"* {c}: mean {f3(d['mean_fraction_drawn_drugs_without_both_classes'])}, max {f3(d['max_fraction'])} over {d['draws']} draws")
    write("bootstrap_coverage", out, "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
