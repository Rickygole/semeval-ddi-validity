import argparse
import json

import numpy as np
from scipy.stats import norm, rankdata

from post7_common import (BOOT_SEED, COHORTS, STATUS, TIERS, additive_scale, cell, ci, codes, comparisons, draws,
                          estimate, ev, f3, partner_design, require_criteria, scheme_weights, summarize, systems,
                          tetrad_design, within_design, write)

ORDER = ("DrugBank lookup", "b2mixed", "Qwen names only", "b1names", "b2sentence")
STATS = ("within", "partner_stratified", "tetrad")
LAMBDAS = (-np.inf, -5.0, -2.0, -1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0, 2.0, 5.0, np.inf)


def designs(y, g, q):
    return {"within": within_design(y, g, q), "partner_stratified": partner_design(y, g, q), "tetrad": tetrad_design(y, g, q)}


def stat_block(D, scores, scheme, boot, seed):
    first = next(iter(D.values()))
    W1, W2 = scheme_weights(scheme, first["nd"], first["nq"], boot, seed)
    out = {}
    for k, d in D.items():
        H = np.vstack([comparisons(d, s) for s in scores])
        v, _ = draws(d, H, W1, W2)
        out[k] = v
    return out


def explained(w, s_block, valid):
    if s_block["ci95"] is None:
        return {"contains_0.5": None, "moved": None, "valid": valid, "explained": False}
    lo, hi = s_block["ci95"]
    contains = bool(lo <= 0.5 <= hi)
    moved = bool(abs(s_block["value"] - 0.5) <= abs(w - 0.5) - 0.03)
    return {"contains_0.5": contains, "moved_at_least_0.03_toward_0.5": moved, "valid": valid,
            "explained": bool(contains and moved and valid)}


def decomposition(truth, S, boot):
    res = {}
    for cohort in COHORTS:
        for tier in TIERS:
            c = cell(truth, cohort, tier)
            y, g, q = c["y"], c["g"], c["q"]
            D = designs(y, g, q)
            scores = [additive_scale(n, S[cohort][n][c["mask"]]) for n in ORDER]
            blocks = {sc: stat_block(D, scores, sc, boot, BOOT_SEED[cohort]) for sc in ("two_way", "one_way_drug")}
            cellres = {"n": int(len(y)), "n_drugs": int(len(set(g))),
                       "n_comparisons": {k: int(len(d["a"] if k == "tetrad" else d["i"])) for k, d in D.items()},
                       "n_drugs_in_tetrads": int(len(set(D["tetrad"]["d1"]) | set(D["tetrad"]["d2"]))), "systems": {}}
            for si, name in enumerate(ORDER):
                row = {}
                for k in STATS:
                    est = estimate(D[k], scores[si])
                    row[k] = {"value": est}
                    for sc, b in blocks.items():
                        row[k][sc] = summarize(est, b[k][si])
                        if k != "within":
                            w = b["within"][si]
                            v = b[k][si]
                            ok = ~np.isnan(w) & ~np.isnan(v)
                            sh = summarize(row["within"]["value"] - est, w[ok] - v[ok])
                            row[k][sc]["partner_component_within_minus_this"] = {kk: sh[kk] for kk in ("value", "ci90", "ci95", "n_draws")}
                cellres["systems"][name] = row
            res[f"{cohort}:{tier}"] = cellres
    for key, cr in res.items():
        cohort, tier = key.split(":")
        ref = res[f"{cohort}:A"]["systems"]["DrugBank lookup"]
        for k in ("partner_stratified", "tetrad"):
            lo = ref[k]["two_way"]["ci95"][0] if ref[k]["two_way"]["ci95"] else None
            valid = bool(lo is not None and lo > 0.5)
            cr.setdefault("validity", {})[k] = {"drugbank_tier_A_value": ref[k]["value"], "drugbank_tier_A_lower95_two_way": lo,
                                                "valid": valid}
            for name, row in cr["systems"].items():
                if name == "DrugBank lookup":
                    continue
                for sc in ("two_way", "one_way_drug"):
                    row[k][sc]["verdict"] = explained(row["within"]["value"], row[k][sc], valid)
    return res


def within_ranks(x, gc):
    dense = rankdata(x, method="dense")
    r = rankdata(gc.astype(np.int64) * (len(x) + 1) + dense)
    size = np.bincount(gc)
    r = r - (np.cumsum(size) - size)[gc]
    m = np.bincount(gc, weights=r) / size
    return r - m[gc]


