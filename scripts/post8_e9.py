import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np

import post8_common as pc
from ddiood import amend7_analysis as aa
from ddiood import amend7_panel as pn
from ddiood import evaluate2 as ev
from ddiood.metrics import binary_f1

E9 = pc.ROOT / "results" / "revision" / "amend7" / "e9.json"
BOUND = 0.60


def load_panel(preds, ytest):
    models = []
    for path in sorted(Path(preds).glob("a7-panel-*.json")):
        r = json.loads(path.read_text())
        if r["config"]["variant"] in ("masked", "external"):
            continue
        e = r["eval"]
        models.append({"name": r["config"]["name"], "semeval_binary_f1": float(binary_f1(ytest, e["test_sentence"]["preds"])),
                       "ood": np.asarray(e["ood_empty"]["p"], float), "oodold": np.asarray(e["oodold_empty"]["p"], float)})
    return models


def panel_draws(c, scores, n, seed):
    st = pn.pair_structure(c["y"], c["g"], c["q"])
    W = np.stack([pn.win_values(s, st) for s in scores])
    point = W.mean(1)
    rng = np.random.RandomState(seed)
    D = np.zeros((n, len(scores)))
    for b in range(n):
        w1 = np.bincount(rng.randint(0, st["k1"], st["k1"]), minlength=st["k1"])
        w2 = np.bincount(rng.randint(0, st["k2"], st["k2"]), minlength=st["k2"])
        w = w1[st["drug"]] * w2[st["qpos"]] * w2[st["qneg"]]
        D[b] = (W * w).sum(1) / max(w.sum(), 1e-12)
    return point, D, st


def cohort_block(truth, cname, models, db, n):
    c = truth.cohort(cname)
    key = "ood" if cname == "novel" else "oodold"
    scores = [m[key][c["mask"]] for m in models] + [db[key][c["mask"]]]
    point, D, st = panel_draws(c, scores, n, aa.BOOT_SEED[cname])
    A, Ad = point[:-1], D[:, :-1]
    dbp, dbd = point[-1], D[:, -1]
    names = [m["name"] for m in models]
    hi95 = np.percentile(Ad, 97.5, axis=0)
    lo95 = np.percentile(Ad, 2.5, axis=0)
    single = np.var(Ad, axis=0, ddof=1)
    pair_var = {f"{names[i]}|{names[j]}": float(np.var(Ad[:, i] - Ad[:, j], ddof=1)) for i, j in combinations(range(len(names)), 2)}
    paired_ref = float(np.mean(list(pair_var.values())) / 2)
    between = float(np.var(A, ddof=1))
    kd = (Ad - 0.5) / (dbd[:, None] - 0.5)
    kpt = (A - 0.5) / (dbp - 0.5)
    x = np.array([m["semeval_binary_f1"] for m in models])
    per = []
    for i, nm in enumerate(names):
        per.append({"name": nm, "semeval_binary_f1": float(x[i]), "auroc_within": float(A[i]), "lo95": float(lo95[i]),
                    "hi95": float(hi95[i]), "upper_at_most_0.60": bool(hi95[i] <= BOUND), "bootstrap_variance": float(single[i]),
                    "kappa": float(kpt[i]), "kappa_lo95": float(np.percentile(kd[:, i], 2.5)),
                    "kappa_hi95": float(np.percentile(kd[:, i], 97.5)),
                    "kappa_upper95_one_sided": float(np.percentile(kd[:, i], 95))})
    return {"n_rows": int(len(c["y"])), "n_pos": int(c["y"].sum()), "n_drugs": int(st["k1"]), "seed": aa.BOOT_SEED[cname],
            "drugbank_within": float(dbp), "drugbank_lo95": float(np.percentile(dbd, 2.5)), "drugbank_hi95": float(np.percentile(dbd, 97.5)),
            "per_checkpoint": per, "n_upper_at_most_0.60": int((hi95 <= BOUND).sum()), "n_models": len(names),
            "between_variance": between, "mean_single_bootstrap_variance": float(single.mean()),
            "ratio_old": between / float(single.mean()), "mean_paired_difference_variance": float(np.mean(list(pair_var.values()))),
            "paired_within_reference": paired_ref, "ratio_paired": between / paired_ref if paired_ref else None,
            "mean_bootstrap_covariance": float(single.mean() - paired_ref),
            "pair_variance_range": [float(min(pair_var.values())), float(max(pair_var.values()))],
            "kappa_hi95_range": [float(np.min([p["kappa_hi95"] for p in per])), float(np.max([p["kappa_hi95"] for p in per]))],
            "kappa_upper95_one_sided_range": [float(np.min([p["kappa_upper95_one_sided"] for p in per])),
                                              float(np.max([p["kappa_upper95_one_sided"] for p in per]))],
            "kappa_point_range": [float(kpt.min()), float(kpt.max())],
            "rho_semeval_f1_vs_auroc": pn.spearman(x, A)}


