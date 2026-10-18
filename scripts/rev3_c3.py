import argparse
from itertools import combinations

import numpy as np
from scipy.stats import rankdata, spearmanr, t as tdist

import rev3_common as rc
import post8_common as pc
import post8_e9 as p8
import rev2_m4 as m4
from ddiood import amend7_analysis as aa
from ddiood import amend7_panel as pn
from ddiood import evaluate2 as ev

M7 = rc.ROOT / "results" / "revision" / "rev2" / "m7_prereg_endpoint.json"
DECISIONS = rc.ROOT / "results" / "revision" / "eval" / "decisions.json"
POST8_E9 = rc.ROOT / "results" / "revision" / "post8" / "e9.json"
AMEND7_E9 = rc.ROOT / "results" / "revision" / "amend7" / "e9.json"
LO, HI = 0.40, 0.60
ALPHA = 0.05
BETAS = [round(0.005 * i, 3) for i in range(0, 17)]
POWER_SIMS = 5000
POWER_SEED = 2026
NESTED_DRAWS = 10000
NESTED_SEED = 42


def part_a():
    ep = rc.load(M7)["endpoint"]
    dec = rc.load(DECISIONS)
    p_orig = ep["drug_cluster"]["p_tost"]
    fam_sub = {"H1_original_endpoint": p_orig, "H4": dec["H4"]["p_tost"], "H6": dec["H6"]["p_tost"]}
    fam_amended = {"H1": dec["H1"]["p_tost"], "H4": dec["H4"]["p_tost"], "H6": dec["H6"]["p_tost"]}
    adj_sub, adj_am = ev.holm(fam_sub), ev.holm(fam_amended)
    sens = {}
    for drop in ("H4", "H6"):
        f = {k: v for k, v in fam_sub.items() if k != drop}
        sens[f"without_{drop}"] = {"p": f, "holm": ev.holm(f)}
    ci95, ci90 = ep["drug_cluster"]["ci95"], ep["drug_cluster"]["ci90"]
    return {"original_endpoint": {"value": ep["value"], "n": ep["n"], "n_drugs": ep["n_drugs"], "ci95": ci95, "ci90": ci90,
                                  "p_tost": p_orig, "source": "results/revision/rev2/m7_prereg_endpoint.json",
                                  "reproduces_tables_md": ep["reproduces_tables_md"]},
            "family_substituted": {"p": fam_sub, "holm": adj_sub},
            "family_amended_as_filed": {"p": fam_amended, "holm": adj_am},
            "family_size_sensitivity": sens,
            "h1_supported_by_holm": bool(adj_sub["H1_original_endpoint"] < ALPHA and ci90[0] > LO and ci90[1] < HI),
            "h1_reading_95_interval_inside_margin": bool(ci95[0] > LO and ci95[1] < HI),
            "h1_reading_90_interval_inside_margin": bool(ci90[0] > LO and ci90[1] < HI),
            "h1_unadjusted_p_below_alpha": bool(p_orig < ALPHA),
            "rule": "Amendment 5 item 3 family H1, H4, H6; ev.holm; supported needs adjusted p below 0.05 and the 90% interval inside [0.40, 0.60]"}


def draws_matrix(W, st, n, seed, oneway):
    rng = np.random.RandomState(seed)
    D = np.zeros((n, W.shape[0]))
    for b in range(n):
        w1 = np.bincount(rng.randint(0, st["k1"], st["k1"]), minlength=st["k1"])
        if oneway:
            w = w1[st["drug"]].astype(float)
        else:
            w2 = np.bincount(rng.randint(0, st["k2"], st["k2"]), minlength=st["k2"])
            w = w1[st["drug"]] * w2[st["qpos"]] * w2[st["qneg"]]
        D[b] = (W * w).sum(1) / max(w.sum(), 1e-12)
    return D


def variance_block(A, D, names, f1, bound=0.60):
    single = np.var(D, axis=0, ddof=1)
    pair_var = [float(np.var(D[:, i] - D[:, j], ddof=1)) for i, j in combinations(range(len(names)), 2)]
    paired_ref = float(np.mean(pair_var) / 2)
    between = float(np.var(A, ddof=1))
    hi95 = np.percentile(D, 97.5, axis=0)
    return {"between_variance": between, "mean_single_bootstrap_variance": float(single.mean()),
            "ratio_old": between / float(single.mean()), "mean_paired_difference_variance": float(np.mean(pair_var)),
            "paired_within_reference": paired_ref, "ratio_paired": between / paired_ref if paired_ref else None,
            "mean_bootstrap_covariance": float(single.mean() - paired_ref), "n_models": len(names),
            "n_upper_at_most_0.60": int((hi95 <= bound).sum()), "point_range": [float(A.min()), float(A.max())]}


