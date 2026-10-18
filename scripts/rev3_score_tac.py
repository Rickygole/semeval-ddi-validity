import argparse
from pathlib import Path

import numpy as np

import rev3_common as rc
from rev2_score_adjudicator import cp

BOOT_DRAWS = 2000
RG_DRAWS = 10000
SEED = 42
TREATMENTS = ("unsure_not_yes", "unsure_excluded", "unsure_as_yes")
YOUDEN_NOTE = 0.3


def decision_flags(item, treatment):
    answered = not item["non_answer"]
    d = item["decision"]
    if treatment == "unsure_not_yes":
        return True, bool(answered and d == "yes")
    if treatment == "unsure_excluded":
        return bool(answered and d in ("yes", "no")), bool(answered and d == "yes")
    return True, bool(answered and d in ("yes", "unsure"))


def tabulate(items, treatment):
    rows = []
    for it in items:
        valid, yes = decision_flags(it, treatment)
        if valid:
            rows.append((it["set"] + "|" + it["ood_drug"], it["gold"], int(yes)))
    return rows


def counts(rows):
    tp = sum(1 for _, g, y in rows if g == 1 and y == 1)
    fn = sum(1 for _, g, y in rows if g == 1 and y == 0)
    tn = sum(1 for _, g, y in rows if g == 0 and y == 0)
    fp = sum(1 for _, g, y in rows if g == 0 and y == 1)
    return tp, fn, tn, fp


def cluster_draws(rows, n, seed):
    clusters = sorted({c for c, _, _ in rows})
    idx = {c: i for i, c in enumerate(clusters)}
    k = len(clusters)
    mat = np.zeros((k, 4))
    for c, g, y in rows:
        mat[idx[c], (0 if y else 1) if g == 1 else (3 if y else 2)] += 1
    rng = np.random.RandomState(seed)
    se, sp = [], []
    for _ in range(n):
        w = np.bincount(rng.randint(0, k, k), minlength=k)
        tp, fn, tn, fp = w @ mat
        se.append(tp / (tp + fn) if tp + fn else np.nan)
        sp.append(tn / (tn + fp) if tn + fp else np.nan)
    return np.array(se), np.array(sp)


def se_sp(items, treatment, seed=SEED):
    rows = tabulate(items, treatment)
    tp, fn, tn, fp = counts(rows)
    se_n, sp_n = tp + fn, tn + fp
    se, sp = (tp / se_n if se_n else None), (tn / sp_n if sp_n else None)
    dse, dsp = cluster_draws(rows, BOOT_DRAWS, seed) if rows else (np.array([]), np.array([]))
    return {"n_items": len(rows), "n_labels": len({c for c, _, _ in rows}), "tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "sensitivity": se, "sensitivity_cp95": cp(tp, se_n) if se_n else None, "sensitivity_label_cluster95": rc.pct(dse),
            "specificity": sp, "specificity_cp95": cp(tn, sp_n) if sp_n else None, "specificity_label_cluster95": rc.pct(dsp),
            "youden": None if se is None or sp is None else se + sp - 1}, (dse, dsp)


def subset(items, sets=None, ptype=None):
    return [i for i in items if (sets is None or i["set"] in sets) and (ptype is None or i["partner_type"] == ptype)]