def weighted_corr(a, b, w):
    num = (w * a * b).sum()
    den = np.sqrt((w * a * a).sum() * (w * b * b).sum())
    return float(num / den) if den > 0 else float("nan")


def within_spearman_matrix(Sm, f, gc):
    fb = within_ranks(f, gc)
    out = []
    for s in Sm:
        out.append(weighted_corr(within_ranks(s, gc), fb, np.ones(len(f))))
    return np.asarray(out)


def popularity(truth):
    from ddiood import baselines, config
    ctx = baselines.Context(json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text()))
    return ctx


def normal_scores(x):
    return norm.ppf((rankdata(x) - 0.5) / len(x))


def curve(y, g, q, f, reps, rng):
    D = within_design(y, g, q)
    gc = codes(g)
    z = normal_scores(f)
    rows = []
    for lam in LAMBDAS:
        if np.isinf(lam):
            Sm = np.sign(lam) * z[None, :]
        else:
            Sm = lam * z[None, :] + rng.standard_normal((reps, len(y)))
        H = np.vstack([comparisons(D, s) for s in Sm])
        auc = H.mean(1)
        sp = within_spearman_matrix(Sm, f, gc)
        rows.append({"lambda": float(lam) if not np.isinf(lam) else ("+inf" if lam > 0 else "-inf"),
                     "mean_within_auroc": float(auc.mean()), "sd_within_auroc": float(auc.std()),
                     "mean_within_spearman": float(np.nanmean(sp))})
    return rows


def interp_on(rows, xkey, ykey, x):
    xs = np.asarray([r[xkey] for r in rows])
    ys = np.asarray([r[ykey] for r in rows])
    o = np.argsort(xs)
    xs, ys = xs[o], ys[o]
    if x < xs.min() or x > xs.max():
        return None
    return float(np.interp(x, xs, ys))


def lambda_for_auc(rows, target):
    vals = [(r["lambda"], r["mean_within_auroc"]) for r in rows]
    for (l1, a1), (l2, a2) in zip(vals, vals[1:]):
        if (a1 - target) * (a2 - target) <= 0 and a1 != a2:
            return {"between_lambda": [l1, l2], "reachable": True}
    a = [v for _, v in vals]
    return {"reachable": False, "auroc_range_over_lambda": [float(min(a)), float(max(a))]}


def simulation(truth, S, reps, boot):
    from amend7_cpu_exp7_below_chance import loo_partner
    ctx = popularity(truth)
    rng = np.random.default_rng(21)
    out = {}
    for cohort in COHORTS:
        full = cell(truth, cohort, "A")
        _, loo = loo_partner(full["y"], full["g"], full["q"])
        for tier in TIERS:
            c = cell(truth, cohort, tier)
            sel = c["mask"][full["mask"]]
            y, g, q = c["y"], c["g"], c["q"]
            gc = codes(g)
            b2 = additive_scale("b2mixed", S[cohort]["b2mixed"][c["mask"]])
            w_b2 = estimate(within_design(y, g, q), b2)
            feats = {"label-free popularity": np.asarray([ctx.partner_prior(x) for x in q]),
                     "leave-one-drug-out partner positive rate (label-derived contrast)": loo[sel]}
            cres = {"b2mixed_within_auroc": w_b2, "features": {}}
            for fname, f in feats.items():
                rows = curve(y, g, q, f, reps, rng)
                sp_b2 = float(within_spearman_matrix(b2[None, :], f, gc)[0])
                pos = [r for r in rows if r["lambda"] == "+inf" or (not isinstance(r["lambda"], str) and r["lambda"] >= 0)]
                neg = [r for r in rows if r["lambda"] == "-inf" or (not isinstance(r["lambda"], str) and r["lambda"] <= 0)]
                side = pos if sp_b2 >= 0 else neg
                matched = interp_on(side, "mean_within_spearman", "mean_within_auroc", sp_b2)
                feature_auc = estimate(within_design(y, g, q), f)
                cres["features"][fname] = {"feature_within_auroc": feature_auc, "curve": rows,
                                           "b2mixed_within_spearman": sp_b2,
                                           "matched_auroc": matched,
                                           "matched_reachable": matched is not None,
                                           "auroc_equal_to_b2mixed": lambda_for_auc(rows, w_b2)}
                gap = w_b2 - 0.5
                share = None if matched is None or gap == 0 else (matched - 0.5) / gap
                cres["features"][fname]["share_of_gap_reproduced"] = share
                if fname == "label-free popularity":
                    cres["features"][fname]["popularity_explains"] = bool(share is not None and share >= 0.5)
                    cres["features"][fname]["decomposition"] = popularity_decomposition(y, g, b2, f, side, boot, BOOT_SEED[cohort])
            out[f"{cohort}:{tier}"] = cres
    return out