def rho_intervals(x, A, D_two, D_one, idx, nboot):
    x, A = np.asarray(x, float)[idx], np.asarray(A, float)[idx]
    out = {"n_checkpoints": int(len(idx)), "rho": float(spearmanr(x, A).statistic)}
    for label, D in (("two_way", D_two), ("one_way", D_one)):
        r = np.array([pn.spearman(x, D[b][idx]) for b in range(len(D))])
        ok = r[~np.isnan(r)]
        out[f"shared_draw_{label}"] = {"ci95": rc.pct(ok), "ci90": rc.pct(ok, 5, 95), "n_draws": int(len(ok)),
                                       "share_below_0": float((ok < 0).mean())}
    d, dropped = m4.rho_boot(x, A, nboot, 42)
    out["checkpoint_bootstrap"] = {"ci95": rc.pct(d), "ci90": rc.pct(d, 5, 95), "n_draws": int(len(d)), "dropped_constant_draws": dropped,
                                   "share_below_0": float((d < 0).mean()), "perm_p_two_sided": m4.perm_p(x, A, 10000, 43)}
    rng = np.random.RandomState(NESTED_SEED)
    nested = []
    for _ in range(NESTED_DRAWS):
        i = rng.randint(0, len(x), len(x))
        row = D_two[rng.randint(0, len(D_two))][idx]
        if np.ptp(x[i]) == 0 or np.ptp(row[i]) == 0:
            continue
        nested.append(spearmanr(x[i], row[i]).statistic)
    out["nested_two_way"] = {"ci95": rc.pct(nested), "ci90": rc.pct(nested, 5, 95), "n_draws": len(nested),
                             "share_below_0": float((np.asarray(nested) < 0).mean()), "seed": NESTED_SEED}
    return out


def fast_spearman_rows(zr, A):
    ra = rankdata(A, axis=1)
    zc, ac = zr - zr.mean(), ra - ra.mean(axis=1, keepdims=True)
    return (ac @ zc) / np.sqrt((zc ** 2).sum() * (ac ** 2).sum(axis=1))


def power_curve(z, mu, cov, tau, sims, seed):
    n = len(z)
    zs = (z - z.mean()) / z.std(ddof=1)
    zr = rankdata(zs)
    rows = []
    for beta in BETAS:
        rng = np.random.RandomState(seed + int(round(beta * 1000)))
        e = rng.multivariate_normal(np.zeros(n), cov, size=sims)
        u = rng.normal(0, tau, size=(sims, n)) if tau > 0 else 0.0
        A = mu + beta * zs[None, :] + e + u
        r = fast_spearman_rows(zr, A)
        tt = r * np.sqrt((n - 2) / np.maximum(1 - r ** 2, 1e-12))
        p = 2 * tdist.sf(np.abs(tt), n - 2)
        rows.append({"beta": beta, "power": float((p < ALPHA).mean()), "mean_rho": float(r.mean()), "mean_abs_rho": float(np.abs(r).mean())})
    return rows


def power_summary(curve, observed_rho):
    hit = next((r for r in curve if r["power"] >= 0.80), None)
    xs = [r["mean_rho"] for r in curve]
    ps = [r["power"] for r in curve]
    at_obs = float(np.interp(abs(observed_rho), xs, ps)) if max(xs) >= abs(observed_rho) else None
    return {"smallest_beta_power_at_least_0.80": hit["beta"] if hit else None,
            "expected_observed_rho_at_that_beta": hit["mean_rho"] if hit else None,
            "reached_on_grid": hit is not None, "power_at_observed_abs_rho": at_obs,
            "power_at_beta_0": curve[0]["power"], "max_grid_power": max(ps)}


