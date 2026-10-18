import rev2_common as rc

SENS = rc.ROOT / "results" / "revision" / "sensitivity" / "bootstrap_coverage.json"
POST7 = rc.ROOT / "results" / "revision" / "post7"
SPIKE = rc.ROOT / "results" / "revision" / "spikein"
Z90 = 1.6448536269514722


def sens_rows():
    d = rc.load(SENS)
    out = []
    for model in ("model_shift", "model_slope"):
        for cohort, scen in d[model].items():
            for name, r in scen.items():
                for scheme, v in (r.items() if "two_way" in r else [("two_way", r)]):
                    if not isinstance(v, dict) or "halfwidth90_over_sd" not in v:
                        continue
                    out.append({"source": "sensitivity", "cohort": cohort, "tier": "A", "model": model, "scenario": name, "scheme": scheme,
                                "sd": v["sd_of_estimate"], "halfwidth90": v["mean_halfwidth90"], "halfwidth_over_sd": v["halfwidth90_over_sd"],
                                "ratio": v["halfwidth90_over_nominal"], "coverage90": v["coverage90"]})
    return d, out


def post7_rows():
    d = rc.load(POST7 / "coverage.json")
    out = []
    for r in d["rows"]:
        cohort, tier = r["design"].split(" tier ")
        for scheme, v in r["result"]["schemes"].items():
            out.append({"source": "post7", "cohort": cohort, "tier": tier, "scenario": r["scenario"], "scheme": scheme,
                        "sd": r["result"]["sd_of_estimate"], "halfwidth90": v["mean_halfwidth90"], "ratio": v["halfwidth90_over_nominal"],
                        "halfwidth_over_sd": v["mean_halfwidth90"] / r["result"]["sd_of_estimate"], "coverage90": v["coverage90"]})
    return d, out


def rng(rows, key):
    v = [r[key] for r in rows]
    return [min(v), max(v)] if v else None


