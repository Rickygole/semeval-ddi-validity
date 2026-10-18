import argparse
import json

import numpy as np
from scipy.stats import spearmanr

import rev2_common as rc
from amend7_cpu_common import BOOT_SEED, cohort_arrays, drugbank_score, fast_within_auroc, logit, paired_draws, seed_mean, single
from amend7_cpu_exp7_below_chance import partial
from post7_common import comparisons, draws, scheme_weights, tetrad_design
from ddiood import baselines, config
from ddiood import evaluate2 as ev

POST8_E9 = rc.ROOT / "results" / "revision" / "post8" / "e9.json"
AMEND7_E9 = rc.ROOT / "results" / "revision" / "amend7" / "e9.json"
EXP7 = rc.ROOT / "results" / "revision" / "amend7" / "cpu" / "exp7_below_chance.json"
POST7_PARTNER = rc.ROOT / "results" / "revision" / "post7" / "partner.json"
COHORTS = ("novel", "older_clean")
POST7_NAMES = {"b2mixed BiomedBERT": "b2mixed", "Qwen names only": "Qwen names only", "DrugBank lookup": "DrugBank lookup"}
EXP7_NAMES = {"b2mixed BiomedBERT": "b2mixed-biomedbert", "Qwen names only": "llm-qwen-names", "DrugBank lookup": "DrugBank lookup"}


def rho_boot(x, y, n, seed):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.RandomState(seed)
    out, dropped = [], 0
    for _ in range(n):
        i = rng.randint(0, len(x), len(x))
        if np.ptp(x[i]) == 0 or np.ptp(y[i]) == 0:
            dropped += 1
            continue
        out.append(spearmanr(x[i], y[i]).statistic)
    return np.asarray(out), dropped


def perm_p(x, y, n, seed):
    rng = np.random.RandomState(seed)
    obs = abs(spearmanr(x, y).statistic)
    y = np.asarray(y)
    hits = sum(abs(spearmanr(x, rng.permutation(y)).statistic) >= obs - 1e-12 for _ in range(n))
    return float((1 + hits) / (n + 1))


def rho_rows(nboot):
    p8 = rc.load(POST8_E9)
    a7 = rc.load(AMEND7_E9)["e9"]["panel"]
    f1 = {c["name"]: c["semeval_binary_f1"] for c in p8["tiers"]["A"]["older_primary"]["per_checkpoint"]}
    rows = []
    for tier in ("A", "C-auto"):
        for cohort in ("older_primary", "novel"):
            if tier == "A":
                au = dict(zip(a7[cohort]["names"], a7[cohort]["auroc"]))
            else:
                au = {c["name"]: c["auroc_within"] for c in p8["tiers"][tier][cohort]["per_checkpoint"]}
            for fmt in ("marker", "pair", "all"):
                names = [n for n in au if fmt == "all" or n.endswith("-" + fmt)]
                x, y = [f1[n] for n in names], [au[n] for n in names]
                d, dropped = rho_boot(x, y, nboot, 42)
                rows.append({"tier": tier, "cohort": cohort, "format": fmt, "n_checkpoints": len(names),
                             "rho": float(spearmanr(x, y).statistic), "ci95": rc.pct(d), "ci90": rc.pct(d, 5, 95),
                             "n_draws": int(len(d)), "dropped_constant_draws": dropped,
                             "share_draws_below_0": float((d < 0).mean()), "perm_p_two_sided": perm_p(x, y, 10000, 43),
                             "auroc_range": [float(min(y)), float(max(y))], "f1_range": [float(min(x)), float(max(x))]})
    return rows


def panel_scores():
    out = {c: {} for c in COHORTS}
    for r in rc.panel_files():
        name = r["config"]["name"].replace("a7-panel-", "panel ")
        out["novel"][name] = logit(np.asarray(r["eval"]["ood_empty"]["p"], float))
        out["older_clean"][name] = logit(np.asarray(r["eval"]["oodold_empty"]["p"], float))
    return out


def main_scores(truth):
    out = {}
    for cohort, tag in (("novel", "ood"), ("older_clean", "oodold")):
        b2, n = seed_mean("b2mixed-biomedbert", f"{tag}_empty")
        if n != 5:
            raise ValueError("b2mixed needs five seeds")
        out[cohort] = {"b2mixed BiomedBERT": logit(b2), "Qwen names only": logit(single("llm-qwen-names", tag)),
                       "DrugBank lookup": drugbank_score(truth, tag)}
    return out


