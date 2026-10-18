import argparse
import json

import numpy as np

import spikein_core as sc
from ddiood import evaluate2 as ev

OBS_KAPPA_UPPER = 0.133
RULES = (("auroc_rule", "AUROC rule, two-way"), ("auroc_rule_holm", "AUROC rule, Holm"),
         ("auroc_rule_one_way", "AUROC rule, one-way drug bootstrap"), ("kappa_rule", "kappa rule (upper95 <= 0.25)"))


def f3(v):
    return "NA" if v is None or (isinstance(v, float) and v != v) else f"{v:.3f}"


def f2(v):
    return "NA" if v is None else f"{v:.2f}"


def thresholds(grid_rows):
    k = [r["target_kappa"] for r in grid_rows]
    out = {}
    for rule, _ in RULES:
        pf = [r[rule]["falsified"] for r in grid_rows]
        pe = [r[rule]["equivalent"] for r in grid_rows]
        b_grid, b_x = sc.crossing_up(k, pf, 0.80)
        c_grid, c_x = sc.crossing_down(k, pe, 0.20)
        out[rule] = {"b_falsified80_grid": b_grid, "b_falsified80_interp": b_x,
                     "c_equivalent20_grid": c_grid, "c_equivalent20_interp": c_x,
                     "equivalent50_interp": sc.crossing_down(k, pe, 0.50)[1]}
    pd = [r["p_detected"] for r in grid_rows]
    out["detected80"] = dict(zip(("grid", "interp"), sc.crossing_up(k, pd, 0.80)))
    out["detected80_one_way"] = dict(zip(("grid", "interp"), sc.crossing_up(k, [r["p_detected_one_way"] for r in grid_rows], 0.80)))
    return out


def at_kappa(grid_rows, x):
    k = np.array([r["target_kappa"] for r in grid_rows])
    if x < k.min() or x > k.max():
        return None
    out = {}
    for rule, _ in RULES:
        out[rule] = {d: float(np.interp(x, k, [r[rule][d] for r in grid_rows])) for d in ("falsified", "equivalent", "inconclusive")}
    out["p_detected"] = float(np.interp(x, k, [r["p_detected"] for r in grid_rows]))
    return out


