import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import spikein_core as sc
from amend7_cpu_common import BOOT_SEED, cohort_arrays, drugbank_score, fast_within_auroc, paired_draws
from ddiood import evaluate2 as ev

ROOT = sc.ROOT
OUT = ROOT / "results" / "revision" / "gate8"
CRITERIA = OUT / "criteria.json"
SCREEN = ROOT / "results" / "revision" / "post8" / "screen.json"
VARIANTS = ("as_is", "validated_rule", "validated_rule_plus_db")
GOVERNING = "validated_rule"
OPTIMISTIC = "validated_rule_plus_db"
DESIGNS = ("novel48", "novel60", "older_clean60")
SCREEN_COHORT = {"novel": "novel", "older_clean": "older"}
CONTROL_KAPPA = 0.6
CONTROL_BAR = 0.25
POWER_BAR = 0.80


def load_criteria():
    if not CRITERIA.exists():
        raise SystemExit("results/revision/gate8/criteria.json must be written before this analysis runs")
    return json.loads(CRITERIA.read_text())


def flag_vector(screen, cohort, n_rows):
    v = np.zeros(n_rows, bool)
    for it in screen["flagged_items"]:
        if it["cohort"] == cohort and int(it["flag"]) == 1:
            v[int(it["row_index"])] = True
    return v


def cohort_data(truth, screen):
    out = {}
    for c in ("novel", "older_clean"):
        a = cohort_arrays(truth, c, "A")
        n_full = len(truth.sets[a["tag"]]["y"])
        flag = flag_vector(screen, SCREEN_COHORT[c], n_full)
        y_full = np.asarray(truth.sets[a["tag"]]["y"])
        if (y_full[flag] != 1).any():
            raise ValueError("a post8 flag points at a row that is not a positive")
        db = drugbank_score(truth, a["tag"])[a["mask"]]
        out[c] = {"y": np.asarray(a["y"], int), "g": np.asarray(a["g"]).astype(str), "q": np.asarray(a["q"]).astype(str),
                  "db": db, "flag": flag[a["mask"]], "seed": BOOT_SEED[c]}
    return out


def variant_mask(d, variant):
    m = np.ones(len(d["y"]), bool)
    if variant in ("validated_rule", "validated_rule_plus_db"):
        m &= ~d["flag"]
    if variant == "validated_rule_plus_db":
        m &= ~((d["y"] == 0) & (d["db"] == 1))
    return m


def subset(d, m):
    return {k: (v[m] if isinstance(v, np.ndarray) else v) for k, v in d.items()}


def pick_drugs(d, design, seed):
    drugs = np.unique(d["g"])
    rng = np.random.RandomState(seed)
    if design == "novel60":
        return list(drugs) + list(rng.choice(drugs, 60 - len(drugs), replace=False))
    if design == "older_clean60":
        return list(rng.choice(drugs, 60, replace=False))
    return list(drugs)


def assemble(d, picked):
    parts = {k: [] for k in ("y", "g", "q", "db", "flag")}
    for j, drug in enumerate(picked):
        m = d["g"] == drug
        for k in ("y", "q", "db", "flag"):
            parts[k].append(d[k][m])
        parts["g"].append(np.array([f"d{j}:{drug}"] * int(m.sum())))
    out = {k: np.concatenate(v) for k, v in parts.items()}
    out["seed"] = d["seed"]
    return out


def design_jobs(data, crit):
    sim = crit["simulation"]
    jobs = []
    plan = [("novel48", "novel", [0]), ("novel60", "novel", [1, 2, 3]), ("older_clean60", "older_clean", [1, 2, 3])]
    for di, (design, cohort, reals) in enumerate(plan):
        for real in reals:
            picked = pick_drugs(data[cohort], design, real)
            base = assemble(data[cohort], picked)
            for vi, variant in enumerate(VARIANTS):
                d = subset(base, variant_mask(base, variant))
                jobs.append({"design": design, "cohort": cohort, "realisation": real, "variant": variant,
                             "cohort_id": 1000 + 100 * di + 10 * real + vi, "data": d, "picked": [str(x) for x in picked],
                             "reps": sim["reps_per_point"], "boot": sim["bootstrap_draws_per_rep"],
                             "n_cal": sim["calibration_draws"], "K": crit["K_values"]})
    return jobs