def summ(est, d):
    return {"value": float(est), "ci95": rc.pct(d), "ci90": rc.pct(d, 5, 95), "n_draws": int(np.sum(~np.isnan(np.asarray(d, float))))}


def adjust_block(truth, ctx, scores, boot):
    res = {}
    for cohort in COHORTS:
        c = cohort_arrays(truth, cohort, "A")
        y, g, q = c["y"], c["g"], c["q"]
        prior = np.asarray([ctx.partner_prior(x) for x in q])
        names = list(scores[cohort])
        raw = [scores[cohort][n][c["mask"]] for n in names]
        adj, slopes = [], []
        for s in raw:
            r, b = partial(s, [prior], g)
            adj.append(r)
            slopes.append(b[0])
        D = paired_draws(y, raw + adj, g, q, boot, BOOT_SEED[cohort])
        k = len(names)
        T = tetrad_design(y, g, q)
        W1, W2 = scheme_weights("two_way", T["nd"], T["nq"], boot, BOOT_SEED[cohort])
        H = np.vstack([comparisons(T, s) for s in raw])
        TV, _ = draws(T, H, W1, W2)
        rows = {}
        for i, n in enumerate(names):
            w, a = fast_within_auroc(y, raw[i], g), fast_within_auroc(y, adj[i], g)
            t = float(H[i].mean())
            rows[n] = {"within": summ(w, D[i]), "partner_adjusted_within": summ(a, D[k + i]),
                       "adjusted_minus_raw": summ(a - w, D[k + i] - D[i]), "slope_on_prior": float(slopes[i]),
                       "tetrad": summ(t, TV[i])}
        res[cohort] = {"n": int(len(y)), "n_pos": int(y.sum()), "n_drugs": int(len(set(g))), "n_partners": int(len(set(q))),
                       "n_tetrads": int(len(T["a"])), "prior_within_auroc": fast_within_auroc(y, prior, g), "systems": rows}
    return res


def checks(res):
    exp7 = rc.load(EXP7)["causes"]
    post7 = rc.load(POST7_PARTNER)["decomposition"]
    out = []
    for cohort in COHORTS:
        for mine, theirs in EXP7_NAMES.items():
            ref = exp7[cohort]["A"]["systems"][theirs]["by_feature"]["iii2_partner_prior_vocab_di"]["partialled_within_auroc"]
            got = res[cohort]["systems"][mine]["partner_adjusted_within"]
            out.append({"check": f"exp7 iii2 partialled, {cohort}, {mine}", "reference": ref["value"], "got": got["value"],
                        "reference_ci95": ref["ci95"], "got_ci95": got["ci95"],
                        "match": abs(ref["value"] - got["value"]) < 6e-4})
        for mine, theirs in POST7_NAMES.items():
            ref = post7[f"{cohort}:A"]["systems"][theirs]["tetrad"]
            got = res[cohort]["systems"][mine]["tetrad"]
            out.append({"check": f"post7 tetrad, {cohort}, {mine}", "reference": ref["value"], "got": got["value"],
                        "reference_ci95": ref["two_way"]["ci95"], "got_ci95": got["ci95"],
                        "match": abs(ref["value"] - got["value"]) < 6e-4 and np.allclose(ref["two_way"]["ci95"], got["ci95"], atol=6e-4)})
    return out


def panel_summary(res):
    out = {}
    for cohort in COHORTS:
        S = {k: v for k, v in res[cohort]["systems"].items() if k.startswith("panel ")}
        out[cohort] = {}
        for stat in ("within", "partner_adjusted_within", "tetrad"):
            v = np.asarray([r[stat]["value"] for r in S.values()])
            out[cohort][stat] = {"min": float(v.min()), "median": float(np.median(v)), "max": float(v.max()),
                                 "n_ci95_upper_below_0.5": int(sum(r[stat]["ci95"][1] < 0.5 for r in S.values())),
                                 "n_ci95_lower_above_0.5": int(sum(r[stat]["ci95"][0] > 0.5 for r in S.values()))}
        d = np.asarray([r["adjusted_minus_raw"]["value"] for r in S.values()])
        out[cohort]["adjusted_minus_raw"] = {"min": float(d.min()), "median": float(np.median(d)), "max": float(d.max())}
    return out