def popularity_decomposition(y, g, b2, f, side, boot, seed):
    D = within_design(y, g, np.arange(len(y)))
    gc = codes(g)
    H = comparisons(D, b2)
    U = np.bincount(D["d"], weights=H, minlength=D["nd"])
    N = np.bincount(D["d"], minlength=D["nd"]).astype(float)
    rs, rf = within_ranks(b2, gc), within_ranks(f, gc)
    W1, _ = scheme_weights("one_way_drug", D["nd"], 1, boot, seed)
    xs = np.asarray([r["mean_within_spearman"] for r in side])
    ys = np.asarray([r["mean_within_auroc"] for r in side])
    o = np.argsort(xs)
    xs, ys = xs[o], ys[o]
    comp, resid, clipped = [], [], 0
    for w in W1:
        a = float((w @ U) / (w @ N))
        sp = weighted_corr(rs, rf, w[gc])
        if sp < xs.min() or sp > xs.max():
            clipped += 1
        m = float(np.interp(sp, xs, ys))
        comp.append(m - 0.5)
        resid.append(a - m)
    est_sp = weighted_corr(rs, rf, np.ones(len(y)))
    m0 = float(np.interp(est_sp, xs, ys))
    a0 = float(U.sum() / N.sum())
    return {"popularity_component": summarize(m0 - 0.5, np.asarray(comp)),
            "residual": summarize(a0 - m0, np.asarray(resid)),
            "draws_outside_curve_clipped": int(clipped), "bootstrap": f"one-way drug, {boot} draws, seed {seed}"}