def check(block, cname):
    ref = json.loads(E9.read_text())["e9"]["panel"][cname]
    hi = [p["hi95"] for p in block["per_checkpoint"]]
    if [p["name"] for p in block["per_checkpoint"]] != ref["names"] or np.max(np.abs(np.array(hi) - np.array(ref["hi95"]))) > 1e-12:
        raise ValueError(f"E9 {cname}: tier A does not reproduce e9.json")
    if abs(block["mean_single_bootstrap_variance"] - ref["mean_within_bootstrap_variance"]) > 1e-12:
        raise ValueError(f"E9 {cname}: within variance does not reproduce e9.json")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    crit, rows, rule, screens = pc.screens_for_run()
    base, _, (db_ood, db_old) = pc.a7_truth()
    ytest = ev.load_truth().test_y
    models = load_panel(pc.PREDS, ytest)
    db = {"ood": aa.drugbank_scores(rows["novel"], db_ood), "oodold": aa.drugbank_scores(rows["older"], db_old)}
    tiers = {"A": base, "C-auto": pc.TruthC(base, pc.keep_masks(screens))}
    out = {"status": pc.STATUS, "boot": a.boot, "bound": BOUND, "tiers": {}, "checks": {}}
    for t, tr in tiers.items():
        out["tiers"][t] = {c: cohort_block(tr, c, models, db, a.boot) for c in ("older_primary", "novel")}
    for c in ("older_primary", "novel"):
        out["checks"][f"{c}_tier_A_reproduces_e9_json"] = check(out["tiers"]["A"][c], c)
    L = ["# E9 additions and tier C-auto (post hoc, exploratory)", "", f"Status: {pc.STATUS}.", "",
         "SemEval binary F1 is ddiood.metrics.binary_f1 of test_sentence predictions against label_id != 0. "
         "Within-drug AUROC, 95% intervals and kappa use the shared two-way draws of ddiood.amend7_panel.panel_stats (Older-primary seed 42, Novel seed 1042). "
         "kappa = (AUROC - 0.5) / (DrugBank within-drug AUROC - 0.5) on the same draw.", ""]
    for c in ("older_primary", "novel"):
        A, C = out["tiers"]["A"][c], out["tiers"]["C-auto"][c]
        L += [f"## {c}", "",
              f"DrugBank within-drug: tier A {pc.f3(A['drugbank_within'])} {pc.ci(A['drugbank_lo95'], A['drugbank_hi95'])}; C-auto {pc.f3(C['drugbank_within'])} {pc.ci(C['drugbank_lo95'], C['drugbank_hi95'])}.", "",
              "| checkpoint | SemEval binary F1 | AUROC A | 95% CI A | AUROC C-auto | 95% CI C-auto | kappa A | kappa 95% CI A | kappa C-auto | kappa 95% CI C-auto |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for pa, pcc in zip(A["per_checkpoint"], C["per_checkpoint"]):
            L.append(f"| {pa['name'].replace('a7-panel-', '')} | {pc.f3(pa['semeval_binary_f1'])} | {pc.f3(pa['auroc_within'])} | {pc.ci(pa['lo95'], pa['hi95'])} | "
                     f"{pc.f3(pcc['auroc_within'])} | {pc.ci(pcc['lo95'], pcc['hi95'])} | {pc.f3(pa['kappa'])} | {pc.ci(pa['kappa_lo95'], pa['kappa_hi95'])} | "
                     f"{pc.f3(pcc['kappa'])} | {pc.ci(pcc['kappa_lo95'], pcc['kappa_hi95'])} |")
        L += ["", "| statistic | tier A | C-auto |", "| --- | --- | --- |"]
        for k in ("n_rows", "n_pos", "n_upper_at_most_0.60", "between_variance", "mean_single_bootstrap_variance", "ratio_old",
                  "mean_paired_difference_variance", "paired_within_reference", "ratio_paired", "mean_bootstrap_covariance",
                  "rho_semeval_f1_vs_auroc"):
            fa = A[k] if isinstance(A[k], int) else f"{A[k]:.6g}"
            fc = C[k] if isinstance(C[k], int) else f"{C[k]:.6g}"
            L.append(f"| {k} | {fa} | {fc} |")
        L.append(f"| kappa 95% upper bound range (97.5th percentile) | {pc.ci(A['kappa_hi95_range'])} | {pc.ci(C['kappa_hi95_range'])} |")
        L.append(f"| kappa one-sided 95% upper bound range (95th percentile) | {pc.ci(A['kappa_upper95_one_sided_range'])} | {pc.ci(C['kappa_upper95_one_sided_range'])} |")
        L.append(f"| kappa point range | {pc.ci(A['kappa_point_range'])} | {pc.ci(C['kappa_point_range'])} |")
        L.append("")
    L.append("paired_within_reference = mean over checkpoint pairs of Var_b(A_i - A_j) / 2; ratio_paired = between-checkpoint variance / that reference. ratio_old is the Amendment 7 ratio against the mean single-checkpoint bootstrap variance.")
    pc.write("e9", out, "\n".join(L) + "\n")
    for t in out["tiers"]:
        for c, b in out["tiers"][t].items():
            print(t, c, b["n_upper_at_most_0.60"], round(b["ratio_old"], 4), round(b["ratio_paired"], 4), [round(v, 3) for v in b["kappa_hi95_range"]], [round(v, 3) for v in b["kappa_upper95_one_sided_range"]])


if __name__ == "__main__":
    main()
