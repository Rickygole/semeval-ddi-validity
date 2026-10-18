import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import rev3_common as rc
import rev2_analyze_a as an
import rev2_m3b as m3b
import rev3_d9 as d9
import post7_common as p7
from amend7_cpu_common import cohort_arrays
from amend7_cpu_exp5_dissociation import resolve
from ddiood import amend7_analysis as aa
from ddiood import amend7_data as ad
from ddiood import config, semeval

BOOT_SEED = {"novel": 1042, "older_clean": 42, "seen": 42}
SPEARMAN_SEED = 42
KEY = {"novel": "ood_empty", "older_clean": "oodold_empty", "seen": "train_empty"}
R2A_FAMILIES = ("b2mixed", "b2sentence", "marker")
RUNS_PREDS = rc.ROOT / "runs" / "preds"


def loo_stats(g, q, y, s):
    g, q = np.asarray(g), np.asarray(q)
    y, s = np.asarray(y, float), np.asarray(s, float)
    by_q = defaultdict(list)
    by_gq = defaultdict(list)
    for i in range(len(y)):
        by_q[q[i]].append(i)
        by_gq[(g[i], q[i])].append(i)
    n_other = np.zeros(len(y), int)
    rate = np.zeros(len(y))
    marginal = np.full(len(y), np.nan)
    for i in range(len(y)):
        rows = by_q[q[i]]
        drop = set(by_gq[(g[i], q[i])])
        if g[i] == q[i]:
            drop |= set(rows)
        keep = [j for j in rows if j not in drop]
        pos = float(y[keep].sum()) if keep else 0.0
        n_other[i] = len(keep)
        rate[i] = (pos + 1) / (len(keep) + 2)
        if keep:
            marginal[i] = float(s[keep].mean())
    return rate, marginal, n_other


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return float(spearmanr(a, b).statistic)


