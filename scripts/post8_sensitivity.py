import argparse
import json

import numpy as np

import post8_common as pc
from amend7_cpu_common import cohort_arrays, drugbank_score, paired_draws, seed_mean, single
from ddiood import amend7_analysis as aa
from ddiood import evaluate2 as ev

DECISIONS = pc.ROOT / "results" / "revision" / "eval" / "decisions.json"
E7 = pc.ROOT / "results" / "revision" / "amend7" / "e7.json"
E8 = pc.ROOT / "results" / "revision" / "amend7" / "e8.json"
TIERS = ("A", "C-auto", "C-auto-broad")


def pct(d, a):
    return float(np.percentile(d, a))


def hrow(y, s, db, g, q, seed, n):
    d = paired_draws(y, [s, db], g, q, n, seed)
    est = aa.fast_within(y, s, g)
    dbe = aa.fast_within(y, db, g)
    kd = (d[0] - 0.5) / (d[1] - 0.5)
    return {"n": int(len(y)), "n_pos": int(np.sum(y)), "n_drugs": int(len(set(g.tolist()))), "value": est,
            "ci90": [pct(d[0], 5), pct(d[0], 95)], "ci95": [pct(d[0], 2.5), pct(d[0], 97.5)], "upper95_one_sided": pct(d[0], 95),
            "lo95": pct(d[0], 2.5), "p_tost": ev.tost_p(d[0]), "drugbank_within": dbe,
            "drugbank_ci95": [pct(d[1], 2.5), pct(d[1], 97.5)],
            "kappa": (est - 0.5) / (dbe - 0.5), "kappa_ci95": [pct(kd, 2.5), pct(kd, 97.5)], "kappa_upper95": pct(kd, 97.5),
            "n_draws": int(d.shape[1]), "_draws": d[0]}


def h_family(truth, keep, n):
    b2o = seed_mean("b2mixed-biomedbert", "oodold_empty")[0]
    b2n = seed_mean("b2mixed-biomedbert", "ood_empty")[0]
    krag = seed_mean("krag-hybrid-k5-c400-biomedbert", "ood")[0]
    dbo, dbn = drugbank_score(truth, "oodold"), drugbank_score(truth, "ood")
    old = cohort_arrays(truth, "older_clean")
    nov = cohort_arrays(truth, "novel")
    mo = old["mask"] & keep["oodold"]
    mn = nov["mask"] & keep["ood"]
    so, sn = truth.sets["oodold"], truth.sets["ood"]
    arr = lambda s, m: (np.asarray(s["y"])[m], np.asarray(s["g"])[m], np.asarray(s["partner"])[m])
    yo, go, qo = arr(so, mo)
    yn, gn, qn = arr(sn, mn)
    rows = {"H1": hrow(yo, b2o[mo], dbo[mo], go, qo, 42, n),
            "H1-novel": hrow(yn, b2n[mn], dbn[mn], gn, qn, 1042, n),
            "H6": hrow(yn, krag[mn], dbn[mn], gn, qn, 1042, n)}
    a, b = rows["H1"]["_draws"], rows["H1-novel"]["_draws"]
    k = min(len(a), len(b))
    diff = a[:k] - b[:k]
    rows["H4"] = {"value": rows["H1"]["value"] - rows["H1-novel"]["value"], "ci90": [pct(diff, 5), pct(diff, 95)],
                  "ci95": [pct(diff, 2.5), pct(diff, 97.5)], "p_tost": ev.tost_p(diff + 0.5)}
    ps = {h: rows[h]["p_tost"] for h in ("H1", "H4", "H6")}
    adj = ev.holm(ps)
    for h in ("H1", "H4", "H6"):
        rows[h]["p_holm"] = adj[h]
    for h in ("H1", "H6"):
        rows[h]["would_be_label"] = ev.decide_equivalence(rows[h], adj[h])
    o, nv = rows["H1"], rows["H1-novel"]
    if adj["H4"] < 0.05 and o["lo95"] <= ev.HI:
        lab = "supported"
    elif o["lo95"] > ev.HI and nv["upper95_one_sided"] <= ev.HI:
        lab = "falsified"
    else:
        lab = "inconclusive"
    rows["H4"]["would_be_label"] = lab
    for r in rows.values():
        r.pop("_draws", None)
    return rows


def check_primary(rows):
    dec = json.loads(DECISIONS.read_text())
    for h in ("H1", "H1-novel", "H6", "H4"):
        ref = dec[h]
        if abs(rows[h]["value"] - ref["value"]) > 1e-3 or abs(rows[h]["ci95"][0] - ref["interval"][0]) > 1e-3:
            raise ValueError(f"{h}: tier A does not reproduce decisions.json")
        if h != "H1-novel" and abs(rows[h]["p_tost"] - ref["p_tost"]) > 1e-3:
            raise ValueError(f"{h}: p_TOST does not reproduce decisions.json")
    return True


