import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from . import amend7_panel as pn
from . import inputs
from .evaluate2 import drugbank_state
from .metrics import extended

SEEDS = [42, 1, 2, 3, 4]
BOOT_SEED = {"novel": 1042, "older_primary": 42, "older_clean": 42, "pooled": 42}
H5_AUROC, H5_MCC = 0.75, 0.30
E7B_LOWER = 0.70
ORACLE_FLOOR = 0.90
ORACLE_GAP = 0.05
STEM_DROP = 0.05
ROBUST_GAP = 0.05
TOST = (0.40, 0.60)
OLDER_ARTIFACTS = ("almotriptan malate", "atazanavir sulfate", "atorvastatin calcium", "citalopram hydrobromide",
                   "darifenacin hydrobromide", "rosuvastatin calcium", "benzoate")
OLDER_MISSED = ("clopidogrel bisulfate", "perindopril erbumine", "peginterferon alfa-2a", "calcitonin", "esmolol",
                "toremifene citrate", "trospium chloride")
ARMS = {"a": "h5contam", "b": "fixedownlabel", "c": "names", "d": "fixedother", "e": "fixedclean"}
KEYS = {"a": ("test", "ood", "oodold"), "b": ("test", "ood", "oodold"), "c": ("test_names", "ood_names", "oodold_names"),
        "d": ("test", "ood", "oodold"), "e": ("test", "ood", "oodold")}


class Truth:
    def __init__(self, ood_rows, old_rows, db_ood=None, db_old=None, sensitivity=None, test_y=None):
        self.sets = {}
        for tag, rows, db in (("ood", ood_rows, db_ood), ("oodold", old_rows, db_old)):
            pairs = inputs.ood_as_pairs(rows)
            self.sets[tag] = {"y": np.array([p["y"] for p in pairs]), "g": np.array([p["drug_a"] for p in pairs]),
                              "q": np.array([p["drug_b"] for p in pairs]), "hash": inputs.pairs_hash(pairs),
                              "db": None if db is None else drugbank_state(rows, db)}
        self.test_y = None if test_y is None else np.asarray(test_y)
        self.sensitivity = sensitivity or {"novel": [], "older_primary": []}

    def cohort(self, name, tier="A", drop=()):
        tag = "ood" if name == "novel" else "oodold"
        s = self.sets[tag]
        m = np.ones(len(s["y"]), bool)
        if name == "older_primary":
            m &= ~np.isin(s["g"], OLDER_ARTIFACTS + OLDER_MISSED)
        if name == "older_clean":
            m &= ~np.isin(s["g"], OLDER_ARTIFACTS)
        if len(drop):
            m &= ~np.isin(s["g"], list(drop))
        if tier == "B":
            if s["db"] is None:
                raise ValueError("tier B needs the DrugBank validation file")
            m &= s["db"] == 1
        return {"tag": tag, "mask": m, "y": s["y"][m], "g": s["g"][m], "q": s["q"][m], "name": name}


def fast_within(y, s, strata, weighted_by_drug=False):
    y = np.asarray(y)
    st = np.unique(np.asarray(strata), return_inverse=True)[1].ravel()
    dense = np.unique(np.asarray(s, float), return_inverse=True)[1].ravel()
    r = rankdata(st.astype(np.int64) * (dense.max() + 1) + dense)
    size = np.bincount(st)
    offset = (np.cumsum(size) - size)[st]
    npos = np.bincount(st, weights=y.astype(float), minlength=len(size))
    nneg = size - npos
    u = np.bincount(st, weights=(r - offset) * y, minlength=len(size)) - npos * (npos + 1) / 2
    ok = (npos > 0) & (nneg > 0)
    if weighted_by_drug:
        return float(np.mean(u[ok] / (npos[ok] * nneg[ok]))) if ok.any() else float("nan")
    total = float((npos * nneg).sum())
    return float(u.sum() / total) if total else float("nan")


def point(y, s, g, mode="within"):
    if mode == "pooled":
        return fast_within(y, s, np.zeros(len(y), int))
    return fast_within(y, s, g, weighted_by_drug=(mode == "drug_weighted"))


