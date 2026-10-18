import argparse

import numpy as np
from scipy.stats import spearmanr

import rev3_common as rc
import rev3_c3 as c3
import post8_common as pc
import post8_e9 as p8
from ddiood import amend7_analysis as aa
from ddiood import amend7_panel as pn
from ddiood import evaluate2 as ev

C3 = rc.OUT / "c3_statistics.json"
TAUS = ("tau_0", "tau_observed_between_sd")


def simulate(z, A, D, sims, seed=c3.POWER_SEED):
    cov = np.cov(D.T)
    tau_obs = float(np.std(A, ddof=1))
    rho = float(spearmanr(z, A).statistic)
    entry = {}
    for tlabel, tau in (("tau_0", 0.0), ("tau_observed_between_sd", tau_obs)):
        curve = c3.power_curve(z, float(A.mean()), cov, tau, sims, seed)
        entry[tlabel] = {"tau": tau, "curve": curve, "summary": c3.power_summary(curve, rho)}
    entry["mean_sampling_sd"] = float(np.sqrt(np.mean(np.diag(cov))))
    entry["f1_sd"] = float(z.std(ddof=1))
    entry["observed_rho"] = rho
    return entry


def reproduction(two_way, stored):
    out = {}
    for t in TAUS:
        diffs = [abs(x["power"] - y["power"]) for x, y in zip(two_way[t]["curve"], stored[t]["curve"])]
        sa, sb = two_way[t]["summary"], stored[t]["summary"]
        out[t] = {"curve_matches": bool(max(diffs) < 5e-7), "max_abs_power_difference": float(max(diffs)),
                  "smallest_beta_matches": bool(sa["smallest_beta_power_at_least_0.80"] == sb["smallest_beta_power_at_least_0.80"]),
                  "stored_smallest_beta": sb["smallest_beta_power_at_least_0.80"], "stored_max_grid_power": sb["max_grid_power"]}
    return out


def md(res):
    L = ["# D2: panel power under the one-way drug bootstrap", "", f"Status: {rc.STATUS}.", "",
         "Tier A. The one-way bootstrap resamples anchor drugs only, so the panel is treated as scoring the same partners every time. The two-way rows are recomputed with the same "
         "code and are a reproduction of C3(d), not a new result. beta is AUROC per standard deviation of SemEval F1; tau is extra between-model SD.", ""]
    rows = []
    for tag, strata in res["power"].items():
        for s, v in strata.items():
            for sch in ("one_way", "two_way"):
                e = v[sch]
                for tl in TAUS:
                    sm = e[tl]["summary"]
                    rows.append([tag, s, sch, tl, f"{e['mean_sampling_sd']:.4f}", f"{e[tl]['tau']:.4f}", rc.f3(e["observed_rho"]),
                                 sm["smallest_beta_power_at_least_0.80"] if sm["reached_on_grid"] else "not reached", rc.f3(sm["expected_observed_rho_at_that_beta"]),
                                 rc.f3(sm["power_at_observed_abs_rho"]), rc.f3(sm["max_grid_power"]), rc.f3(sm["power_at_beta_0"])])
    L += rc.table(["tier/cohort", "stratum", "bootstrap", "setting", "mean sampling SD", "tau", "observed rho", "smallest beta, power >= 0.80", "expected rho there",
                   "power at observed |rho|", "max power on grid", "size at beta 0"], rows) + [""]
    L += [f"Two-way power curves reproduce c3_statistics.json to 6 decimals: {res['two_way_reproduces_c3']}.", ""]
    rows = [[tag, s, t, v["curve_matches"], f"{v['max_abs_power_difference']:.6f}", v["smallest_beta_matches"]]
            for tag, st in res["two_way_reproduction"].items() for s, byt in st.items() for t, v in byt.items()]
    L += rc.table(["tier/cohort", "stratum", "setting", "curve matches", "max abs power difference", "smallest beta matches"], rows) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--sims", type=int, default=c3.POWER_SIMS)
    a = ap.parse_args()
    crit, rows, rule, screens = pc.screens_for_run()
    base, _, _ = pc.a7_truth()
    ytest = ev.load_truth().test_y
    models = p8.load_panel(pc.PREDS, ytest)
    names = [m["name"] for m in models]
    f1 = np.array([m["semeval_binary_f1"] for m in models])
    strata = {"all": list(range(len(names))), "marker": [i for i, n in enumerate(names) if n.endswith("-marker")],
              "pair": [i for i, n in enumerate(names) if n.endswith("-pair")]}
    stored = rc.load(C3)["d"]
    power, repro = {}, {}
    for cname in ("older_primary", "novel"):
        key = "ood" if cname == "novel" else "oodold"
        c = base.cohort(cname)
        st = pn.pair_structure(c["y"], c["g"], c["q"])
        W = np.stack([pn.win_values(m[key][c["mask"]], st) for m in models])
        A = W.mean(1)
        seed = aa.BOOT_SEED[cname]
        D1 = c3.draws_matrix(W, st, a.boot, seed, True)
        D2 = c3.draws_matrix(W, st, a.boot, seed, False)
        tag = f"A/{cname}"
        power[tag], repro[tag] = {}, {}
        for sname, idx in strata.items():
            idx = np.array(idx)
            one = simulate(f1[idx], A[idx], D1[:, idx], a.sims)
            two = simulate(f1[idx], A[idx], D2[:, idx], a.sims)
            power[tag][sname] = {"one_way": one, "two_way": two}
            repro[tag][sname] = reproduction(two, stored[tag][sname])
    ok = bool(all(v["curve_matches"] for t in repro.values() for s in t.values() for v in s.values()))
    res = {"power": power, "two_way_reproduction": repro, "two_way_reproduces_c3": ok, "boot": a.boot, "power_sims": a.sims,
           "power_grid": c3.BETAS, "power_seed": c3.POWER_SEED}
    rc.write("d2_power_oneway", res, md(res))
    print(rc.OUT / "d2_power_oneway.md")


if __name__ == "__main__":
    main()