def partner_bootstrap(q, fn, n, seed=SPEARMAN_SEED):
    q = np.asarray(q)
    parts, inv = np.unique(q, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    bounds = np.searchsorted(inv[order], np.arange(len(parts) + 1))
    rows = [order[bounds[k]:bounds[k + 1]] for k in range(len(parts))]
    rng = np.random.RandomState(seed)
    vals = []
    for _ in range(n):
        idx = np.concatenate([rows[k] for k in rng.randint(0, len(parts), len(parts))])
        v = fn(idx)
        if v is not None:
            vals.append(v)
    return vals


def partner_level(q, y, s):
    q = np.asarray(q)
    parts, inv = np.unique(q, return_inverse=True)
    cnt = np.bincount(inv)
    mean_s = np.bincount(inv, weights=np.asarray(s, float)) / cnt
    rate = np.bincount(inv, weights=np.asarray(y, float)) / cnt
    keep = cnt >= 2
    return mean_s[keep], rate[keep], parts[keep]


def system_block(c, s, n):
    y, g, q = np.asarray(c["y"]), np.asarray(c["g"]), np.asarray(c["q"])
    s = np.asarray(s, float)
    rate, marginal, n_other = loo_stats(g, q, y, s)
    ok = ~np.isnan(marginal)
    out = {"n_pairs": int(len(y)), "n_with_other_anchor_pairs": int(ok.sum()), "n_dropped_no_other_pair": int((~ok).sum())}
    yo, go, qo, mo, ro, so = y[ok], g[ok], q[ok], marginal[ok], rate[ok], s[ok]
    rho = spearman(mo, ro)
    vals = partner_bootstrap(qo, lambda idx: spearman(mo[idx], ro[idx]), n)
    out["pair_level_spearman_marginal_vs_loo_rate"] = {"value": rho, "ci95": rc.pct(vals), "n_draws": len(vals)}
    ps, pr, _ = partner_level(q, y, s)
    prho = spearman(ps, pr)
    pvals = partner_bootstrap(np.arange(len(ps)), lambda idx: spearman(ps[idx], pr[idx]), n)
    out["partner_level_spearman_mean_score_vs_rate"] = {"value": prho, "ci95": rc.pct(pvals), "n_partners": int(len(ps)), "n_draws": len(pvals)}
    seed = BOOT_SEED[c["name"]]
    for name, vec in (("marginal_score_within_drug_auroc", mo), ("system_own_within_drug_auroc", so), ("loo_rate_within_drug_auroc", ro)):
        d = aa.draws(yo, [vec], go, qo, n, seed, "within")[0]
        out[name] = aa.summ(aa.point(yo, vec, go, "within"), d)
    return out


def seen_cohort():
    rows = [ad.Data._train_row(x) for x in ad.read_rows_csv(rc.ROOT / "artifacts" / "amend7" / "train_pairs.csv")]
    return rows, {"name": "seen", "y": np.array([r["y"] for r in rows]), "g": np.array([r["drug_a"] for r in rows]),
                  "q": np.array([r["drug_b"] for r in rows])}


def r2a_scores(key):
    out = {}
    for f in R2A_FAMILIES:
        p, have, _ = an.seed_p(RUNS_PREDS, f, key)
        if p is not None:
            out[f"R2a {f}"] = (np.asarray(p, float), have)
    return out


def md(o):
    L = ["# D8: consequence of the partner anti-correlation for the evaluated systems", "", f"Status: {rc.STATUS}.", "",
         "For each pair (anchor A, partner y) the other pairs of y are those of the same cohort with anchor A removed (the exclusion of `rev3_c2.lodo_scores`). "
         "The leave-one-drug-out rate is the smoothed positive rate (pos + 1) / (n + 2) of those pairs; the partner-marginal score is the unweighted mean of the "
         "system's stored score (probability, or 0 or 1 for DrugBank) over the same pairs. Pairs with no other pair of the partner are dropped and counted. "
         f"Intervals: 95% percentile, {o['n_boot']} draws; the Spearman intervals resample partner drugs (seed {SPEARMAN_SEED}), the within-drug AUROC "
         "intervals are the two-way cluster bootstrap of `aa.draws` with the cohort seed, scores held fixed across draws. "
         "The partner-marginal score is a scorer only in the sense that the partner-matched label construction would reward it; no causal statement is made.", ""]
    for cname, cb in o["cohorts"].items():
        L += [f"## {cname}", "", f"{cb['n_pairs']} pairs, {cb['n_positive']} positive, {cb['n_anchor_drugs']} anchor drugs, {cb['n_partner_drugs']} partner drugs.", ""]
        rows = []
        for sname, b in cb["systems"].items():
            r = b["pair_level_spearman_marginal_vs_loo_rate"]
            p = b["partner_level_spearman_mean_score_vs_rate"]
            w = b["marginal_score_within_drug_auroc"]
            own = b["system_own_within_drug_auroc"]
            lr = b["loo_rate_within_drug_auroc"]
            rows.append([sname, b.get("seeds", ""), b["n_with_other_anchor_pairs"], rc.f3(r["value"]), rc.ci(r["ci95"]), rc.f3(p["value"]), rc.ci(p["ci95"]),
                         p["n_partners"], rc.f3(w["value"]), rc.ci([w["lo95"], w["hi95"]]), rc.f3(own["value"]), rc.f3(lr["value"])])
        L += rc.table(["system", "seeds", "pairs used", "pair-level Spearman", "95% CI", "partner-level Spearman", "95% CI", "partners", "marginal-score within-drug AUROC",
                       "95% CI", "own within-drug AUROC", "LOO-rate within-drug AUROC"], rows) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--drugbank", default=str(m3b.DEFAULT_ZIP))
    a = ap.parse_args()
    truth = p7.ev.load_truth()
    stored = p7.systems(truth)
    out = {"n_boot": a.boot, "cohorts": {}}
    plan = {"older_clean": ("oodold", {"DrugBank lookup": "DrugBank lookup", "stored b2mixed": "b2mixed", "stored b2sentence": "b2sentence",
                                       "Qwen names only": "Qwen names only"}),
            "novel": ("ood", {"DrugBank lookup": "DrugBank lookup", "stored b2mixed": "b2mixed", "stored b2sentence": "b2sentence",
                              "Qwen names only": "Qwen names only"})}
    for cname, (tag, names) in plan.items():
        c = cohort_arrays(truth, cname)
        c = {**c, "name": cname}
        scores = {k: (np.asarray(stored[cname][v], float)[c["mask"]], None) for k, v in names.items()}
        for k, (p, have) in r2a_scores(KEY[cname]).items():
            scores[k] = (p[c["mask"]], have)
        out["cohorts"][cname] = cohort_block(c, scores, a.boot)
    rows, c = seen_cohort()
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    table, table_source = d9.load_cached_table(a.drugbank, str(rc.RUNS / "drugbank_table.pkl"))
    db = np.array([float(resolve(r["drug_a"], r["drug_b"], table, lookup)[0] == "positive") for r in rows])
    scores = {"DrugBank lookup": (db, None)}
    for k, (p, have) in r2a_scores(KEY["seen"]).items():
        scores[k] = (p, have)
    out["cohorts"]["seen"] = cohort_block(c, scores, a.boot)
    out["drugbank_table_source"] = table_source
    rc.write("d8_partner_marginal", out, md(out))
    print(md(out))


def cohort_block(c, scores, n):
    block = {"n_pairs": int(len(c["y"])), "n_positive": int(np.sum(c["y"])), "n_anchor_drugs": int(len(set(c["g"]))),
             "n_partner_drugs": int(len(set(c["q"]))), "systems": {}}
    for name, (s, have) in scores.items():
        if len(s) != len(c["y"]):
            raise SystemExit(f"{name}: score length {len(s)} differs from the cohort {len(c['y'])}")
        b = system_block(c, s, n)
        if have is not None:
            b["seeds"] = have
        block["systems"][name] = b
    return block


if __name__ == "__main__":
    main()