def draws(y, scores, g, q, n=1000, seed=42, mode="within"):
    y = np.asarray(y)
    scores = [np.asarray(s, float) for s in scores]
    c1 = np.unique(g, return_inverse=True)[1].ravel()
    c2 = np.unique(q, return_inverse=True)[1].ravel()
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = np.repeat(np.arange(len(rep)), rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        copy = r // w2[c2][idx]
        strata = np.zeros(len(idx), int) if mode == "pooled" else c1[idx] * (w1.max() + 1) + copy
        v = [fast_within(y[idx], s[idx], strata, weighted_by_drug=(mode == "drug_weighted")) for s in scores]
        if not any(np.isnan(v)):
            out.append(v)
    return np.asarray(out).T if out else np.zeros((len(scores), 0))


def summ(est, d):
    d = np.asarray(d)
    if not len(d):
        return {"value": est, "lo95": None, "hi95": None, "lo90": None, "hi90": None, "n_draws": 0}
    return {"value": float(est), "lo95": float(np.percentile(d, 2.5)), "hi95": float(np.percentile(d, 97.5)),
            "lo90": float(np.percentile(d, 5)), "hi90": float(np.percentile(d, 95)), "n_draws": int(len(d))}


def estimate(c, s, n=1000, mode="within"):
    d = draws(c["y"], [s], c["g"], c["q"], n, BOOT_SEED[c["name"]], mode)[0]
    return summ(point(c["y"], s, c["g"], mode), d)


def paired(c, a, b, n=1000, mode="within"):
    d = draws(c["y"], [a, b], c["g"], c["q"], n, BOOT_SEED[c["name"]], mode)
    return summ(point(c["y"], a, c["g"], mode) - point(c["y"], b, c["g"], mode), d[0] - d[1])


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def additive_residual(s, g1, g2, iters=200):
    c1 = np.unique(g1, return_inverse=True)[1].ravel()
    c2 = np.unique(g2, return_inverse=True)[1].ravel()
    a, b = np.zeros(c1.max() + 1), np.zeros(c2.max() + 1)
    mu = s.mean()
    for _ in range(iters):
        a = np.bincount(c1, s - mu - b[c2], minlength=len(a)) / np.bincount(c1, minlength=len(a))
        b = np.bincount(c2, s - mu - a[c1], minlength=len(b)) / np.bincount(c2, minlength=len(b))
    return np.round(s - mu - a[c1] - b[c2], 8)


def tost(d, margin=TOST):
    if not len(d):
        return None
    lo, hi = np.percentile(d, 5), np.percentile(d, 95)
    return {"equivalent": bool(lo > margin[0] and hi < margin[1]), "lo90": float(lo), "hi90": float(hi), "margin": list(margin)}


def read_job(preds, name):
    f = Path(preds) / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def seed_average(preds, arm, key, seeds=SEEDS):
    slug = ARMS[arm]
    ps, pbs, have = [], [], []
    for s in seeds:
        r = read_job(preds, f"a7-e7{arm}-{slug}-s{s}")
        if r is None or key not in r["eval"]:
            continue
        e = r["eval"][key]
        ps.append(np.asarray(e["p"], float))
        pbs.append((np.asarray(e["preds"]) != 0).astype(int))
        have.append(s)
    if not ps:
        return None
    return {"p": np.mean(ps, axis=0), "pb": (np.mean(pbs, axis=0) >= 0.5).astype(int), "seeds": have,
            "complete": sorted(have) == sorted(seeds)}


def row_view(c, vec, full_len, index=None):
    vec = np.asarray(vec)
    if index is not None:
        full = np.full(full_len, np.nan)
        full[np.asarray(index)] = vec
        vec = full
    return vec[c["mask"]]


def e7a_verdict(preds, truth, n=1000):
    avg = seed_average(preds, "a", "ood")
    if avg is None:
        return {"decision": "pending (no seeds)"}
    c = truth.cohort("novel")
    p, pb = avg["p"][c["mask"]], avg["pb"][c["mask"]]
    auc = point(c["y"], p, c["g"], "pooled")
    d = draws(c["y"], [p], c["g"], c["q"], n, BOOT_SEED["novel"], "pooled")[0]
    mcc = extended(c["y"], pb)["mcc"]
    ok = bool(auc >= H5_AUROC and mcc >= H5_MCC)
    res = {"pooled_auroc": summ(auc, d), "mcc_majority_vote": float(mcc), "thresholds": [H5_AUROC, H5_MCC],
           "seeds": avg["seeds"], "complete": avg["complete"], "pass": ok}
    res["decision"] = ("pass" if ok else "fail") if avg["complete"] else f"pending ({len(avg['seeds'])} of {len(SEEDS)} seeds)"
    return res


def e7b_verdict(preds, truth, thresholds, n=1000):
    avg = {"ood": seed_average(preds, "b", "ood"), "oodold": seed_average(preds, "b", "oodold")}
    if avg["ood"] is None or avg["oodold"] is None:
        return {"decision": "pending (no seeds)"}
    out, ok = {}, True
    for cname, key, tkey in (("novel", "ood", "threshold_novel"), ("older_primary", "oodold", "threshold_older_primary")):
        c = truth.cohort(cname)
        p = avg[key]["p"][c["mask"]]
        est = estimate(c, p, n)
        T = thresholds[tkey]
        good = bool(est["value"] >= T and est["lo95"] is not None and est["lo95"] > E7B_LOWER)
        out[cname] = {"within": est, "threshold": T, "lower_bound_floor": E7B_LOWER, "pass": good}
        ok &= good
    complete = avg["ood"]["complete"] and avg["oodold"]["complete"]
    out["decision"] = ("pass" if ok else "fail") if complete else "pending (seeds missing)"
    out["pass"] = bool(ok)
    return out


def knowledge_arms(preds, truth, cpu, prior_name="a7-prior-partner-train", n=1000, drop=None):
    prior = read_job(cpu, prior_name)
    out = {}
    for arm in ("c", "d", "e"):
        out[arm] = {}
        for cname, key_i in (("novel", 1), ("older_primary", 2), ("older_clean", 2)):
            key = KEYS[arm][key_i]
            avg = seed_average(preds, arm, key)
            if avg is None:
                continue
            for tier in ("A", "B"):
                try:
                    c = truth.cohort(cname, tier, drop=(drop or {}).get(cname, ()))
                except ValueError:
                    continue
                if not len(c["y"]):
                    continue
                p = avg["p"][c["mask"]]
                entry = {"within": estimate(c, p, n), "drug_weighted": estimate(c, p, n, "drug_weighted"),
                         "pooled": estimate(c, p, n, "pooled"), "seeds": avg["seeds"], "complete": avg["complete"]}
                res = additive_residual(logit(p), c["g"], c["q"])
                entry["residual_within"] = estimate(c, res, n)
                if prior is not None:
                    pk = "ood" if cname == "novel" else "oodold"
                    pr_ = np.asarray(prior["eval"][pk]["p"], float)[c["mask"]]
                    entry["partner_prior_within"] = estimate(c, pr_, n)
                    entry["paired_vs_partner_prior"] = paired(c, p, pr_, n)
                lo_res = entry["residual_within"]["lo95"]
                lo_pair = entry.get("paired_vs_partner_prior", {}).get("lo95")
                dd = draws(c["y"], [p], c["g"], c["q"], n, BOOT_SEED[cname])[0]
                entry["tost_older_primary"] = tost(dd) if cname == "older_primary" else None
                if lo_res is not None and lo_pair is not None and lo_res > 0.5 and lo_pair > 0:
                    label = "signal"
                elif entry["tost_older_primary"] and entry["tost_older_primary"]["equivalent"]:
                    label = "no signal"
                else:
                    label = "neither"
                entry["label"] = label
                out[arm][f"{cname}/{tier}"] = entry
    return out


def kappa(est, db_est):
    return (est - 0.5) / (db_est - 0.5) if db_est is not None and db_est != 0.5 else None


def drugbank_scores(rows, db_rows):
    idx = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in db_rows}
    return np.array([1.0 if idx.get((r["ood_drug"], r["semeval_drug"])) == "positive" else 0.0 for r in rows])


