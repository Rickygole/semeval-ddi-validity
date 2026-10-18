import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ddiood import config, stats


def load(name):
    rows = list(csv.DictReader(open(config.RESULTS / "corrected" / name)))
    return (np.array([int(r["label"]) for r in rows]), [r["ood_drug"] for r in rows],
            [r["semeval_drug"] for r in rows], rows)


def drugbank_flags(rows, name):
    path = config.ARTIFACTS / "ood" / ("drugbank_validation.csv" if name == "ood_pairs.csv" else "drugbank_validation_old.csv")
    if not path.exists():
        return None
    db = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in csv.DictReader(open(path))}
    return np.array([db.get((r["ood_drug"], r["semeval_drug"]), "unresolvable") for r in rows])


def simulate(y_true, auc, rng):
    d = np.sqrt(2) * norm.ppf(auc)
    return rng.normal(0, 1, len(y_true)) + d * y_true


def run(y, g1, g2, true_y, aucs, reps, n_boot, seed):
    rng = np.random.RandomState(seed)
    out = {}
    for auc in aucs:
        obs, half, upper95, inside = [], [], [], []
        for r in range(reps):
            s = simulate(true_y, auc, rng)
            obs.append(stats.stratified_auroc(y, s, g1))
            draws = stats.two_way_samples(stats.stratified_auroc, y, s, g1, g2, n_boot, seed + r, strat=g1)
            lo, hi = np.percentile(draws, [5, 95])
            half.append((hi - lo) / 2)
            upper95.append(hi)
            inside.append(lo > 0.40 and hi < 0.60)
        out[f"{auc:.2f}"] = {"observed_mean": float(np.mean(obs)), "ci90_half_width": float(np.mean(half)),
                             "one_sided_upper95_mean": float(np.mean(upper95)),
                             "share_ci90_inside_margin": float(np.mean(inside))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--boot", type=int, default=300)
    ap.add_argument("--out", default=str(config.RESULTS / "corrected" / "power_analysis.json"))
    a = ap.parse_args()
    aucs = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
    res = {"method": "synthetic scores with a known within-drug AUROC on the real pair structure; two-way cluster "
                     "bootstrap over novel drugs and partners; statistic is the within-drug (drug-stratified) AUROC",
           "reps": a.reps, "n_boot": a.boot}
    for name in ("ood_pairs.csv", "ood_old_pairs.csv"):
        y, g1, g2, rows = load(name)
        res[name] = {"clean_labels": run(y, g1, g2, y, aucs, a.reps, a.boot, 42)}
        flags = drugbank_flags(rows, name)
        if flags is not None:
            noisy_true = np.where(flags == "positive", 1, np.where(flags == "negative", 0, y))
            res[name]["drugbank_truth_fda_labels_scored"] = run(y, g1, g2, noisy_true, aucs, a.reps, a.boot, 43)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