def kappa_bounds(two, ddb):
    k = (two - 0.5) / (ddb[None, :] - 0.5)
    return {"up95_one_sided": np.percentile(k, 95, axis=1), "lo95_two_sided": np.percentile(k, 2.5, axis=1),
            "lo95_one_sided": np.percentile(k, 5, axis=1)}


def run_job(spec):
    t0 = time.time()
    d, reps, n_boot = spec["data"], spec["reps"], spec["boot"]
    y, g, q, db = d["y"], d["g"], d["q"], d["db"]
    cal = sc.calibrate(y, g, db, None, "noise", spec["cohort_id"], [0.0, CONTROL_KAPPA], spec["n_cal"])
    w_ctrl = cal["w"][1]
    blocks = [sc.make_scores(db, None, "noise", spec["cohort_id"], 0, 0.0, reps)]
    if w_ctrl is not None:
        blocks.append(sc.make_scores(db, None, "noise", spec["cohort_id"], 1, w_ctrl, reps))
    s = np.vstack(blocks)
    dr = sc.draws(y, np.vstack([s, db[None, :]]), g, q, n_boot, d["seed"])
    two, ddb = dr[:-1], dr[-1]
    b = kappa_bounds(two, ddb)
    est = sc.point_within(y, s, g)
    a_db = float(fast_within_auroc(y, db, g))
    kest = (est - 0.5) / (a_db - 0.5)
    null = slice(0, reps)
    res = {k: spec[k] for k in ("design", "cohort", "realisation", "variant", "cohort_id", "picked")}
    res.update({"n_rows": int(len(y)), "n_pos": int(y.sum()), "n_neg": int((1 - y).sum()), "n_drugs": int(len(set(g))),
                "n_drugs_informative": int(sum(1 for x in set(g) if 0 < y[g == x].sum() < (g == x).sum())),
                "n_partners": int(len(set(q))), "drugbank_within": a_db, "n_draws": int(two.shape[1]),
                "drugbank_draws_at_or_below_half": float(np.mean(ddb <= 0.5)),
                "drugbank_draw_ci95": [float(np.percentile(ddb, 2.5)), float(np.percentile(ddb, 97.5))],
                "w_control": w_ctrl, "calibration_curve_w0": cal["curve"][0], "calibration_curve_w1": cal["curve"][-1]})
    up = b["up95_one_sided"][null]
    res["null"] = {"reps": reps, "realised_kappa_mean": float(kest[null].mean()), "realised_kappa_sd": float(kest[null].std(ddof=1)),
                   "up95_mean": float(up.mean()), "up95_median": float(np.median(up)),
                   "up95_values": up.tolist(),
                   "power_by_K": {str(K): float(np.mean(up <= K)) for K in spec["K"]}}
    if w_ctrl is not None:
        c = slice(reps, 2 * reps)
        lo, lo1 = b["lo95_two_sided"][c], b["lo95_one_sided"][c]
        res["control"] = {"reps": reps, "realised_kappa_mean": float(kest[c].mean()), "realised_kappa_sd": float(kest[c].std(ddof=1)),
                          "lo95_mean": float(lo.mean()), "lo95_median": float(np.median(lo)), "lo95_values": lo.tolist(),
                          "lo95_one_sided_values": lo1.tolist(),
                          "power": float(np.mean(lo >= CONTROL_BAR)), "power_one_sided": float(np.mean(lo1 >= CONTROL_BAR))}
    else:
        res["control"] = None
    res["seconds"] = time.time() - t0
    return res