def add_kappas(knowledge, truth, db_scores, n=1000):
    for arm, cells in knowledge.items():
        for cell, entry in cells.items():
            cname, tier = cell.split("/")
            if tier != "A":
                continue
            c = truth.cohort(cname)
            s = db_scores["ood" if cname == "novel" else "oodold"][c["mask"]]
            db_est = point(c["y"], s, c["g"])
            entry["drugbank_within"] = db_est
            entry["kappa"] = kappa(entry["within"]["value"], db_est)
    return knowledge


def arm_differences(preds, truth, n=1000):
    out = {}
    for cname, key_i in (("novel", 1), ("older_primary", 2)):
        c = truth.cohort(cname)
        vecs = {}
        for arm in "abcde":
            avg = seed_average(preds, arm, KEYS[arm][key_i])
            if avg is not None:
                vecs[arm] = avg["p"][c["mask"]]
        names = sorted(vecs)
        if len(names) < 2:
            continue
        d = draws(c["y"], [vecs[a] for a in names], c["g"], c["q"], n, BOOT_SEED[cname])
        for i, a in enumerate(names):
            for j, b in enumerate(names):
                if i < j:
                    est = point(c["y"], vecs[a], c["g"]) - point(c["y"], vecs[b], c["g"])
                    out[f"{cname}/{a}-{b}"] = summ(est, d[i] - d[j])
    return out