def grid_table(rows):
    md = ["| kappa | w | realised kappa (sd) | AUROC | mean 90% CI | P fals | P equiv | P inc | P equiv Holm | P fals 1-way | P equiv 1-way | "
          "kappa rule P fals | kappa rule P equiv | mean kappa 95% CI | P detected |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        a, h, o, k = r["auroc_rule"], r["auroc_rule_holm"], r["auroc_rule_one_way"], r["kappa_rule"]
        md.append(f"| {r['target_kappa']} | {f3(r['w'])} | {f3(r['realised_kappa_mean'])} ({f3(r['realised_kappa_sd'])}) | "
                  f"{f3(r['realised_auroc_mean'])} | [{f3(r['mean_lo90'])}, {f3(r['mean_hi90'])}] | {f2(a['falsified'])} | "
                  f"{f2(a['equivalent'])} | {f2(a['inconclusive'])} | {f2(h['equivalent'])} | {f2(o['falsified'])} | "
                  f"{f2(o['equivalent'])} | {f2(k['falsified'])} | {f2(k['equivalent'])} | "
                  f"[{f3(r['mean_kappa_lo95'])}, {f3(r['mean_kappa_hi95'])}] | {f2(r['p_detected'])} |")
    return md


def summary_line(name, tier, t):
    a, k, o = t["auroc_rule"], t["kappa_rule"], t["auroc_rule_one_way"]
    return (f"| {name} | {tier} | {f2(a['b_falsified80_grid'])} ({f3(a['b_falsified80_interp'])}) | "
            f"{f2(a['c_equivalent20_grid'])} ({f3(a['c_equivalent20_interp'])}) | "
            f"{f2(t['auroc_rule_holm']['c_equivalent20_grid'])} | {f2(o['b_falsified80_grid'])} | {f2(o['c_equivalent20_grid'])} | "
            f"{f2(k['b_falsified80_grid'])} ({f3(k['b_falsified80_interp'])}) | "
            f"{f2(k['c_equivalent20_grid'])} ({f3(k['c_equivalent20_interp'])}) | "
            f"{f2(t['detected80']['grid'])} ({f3(t['detected80']['interp'])}) |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(sc.OUT / "spikein_raw.json"))
    a = ap.parse_args()
    raw = json.loads(open(a.raw).read())
    crit = sc.load_criteria()
    if raw["criteria"] != crit:
        raise ValueError("criteria changed after the run")
    jobs = {j["name"]: j for j in raw["jobs"]}
    summ = {}
    for name, j in jobs.items():
        for tier, t in j["tiers"].items():
            summ[f"{name}:{tier}"] = thresholds(t["grid"])
    obs = raw["observed_b2mixed"]
    place = {}
    for base in ("b2mixed", "noise"):
        rows = jobs[f"older_clean:{base}"]["tiers"]["A"]["grid"]
        place[base] = {"at_kappa_upper_0.133": at_kappa(rows, OBS_KAPPA_UPPER),
                       "grid_points_excluded_by_upper_bound": [r["target_kappa"] for r in rows if r["target_kappa"] > OBS_KAPPA_UPPER]}
    mid = {}
    for base in ("b2mixed", "noise"):
        ref = summ[f"older_clean:{base}:A"]
        reals = [summ[k] for k in summ if k.startswith("middle") and k.endswith(f":{base}:A")]
        mid[base] = {}
        for rule in ("auroc_rule", "kappa_rule"):
            for key in ("b_falsified80_interp", "c_equivalent20_interp"):
                vals = [r[rule][key] for r in reals]
                mid[base][f"{rule}:{key}"] = {"older_clean": ref[rule][key], "middle_realisations": vals,
                                              "middle_mean": None if any(v is None for v in vals) else float(np.mean(vals))}
        dv = [r["detected80"]["interp"] for r in reals]
        mid[base]["detected80_interp"] = {"older_clean": ref["detected80"]["interp"], "middle_realisations": dv}
    out = {"status": crit["status"], "criteria": crit, "settings": raw["settings"], "observed_b2mixed": obs,
           "thresholds": summ, "observed_placement": place, "middle_cohort": mid,
           "jobs": {n: {"calibration": j["calibration"], "unreachable": j["unreachable"], "picked": j.get("picked"),
                        "tiers": j["tiers"]} for n, j in jobs.items()}}
    (sc.OUT / "spikein.json").write_text(json.dumps(ev.clean(out), indent=1) + "\n")

    md = ["# Spike-in sensitivity calibration", "",
          "Post hoc and exploratory; it changes no preregistered decision. Criteria were fixed in `criteria.json` before any run.", "",
          "Synthetic scores on the frozen rows: s = w * rank(DrugBank lookup, random tie-break) + (1 - w) * (rank(base) + 0.1 * z), "
          "w calibrated so the realised within-drug kappa (against the real DrugBank within-drug AUROC of the same rows) matches the target "
          "in expectation. Each rep goes through the H1 pipeline: within-drug AUROC, two-way cluster bootstrap "
          f"({raw['settings']['boot']} draws, seed 42 Older, 1042 Novel), 90% and 95% percentile intervals, p_TOST, decision. "
          f"{raw['settings']['reps']} reps per grid point.", "",
          "Rules. AUROC rule (H1): equivalent if the 90% interval is inside (0.40, 0.60), falsified if the 95% lower bound is above 0.60. "
          "Holm: evaluate2.decide_equivalence with Holm over H1, H4 = 0.3387, H6 = 0.1019. Kappa rule: equivalent if the paired kappa 95% "
          "upper bound is at most 0.25, falsified if its 95% lower bound is above 0.25. Detected: within-drug AUROC 95% lower bound above 0.50.", "",
          "Deviation from criteria.json, decided after a smoke run with tiny settings and before the full run: the criteria flag a "
          "target outside the calibration curve as unreachable. Monte Carlo error put the exact endpoints (kappa 1 at w = 1 for both "
          "bases, kappa 0 at w = 0 for the noise base) a hair outside the curve, so a target within 3 Monte Carlo standard errors of an "
          "endpoint is set to that endpoint; each job lists the targets this affected. On Novel the b2mixed base already has kappa about "
          "0.10 at w = 0, so its targets 0 and 0.05 are unreachable and were not run; the noise base covers them.", "",
          "Tier B note: the DrugBank lookup agrees with the label on every tier B row by construction, so its tier B ceiling is 1.000 "
          "and tier B kappa is on a different scale; the x axis stays the tier A target.", "",
          "## Observed b2mixed through the same pipeline", "",
          "| cohort | tier | draws | AUROC | 90% CI | 95% CI | p_TOST | decision | Holm | one-way | kappa | kappa 95% CI | kappa rule |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in ("older_clean", "novel"):
        for nd in ("draws_1000", "draws_300"):
            for tier in ("A", "B"):
                o = obs[c][nd][tier]
                md.append(f"| {c} | {tier} | {o['n_draws']} | {f3(o['auroc'])} | [{f3(o['ci90'][0])}, {f3(o['ci90'][1])}] | "
                          f"[{f3(o['ci95'][0])}, {f3(o['ci95'][1])}] | {f3(o['p_tost'])} | {o['decision']} | {o['decision_holm']} | "
                          f"{o['decision_one_way']} | {f3(o['kappa'])} | [{f3(o['kappa_ci95'][0])}, {f3(o['kappa_ci95'][1])}] | {o['kappa_decision']} |")
    md += ["", "Older-clean tier A with 1000 draws reproduces decisions.json H1 (0.452, 90% [0.395, 0.509], p_TOST 0.061, inconclusive) "
           "and kappa_weighting.md (kappa -0.342, 95% [-0.794, 0.133]).", "",
           "## Thresholds", "",
           "b = smallest kappa falsified with 80% power; c = largest kappa still judged equivalent at least 20% of the time. "
           "Grid value, then the interpolated crossing in parentheses. NA = never reached on the grid.", "",
           "| job | tier | b AUROC rule | c AUROC rule | c Holm | b one-way | c one-way | b kappa rule | c kappa rule | detected 80% |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, t in summ.items():
        n, base, tier = k.rsplit(":", 2)
        md.append(summary_line(f"{n}:{base}", tier, t))
    md += ["", "## Where the observed result sits (Older-clean tier A)", ""]
    for base, p in place.items():
        at = p["at_kappa_upper_0.133"]
        md.append(f"- base {base}: at kappa 0.133, P(equivalent) {f2(at['auroc_rule']['equivalent'])}, "
                  f"P(falsified) {f2(at['auroc_rule']['falsified'])} on the AUROC rule; kappa rule P(equivalent) "
                  f"{f2(at['kappa_rule']['equivalent'])}; P(detected) {f2(at['p_detected'])}.")
    md += ["", "## Middle cohort simulation (Older-clean plus 60 resampled drugs, 188 drugs, tier A)", "",
           "| base | quantity | Older-clean | middle realisations | middle mean |", "| --- | --- | --- | --- | --- |"]
    for base, m in mid.items():
        for q, v in m.items():
            reals = ", ".join(f3(x) for x in v["middle_realisations"])
            md.append(f"| {base} | {q} | {f3(v['older_clean'])} | {reals} | {f3(v.get('middle_mean'))} |")
    for name, j in jobs.items():
        for tier, t in j["tiers"].items():
            md += ["", f"## {name}, tier {tier}", "",
                   f"n = {t['n']}, {t['n_drugs']} drugs, {t['n_partners']} partners, DrugBank within-drug AUROC {f3(t['drugbank_within'])}. "
                   f"Unreachable targets: {j['unreachable'] or 'none'}; targets set to an endpoint within 3 Monte Carlo SE: "
                   f"{j['calibration']['clamped'] or 'none'}.", ""]
            md += grid_table(t["grid"])
    (sc.OUT / "spikein.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:80]))


if __name__ == "__main__":
    main()
