import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import spikein_core as sc
from amend7_cpu_common import BOOT_SEED, cohort_arrays, drugbank_score, seed_mean
from ddiood import evaluate2 as ev

COHORT_ID = {"novel": 1, "older_clean": 2}
N_MIDDLE = 60


def cohort_data(truth):
    b2 = {"novel": seed_mean("b2mixed-biomedbert", "ood_empty")[0],
          "older_clean": seed_mean("b2mixed-biomedbert", "oodold_empty")[0]}
    out = {}
    for c in ("novel", "older_clean"):
        a = cohort_arrays(truth, c, "A")
        db = drugbank_score(truth, a["tag"])
        out[c] = {"y": np.asarray(a["y"], int), "g": np.asarray(a["g"]).astype(str), "q": np.asarray(a["q"]).astype(str),
                  "db": db[a["mask"]], "b2": b2[c][a["mask"]], "dbstate": a["dbstate"], "seed": BOOT_SEED[c],
                  "cohort_id": COHORT_ID[c]}
    return out


def middle(d, seed, n_new=N_MIDDLE):
    drugs = np.unique(d["g"])
    pick = np.random.RandomState(seed).choice(drugs, n_new, replace=True)
    parts = {k: [d[k]] for k in ("y", "g", "q", "db", "b2", "dbstate")}
    for j, drug in enumerate(pick):
        m = d["g"] == drug
        for k in ("y", "q", "db", "b2", "dbstate"):
            parts[k].append(d[k][m])
        parts["g"].append(np.array([f"mid{j}:{drug}"] * int(m.sum())))
    out = {k: np.concatenate(v) for k, v in parts.items()}
    out.update({"seed": 42, "cohort_id": 10 + seed, "picked": pick.tolist()})
    return out


def run_job(spec):
    t0 = time.time()
    d, base, grid, reps, n_boot, tiers = spec["data"], spec["base"], spec["grid"], spec["reps"], spec["boot"], spec["tiers"]
    base_scores = d["b2"] if base == "b2mixed" else None
    cal = sc.calibrate(d["y"], d["g"], d["db"], base_scores, base, d["cohort_id"], grid, spec["n_cal"])
    keep = [i for i, w in enumerate(cal["w"]) if w is not None]
    blocks = [sc.make_scores(d["db"], base_scores, base, d["cohort_id"], i, cal["w"][i], reps) for i in keep]
    s = np.vstack(blocks)
    res = {"name": spec["name"], "base": base, "calibration": {"a_db": cal["a_db"], "w": cal["w"],
                                                               "w_grid": sc.W_GRID.tolist(), "curve": cal["curve"],
                                                               "clamped": cal["clamped"], "endpoint_se": cal["endpoint_se"]},
           "unreachable": [grid[i] for i in range(len(grid)) if cal["w"][i] is None], "tiers": {}}
    for tier in tiers:
        m = np.ones(len(d["y"]), bool) if tier == "A" else d["dbstate"] == 1
        r = sc.evaluate_scores(d["y"][m], d["g"][m], d["q"][m], s[:, m], d["db"][m], d["seed"], n_boot)
        rows = []
        for j, i in enumerate(keep):
            sl = slice(j * reps, (j + 1) * reps)
            sub = {"est": r["est"][sl], "kappa_est": r["kappa_est"][sl], "n_draws": r["n_draws"], "n_draws_one": r["n_draws_one"],
                   "two": {k: v[sl] for k, v in r["two"].items()}, "one": {k: v[sl] for k, v in r["one"].items()},
                   "kappa": {k: v[sl] for k, v in r["kappa"].items()}}
            rows.append({"target_kappa": grid[i], "w": cal["w"][i], **sc.summarize(sub)})
        res["tiers"][tier] = {"n": int(m.sum()), "n_drugs": int(len(set(d["g"][m]))),
                              "n_partners": int(len(set(d["q"][m]))), "drugbank_within": r["a_db"], "grid": rows}
    res["seconds"] = time.time() - t0
    return res


def observed(d, n_boot):
    out = {}
    for tier in ("A", "B"):
        m = np.ones(len(d["y"]), bool) if tier == "A" else d["dbstate"] == 1
        r = sc.evaluate_scores(d["y"][m], d["g"][m], d["q"][m], d["b2"][None, m], d["db"][m], d["seed"], n_boot)
        out[tier] = {"auroc": float(r["est"][0]), "kappa": float(r["kappa_est"][0]), "drugbank_within": r["a_db"],
                     "ci90": [float(r["two"]["lo90"][0]), float(r["two"]["hi90"][0])],
                     "ci95": [float(r["two"]["lo95"][0]), float(r["two"]["hi95"][0])], "p_tost": float(r["two"]["p_tost"][0]),
                     "decision": str(r["two"]["decision"][0]), "decision_holm": str(r["two"]["holm"][0]),
                     "decision_one_way": str(r["one"]["decision"][0]),
                     "ci95_one_way": [float(r["one"]["lo95"][0]), float(r["one"]["hi95"][0])],
                     "kappa_ci95": [float(r["kappa"]["lo95"][0]), float(r["kappa"]["hi95"][0])],
                     "kappa_decision": str(r["kappa"]["decision"][0]), "n_draws": r["n_draws"]}
    return out


def specs(data, crit, reps, n_boot, n_cal, middle_reals):
    grid = crit["kappa_grid"]
    out = []
    for c in ("older_clean", "novel"):
        for base in ("b2mixed", "noise"):
            out.append({"name": f"{c}:{base}", "data": data[c], "base": base, "grid": grid, "reps": reps, "boot": n_boot,
                        "tiers": ("A", "B"), "n_cal": n_cal})
    for seed in middle_reals:
        md = middle(data["older_clean"], seed)
        for base in ("b2mixed", "noise"):
            out.append({"name": f"middle{seed}:{base}", "data": md, "base": base, "grid": grid, "reps": reps,
                        "boot": n_boot, "tiers": ("A",), "n_cal": n_cal, "picked": md["picked"]})
    return out


def main():
    crit = sc.load_criteria()
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=crit["reps_per_grid_point"])
    ap.add_argument("--boot", type=int, default=crit["bootstrap"]["draws_per_rep"])
    ap.add_argument("--cal", type=int, default=100)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--out", default=str(sc.OUT / "spikein_raw.json"))
    a = ap.parse_args()
    truth = ev.load_truth()
    data = cohort_data(truth)
    reals = crit["middle_cohort_simulation"]["realisation_seeds"]
    jobs = specs(data, crit, a.reps, a.boot, a.cal, reals)
    obs = {c: {"draws_300": observed(data[c], a.boot), "draws_1000": observed(data[c], 1000)} for c in ("older_clean", "novel")}
    with ProcessPoolExecutor(a.workers) as ex:
        results = list(ex.map(run_job, jobs))
    for j, r in zip(jobs, results):
        if "picked" in j:
            r["picked"] = j["picked"]
    out = {"criteria": crit, "settings": {"reps": a.reps, "boot": a.boot, "calibration_draws": a.cal},
           "observed_b2mixed": obs, "jobs": results}
    with open(a.out, "w") as f:
        json.dump(ev.clean(out), f, indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
