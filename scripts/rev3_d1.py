import argparse

import numpy as np

import rev3_common as rc
import rev3_score_tac as st
from rev2_score_adjudicator import cp

TAC = rc.ROOT / "runs" / "preds" / "r3-olmo-tac-calibration.json"
R2B = rc.ROOT / "runs" / "preds" / "r2-olmo-adjudication.json"
C4 = rc.OUT / "c4_calibration.json"
POOLED_CAL = {"primary_substance_pooled": "primary_substance_test1_test2", "all_partners_pooled": "all_partners_test1_test2",
              "test1_substance": "test1_substance", "test2_substance": "test2_substance",
              "test1_all_partners": "test1_all_partners", "test2_all_partners": "test2_all_partners"}
TERCILE_STRATA = ("substance_length_tercile_1", "substance_length_tercile_2", "substance_length_tercile_3")
MIN_CAL_ITEMS = 20


def tercile_of(tokens, edges):
    lo, hi = edges
    return 0 if tokens <= lo else (1 if tokens <= hi else 2)


def length_matched(se_k, sp_k, shares):
    w = np.asarray(shares, float)
    return float(np.dot(w, se_k)), float(np.dot(w, sp_k))


def rg_value(q, se, sp):
    y = se + sp - 1
    return None if y <= 0 else (q + sp - 1) / y


def err_of(t, lab):
    return None if t is None else ((1 - t) if lab == 1 else t)


def cell_rows(items, treatment, cal, draws, edges, seed=st.SEED):
    k_cal = [cal[s][treatment] for s in TERCILE_STRATA]
    k_draws = []
    for s in TERCILE_STRATA:
        dse, dsp = draws[(s, treatment)]
        ok = ~(np.isnan(dse) | np.isnan(dsp))
        k_draws.append((dse[ok], dsp[ok]))
    rng = np.random.RandomState(seed)
    out = []
    cells = [(c, lab) for c in ("older", "novel") for lab in (1, 0)] + [(None, lab) for lab in (1, 0)]
    for cohort, lab in cells:
        sub = [i for i in items if i["set"] == "random" and int(i["current_label"]) == lab and (cohort is None or i["cohort"] == cohort)]
        valid = []
        for i in sub:
            ok, yes = st.decision_flags(i, treatment)
            if ok:
                valid.append((tercile_of(i["tokens"], edges), yes))
        n = len(valid)
        if not n:
            continue
        kcount = [sum(1 for t, _ in valid if t == k) for k in range(3)]
        w = [c / n for c in kcount]
        yes_n = sum(1 for _, y in valid if y)
        q = yes_n / n
        se_k = [r["sensitivity"] for r in k_cal]
        sp_k = [r["specificity"] for r in k_cal]
        if any(s is None for s in se_k + sp_k):
            raise ValueError("empty calibration class in a length tercile")
        se_w, sp_w = length_matched(se_k, sp_k, w)
        raw = rg_value(q, se_w, sp_w)
        qs = rng.binomial(n, q, st.RG_DRAWS) / n
        sew = np.zeros(st.RG_DRAWS)
        spw = np.zeros(st.RG_DRAWS)
        for k in range(3):
            dse, dsp = k_draws[k]
            j = rng.randint(0, len(dse), st.RG_DRAWS)
            sew += w[k] * dse[j]
            spw += w[k] * dsp[j]
        yj = sew + spw - 1
        with np.errstate(all="ignore"):
            tt = np.where(yj > 0, (qs + spw - 1) / yj, np.nan)
        dropped = int(np.sum(np.isnan(tt)))
        e = np.where(np.isnan(tt), np.nan, (1 - np.clip(tt, 0, 1)) if lab == 1 else np.clip(tt, 0, 1))
        clipped = None if raw is None else min(1.0, max(0.0, raw))
        out.append({"cohort": cohort or "pooled_unweighted", "label_class": lab, "n": n, "yes": yes_n, "observed_yes_rate": q,
                    "observed_yes_cp95": cp(yes_n, n), "tercile_counts": kcount, "tercile_shares": w,
                    "calibration_sensitivity": se_w, "calibration_specificity": sp_w, "youden": se_w + sp_w - 1,
                    "corrected_true_share_unclipped": raw, "corrected_error_rate_unclipped": err_of(raw, lab),
                    "corrected_error_rate": err_of(clipped, lab), "corrected_error_ci95": rc.pct(e), "mc_draws_dropped": dropped,
                    "unstable_youden_below_0.3": bool(se_w + sp_w - 1 < st.YOUDEN_NOTE)})
    return out, {"tercile_calibration": {s: {"sensitivity": r["sensitivity"], "specificity": r["specificity"], "n_items": r["n_items"],
                                             "n_positive": r["tp"] + r["fn"], "n_negative": r["tn"] + r["fp"],
                                             "small_class_below_20": bool(r["tp"] + r["fn"] < MIN_CAL_ITEMS or r["tn"] + r["fp"] < MIN_CAL_ITEMS)}
                                 for s, r in zip(TERCILE_STRATA, k_cal)}}