def pooled(rows, K_values):
    null_up = np.concatenate([r["null"]["up95_values"] for r in rows])
    ctrl = [r["control"] for r in rows]
    out = {"realisations": [r["realisation"] for r in rows], "n_null_reps": int(len(null_up)),
           "null_power_by_K": {str(K): float(np.mean(null_up <= K)) for K in K_values},
           "null_power_by_K_per_realisation": {str(K): [r["null"]["power_by_K"][str(K)] for r in rows] for K in K_values},
           "null_up95_mean": float(null_up.mean()),
           "drugbank_within_per_realisation": [r["drugbank_within"] for r in rows],
           "n_drugs_informative_per_realisation": [r["n_drugs_informative"] for r in rows],
           "n_rows_per_realisation": [r["n_rows"] for r in rows]}
    if any(c is None for c in ctrl):
        out.update({"control_power": None, "control_power_one_sided": None, "control_reachable": False})
    else:
        lo = np.concatenate([c["lo95_values"] for c in ctrl])
        lo1 = np.concatenate([c["lo95_one_sided_values"] for c in ctrl])
        out.update({"control_reachable": True, "n_control_reps": int(len(lo)), "control_power": float(np.mean(lo >= CONTROL_BAR)),
                    "control_power_one_sided": float(np.mean(lo1 >= CONTROL_BAR)),
                    "control_power_per_realisation": [c["power"] for c in ctrl], "control_lo95_mean": float(lo.mean()),
                    "control_realised_kappa_mean": float(np.mean([c["realised_kappa_mean"] for c in ctrl]))})
    out["go_by_K"] = {}
    for K in K_values:
        a = out["null_power_by_K"][str(K)] >= POWER_BAR
        bb = out["control_power"] is not None and out["control_power"] >= POWER_BAR
        out["go_by_K"][str(K)] = {"a": bool(a), "b": bool(bb), "go": bool(a and bb)}
    return out


def verdict(table, K_values):
    out = {}
    for K in K_values:
        k = str(K)
        gov = [dz for dz in DESIGNS if table[dz][GOVERNING]["go_by_K"][k]["go"]]
        opt = [dz for dz in DESIGNS if table[dz][OPTIMISTIC]["go_by_K"][k]["go"]]
        asis = [dz for dz in DESIGNS if table[dz]["as_is"]["go_by_K"][k]["go"]]
        out[k] = {"verdict": "GO" if gov else "NO-GO", "governing_designs_passing": gov,
                  "optimistic_upper_bound_designs_passing": opt, "as_is_designs_passing": asis,
                  "note": ("" if gov else ("passes only under the optimistic upper bound that uses DrugBank" if opt else
                                           "no design passes, not even the optimistic upper bound"))}
    return out


def ceilings(data, n_boot=1000):
    out = {}
    for c, d in data.items():
        out[c] = {}
        for v in VARIANTS:
            s = subset(d, variant_mask(d, v))
            dr = paired_draws(s["y"], [s["db"]], s["g"], s["q"], n_boot, d["seed"])[0]
            pt = float(fast_within_auroc(s["y"], s["db"], s["g"]))
            out[c][v] = {"n_rows": int(len(s["y"])), "n_pos": int(s["y"].sum()), "n_drugs": int(len(set(s["g"]))),
                         "drugbank_within": pt, "ci95": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))],
                         "n_draws": int(len(dr)), "at_least_0.80": bool(pt >= 0.80),
                         "optimistic_upper_bound": v == OPTIMISTIC}
    return out


def f3(v):
    return "NA" if v is None else f"{v:.3f}"