def part_bcd(boot, nboot, sims):
    crit, rows, rule, screens = pc.screens_for_run()
    base, _, (db_ood, db_old) = pc.a7_truth()
    ytest = ev.load_truth().test_y
    models = p8.load_panel(pc.PREDS, ytest)
    tiers = {"A": base, "C-auto": pc.TruthC(base, pc.keep_masks(screens))}
    names = [m["name"] for m in models]
    f1 = np.array([m["semeval_binary_f1"] for m in models])
    strata = {"all": list(range(len(names))), "marker": [i for i, n in enumerate(names) if n.endswith("-marker")],
              "pair": [i for i, n in enumerate(names) if n.endswith("-pair")]}
    ref = rc.load(POST8_E9)
    out_b, out_c, out_d, checks = {}, {}, {}, {}
    for tier, truth in tiers.items():
        for cname in ("older_primary", "novel"):
            key = "ood" if cname == "novel" else "oodold"
            c = truth.cohort(cname)
            scores = [m[key][c["mask"]] for m in models]
            st = pn.pair_structure(c["y"], c["g"], c["q"])
            W = np.stack([pn.win_values(s, st) for s in scores])
            A = W.mean(1)
            seed = aa.BOOT_SEED[cname]
            D2 = draws_matrix(W, st, boot, seed, False)
            D1 = draws_matrix(W, st, boot, seed, True)
            tag = f"{tier}/{cname}"
            v2, v1 = variance_block(A, D2, names, f1), variance_block(A, D1, names, f1)
            r = ref["tiers"][tier][cname]
            checks[tag] = {"two_way_ratio_old_reproduces": bool(abs(v2["ratio_old"] - r["ratio_old"]) < 5e-6),
                           "two_way_ratio_paired_reproduces": bool(abs(v2["ratio_paired"] - r["ratio_paired"]) < 5e-6),
                           "stored_ratio_old": r["ratio_old"], "stored_ratio_paired": r["ratio_paired"]}
            out_b[tag] = {"n_rows": int(len(c["y"])), "n_pos": int(c["y"].sum()), "n_drugs": st["k1"], "n_partners": st["k2"], "seed": seed,
                          "two_way": v2, "one_way": v1}
            obs = {}
            for sname, idx in strata.items():
                obs[sname] = rho_intervals(f1, A, D2, D1, np.array(idx), nboot)
                if sname == "all":
                    b = rc.load(AMEND7_E9)["e9"]["panel"][cname] if tier == "A" else None
                    obs[sname]["stored_shared_draw_two_way"] = None if b is None else [b["rho"], b["rho_lo95"], b["rho_hi95"]]
            out_c[tag] = obs
            pw = {}
            for sname, idx in strata.items():
                idx = np.array(idx)
                z = f1[idx]
                cov = np.cov(D2[:, idx].T)
                tau_obs = float(np.std(A[idx], ddof=1))
                entry = {}
                for tlabel, tau in (("tau_0", 0.0), ("tau_observed_between_sd", tau_obs)):
                    curve = power_curve(z, float(A[idx].mean()), cov, tau, sims, POWER_SEED)
                    entry[tlabel] = {"tau": tau, "curve": curve, "summary": power_summary(curve, obs[sname]["rho"])}
                entry["mean_sampling_sd"] = float(np.sqrt(np.mean(np.diag(cov))))
                entry["f1_sd"] = float(z.std(ddof=1))
                pw[sname] = entry
            out_d[tag] = pw
    return out_b, out_c, out_d, checks