def md(res):
    L = ["# Partner structure and the below-chance Older-clean result", "", f"Status: {STATUS}.", "",
         "The partner-stratified and tetrad statistics are a decomposition of the within-drug AUROC by partner structure. They do not "
         "replace H1, whose preregistered statistic and decision are unchanged. The leave-one-drug-out partialling of experiment 7 "
         "drives the DrugBank lookup to 0.398 within drug, which shows that adjustment is broken; it is not used here as an explanation.", "",
         "## 2a. Validity first: does the DrugBank lookup keep its signal?", "",
         "| cohort | statistic | DrugBank tier A | two-way 95% lower bound | valid decomposition |", "| --- | --- | --- | --- | --- |"]
    for cohort in COHORTS:
        for k, v in res["decomposition"][f"{cohort}:A"]["validity"].items():
            L.append(f"| {cohort} | {k} | {f3(v['drugbank_tier_A_value'])} | {f3(v['drugbank_tier_A_lower95_two_way'])} | {v['valid']} |")
    L += ["", "## 2a. Decomposition by system", "",
          "W is the within-drug AUROC (the H1 statistic), P the partner-stratified AUROC (primary), T the tetrad AUROC (secondary). "
          "Intervals are two-way cluster bootstrap 95% (one-way drug in brackets after the slash). W - P and W - T are paired. "
          "Explained: the statistic's 95% interval contains 0.5, |S - 0.5| <= |W - 0.5| - 0.03, and the statistic is valid.", ""]
    for key, cr in res["decomposition"].items():
        L += [f"### {key.replace(':', ', tier ')} (n = {cr['n']}, {cr['n_drugs']} drugs; comparisons: within {cr['n_comparisons']['within']}, "
              f"partner {cr['n_comparisons']['partner_stratified']}, tetrads {cr['n_comparisons']['tetrad']} over {cr['n_drugs_in_tetrads']} drugs)", "",
              "| system | W | W 95% CI | P | P 95% CI two-way / one-way | W - P | 95% CI | P explained (two-way / one-way) | T | T 95% CI two-way / one-way | W - T | 95% CI | T explained (two-way / one-way) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for name, r in cr["systems"].items():
            cells = [name, f3(r["within"]["value"]), f"{ci(r['within']['two_way']['ci95'])} / {ci(r['within']['one_way_drug']['ci95'])}"]
            for k in ("partner_stratified", "tetrad"):
                t, o = r[k]["two_way"], r[k]["one_way_drug"]
                v2 = t.get("verdict", {}).get("explained", "")
                v1 = o.get("verdict", {}).get("explained", "")
                cells += [f3(r[k]["value"]), f"{ci(t['ci95'])} / {ci(o['ci95'])}",
                          f3(t["partner_component_within_minus_this"]["value"]), ci(t["partner_component_within_minus_this"]["ci95"]),
                          "" if name == "DrugBank lookup" else f"{v2} / {v1}"]
            L.append("| " + " | ".join(cells) + " |")
        L.append("")
    L += ["## 2b. Popularity-only scorer on the frozen designs", "",
          "Scorer s = lambda z(pop) + e, z the normal scores of partner popularity (share of vocabulary Drug Interactions sections "
          "naming the partner), e standard normal, 300 replicates per lambda. The label-derived leave-one-drug-out partner positive rate "
          "is run the same way as a contrast and carries no decision.", "",
          "| cell | feature | feature within-drug AUROC | b2mixed W | b2mixed within-drug Spearman | scorer AUROC at matched Spearman | share of gap | AUROC equal to b2mixed reachable | scorer AUROC range |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key, cr in res["simulation"].items():
        for fname, fr in cr["features"].items():
            reach = fr["auroc_equal_to_b2mixed"]
            rng_ = reach.get("auroc_range_over_lambda")
            a = [r["mean_within_auroc"] for r in fr["curve"]]
            L.append(f"| {key} | {fname} | {f3(fr['feature_within_auroc'])} | {f3(cr['b2mixed_within_auroc'])} | {f3(fr['b2mixed_within_spearman'])} | "
                     f"{f3(fr['matched_auroc'])} | {f3(fr.get('share_of_gap_reproduced'))} | {reach['reachable']}"
                     f"{' between lambda ' + str(reach['between_lambda']) if reach['reachable'] else ''} | [{f3(min(a))}, {f3(max(a))}] |")
    L += ["", "Curve for Older-clean tier A:", "", "| feature | lambda | mean within-drug AUROC | SD | mean within-drug Spearman |", "| --- | --- | --- | --- | --- |"]
    for fname, fr in res["simulation"]["older_clean:A"]["features"].items():
        for r in fr["curve"]:
            L.append(f"| {fname} | {r['lambda']} | {f3(r['mean_within_auroc'])} | {f3(r['sd_within_auroc'])} | {f3(r['mean_within_spearman'])} |")
    L += ["", "## 2c. Decomposition of the b2mixed gap from 0.5", "",
          "| cell | W - 0.5 | partner component W - P (two-way 95%) | residual P - 0.5 | tetrad component W - T (two-way 95%) | residual T - 0.5 | popularity component (one-way drug 95%) | residual after popularity |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key in res["decomposition"]:
        r = res["decomposition"][key]["systems"]["b2mixed"]
        dp = res["simulation"][key]["features"]["label-free popularity"]["decomposition"]
        pc, tc = r["partner_stratified"]["two_way"]["partner_component_within_minus_this"], r["tetrad"]["two_way"]["partner_component_within_minus_this"]
        L.append(f"| {key} | {f3(r['within']['value'] - 0.5)} | {f3(pc['value'])} {ci(pc['ci95'])} | {f3(r['partner_stratified']['value'] - 0.5)} | "
                 f"{f3(tc['value'])} {ci(tc['ci95'])} | {f3(r['tetrad']['value'] - 0.5)} | "
                 f"{f3(dp['popularity_component']['value'])} {ci(dp['popularity_component']['ci95'])} | "
                 f"{f3(dp['residual']['value'])} {ci(dp['residual']['ci95'])} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--reps", type=int, default=300)
    a = ap.parse_args()
    crit = require_criteria()
    truth = ev.load_truth()
    S = systems(truth)
    res = {"status": STATUS, "criteria": {k: crit[k] for k in ("analysis_2a_partner_decomposition", "analysis_2b_popularity_simulation",
                                                                "analysis_2c_decomposition")},
           "decomposition": decomposition(truth, S, a.boot), "simulation": simulation(truth, S, a.reps, a.boot),
           "boot": a.boot, "reps": a.reps}
    prim = res["decomposition"]["older_clean:A"]["systems"]["b2mixed"]
    res["primary"] = {"cell": "b2mixed, Older-clean, tier A", "within": prim["within"]["value"],
                      "partner_stratified": prim["partner_stratified"]["two_way"],
                      "tetrad": prim["tetrad"]["two_way"],
                      "popularity": {k: res["simulation"]["older_clean:A"]["features"]["label-free popularity"][k]
                                     for k in ("matched_auroc", "share_of_gap_reproduced", "popularity_explains", "b2mixed_within_spearman")}}
    text = md(res)
    write("partner", res, text)
    print(text)


if __name__ == "__main__":
    main()