def length_terciles(items):
    best = {}
    for i in items:
        key = i["set"] + "|" + i["ood_drug"]
        best[key] = max(best.get(key, 0), i["tokens"])
    vals = sorted(best.values())
    lo, hi = vals[len(vals) // 3], vals[2 * len(vals) // 3]
    return {k: (0 if v <= lo else (1 if v <= hi else 2)) for k, v in best.items()}, [lo, hi]


def calibration(items):
    out = {}
    primary = subset(items, ("test1", "test2"))
    strata = {"primary_substance_test1_test2": subset(primary, None, "substance"), "class_test1_test2": subset(primary, None, "class"),
              "all_partners_test1_test2": primary}
    for s in ("test1", "test2"):
        for p in ("substance", "class"):
            strata[f"{s}_{p}"] = subset(items, (s,), p)
        strata[f"{s}_all_partners"] = subset(items, (s,))
    for p in ("substance", "class"):
        strata[f"train22_{p}"] = subset(items, ("train22",), p)
    strata["train22_all_partners"] = subset(items, ("train22",))
    terc, edges = length_terciles(primary)
    for p in ("substance", "class"):
        for t in range(3):
            strata[f"{p}_length_tercile_{t + 1}"] = [i for i in subset(primary, None, p) if terc[i["set"] + "|" + i["ood_drug"]] == t]
    draws = {}
    for name, its in strata.items():
        out[name] = {}
        for tr in TREATMENTS:
            if not its:
                out[name][tr] = None
                continue
            res, d = se_sp(its, tr)
            out[name][tr] = res
            draws[(name, tr)] = d
    counts_ = {"items": len(items), "non_answers": int(sum(i["non_answer"] for i in items)), "unsure": int(sum(i["decision"] == "unsure" for i in items)),
               "chunked_items": int(sum(i["n_chunks"] > 1 for i in items)),
               "decisions": {d: int(sum(i["decision"] == d for i in items)) for d in ("yes", "no", "unsure")}}
    return out, draws, counts_, edges


def rogan_gladen(items, cal_draws, cal, treatment, stratum, seed=SEED):
    se, sp = cal[stratum][treatment]["sensitivity"], cal[stratum][treatment]["specificity"]
    dse, dsp = cal_draws[(stratum, treatment)]
    ok = ~(np.isnan(dse) | np.isnan(dsp))
    dse, dsp = dse[ok], dsp[ok]
    youden = se + sp - 1
    rows = []
    rng = np.random.RandomState(seed)
    for cohort in ("older", "novel"):
        for lab in (1, 0):
            sub = [i for i in items if i["set"] == "random" and i["cohort"] == cohort and int(i["current_label"]) == lab]
            valid = [(i, decision_flags(i, treatment)) for i in sub]
            valid = [(i, f[1]) for i, f in valid if f[0]]
            n, k = len(valid), sum(y for _, y in valid)
            if not n:
                continue
            q = k / n
            raw = (q + sp - 1) / youden if youden > 0 else None
            t = None if raw is None else min(1.0, max(0.0, raw))
            err = lambda x: (1 - x) if lab == 1 else x
            qs = rng.binomial(n, q, RG_DRAWS) / n
            j = rng.randint(0, len(dse), RG_DRAWS)
            yj = dse[j] + dsp[j] - 1
            with np.errstate(all="ignore"):
                tt = np.where(yj > 0, (qs + dsp[j] - 1) / yj, np.nan)
            tt = np.clip(tt, 0, 1)
            e = err(tt)
            rows.append({"cohort": cohort, "label_class": lab, "n": n, "yes": k, "observed_yes_rate": q, "observed_yes_cp95": cp(k, n),
                         "uncorrected_error_rate": (1 - q) if lab == 1 else q, "uncorrected_error_cp95": ([1 - cp(k, n)[1], 1 - cp(k, n)[0]] if lab == 1 else cp(k, n)),
                         "corrected_true_share_unclipped": raw, "corrected_error_rate_unclipped": None if raw is None else err(raw),
                         "corrected_error_rate": None if t is None else err(t), "corrected_error_ci95": rc.pct(e), "mc_draws_used": int(np.sum(~np.isnan(e))),
                         "youden": youden, "unstable_youden_below_0.3": bool(youden < YOUDEN_NOTE)})
    pooled = []
    for lab in (1, 0):
        sub = [i for i in items if i["set"] == "random" and int(i["current_label"]) == lab]
        valid = [(i, decision_flags(i, treatment)) for i in sub]
        valid = [(i, f[1]) for i, f in valid if f[0]]
        n, k = len(valid), sum(y for _, y in valid)
        if n:
            q = k / n
            raw = (q + sp - 1) / youden if youden > 0 else None
            pooled.append({"label_class": lab, "n": n, "yes": k, "observed_yes_rate": q,
                           "corrected_error_rate_unclipped": None if raw is None else ((1 - raw) if lab == 1 else raw),
                           "note": "errors_unweighted_pool_by_class: an unweighted pool of the two cohort samples, not a population rate"})
    return {"calibration_stratum": stratum, "treatment": treatment, "sensitivity": se, "specificity": sp, "youden": youden,
            "rows": rows, "pooled": pooled}


def md(res):
    L = ["# C4: TAC 2018 calibration of the R2b adjudicator", "", f"Status: {rc.STATUS}.", "",
         f"Items: {res['counts']['items']}; decisions {res['counts']['decisions']}; non-answers {res['counts']['non_answers']}; chunked items {res['counts']['chunked_items']}.",
         f"TAC items sha256 {res['tac_items_sha256']}. Model revision {res['model_revision']}. Length tercile edges (prompt tokens of a label): {res['length_edges']}.", "",
         "Sensitivity is P(yes | gold positive), specificity is P(not yes | gold negative). Treatments: unsure_not_yes (primary), unsure_excluded, unsure_as_yes (non-answers count as not yes). "
         "Gold negatives mean that the provided text of that label does not name the partner; a label can omit a real interaction.", ""]
    rows = []
    for name, d in res["calibration"].items():
        for tr in TREATMENTS:
            r = d[tr]
            if r is None:
                continue
            rows.append([name, tr, r["n_items"], r["n_labels"], f"{r['tp']}/{r['tp'] + r['fn']}", rc.f3(r["sensitivity"]), rc.ci(r["sensitivity_cp95"]), rc.ci(r["sensitivity_label_cluster95"]),
                         f"{r['tn']}/{r['tn'] + r['fp']}", rc.f3(r["specificity"]), rc.ci(r["specificity_cp95"]), rc.ci(r["specificity_label_cluster95"]), rc.f3(r["youden"])])
    L += rc.table(["stratum", "treatment", "items", "labels", "tp/pos", "sensitivity", "CP 95%", "label-cluster 95%", "tn/neg", "specificity", "CP 95%", "label-cluster 95%", "Youden"], rows) + [""]
    if res.get("rogan_gladen"):
        L += ["## Rogan-Gladen corrected error rates of the R2b random sample", ""]
        for rg in res["rogan_gladen"]:
            L += [f"Calibration {rg['calibration_stratum']}, treatment {rg['treatment']}: sensitivity {rc.f3(rg['sensitivity'])}, specificity {rc.f3(rg['specificity'])}, Youden {rc.f3(rg['youden'])}.", ""]
            rows = [[r["cohort"], r["label_class"], r["n"], r["yes"], rc.f3(r["observed_yes_rate"]), rc.f3(r["uncorrected_error_rate"]), rc.ci(r["uncorrected_error_cp95"]),
                     rc.f3(r["corrected_error_rate_unclipped"]), rc.f3(r["corrected_error_rate"]), rc.ci(r["corrected_error_ci95"]), "unstable" if r["unstable_youden_below_0.3"] else ""] for r in rg["rows"]]
            L += rc.table(["cohort", "label class", "n", "yes", "observed yes rate", "uncorrected error", "CP 95%", "corrected unclipped", "corrected", "95% interval", "note"], rows) + [""]
    else:
        L += ["R2b random-sample output not supplied; Rogan-Gladen correction pending.", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tac", required=True)
    ap.add_argument("--r2b")
    a = ap.parse_args()
    tac = rc.load(a.tac)
    items = tac["eval"]["items"]
    cal, draws, cnt, edges = calibration(items)
    res = {"counts": cnt, "tac_items_sha256": tac["tac_items_sha256"], "model_revision": tac["model"]["revision"], "length_edges": edges, "calibration": cal,
           "boot_draws": BOOT_DRAWS, "rg_draws": RG_DRAWS, "seed": SEED}
    if a.r2b and not Path(a.r2b).exists():
        raise SystemExit(f"--r2b file not found: {a.r2b}")
    if a.r2b:
        r2b = rc.load(a.r2b)["eval"]["items"]
        res["rogan_gladen"] = [rogan_gladen(r2b, draws, cal, tr, st) for st in ("primary_substance_test1_test2", "all_partners_test1_test2") for tr in TREATMENTS]
        res["r2b_file"] = Path(a.r2b).name
    rc.write("c4_calibration", res, md(res))
    print(rc.OUT / "c4_calibration.md")


if __name__ == "__main__":
    main()