def transport(row, se, sp, youden):
    q = row["observed_yes_rate"]
    if row["label_class"] == 1:
        ref, d = se, q - se
        name = "calibration_sensitivity"
    else:
        ref, d = 1 - sp, q - (1 - sp)
        name = "calibration_false_yes_rate"
    return {name: ref, "observed_minus_reference": d, "observed_yes_cp95": row["observed_yes_cp95"]}


def standard_rows(items, draws, cal, treatment, stratum):
    rg = st.rogan_gladen(items, draws, cal, treatment, stratum)
    rows = []
    for r in rg["rows"]:
        rows.append({**r, "calibration_sensitivity": rg["sensitivity"], "calibration_specificity": rg["specificity"],
                     "transport": transport(r, rg["sensitivity"], rg["specificity"], rg["youden"])})
    for p in rg["pooled"]:
        se, sp = rg["sensitivity"], rg["specificity"]
        q = p["observed_yes_rate"]
        raw = rg_value(q, se, sp)
        p = {**p, "cohort": "pooled_unweighted", "calibration_sensitivity": se, "calibration_specificity": sp, "youden": rg["youden"],
             "corrected_error_rate": None if raw is None else err_of(min(1.0, max(0.0, raw)), p["label_class"]),
             "observed_yes_cp95": cp(p["yes"], p["n"])}
        p["transport"] = transport(p, se, sp, rg["youden"])
        rows.append(p)
    return rows


def analyze(tac_items, r2b_items, edges):
    cal, draws, _, tedges = st.calibration(tac_items)
    if [round(float(x), 6) for x in tedges] != [round(float(x), 6) for x in edges]:
        raise ValueError("TAC tercile edges differ from the stored C4 edges")
    result = {"length_edges": tedges, "edges_used": list(edges), "calibrations": {}}
    for treatment in st.TREATMENTS:
        for name, stratum in POOLED_CAL.items():
            rg = st.rogan_gladen(r2b_items, draws, cal, treatment, stratum)
            result["calibrations"].setdefault(name, {})[treatment] = {
                "stratum": stratum, "sensitivity": rg["sensitivity"], "specificity": rg["specificity"], "youden": rg["youden"],
                "rows": standard_rows(r2b_items, draws, cal, treatment, stratum)}
        rows, extra = cell_rows(r2b_items, treatment, cal, draws, edges)
        for r in rows:
            r["transport"] = transport(r, r["calibration_sensitivity"], r["calibration_specificity"], r["youden"])
        result["calibrations"].setdefault("length_matched_substance", {})[treatment] = {"stratum": "substance_length_tercile_1..3", "rows": rows, **extra}
    return result, cal, draws


def check_against_c4(result):
    stored = rc.load(C4)["rogan_gladen"]
    out = []
    for rg in stored:
        name = "primary_substance_pooled" if rg["calibration_stratum"] == "primary_substance_test1_test2" else "all_partners_pooled"
        mine = {(r["cohort"], r["label_class"]): r for r in result["calibrations"][name][rg["treatment"]]["rows"]}
        for r in rg["rows"]:
            m = mine[(r["cohort"], r["label_class"])]
            out.append({"calibration": name, "treatment": rg["treatment"], "cohort": r["cohort"], "label_class": r["label_class"],
                        "unclipped_matches": bool(abs(m["corrected_error_rate_unclipped"] - r["corrected_error_rate_unclipped"]) < 5e-7),
                        "interval_matches": bool(np.allclose(m["corrected_error_ci95"], r["corrected_error_ci95"], atol=5e-7))})
    return out