def names_prompts(preds, truth, n=1000):
    r = read_job(preds, "a7-qwen-names")
    if r is None:
        return None
    out = {"answer": r.get("answer"), "cohorts": {}}
    from .amend7_prompts import NAMES_PROMPTS, PRIMARY
    for cname, key in (("novel", "ood"), ("older_primary", "oodold")):
        c = truth.cohort(cname)
        per = {}
        for pid, _, _ in NAMES_PROMPTS:
            per[pid] = estimate(c, np.asarray(r["eval"][f"{key}_{pid}"]["p"], float)[c["mask"]], n)
        vals = [v["value"] for v in per.values()]
        prim = per[PRIMARY]["value"]
        out["cohorts"][cname] = {"per_prompt": per, "primary": prim, "min": min(vals), "max": max(vals),
                                 "robust": bool(all(abs(v - prim) <= ROBUST_GAP for v in vals))}
    out["robust"] = bool(all(v["robust"] for v in out["cohorts"].values()))
    return out


def oracle_rule(preds, truth, cpu, n=1000):
    r = read_job(preds, "a7-qwen-oracle")
    g = read_job(cpu, "a7-grep-qwen-oracle")
    if r is None or g is None:
        return {"decision": "pending"}
    out, ok = {}, True
    for cname, key in (("novel", "ood"), ("older_primary", "oodold")):
        c = truth.cohort(cname)
        s = np.asarray(r["eval"][key]["p"], float)[c["mask"]]
        grep = point(c["y"], np.asarray(g["eval"][key]["p"], float)[c["mask"]], c["g"])
        est = estimate(c, s, n)
        bar = max(ORACLE_FLOOR, grep - ORACLE_GAP)
        stat = est["lo95"] if cname == "older_primary" else est["value"]
        good = bool(stat is not None and stat >= bar)
        out[cname] = {"within": est, "grep": grep, "bar": bar, "statistic": "lower95" if cname == "older_primary" else "point",
                      "pass": good}
        ok &= good
    out["decision"] = "pass" if ok else "fail"
    out["pass"] = bool(ok)
    return out


def evidence_arms(preds, truth, n=1000):
    names = read_job(preds, "a7-qwen-names")
    out = {}
    for cond, job in (("oracle", "oracle"), ("masked", "maskedoracle"), ("wrong", "wrongoracle"),
                      ("redacted", "redactedoracle"), ("contam", "contam"), ("other", "other"), ("clean", "clean")):
        r = read_job(preds, f"a7-qwen-{job}")
        if r is None:
            continue
        out[cond] = {"answer": r.get("answer"), "context": {k: {x: y for x, y in v.items() if x != "partner_in_context"}
                                                              for k, v in (r.get("context") or {}).items()}}
        for cname, key in (("novel", "ood"), ("older_primary", "oodold")):
            for tier in ("A", "B"):
                try:
                    c = truth.cohort(cname, tier)
                except ValueError:
                    continue
                s = np.asarray(r["eval"][key]["p"], float)[c["mask"]]
                cell = {"within": estimate(c, s, n)}
                if names is not None and tier == "A":
                    base = np.asarray(names["eval"][key]["p"], float)[c["mask"]]
                    cell["minus_names_only"] = paired(c, s, base, n)
                out[cond][f"{cname}/{tier}"] = cell
    return out


