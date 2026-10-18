import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ddiood import config, stats
from ddiood.evaluate2 import OLDER_ARTIFACTS

SEEDS = (42, 1, 2, 3, 4)
SYSTEMS = ("b2mixed-biomedbert", "b2sentence-biomedbert", "b1names-biomedbert", "b2mixed-bertbase", "b2sentence-bertbase")


def rows_for(name):
    return list(csv.DictReader(open(config.RESULTS / "corrected" / name)))


def tiers(rows, path):
    if not path.exists():
        return None
    db = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in csv.DictReader(open(path))}
    out = []
    for r in rows:
        d = db.get((r["ood_drug"], r["semeval_drug"]), "unresolvable")
        out.append((d == "positive" and r["label"] == "1") or (d == "negative" and r["label"] == "0"))
    return np.array(out)


def seed_mean(preds, system, key):
    ps = []
    for s in SEEDS:
        f = preds / f"{system}-s{s}.json"
        if f.exists():
            ev = json.load(open(f))["eval"]
            ps.append(np.array(ev[key if key in ev else key.replace("_empty", "_names")]["p"], dtype=float))
    return (np.mean(ps, axis=0), len(ps)) if ps else (None, 0)


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def additive_residual(s, g1, g2, iters=200):
    c1, c2 = stats._codes(g1), stats._codes(g2)
    a, b = np.zeros(c1.max() + 1), np.zeros(c2.max() + 1)
    mu = s.mean()
    for _ in range(iters):
        a = np.bincount(c1, s - mu - b[c2], minlength=len(a)) / np.bincount(c1, minlength=len(a))
        b = np.bincount(c2, s - mu - a[c1], minlength=len(b)) / np.bincount(c2, minlength=len(b))
    return np.round(s - mu - a[c1] - b[c2], 8)


def null_check(g1, g2, y, reps=200):
    c1, c2 = stats._codes(g1), stats._codes(g2)
    rng = np.random.RandomState(0)
    v = []
    for _ in range(reps):
        s = rng.normal(0, 1, c1.max() + 1)[c1] + rng.normal(0, 1, c2.max() + 1)[c2] + rng.normal(0, 0.5, len(y))
        v.append(stats.stratified_auroc(y, additive_residual(s, g1, g2), g1))
    return {"mean": round(float(np.mean(v)), 6), "sd": round(float(np.std(v)), 6), "reps": reps}


def summarize(y, s, g1, g2, n_boot, seed):
    draws = stats.two_way_samples(stats.stratified_auroc, y, s, g1, g2, n_boot, seed, strat=g1)
    lo90, hi90 = np.percentile(draws, [5, 95])
    lo95, hi95 = np.percentile(draws, [2.5, 97.5])
    return {"auroc_within": round(float(stats.stratified_auroc(y, s, g1)), 6), "auroc_pooled": round(float(stats.auroc(y, s)), 6),
            "ci90": [round(float(lo90), 6), round(float(hi90), 6)], "ci95": [round(float(lo95), 6), round(float(hi95), 6)]}


def partner_prior(rows, mask):
    pos = {}
    for r, m in zip(rows, mask):
        if m:
            pos.setdefault(r["semeval_drug"], []).append(int(r["label"]))
    return np.array([float(np.mean(pos.get(r["semeval_drug"], [0]))) for r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default=str(config.RESULTS / "revision" / "preds"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--out", default=str(config.RESULTS / "revision" / "eval" / "residual_analysis.json"))
    a = ap.parse_args()
    preds = Path(a.preds)
    res = {"status": "exploratory, not pre-registered",
           "method": "seed-averaged logit scores minus an additive drug effect plus partner effect fitted by alternating least squares; "
                     "AUROC of the residual within drug and pooled, two-way cluster bootstrap over OOD drugs and partners",
           "cohorts": {}}
    cohorts = {"novel": ("ood_pairs.csv", "ood_empty", config.ARTIFACTS / "ood" / "drugbank_validation.csv", False),
               "older_clean": ("ood_old_pairs.csv", "oodold_empty", config.ARTIFACTS / "ood" / "drugbank_validation_old.csv", True)}
    for cname, (fname, key, dbpath, clean) in cohorts.items():
        seed = 1042 if cname == "novel" else 42
        rows = rows_for(fname)
        keep = np.array([not (clean and r["ood_drug"].strip().lower() in OLDER_ARTIFACTS) for r in rows])
        tb = tiers(rows, dbpath)
        out = {}
        for tier in ("A", "B"):
            m = keep if tier == "A" else keep & tb
            sub = [r for r, k in zip(rows, m) if k]
            y = np.array([int(r["label"]) for r in sub])
            g1 = [r["ood_drug"] for r in sub]
            g2 = [r["semeval_drug"] for r in sub]
            cell = {"bootstrap_seed": seed, "n": int(len(sub)), "n_drugs": len(set(g1)), "n_partners": len(set(g2)),
                    "null_additive_scores_residual_auroc": null_check(g1, g2, y)}
            prior = partner_prior(rows, keep)[m]
            cell["partner_prior_raw"] = summarize(y, prior, g1, g2, a.boot, seed)
            cell["partner_prior_residual"] = summarize(y, additive_residual(prior, g1, g2), g1, g2, a.boot, seed)
            for system in SYSTEMS:
                p, k = seed_mean(preds, system, key)
                if p is None:
                    continue
                s = logit(p)[m]
                part = {"n_seeds": k, "raw": summarize(y, s, g1, g2, a.boot, seed),
                        "residual": summarize(y, additive_residual(s, g1, g2), g1, g2, a.boot, seed)}
                if tier == "A":
                    pm = {}
                    for pn, sc in zip(g2, s):
                        pm.setdefault(pn, []).append(sc)
                    names = sorted(pm)
                    mean_score = [float(np.mean(pm[n])) for n in names]
                    deg = [sum(1 for r in rows if r["semeval_drug"] == n and r["label"] == "1") for n in names]
                    rho, pv = spearmanr(mean_score, deg)
                    part["partner_mean_score_vs_positive_count"] = {"spearman": round(float(rho), 6), "p": float(pv), "n_partners": len(names)}
                cell[system] = part
            out[tier] = cell
        res["cohorts"][cname] = out
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