def reconcile():
    sd, srows = sens_rows()
    pd, prows = post7_rows()
    cells = []
    for cohort in ("novel", "older_clean"):
        s = [r for r in srows if r["cohort"] == cohort and r["scheme"] == "two_way"]
        for tier in ("A", "B"):
            p = [r for r in prows if r["cohort"] == cohort and r["tier"] == tier and r["scheme"] == "two_way"]
            cells.append({"cohort": cohort, "tier": tier, "scheme": "two_way",
                          "sensitivity_halfwidth_over_sd": rng(s, "halfwidth_over_sd") if tier == "A" else None,
                          "sensitivity_ratio": rng(s, "ratio") if tier == "A" else None,
                          "post7_halfwidth_over_sd": rng(p, "halfwidth_over_sd"), "post7_ratio": rng(p, "ratio"),
                          "sensitivity_coverage90": rng(s, "coverage90") if tier == "A" else None, "post7_coverage90": rng(p, "coverage90"),
                          "n_sensitivity_scenarios": len(s) if tier == "A" else 0, "n_post7_scenarios": len(p)})
    s_two = [r for r in srows if r["scheme"] == "two_way"]
    p_two_a = [r for r in prows if r["scheme"] == "two_way" and r["tier"] == "A"]
    p_two = [r for r in prows if r["scheme"] == "two_way"]
    one_s = [r for r in srows if r["scheme"] != "two_way"]
    one_p = [r for r in prows if r["scheme"] == "one_way_drug"]
    overall = {"sensitivity_two_way_halfwidth_over_sd": rng(s_two, "halfwidth_over_sd"), "sensitivity_two_way_ratio": rng(s_two, "ratio"),
               "post7_two_way_tierA_ratio": rng(p_two_a, "ratio"), "post7_two_way_tierA_halfwidth_over_sd": rng(p_two_a, "halfwidth_over_sd"),
               "post7_two_way_all_ratio": rng(p_two, "ratio"), "post7_two_way_all_halfwidth_over_sd": rng(p_two, "halfwidth_over_sd"),
               "post7_older_clean_A_two_way_ratio": rng([r for r in p_two_a if r["cohort"] == "older_clean"], "ratio"),
               "sensitivity_one_way_drug_ratio": rng(one_s, "ratio"), "post7_one_way_drug_ratio": rng(one_p, "ratio"),
               "sensitivity_two_way_coverage90": rng(s_two, "coverage90"), "post7_two_way_coverage90": rng(p_two, "coverage90")}
    differences = [
        {"aspect": "normalisation", "sensitivity": "90% half-width / replicate SD; a calibrated interval gives 1.645",
         "post7": "90% half-width / (1.645 x replicate SD); a calibrated interval gives 1", "effect": "the main difference: 2.52 / 1.645 = 1.53 and 3.75 / 1.645 = 2.28"},
        {"aspect": "replicates and seed", "sensitivity": f"{sd['reps']} replicates, {sd['boot']} bootstrap draws, seed {sd['seed']}",
         "post7": f"{pd['reps']} replicates, {pd['boot']} bootstrap draws, seed {pd['seed']}", "effect": "Monte Carlo noise only"},
        {"aspect": "designs", "sensitivity": "Novel and Older-clean, tier A only", "post7": "Novel and Older-clean, tiers A and B",
         "effect": "the post7 headline 1.546 to 2.186 is Older-clean tier A only; over all post7 designs the two-way ratio is wider"},
        {"aspect": "scenarios", "sensitivity": "model A: fixed signal 0 or 0.37 on the score scale, partner SD 0 or 1, drug SD 1; model B: per-drug random slope (mean 0 or 0.37, SD 0.6), partner SD 0 or 1",
         "post7": "target true AUROC 0.45, 0.50, 0.60 crossed with partner SD 0 or 1 and slope SD 0 or 0.5, drug SD 1",
         "effect": "different grids; both have label-independent partner effects; only post7 has a below-chance truth"},
        {"aspect": "true value", "sensitivity": "mean estimate over replicates", "post7": "analytic Phi(beta / sqrt(2 (sigma_p^2 + 1) + tau^2))",
         "effect": "affects coverage, not the half-width ratio"},
        {"aspect": "SD estimator", "sensitivity": "numpy std, ddof 0", "post7": "ddof 1", "effect": "factor sqrt(n/(n-1)), at most 0.2% at 300 replicates"},
        {"aspect": "criteria file", "sensitivity": "none (sensitivity analysis)", "post7": "results/revision/post7/criteria.json analysis_1b_coverage",
         "effect": "only the post7 run is criteria-backed"}]
    p = overall
    statement = (f"Both simulations find the two-way cluster bootstrap conservative on these designs. On a common scale (mean 90% half-width "
                 f"divided by the calibrated 1.645 x SD) the two-way interval is {rc.f3(p['sensitivity_two_way_ratio'][0])} to "
                 f"{rc.f3(p['sensitivity_two_way_ratio'][1])} times nominal in the 300-replicate sensitivity run and "
                 f"{rc.f3(p['post7_two_way_all_ratio'][0])} to {rc.f3(p['post7_two_way_all_ratio'][1])} times nominal over every design of the "
                 f"1000-replicate post7 run ({rc.f3(p['post7_older_clean_A_two_way_ratio'][0])} to {rc.f3(p['post7_older_clean_A_two_way_ratio'][1])} on Older-clean tier A); "
                 f"90% coverage is {rc.f3(p['post7_two_way_coverage90'][0])} to 1.000. The 2.52 to 3.75 figure is the same quantity before division by 1.645. "
                 f"The one-way drug bootstrap is near nominal in both ({rc.f3(p['sensitivity_one_way_drug_ratio'][0])} to {rc.f3(p['sensitivity_one_way_drug_ratio'][1])} and "
                 f"{rc.f3(p['post7_one_way_drug_ratio'][0])} to {rc.f3(p['post7_one_way_drug_ratio'][1])}). In both simulations partner effects are independent of "
                 f"the labels, which the real partner-matched design is not.")
    return {"cells": cells, "overall": overall, "differences": differences, "statement": statement}


def collect():
    cal = rc.load(POST7 / "calibration.json")
    cov = rc.load(POST7 / "coverage.json")
    sp = rc.load(SPIKE / "spikein.json")
    bayes = [r for r in cal["bayes"] if r["id"] == "H1" and r["tier"] == "A"]
    iv = [r for r in cal["intervals"] if r["id"] == "H1" and r["tier"] == "A"]
    po = [s for s in cov["summary"] if s["scheme"] == "partner_only"]
    obs = sp["observed_b2mixed"]["older_clean"]["draws_1000"]["A"]
    thr = sp["thresholds"]["older_clean:b2mixed:A"]
    thr_noise = sp["thresholds"]["older_clean:noise:A"]
    return {
        "bayesian_rope": {"criteria": "results/revision/post7/criteria.json analysis_1c_bayes", "source": "results/revision/post7/calibration.json bayes",
                          "rows": bayes},
        "one_way_and_partner_only_bootstrap": {"criteria": "results/revision/post7/criteria.json analysis_1a_one_way",
                                               "source": "results/revision/post7/calibration.json intervals", "rows": iv},
        "partner_only_coverage": {"criteria": "results/revision/post7/criteria.json analysis_1b_coverage", "source": "results/revision/post7/coverage.json summary",
                                  "rows": po},
        "spikein_kappa_rule": {"criteria": "results/revision/spikein/criteria.json", "source": "results/revision/spikein/spikein.json",
                               "rule": "equivalent if the paired kappa 95% upper bound is at most 0.25, falsified if its 95% lower bound is above 0.25",
                               "b2mixed_base_kappa_falsified_80pct": thr["kappa_rule"], "noise_base_kappa_falsified_80pct": thr_noise["kappa_rule"],
                               "observed_b2mixed_older_clean_A_1000_draws": obs}}