def md(out):
    L = ["# M4: partner anti-correlation", "", f"Status: {rc.STATUS}.", "",
         "## (a) SemEval binary F1 against within-drug AUROC, by input format", "",
         "F1 from `results/revision/post8/e9.json`; tier A AUROC from `results/revision/amend7/e9.json`, C-auto from post8. "
         "Percentile bootstrap over checkpoints (10,000 draws, seed 42); permutation p from 10,000 permutations. With 10 checkpoints per "
         "format the interval is wide, and it ignores the within-checkpoint bootstrap uncertainty of each AUROC.", "",
         "| tier | cohort | format | checkpoints | rho | 95% CI | 90% CI | share of draws < 0 | permutation p | AUROC range |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in out["rho"]:
        L.append(f"| {r['tier']} | {r['cohort']} | {r['format']} | {r['n_checkpoints']} | {rc.f3(r['rho'])} | {rc.ci(r['ci95'])} | "
                 f"{rc.ci(r['ci90'])} | {rc.f3(r['share_draws_below_0'])} | {rc.f3(r['perm_p_two_sided'])} | {rc.ci(r['auroc_range'])} |")
    L += ["", "## (b) Within-drug AUROC, partner-prior-adjusted within-drug AUROC and tetrad AUROC", "",
          "Tier A labels. Partner prior: share of vocabulary Drug Interactions sections naming the partner (label-free, experiment 7 feature iii2). "
          "Adjusted: score residualized on the prior within OOD drug (experiment 7 `partial`). Tetrad: doubly matched tetrad AUROC (post7). "
          "Two-way cluster bootstrap over OOD drugs and partners, 1,000 draws, seeds 1042 Novel and 42 Older-clean; raw and adjusted share draws. "
          "Models on the logit scale, DrugBank on 0/1. Panel checkpoints are single seeds; b2mixed averages 5 seeds.", ""]
    for cohort in COHORTS:
        b = out["adjust"][cohort]
        L += [f"### {cohort} (n = {b['n']}, {b['n_pos']} positive, {b['n_drugs']} drugs, {b['n_partners']} partners, {b['n_tetrads']} tetrads; "
              f"prior alone within-drug AUROC {rc.f3(b['prior_within_auroc'])})", "",
              "| system | within | 95% CI | adjusted | 95% CI | adjusted - within | 95% CI | slope | tetrad | 95% CI |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for n, r in b["systems"].items():
            L.append(f"| {n} | {rc.f3(r['within']['value'])} | {rc.ci(r['within']['ci95'])} | {rc.f3(r['partner_adjusted_within']['value'])} | "
                     f"{rc.ci(r['partner_adjusted_within']['ci95'])} | {rc.f3(r['adjusted_minus_raw']['value'])} | {rc.ci(r['adjusted_minus_raw']['ci95'])} | "
                     f"{r['slope_on_prior']:.3g} | {rc.f3(r['tetrad']['value'])} | {rc.ci(r['tetrad']['ci95'])} |")
        p = out["panel_summary"][cohort]
        L += ["", "Panel (20 checkpoints): " + "; ".join(
            f"{k} min {rc.f3(v['min'])}, median {rc.f3(v['median'])}, max {rc.f3(v['max'])}"
            + (f", 95% upper < 0.5 in {v['n_ci95_upper_below_0.5']}, 95% lower > 0.5 in {v['n_ci95_lower_above_0.5']}" if "n_ci95_upper_below_0.5" in v else "")
            for k, v in p.items()) + ".", ""]
    L += ["## Reproduction checks", "", "| check | reference | got | reference 95% | got 95% | match |", "| --- | --- | --- | --- | --- | --- |"]
    L += [f"| {c['check']} | {rc.f3(c['reference'])} | {rc.f3(c['got'])} | {rc.ci(c['reference_ci95'])} | {rc.ci(c['got_ci95'])} | {c['match']} |" for c in out["checks"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--rho-boot", type=int, default=10000)
    a = ap.parse_args()
    crit = rc.require_criteria()
    truth = ev.load_truth()
    ctx = baselines.Context(json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text()))
    scores = main_scores(truth)
    pan = panel_scores()
    for c in COHORTS:
        scores[c].update(pan[c])
    out = {"status": rc.STATUS, "criteria": crit["m4"], "rho": rho_rows(a.rho_boot), "adjust": adjust_block(truth, ctx, scores, a.boot)}
    out["panel_summary"] = panel_summary(out["adjust"])
    out["checks"] = checks(out["adjust"])
    text = md(out)
    rc.write("m4_partner", out, text)
    print(text)


if __name__ == "__main__":
    main()