def markdown(res):
    K_values = res["criteria"]["K_values"]
    L = ["# Gate 8: can a validated-label Amendment 8 on about 60 drugs reach a decision?", "",
         "Status: synthetic power simulation, post hoc and exploratory; criteria.json was written before any run; changes no preregistered decision.", "",
         "Scores are synthetic. No model score of any tested system is used; the only real score is the DrugBank lookup, the kappa reference. "
         "Null scorer: noise (true kappa 0). Positive control: DrugBank blend on the noise base calibrated to true kappa 0.6. "
         f"{res['settings']['reps']} reps per point, {res['settings']['boot']} two-way bootstrap draws per rep.", "",
         "Rules: (a) H8 supported if the one-sided 95% upper bound of kappa is at most K, power at true kappa 0 at least 0.80; "
         "(b) control detected if the kappa 95% lower bound (2.5th percentile) is at least 0.25, power at true kappa 0.6 at least 0.80. GO needs both.", "",
         "## Verdict", "", "| K | verdict | governing designs passing (validated_rule) | optimistic bound passing | note |", "| --- | --- | --- | --- | --- |"]
    for K in K_values:
        v = res["verdict"][str(K)]
        L.append(f"| {K} | {v['verdict']} | {', '.join(v['governing_designs_passing']) or 'none'} | "
                 f"{', '.join(v['optimistic_upper_bound_designs_passing']) or 'none'} | {v['note']} |")
    L += ["", "## Power", "",
          "| design | labels | rows (per realisation) | informative drugs | DrugBank within | P(a) K=0.25 | P(a) K=0.33 | P(a) K=0.50 | mean null upper bound | P(b) | P(b) one-sided | mean control lower bound |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for dz in DESIGNS:
        for v in VARIANTS:
            t = res["power"][dz][v]
            lab = v + (" (OPTIMISTIC UPPER BOUND, uses DrugBank)" if v == OPTIMISTIC else "")
            pk = " | ".join(f3(t["null_power_by_K"][str(K)]) for K in K_values)
            L.append(f"| {dz} | {lab} | {', '.join(map(str, t['n_rows_per_realisation']))} | "
                     f"{', '.join(map(str, t['n_drugs_informative_per_realisation']))} | "
                     f"{', '.join(f3(x) for x in t['drugbank_within_per_realisation'])} | {pk} | {f3(t['null_up95_mean'])} | "
                     f"{f3(t['control_power'])} | {f3(t['control_power_one_sided'])} | {f3(t.get('control_lo95_mean'))} |")
    L += ["", "Powers pool the reps of all realisations (seeds 1, 2, 3 for the 60-drug designs); per-realisation values are in gate8.json.", "",
          "## DrugBank within-drug ceiling on the existing cohorts", "",
          "| cohort | labels | rows | positives | drugs | DrugBank within | 95% CI | at least 0.80 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c, rows in res["ceilings"].items():
        for v, r in rows.items():
            lab = v + (" (OPTIMISTIC UPPER BOUND, uses DrugBank)" if r["optimistic_upper_bound"] else "")
            L.append(f"| {c} | {lab} | {r['n_rows']} | {r['n_pos']} | {r['n_drugs']} | {f3(r['drugbank_within'])} | "
                     f"[{f3(r['ci95'][0])}, {f3(r['ci95'][1])}] | {'yes' if r['at_least_0.80'] else 'no'} |")
    L += ["", "A ceiling of at least 0.80 would mean the kappa denominator widens. On the optimistic variant the ceiling is raised by construction, "
          "because the negatives it drops are exactly those DrugBank scores as positive.", ""]
    return "\n".join(L)


def main():
    crit = load_criteria()
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--reps", type=int, default=crit["simulation"]["reps_per_point"])
    ap.add_argument("--boot", type=int, default=crit["simulation"]["bootstrap_draws_per_rep"])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    crit["simulation"]["reps_per_point"], crit["simulation"]["bootstrap_draws_per_rep"] = a.reps, a.boot
    screen = json.loads(SCREEN.read_text())
    truth = ev.load_truth()
    data = cohort_data(truth, screen)
    jobs = design_jobs(data, crit)
    with ProcessPoolExecutor(a.workers) as ex:
        results = list(ex.map(run_job, jobs))
    table = {dz: {v: pooled([r for r in results if r["design"] == dz and r["variant"] == v], crit["K_values"]) for v in VARIANTS}
             for dz in DESIGNS}
    out = {"status": crit["status"], "criteria": crit, "settings": {"reps": a.reps, "boot": a.boot},
           "verdict": verdict(table, crit["K_values"]), "power": table, "ceilings": ceilings(data),
           "jobs": [{k: v for k, v in r.items()} for r in results]}
    for r in out["jobs"]:
        r["null"] = {k: v for k, v in r["null"].items() if k != "up95_values"}
        if r["control"]:
            r["control"] = {k: v for k, v in r["control"].items() if not k.endswith("_values")}
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "gate8.json").write_text(json.dumps(ev.clean(out), indent=1) + "\n")
    (od / "gate8.md").write_text(markdown(out))
    print(json.dumps(out["verdict"], indent=1))


if __name__ == "__main__":
    main()