def md(o):
    r = o["reconcile"]
    L = ["# M8: coverage simulations reconciled, and the criteria-backed post hoc results", "", f"Status: {rc.STATUS}.", "",
         "## Reconciled statement", "", r["statement"], "",
         "## Two-way bootstrap by cell", "",
         "| cohort | tier | sensitivity half-width / SD | sensitivity ratio | post7 half-width / SD | post7 ratio | sensitivity 90% coverage | post7 90% coverage | scenarios (sens / post7) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in r["cells"]:
        L.append(f"| {c['cohort']} | {c['tier']} | {rc.ci(c['sensitivity_halfwidth_over_sd'])} | {rc.ci(c['sensitivity_ratio'])} | {rc.ci(c['post7_halfwidth_over_sd'])} | "
                 f"{rc.ci(c['post7_ratio'])} | {rc.ci(c['sensitivity_coverage90'])} | {rc.ci(c['post7_coverage90'])} | {c['n_sensitivity_scenarios']} / {c['n_post7_scenarios']} |")
    L += ["", "Ratio = half-width / (1.645 SD); 1 is calibrated. Half-width / SD: 1.645 is calibrated.", "", "## What differs", "",
          "| aspect | sensitivity/bootstrap_coverage | post7/coverage | consequence |", "| --- | --- | --- | --- |"]
    L += [f"| {d['aspect']} | {d['sensitivity']} | {d['post7']} | {d['effect']} |" for d in r["differences"]]
    c = o["collect"]
    L += ["", "## Post hoc results with a criteria file (copied, not recomputed)", "",
          f"Bayesian region of practical equivalence [0.40, 0.60], H1 Older-clean tier A ({c['bayesian_rope']['criteria']}):", "",
          "| model | posterior mean | 95% CrI | P(in region) | P(AUROC < 0.5) | verdict |", "| --- | --- | --- | --- | --- | --- |"]
    L += [f"| {b['model']} | {rc.f3(b['posterior_mean'])} | {rc.ci(b['cri95'])} | {rc.f3(b['p_in_rope'])} | {rc.f3(b['p_below'])} | {b['verdict']} |" for b in c["bayesian_rope"]["rows"]]
    L += ["", f"Bootstrap schemes, H1 Older-clean tier A ({c['one_way_and_partner_only_bootstrap']['criteria']}):", "",
          "| bootstrap | estimate | 90% CI | 95% CI | p_TOST | Holm (H1, H4, H6) | 95% CI below 0.5 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    L += [f"| {b['scheme']} | {rc.f3(b['value'])} | {rc.ci(b['ci90'])} | {rc.ci(b['ci95'])} | {rc.f3(b['p_tost'])} | {rc.f3(b['p_holm_family_H1_H4_H6'])} | {b['ci95_below_0.5']} |"
          for b in c["one_way_and_partner_only_bootstrap"]["rows"]]
    L += ["", "The one-way drug and partner-only intervals lie inside 0.40 to 0.60 (p_TOST 0.005 and 0.004) and also below 0.5: under those bootstraps the model is below chance, which is inverted information, not equivalence support.", "",
          f"Partner-only coverage ({c['partner_only_coverage']['criteria']}):", "", "| design | 90% coverage range | ratio range | labels | adequate |", "| --- | --- | --- | --- | --- |"]
    L += [f"| {s['design']} | {rc.ci(s['coverage90_range'])} | {rc.ci(s['ratio_range'])} | {s['labels']} | {s['adequate']} |" for s in c["partner_only_coverage"]["rows"]]
    k = c["spikein_kappa_rule"]
    ob = k["observed_b2mixed_older_clean_A_1000_draws"]
    L += ["", f"Spike-in kappa rule ({k['criteria']}): {k['rule']}. Smallest kappa falsified with 80% power on Older-clean tier A: "
          f"{rc.f3(k['b2mixed_base_kappa_falsified_80pct']['b_falsified80_interp'])} (b2mixed base, grid {k['b2mixed_base_kappa_falsified_80pct']['b_falsified80_grid']}), "
          f"{rc.f3(k['noise_base_kappa_falsified_80pct']['b_falsified80_interp'])} (noise base). Observed b2mixed: kappa {rc.f3(ob['kappa'])}, 95% {rc.ci(ob['kappa_ci95'])}, "
          f"upper bound {rc.f3(ob['kappa_ci95'][1])}, decision under the kappa rule: {ob['kappa_decision']}.", ""]
    return "\n".join(L) + "\n"


def main():
    crit = rc.require_criteria()
    out = {"status": rc.STATUS, "criteria": crit["m8"], "reconcile": reconcile(), "collect": collect()}
    text = md(out)
    rc.write("m8_coverage", out, text)
    print(text)


if __name__ == "__main__":
    main()