def md(res):
    a, b, c, d = res["a"], res["b"], res["c"], res["d"]
    L = ["# C3: statistics", "", f"Status: {rc.STATUS}.", "", "## (a) Holm family with the originally registered H1 endpoint", ""]
    o = a["original_endpoint"]
    L += [f"Original endpoint: pooled Novel AUROC {rc.f3(o['value'])}, n = {o['n']}, {o['n_drugs']} drugs, 95% {rc.ci(o['ci95'])}, 90% {rc.ci(o['ci90'])}, "
          f"p_TOST {o['p_tost']:.6f}. Reproduces tables.md: {o['reproduces_tables_md']}.", ""]
    rows = []
    for name, fam in (("substituted (original H1, amended H4, H6)", a["family_substituted"]), ("as filed (Older-clean H1, H4, H6)", a["family_amended_as_filed"])):
        for k in fam["p"]:
            rows.append((name, k, f"{fam['p'][k]:.6f}", f"{fam['holm'][k]:.6f}"))
    L += rc.table(["family", "hypothesis", "raw p_TOST", "Holm adjusted p"], rows) + [""]
    rows = [(k, ", ".join(f"{h}={p:.4f}" for h, p in v["holm"].items())) for k, v in a["family_size_sensitivity"].items()]
    L += ["Family size sensitivity (Holm adjusted):", ""] + rc.table(["family", "adjusted p"], rows) + [""]
    L += [f"H1 supported by the Holm rule (adjusted p below 0.05 and 90% interval inside [0.40, 0.60]): {a['h1_supported_by_holm']}.",
          f"Unadjusted p_TOST below 0.05: {a['h1_unadjusted_p_below_alpha']}. 95% interval inside [0.40, 0.60]: {a['h1_reading_95_interval_inside_margin']}. "
          f"90% interval inside [0.40, 0.60]: {a['h1_reading_90_interval_inside_margin']}.", "",
          "## (b) Panel between-model to sampling variance ratio, two-way against one-way drug bootstrap", ""]
    rows = []
    for tag, v in b.items():
        for sch in ("two_way", "one_way"):
            x = v[sch]
            rows.append((tag, sch, v["n_drugs"], v["n_partners"], f"{x['between_variance']:.6f}", f"{x['mean_single_bootstrap_variance']:.6f}",
                         f"{x['ratio_old']:.3f}", f"{x['paired_within_reference']:.6f}", f"{x['ratio_paired']:.3f}", f"{x['mean_bootstrap_covariance']:.6f}",
                         x["n_upper_at_most_0.60"]))
    L += rc.table(["tier/cohort", "bootstrap", "drugs", "partners", "between variance", "mean single variance", "ratio_old", "paired reference",
                   "ratio_paired", "mean covariance", "upper95 <= 0.60"], rows) + [""]
    rows = [(t, v["two_way_ratio_old_reproduces"], v["two_way_ratio_paired_reproduces"], f"{v['stored_ratio_old']:.3f}", f"{v['stored_ratio_paired']:.3f}") for t, v in res["checks"].items()]
    L += ["Reproduction of the stored two-way ratios (results/revision/post8/e9.json):", ""] + rc.table(["tier/cohort", "ratio_old", "ratio_paired", "stored ratio_old", "stored ratio_paired"], rows) + [""]
    L += ["## (c) Spearman rho of SemEval binary F1 against within-drug AUROC", ""]
    rows = []
    for tag, strata in c.items():
        for s, v in strata.items():
            sd2, sd1, cb, ne = v["shared_draw_two_way"], v["shared_draw_one_way"], v["checkpoint_bootstrap"], v["nested_two_way"]
            rows.append((tag, s, v["n_checkpoints"], rc.f3(v["rho"]), rc.ci(sd2["ci95"]), rc.ci(sd1["ci95"]), rc.ci(cb["ci95"]), f"{cb['perm_p_two_sided']:.3f}", rc.ci(ne["ci95"])))
    L += rc.table(["tier/cohort", "stratum", "checkpoints", "rho", "shared-draw two-way 95%", "shared-draw one-way 95%", "checkpoint bootstrap 95%",
                   "permutation p", "nested 95%"], rows) + [""]
    L += ["## (d) Power by simulation", "",
          "beta is AUROC per standard deviation of SemEval F1; tau is extra between-model SD. Detectable rho is the mean observed Spearman rho at the smallest beta of the plan grid (0 to 0.08) with power at least 0.80.", ""]
    rows = []
    for tag, strata in d.items():
        for s, v in strata.items():
            for tl in ("tau_0", "tau_observed_between_sd"):
                sm = v[tl]["summary"]
                rows.append((tag, s, tl, f"{v['mean_sampling_sd']:.4f}", f"{v[tl]['tau']:.4f}", sm["smallest_beta_power_at_least_0.80"] if sm["reached_on_grid"] else "not reached",
                             rc.f3(sm["expected_observed_rho_at_that_beta"]), rc.f3(sm["power_at_observed_abs_rho"]), rc.f3(sm["max_grid_power"]), rc.f3(sm["power_at_beta_0"])))
    L += rc.table(["tier/cohort", "stratum", "setting", "mean sampling SD", "tau", "smallest beta, power >= 0.80", "expected rho there", "power at observed |rho|",
                   "max power on grid", "size at beta 0"], rows) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--rho-boot", type=int, default=10000)
    ap.add_argument("--sims", type=int, default=POWER_SIMS)
    a = ap.parse_args()
    ra = part_a()
    b, c, d, checks = part_bcd(a.boot, a.rho_boot, a.sims)
    res = {"a": ra, "b": b, "c": c, "d": d, "checks": checks, "boot": a.boot, "rho_boot": a.rho_boot, "power_sims": a.sims,
           "power_grid": BETAS, "power_seed": POWER_SEED}
    rc.write("c3_statistics", res, md(res))
    print(rc.OUT / "c3_statistics.md")


if __name__ == "__main__":
    main()