def stem_control(preds, truth, n=1000):
    names = read_job(preds, "a7-qwen-names")
    pres = read_job(preds, "a7-qwen-stem-preserved")
    scr = read_job(preds, "a7-qwen-stem-scrambled")
    if names is None or pres is None or scr is None:
        return {"decision": "pending"}
    ys, gs, qs, real, kept, scrambled = [], [], [], [], [], []
    for cname, key, prefix in (("novel", "ood", "n:"), ("older_primary", "oodold", "o:")):
        c = truth.cohort(cname)
        idx = np.asarray(pres["eval"][key]["index"])
        if list(idx) != list(scr["eval"][key]["index"]):
            raise ValueError("stem jobs scored different rows")
        full_idx = np.where(c["mask"])[0]
        keep = np.isin(idx, full_idx)
        sel = idx[keep]
        tag = truth.sets[c["tag"]]
        ys.append(tag["y"][sel])
        gs.append(np.array([prefix + x for x in tag["g"][sel]]))
        qs.append(tag["q"][sel])
        real.append(np.asarray(names["eval"][key]["p"], float)[sel])
        kept.append(np.asarray(pres["eval"][key]["p"], float)[keep])
        scrambled.append(np.asarray(scr["eval"][key]["p"], float)[keep])
    y, g, q = np.concatenate(ys), np.concatenate(gs), np.concatenate(qs)
    real, kept, scrambled = np.concatenate(real), np.concatenate(kept), np.concatenate(scrambled)
    d = draws(y, [real, kept, scrambled], g, q, n, BOOT_SEED["pooled"])
    est = [point(y, s, g) for s in (real, kept, scrambled)]
    diff = summ(est[1] - est[2], d[1] - d[2])
    expected = bool(diff["value"] >= STEM_DROP and diff["lo95"] is not None and diff["lo95"] > 0)
    return {"n_rows": int(len(y)), "n_drugs": int(len(set(g.tolist()))), "real": summ(est[0], d[0]),
            "preserved": summ(est[1], d[1]), "scrambled": summ(est[2], d[2]),
            "preserved_minus_scrambled": diff, "expected_drop_observed": expected,
            "decision": "drop of at least 0.05 with an interval excluding 0" if expected else "smaller or inconsistent drop"}


def panel(preds, truth, ytest, n=1000):
    models = {"novel": [], "older_primary": []}
    masked, external = {}, {}
    from .metrics import binary_f1
    for path in sorted(Path(preds).glob("a7-panel-*.json")) + sorted(Path(preds).glob("a7-ext-*.json")):
        r = json.loads(path.read_text())
        ev = r["eval"]
        x = binary_f1(ytest, ev["test_sentence"]["preds"])
        variant = r["config"]["variant"]
        for cname, key in (("novel", "ood_empty"), ("older_primary", "oodold_empty")):
            c = truth.cohort(cname)
            m = {"name": r["config"]["name"], "semeval": x, "y": c["y"], "groups": c["g"], "partners": c["q"],
                 "p": np.asarray(ev[key]["p"], float)[c["mask"]]}
            if variant == "masked":
                masked.setdefault(cname, []).append(m)
            elif variant == "external":
                external.setdefault(cname, []).append(m)
            else:
                models[cname].append(m)
    out = {"panel": {}, "masked": {}, "external": {}}
    for cname, ms in models.items():
        if len(ms) >= 3:
            out["panel"][cname] = pn.panel_stats(ms, n_boot=n, seed=BOOT_SEED[cname])
    for kind, store in (("masked", masked), ("external", external)):
        for cname, ms in store.items():
            st = pn.pair_structure(ms[0]["y"], ms[0]["groups"], ms[0]["partners"])
            out[kind][cname] = {m["name"]: {"auroc_within": float(pn.win_values(m["p"], st).mean()),
                                            "semeval_binary_f1": m["semeval"]} for m in ms}
    return out


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if o != o else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o