def md(res):
    L = ["# D1: R2c transport", "", f"Status: {rc.STATUS}.", "",
         f"TAC length tercile edges (prompt tokens): {res['length_edges']}. Edges used for R2b items: {res['edges_used']}. TAC terciles were assigned per label from the longest item of the label; "
         "R2b items are assigned from their own prompt token count (`tokens`), so the two assignments differ.", "",
         "Corrected error rate of a label-1 item is 1 minus the Rogan-Gladen true share, of a label-0 item the true share. Intervals: Monte Carlo, 10,000 draws, seed 42. "
         "Transport check: observed yes rate among label-1 items minus the calibration sensitivity (label-0: minus 1 minus specificity). A positive difference for label-1 items "
         "gives a negative unclipped corrected error rate and cannot be fit with a label-error rate of zero or more under that calibration. "
         "The transport assumption (Se and Sp measured on TAC label sections apply to OpenFDA sections) is not tested here, and no calibration is chosen.", ""]
    for treatment in st.TREATMENTS:
        L += [f"## Treatment {treatment}", ""]
        rows = []
        for name, byt in res["calibrations"].items():
            for r in byt[treatment]["rows"]:
                t = r["transport"]
                ref = t.get("calibration_sensitivity", t.get("calibration_false_yes_rate"))
                rows.append([name, r["cohort"], r["label_class"], r["n"], r["yes"], rc.f3(r["observed_yes_rate"]), rc.ci(r["observed_yes_cp95"]),
                             rc.f3(r["calibration_sensitivity"]), rc.f3(r["calibration_specificity"]), rc.f3(r["youden"]),
                             rc.f3(r["corrected_error_rate_unclipped"]), rc.f3(r["corrected_error_rate"]), rc.ci(r.get("corrected_error_ci95")),
                             rc.f3(ref), rc.f3(t["observed_minus_reference"]), "unstable" if r.get("unstable_youden_below_0.3") else ""])
        L += rc.table(["calibration", "cohort", "class", "n", "yes", "observed yes", "CP 95%", "Se", "Sp", "Youden", "corrected unclipped", "corrected clipped",
                       "95% interval", "reference rate", "observed minus reference", "note"], rows) + [""]
    lm = res["calibrations"]["length_matched_substance"]["unsure_not_yes"]
    L += ["## Length-matched calibration inputs (unsure counted as not yes)", ""]
    L += rc.table(["tercile stratum", "Se", "Sp", "TAC positives", "TAC negatives", "small class"],
                  [[s, rc.f3(v["sensitivity"]), rc.f3(v["specificity"]), v["n_positive"], v["n_negative"], v["small_class_below_20"]] for s, v in lm["tercile_calibration"].items()]) + [""]
    L += rc.table(["cohort", "class", "R2b items by tercile", "shares"], [[r["cohort"], r["label_class"], r["tercile_counts"], [round(x, 6) for x in r["tercile_shares"]]] for r in lm["rows"]]) + [""]
    L += ["## Reproduction of C4 values", "", f"All reproduced: {res['c4_reproduction_all_match']}.", ""]
    return "\n".join(L) + "\n"


def main():
    argparse.ArgumentParser().parse_args()
    tac = rc.load(TAC)
    r2b = rc.load(R2B)["eval"]["items"]
    missing = [i["item_id"] for i in r2b if i["set"] == "random" and i.get("tokens") is None]
    if missing:
        raise SystemExit(f"random-sample items without tokens: {missing[:5]}")
    res, _, _ = analyze(tac["eval"]["items"], r2b, rc.load(C4)["length_edges"])
    chk = check_against_c4(res)
    res["c4_reproduction"] = chk
    res["c4_reproduction_all_match"] = bool(all(c["unclipped_matches"] and c["interval_matches"] for c in chk))
    res["rg_draws"] = st.RG_DRAWS
    res["seed"] = st.SEED
    rc.write("d1_transport", res, md(res))
    print(rc.OUT / "d1_transport.md")


if __name__ == "__main__":
    main()