def drugbank_rows(truth, keep, n):
    out = {}
    for cohort, tag in (("novel", "ood"), ("older_full", "oodold"), ("older_clean", "oodold"), ("older_primary", "oodold")):
        s = truth.sets[tag]
        m = np.ones(len(s["y"]), bool)
        g_all = np.asarray(s["g"])
        if cohort == "older_clean":
            m &= s["clean"]
        if cohort == "older_primary":
            m &= ~np.isin(g_all, aa.OLDER_ARTIFACTS + aa.OLDER_MISSED)
        m &= keep[tag]
        y, g, q = np.asarray(s["y"])[m], g_all[m], np.asarray(s["partner"])[m]
        db = drugbank_score(truth, tag)[m]
        d = paired_draws(y, [db], g, q, n, 1042 if tag == "ood" else 42)[0]
        pooled_d = ev.boot_auroc(y, db, g, q, n)
        out[cohort] = {"n": int(len(y)), "n_pos": int(y.sum()), "auroc_within": aa.fast_within(y, db, g),
                       "within_ci95": [pct(d, 2.5), pct(d, 97.5)], "auroc_pooled": ev.auroc(y, db),
                       "pooled_ci95": list(ev.interval(pooled_d))}
    return out


def e8_rows(truth, n):
    r = aa.oracle_rule(str(pc.PREDS), truth, str(pc.CPU), n)
    return r


def strip_e7(know):
    out = {}
    for arm, cells in know.items():
        out[arm] = {}
        for cell, e in cells.items():
            out[arm][cell] = {"within": e["within"], "drug_weighted": e["drug_weighted"], "pooled": e["pooled"],
                              "residual_within": e["residual_within"], "partner_prior_within": e.get("partner_prior_within"),
                              "paired_vs_partner_prior": e.get("paired_vs_partner_prior"),
                              "tost_older_primary": e.get("tost_older_primary"), "label": e["label"],
                              "drugbank_within": e.get("drugbank_within"), "kappa": e.get("kappa"),
                              "n": None, "seeds": e["seeds"], "complete": e["complete"]}
    return out


def e7_rows(truth, db_scores, n):
    know = aa.knowledge_arms(str(pc.PREDS), truth, str(pc.CPU), n=n)
    know = aa.add_kappas(know, truth, db_scores, n)
    return strip_e7(know)


def check_e7(primary):
    ref = json.loads(E7.read_text())["knowledge"]
    for arm, cells in primary.items():
        for cell, e in cells.items():
            if cell in ref.get(arm, {}):
                for k in ("within", "residual_within"):
                    if abs(e[k]["value"] - ref[arm][cell][k]["value"]) > 1e-9 or abs(e[k]["lo95"] - ref[arm][cell][k]["lo95"]) > 1e-9:
                        raise ValueError(f"E7 {arm} {cell} {k} does not reproduce e7.json")
    return True


def check_e8(primary):
    ref = json.loads(E8.read_text())["e8_oracle_rule"]
    for c in ("novel", "older_primary"):
        if abs(primary[c]["within"]["lo95"] - ref[c]["within"]["lo95"]) > 1e-9:
            raise ValueError("E8 oracle rule does not reproduce e8.json")
    return True


def counts_by_cohort(truth, keep):
    out = {}
    for cname in ("novel", "older_primary", "older_clean"):
        c = truth.cohort(cname)
        m = c["mask"] & keep[c["tag"]]
        y = truth.sets[c["tag"]]["y"]
        out[cname] = {"positives": int(y[m].sum()), "negatives": int((y[m] == 0).sum()),
                      "positives_dropped": int(y[c["mask"]].sum() - y[m].sum())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--which", nargs="+", default=["h", "e8", "e7", "drugbank"])
    a = ap.parse_args()
    crit, rows, rule, screens = pc.screens_for_run()
    keeps = {"A": {"ood": np.ones(len(rows["novel"]), bool), "oodold": np.ones(len(rows["older"]), bool)},
             "C-auto": pc.keep_masks(screens), "C-auto-broad": pc.keep_masks(screens, broad=True)}
    truth = ev.load_truth()
    a7, _, (db_ood, db_old) = pc.a7_truth()
    db_scores = {"ood": aa.drugbank_scores(rows["novel"], db_ood), "oodold": aa.drugbank_scores(rows["older"], db_old)}
    out = {"status": pc.STATUS, "tiers": {t: counts_by_cohort(a7, k) for t, k in keeps.items()}, "boot": a.boot,
           "checks": {}}
    path = pc.OUT / "sensitivity.json"
    prev = json.loads(path.read_text()) if path.exists() else {}
    for part in ("h", "e8", "e7", "drugbank"):
        if part not in a.which and part in prev:
            out[part] = prev[part]
    if "h" in a.which:
        out["h"] = {t: h_family(truth, keeps[t], a.boot) for t in TIERS}
        out["checks"]["h_tier_A_reproduces_decisions"] = check_primary(out["h"]["A"])
    if "e8" in a.which:
        out["e8"] = {t: e8_rows(a7 if t == "A" else pc.TruthC(a7, keeps[t]), a.boot) for t in TIERS}
        out["checks"]["e8_tier_A_reproduces_e8_json"] = check_e8(out["e8"]["A"])
    if "e7" in a.which:
        out["e7"] = {t: e7_rows(a7 if t == "A" else pc.TruthC(a7, keeps[t]), db_scores, a.boot) for t in ("A", "C-auto")}
        out["checks"]["e7_tier_A_reproduces_e7_json"] = check_e7(out["e7"]["A"])
    if "drugbank" in a.which:
        out["drugbank"] = {t: drugbank_rows(truth, keeps[t], a.boot) for t in ("A", "C-auto")}
    pc.write("sensitivity", out, None)
    print(json.dumps({k: v for k, v in out.items() if k in ("checks", "tiers")}, indent=1))


if __name__ == "__main__":
    main()
