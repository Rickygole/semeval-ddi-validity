import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

from . import inputs, semeval, stats
from .metrics import extended

ROOT = Path(__file__).resolve().parents[1]
CORRECTED = ROOT / "results" / "corrected"
ARTIFACTS = ROOT / "artifacts" / "ood"
SEEDS = [1, 2, 3, 4, 42]
OLDER_ARTIFACTS = ("almotriptan malate", "atazanavir sulfate", "atorvastatin calcium", "citalopram hydrobromide",
                   "darifenacin hydrobromide", "rosuvastatin calcium", "benzoate")
OLDER_REMOVED_ROWS = 112
OLDER_SENSITIVITY_DRUGS = ("clopidogrel bisulfate", "perindopril erbumine", "peginterferon alfa-2a", "calcitonin", "esmolol")
OLDER_SENSITIVITY_ROWS = 78
DRUGBANK_FILES = {"ood": ("drugbank_validation.csv",), "oodold": ("drugbank_validation_old.csv",
                                                                 "drugbank_validation_older.csv")}
PRIMARY_KEYS = ("ood_empty", "oodold_empty", "ood_names", "oodold_names", "ood", "oodold")
COHORTS = (("novel", "ood"), ("older_full", "oodold"), ("older_clean", "oodold"))
ATTENUATION_REFERENCE = 0.70
DIFF_MARGIN = 0.10
KINDS = ("vocab", "novel", "pseudo")
LO, HI = 0.40, 0.60
GKEY = ("system", "model", "split", "variant", "k", "chars")
OOD_KEYS = {"b2sentence": ("ood_empty", "oodold_empty"), "b2mixed": ("ood_empty", "oodold_empty"),
            "b2masked": ("ood_empty", "oodold_empty"), "b1names": ("ood_names", "oodold_names"),
            "krag": ("ood", None), "names": ("ood", "oodold"), "rag": ("ood", None)}


def drugbank_state(rows, db_rows):
    if db_rows is None:
        return None
    lookup = {(r["ood_drug"], r["semeval_drug"]): r for r in db_rows}
    out = np.zeros(len(rows), int)
    for i, r in enumerate(rows):
        d = lookup.get((r["ood_drug"], r["semeval_drug"]))
        if d is None:
            continue
        fda, db = int(d["fda_label"]), d["drugbank_label"]
        if db == "unresolvable":
            out[i] = 3
        elif (fda == 1) == (db == "positive"):
            out[i] = 1
        else:
            out[i] = 2
    return out


class Truth:
    def __init__(self, test_labels, ood_rows, ood_old_rows, drugbank=None, test_sid=None):
        drugbank = drugbank or {}
        self.test_y = [int(v != 0) for v in test_labels]
        self.test_sid = None if test_sid is None else np.asarray(test_sid)
        self.sets = {}
        for name, rows in (("ood", ood_rows), ("oodold", ood_old_rows)):
            pairs = inputs.ood_as_pairs(rows)
            clean = np.array([not (name == "oodold" and p["drug_a"].strip().lower() in OLDER_ARTIFACTS)
                              for p in pairs])
            sens = np.array([not (name == "oodold" and p["drug_a"].strip().lower() in OLDER_SENSITIVITY_DRUGS)
                             for p in pairs])
            self.sets[name] = {"y": [p["y"] for p in pairs], "g": [p["drug_a"] for p in pairs],
                               "partner": [p["drug_b"] for p in pairs], "hash": inputs.pairs_hash(pairs),
                               "pairs": pairs, "clean": clean, "sens": sens, "dbstate": drugbank_state(rows, drugbank.get(name))}
        pairs = self.sets["ood"]["pairs"]
        negs = {p["drug_a"] for p in pairs if p["y"] == 0}
        self.swap_groups = []
        for p in pairs:
            if p["y"] == 1 and p["sentence"] and p["drug_a"] in negs:
                self.swap_groups += [p["drug_a"]] * 2


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _find_drugbank(corrected, tag):
    for folder in (ARTIFACTS, Path(corrected)):
        for name in DRUGBANK_FILES[tag]:
            if (folder / name).exists():
                return _read_csv(folder / name)
    return None


class MissingDrugBankError(FileNotFoundError):
    pass


def load_drugbank(corrected=CORRECTED, allow_missing_drugbank=False):
    found = {tag: _find_drugbank(corrected, tag) for tag in DRUGBANK_FILES}
    missing = [tag for tag, rows in found.items() if rows is None]
    if missing and not allow_missing_drugbank:
        looked = ", ".join(str(folder / name) for tag in missing for folder in (ARTIFACTS, Path(corrected))
                           for name in DRUGBANK_FILES[tag])
        raise MissingDrugBankError(f"DrugBank validation CSV missing for {', '.join(missing)}; looked for {looked}. "
                                   "Tier B and the attenuation estimates need it. Pass --allow-missing-drugbank "
                                   "to evaluate without them.")
    return found


def load_truth(corrected=CORRECTED, allow_missing_drugbank=False):
    drugbank = load_drugbank(corrected, allow_missing_drugbank)
    semeval.download()
    test = semeval.load_pairs("test")
    truth = Truth([r["label_id"] for r in test], _read_csv(Path(corrected) / "ood_pairs.csv"),
                  _read_csv(Path(corrected) / "ood_old_pairs.csv"), drugbank, [r["sentence_id"] for r in test])
    removed = int((~truth.sets["oodold"]["clean"]).sum())
    if removed != OLDER_REMOVED_ROWS:
        raise ValueError(f"Older-clean filter removed {removed} rows, Amendment 4 expects {OLDER_REMOVED_ROWS}")
    extra = int((truth.sets["oodold"]["clean"] & ~truth.sets["oodold"]["sens"]).sum())
    if extra != OLDER_SENSITIVITY_ROWS:
        raise ValueError(f"Older-clean sensitivity filter removed {extra} rows, expected {OLDER_SENSITIVITY_ROWS}")
    return truth


def _kind(key):
    if key == "ood_swap_sentence":
        return "swapood"
    if key.startswith("oodold"):
        return "oodold"
    if key.startswith("ood"):
        return "ood"
    return "test"


def _resolve(truth, name, key, e):
    kind = _kind(key)
    p = np.asarray(e["p"], float)
    pb = (np.asarray(e["preds"]) != 0).astype(int)
    clean = sens = dbstate = None
    if kind == "test":
        y, g, partner = np.asarray(truth.test_y), None, None
    elif kind == "swapood":
        y = np.asarray(e["y"])
        g = np.asarray(truth.swap_groups if len(truth.swap_groups) == len(y) else [i // 2 for i in range(len(y))])
        partner = None
    else:
        s = truth.sets[kind]
        idx = e.get("index")
        idx = list(range(len(s["y"]))) if idx is None else idx
        y = np.asarray([s["y"][i] for i in idx])
        g = np.asarray([s["g"][i] for i in idx])
        partner = np.asarray([s["partner"][i] for i in idx])
        clean = s["clean"][idx]
        sens = s["sens"][idx]
        dbstate = None if s["dbstate"] is None else s["dbstate"][idx]
    if not (len(p) == len(pb) == len(y)):
        raise ValueError(f"{name} {key}: prediction length {len(p)} does not match ground truth {len(y)}")
    return {"y": y, "p": p, "pb": pb, "g": g, "partner": partner, "kind": kind, "clean": clean, "sens": sens,
            "dbstate": dbstate}


def load_jobs(preds_dir, truth):
    jobs = []
    for path in sorted(Path(preds_dir).glob("*.json")):
        res = json.loads(path.read_text())
        if "config" not in res or not isinstance(res.get("eval"), dict):
            print(f"skipped {path.name}: not a revision prediction file (no config and eval blocks)", file=sys.stderr)
            continue
        cfg = res["config"]
        for field, tag in (("ood_hash", "ood"), ("ood_old_hash", "oodold")):
            if res.get(field) != truth.sets[tag]["hash"]:
                raise ValueError(f"{cfg['name']}: {field} does not match the OOD pair set")
        evals, unseen = {}, None
        for key, e in res["eval"].items():
            if key == "test_unseen_index":
                unseen = list(e)
            else:
                evals[key] = _resolve(truth, cfg["name"], key, e)
        jobs.append({"name": cfg["name"], "cfg": cfg, "evals": evals, "unseen": unseen})
    return jobs


def gkey(cfg):
    return tuple(cfg.get(f) for f in GKEY)


def label(gk):
    system, model, split, variant, k, chars = gk
    s = f"{system}/{model}"
    if split == "disjoint":
        s += "/disjoint"
    if system == "krag":
        s += f"/{variant}-k{k}-c{chars}"
    return s


def _prep(p):
    return np.unique(p, return_inverse=True)[1].ravel()


def _auc(inv, y, w):
    m = inv.max() + 1
    wp = np.bincount(inv, weights=w * y, minlength=m)
    wn = np.bincount(inv, weights=w * (1 - y), minlength=m)
    P, N = wp.sum(), wn.sum()
    if P <= 0 or N <= 0:
        return float("nan")
    return float((wp * (np.cumsum(wn) - wn + 0.5 * wn)).sum() / (P * N))


def auroc(y, p):
    y = np.asarray(y, float)
    return _auc(_prep(np.asarray(p)), y, np.ones(len(y)))


def boot_auroc(y, p, groups=None, partners=None, n=1000, seed=42):
    y = np.asarray(y, float)
    inv = _prep(np.asarray(p))
    groups = np.arange(len(y)) if groups is None else np.asarray(groups)
    gi = np.unique(groups, return_inverse=True)[1].ravel()
    G = gi.max() + 1
    if partners is not None:
        pi = np.unique(np.asarray(partners), return_inverse=True)[1].ravel()
        Q = pi.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w = np.bincount(rng.randint(0, G, G), minlength=G)[gi].astype(float)
        if partners is not None:
            w = w * np.bincount(rng.randint(0, Q, Q), minlength=Q)[pi]
        out.append(_auc(inv, y, w))
    a = np.array(out)
    return a[~np.isnan(a)]


def interval(draws):
    if len(draws) == 0:
        return None, None
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def tost_p(draws):
    if len(draws) == 0:
        return None
    n = len(draws)
    return float(max((1 + (draws <= LO).sum()) / (n + 1), (1 + (draws >= HI).sum()) / (n + 1)))


def holm(ps):
    m = len(ps)
    order = sorted(ps, key=lambda k: ps[k] if ps[k] is not None else 2)
    out, run = {}, 0.0
    for i, k in enumerate(order):
        v = 1.0 if ps[k] is None else ps[k]
        run = max(run, min(1.0, (m - i) * v))
        out[k] = run
    return out


def cell(y, p, pb, g=None, partner=None, boot=0):
    y = np.asarray(y)
    tp = extended(y, pb)
    row = {"n": int(len(y)), "prevalence": float(y.mean()) if len(y) else None,
           "auroc": auroc(y, p) if len(y) else float("nan"),
           "auprc": float(average_precision_score(y, p)) if 0 < y.sum() < len(y) else float("nan"),
           "f1": tp["binary_f1"], "mcc": tp["mcc"], "balanced_accuracy": tp["balanced_accuracy"],
           "tp": tp["tp"], "fp": tp["fp"], "fn": tp["fn"], "tn": tp["tn"]}
    if partner is not None:
        row["auroc_within"] = stats.stratified_auroc(y, p, g)
    if boot:
        row["auroc_lo"], row["auroc_hi"] = interval(boot_auroc(y, p, g, None, boot))
        if partner is not None:
            row["auroc2_lo"], row["auroc2_hi"] = interval(boot_auroc(y, p, g, partner, boot))
    return row


def aggregate(jobs):
    groups = {}
    for j in jobs:
        groups.setdefault(gkey(j["cfg"]), []).append(j)
    out = {}
    for gk, members in groups.items():
        members = sorted(members, key=lambda j: j["cfg"]["seed"])
        evals = {}
        for key in sorted({k for j in members for k in j["evals"]}):
            have = [(j, j["evals"][key]) for j in members if key in j["evals"]]
            base = have[0][1]
            for j, e in have:
                if len(e["p"]) != len(base["p"]) or not np.array_equal(e["y"], base["y"]):
                    raise ValueError(f"{j['name']} {key}: inconsistent with other seeds of the group")
            ps = np.stack([e["p"] for _, e in have])
            pbs = np.stack([e["pb"] for _, e in have])
            evals[key] = {**base, "p": ps.mean(0), "pb": (pbs.mean(0) >= 0.5).astype(int), "seed_p": list(ps),
                          "seeds": [j["cfg"]["seed"] for j, _ in have]}
        out[gk] = {"seeds": [j["cfg"]["seed"] for j in members], "evals": evals, "jobs": members}
    return out


def load_baselines(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else None


def prior_aurocs(bl):
    out = {}
    for kind, name in (("ood", "novel"), ("oodold", "older")):
        try:
            out[kind] = bl[name]["baselines"]["partner_frequency_prior"]["auroc"]
        except (KeyError, TypeError):
            pass
    return out


def baseline_rows(bl):
    rows = []
    for name, tag in (("novel", "Novel OOD"), ("older", "Older OOD")):
        s = (bl or {}).get(name)
        if not s:
            continue
        for b, r in s["baselines"].items():
            c = r.get("confusion", {})
            ci = r.get("auroc_ci95") or {}
            rows.append({"set": tag, "baseline": b, "n": s["n"], "prevalence": r.get("prevalence"),
                         "auroc": r.get("auroc"), "auroc_lo": ci.get("lower"), "auroc_hi": ci.get("upper"),
                         "auprc": r.get("auprc"), "f1": r.get("binary_f1"), "mcc": r.get("mcc"),
                         "balanced_accuracy": r.get("balanced_accuracy"), "tp": c.get("tp"), "fp": c.get("fp"),
                         "fn": c.get("fn"), "tn": c.get("tn")})
    return rows


def _beats(row, kind, prior):
    if kind not in prior:
        return {}
    lo = row.get("auroc_lo")
    return {"partner_prior_auroc": prior[kind], "beats_partner_prior": None if lo is None else bool(lo > prior[kind])}


def per_job_rows(jobs, boot):
    rows = []
    for j in jobs:
        c = j["cfg"]
        for key, e in j["evals"].items():
            ood = e["kind"] != "test"
            r = cell(e["y"], e["p"], e["pb"], e["g"], e["partner"], boot if ood else 0)
            rows.append({"job": j["name"], "system": c["system"], "model": c["model"], "seed": c["seed"],
                         "split": c["split"], "key": key, **r})
    return rows


def seed_rows(aggs, boot, prior=None):
    rows = []
    for gk, a in aggs.items():
        for key, e in a["evals"].items():
            ood = e["kind"] != "test"
            r = cell(e["y"], e["p"], e["pb"], e["g"], e["partner"], boot if ood else 0)
            r.update(_beats(r, e["kind"], prior or {}))
            per = [auroc(e["y"], p) for p in e["seed_p"]]
            rows.append({"group": label(gk), "system": gk[0], "model": gk[1], "split": gk[2], "variant": gk[3],
                         "k": gk[4], "chars": gk[5], "key": key, "n_seeds": len(per),
                         "seed_auroc_mean": float(np.nanmean(per)) if not np.all(np.isnan(per)) else float("nan"),
                         "seed_auroc_sd": float(np.nanstd(per, ddof=1)) if len(per) > 1 else None, **r})
    return rows


def swap_rows(jobs):
    rows = []
    for j in jobs:
        for suffix in ("sentence", "names"):
            base = j["evals"].get(f"test_{suffix}")
            if base is None:
                continue
            for kind in KINDS:
                e = j["evals"].get(f"swap_{kind}_{suffix}")
                if e is None:
                    continue
                rows.append({"job": j["name"], "system": j["cfg"]["system"], "model": j["cfg"]["model"],
                             "seed": j["cfg"]["seed"], "split": j["cfg"]["split"], "swap": kind,
                             "n": int(len(e["p"])), "flip_rate": float((e["pb"] != base["pb"]).mean()),
                             "mean_abs_dp": float(np.abs(e["p"] - base["p"]).mean())})
    return rows


def masking_rows(jobs):
    rows = []
    for j in jobs:
        m, s = j["evals"].get("test_masked"), j["evals"].get("test_sentence")
        if m is None or s is None:
            continue
        fm, fs = extended(m["y"], m["pb"])["binary_f1"], extended(s["y"], s["pb"])["binary_f1"]
        rows.append({"job": j["name"], "system": j["cfg"]["system"], "model": j["cfg"]["model"],
                     "seed": j["cfg"]["seed"], "split": j["cfg"]["split"], "f1_masked": fm, "f1_sentence": fs,
                     "ratio": fm / fs if fs else float("nan")})
    return rows


def disjoint_rows(jobs):
    rows = []
    for j in jobs:
        if j["cfg"]["split"] != "disjoint" or j["unseen"] is None:
            continue
        for key, e in j["evals"].items():
            if e["kind"] != "test":
                continue
            mask = np.zeros(len(e["y"]), bool)
            mask[j["unseen"]] = True
            for name, sel in (("unseen", mask), ("seen", ~mask)):
                r = cell(e["y"][sel], e["p"][sel], e["pb"][sel])
                rows.append({"job": j["name"], "system": j["cfg"]["system"], "model": j["cfg"]["model"],
                             "seed": j["cfg"]["seed"], "key": key, "subset": name, **r})
    return rows


def grid_rows(aggs, boot, sid=None):
    rows = []
    for gk, a in aggs.items():
        if gk[0] not in ("b2mixed", "b2sentence") or gk[2] != "standard":
            continue
        for fmt, keys in (("sentence", ("test_sentence", "ood_sentence")), ("names only", ("test_empty", "ood_empty"))):
            for nov, key in zip(("SemEval test", "Novel OOD"), keys):
                e = a["evals"].get(key)
                if e is None:
                    continue
                d = boot_auroc(e["y"], e["p"], e["g"], None, boot)
                lo, hi = interval(d)
                if e["kind"] == "test":
                    dc = boot_auroc(e["y"], e["p"], sid, None, boot) if sid is not None else []
                else:
                    dc = boot_auroc(e["y"], e["p"], e["g"], e["partner"], boot)
                clo, chi = interval(dc)
                rows.append({"group": label(gk), "format": fmt, "novelty": nov, "key": key, "n": int(len(e["y"])),
                             "auroc": auroc(e["y"], e["p"]), "lo": lo, "hi": hi, "lo_clustered": clo, "hi_clustered": chi})
    return rows


def seeds_present(a, key):
    if a is None or key not in a["evals"]:
        return []
    return sorted(set(a["evals"][key]["seeds"]) & set(SEEDS))


def gate(a, key):
    k = len(seeds_present(a, key))
    return k == len(SEEDS), f"pending ({k} of {len(SEEDS)} seeds)"


def view(e, cohort, tier="A"):
    if e is None:
        return None
    m = np.ones(len(e["y"]), bool)
    if cohort in ("older_clean", "older_clean_sensitivity"):
        m &= e["clean"]
    if cohort == "older_clean_sensitivity":
        m &= e["sens"]
    if tier == "B":
        if e["dbstate"] is None:
            return None
        m &= e["dbstate"] == 1
    return {k: (e[k][m] if isinstance(e[k], np.ndarray) else e[k]) for k in ("y", "p", "pb", "g", "partner")} | {
        "dbstate": None if e["dbstate"] is None else e["dbstate"][m], "mask": m}


def attenuation(v):
    st = v["dbstate"]
    if st is None:
        return {}
    neg = v["y"] == 0
    resolvable = int((neg & ((st == 1) | (st == 2))).sum())
    if not resolvable:
        return {}
    r = float((neg & (st == 2)).sum()) / resolvable
    return {"neg_disagreement_rate": r, "expected_observed_if_true_070": (1 - r) * ATTENUATION_REFERENCE + 0.5 * r}


def within_stat(v, boot, seed=42):
    y, p, g, q = v["y"], v["p"], v["g"], v["partner"]
    est = stats.stratified_auroc(y, p, g)
    d = stats.two_way_samples(stats.stratified_auroc, y, p, g, q, n=boot, seed=seed, strat=g)
    both = sum(1 for k in set(g.tolist()) if len(set(y[g == k].tolist())) == 2)
    out = {"n": int(len(y)), "n_drugs": int(len(set(g.tolist()))), "n_drugs_contributing": int(both), "auroc_within": est, "auroc_pooled": auroc(y, p),
           "mcc": extended(y, v["pb"])["mcc"], "draws": d, "p_tost": tost_p(d)}
    if len(d):
        out.update({"lo90": float(np.percentile(d, 5)), "hi90": float(np.percentile(d, 95)),
                    "lo95": float(np.percentile(d, 2.5)), "hi95": float(np.percentile(d, 97.5)),
                    "upper95_one_sided": float(np.percentile(d, 95))})
    out.update(attenuation(v))
    return out


def ood_stat(cache, boot, gk, a, key, cohort, tier="A"):
    ck = (gk, key, cohort, tier)
    if ck not in cache:
        v = view(a["evals"].get(key), cohort, tier) if a is not None else None
        cache[ck] = None if v is None or not len(v["y"]) else within_stat(v, boot, 42 if cohort.startswith("older") else 1042)
    return cache[ck]


def find_key(aggs, system, model="biomedbert", variant="hybrid", k=5, chars=None, split="standard"):
    for gk, a in aggs.items():
        if gk[0] == system and gk[1] == model and gk[2] == split:
            if system == "krag" and (gk[3] != variant or gk[4] != k or (chars is not None and gk[5] != chars)):
                continue
            return gk, a
    return None, None


def _fmt(v):
    return "NA" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.3f}"


def entry(statistic, cohort, r=None, value=None, decision="", detail="", p=None, p_holm=None):
    e = {"statistic": statistic, "cohort": cohort, "value": value, "interval": None, "interval90": None,
         "upper95_one_sided": None, "p_tost": p, "p_holm": p_holm, "decision": decision, "detail": detail}
    if r is not None and "lo95" in r:
        e.update({"value": r["auroc_within"] if value is None else value, "interval": [r["lo95"], r["hi95"]],
                  "interval90": [r["lo90"], r["hi90"]], "upper95_one_sided": r["upper95_one_sided"]})
    return e


def decide_equivalence(r, adj_p):
    if adj_p < 0.05:
        return "supported"
    if r["lo95"] > HI:
        return "falsified"
    return "inconclusive"


def h2_spread(ms, sw):
    by = {x["seed"]: x for x in ms}
    seeds = sorted(by)
    ratios = [by[s]["ratio"] for s in seeds]
    pooled = float(np.mean([by[s]["f1_masked"] for s in seeds]) / np.mean([by[s]["f1_sentence"] for s in seeds]))
    parts = []
    for s in seeds:
        f = {x["swap"]: x["flip_rate"] for x in sw if x["seed"] == s}
        over = [k for k in KINDS if f.get(k, 0) > 0.10]
        parts.append(f"s{s} ratio {_fmt(by[s]['ratio'])} flips " + "/".join(_fmt(f.get(k)) for k in KINDS) +
                     (f" (over 0.10: {', '.join(over)})" if over else ""))
    return (f"seed-mean ratio is the preregistered value; median ratio {_fmt(float(np.median(ratios)))}, "
            f"ratio of mean F1s {_fmt(pooled)}, per-seed ratio range {_fmt(min(ratios))} to {_fmt(max(ratios))}; "
            f"per seed (flips {'/'.join(KINDS)}): " + "; ".join(parts) +
            "; the seed-mean aggregation was not preregistered")


def decide(aggs, swaps, masks, boot=1000, cache=None):
    cache = {} if cache is None else cache
    d = {}
    h1k, h1a = find_key(aggs, "b2mixed")
    h6k, h6a = find_key(aggs, "krag", variant="hybrid", chars=400)
    h5k, h5a = find_key(aggs, "krag", variant="contaminated", chars=400)
    h3k, h3a = find_key(aggs, "b2sentence")
    older = ood_stat(cache, boot, h1k, h1a, "oodold_empty", "older_clean")
    novel = ood_stat(cache, boot, h1k, h1a, "ood_empty", "novel")
    krag = ood_stat(cache, boot, h6k, h6a, "ood", "novel")
    ok_old, msg_old = gate(h1a, "oodold_empty")
    ok_nov, msg_nov = gate(h1a, "ood_empty")
    ok_krag, msg_krag = gate(h6a, "ood")
    ps = {"H1": older["p_tost"] if older and ok_old else None,
          "H4": None, "H6": krag["p_tost"] if krag and ok_krag else None}
    diff = None
    if older and novel and "lo95" in older and "lo95" in novel:
        n = min(len(older["draws"]), len(novel["draws"]))
        diff = older["draws"][:n] - novel["draws"][:n]
        if ok_old and ok_nov:
            ps["H4"] = tost_p(diff + 0.5)
    adj = holm(ps)

    if older is None:
        d["H1"] = entry("within-drug AUROC", "Older-clean", decision=msg_old, detail="no b2mixed oodold_empty cell")
    else:
        dec = decide_equivalence(older, adj["H1"]) if ok_old else msg_old
        d["H1"] = entry("within-drug AUROC", "Older-clean", older, p=older["p_tost"] if ok_old else None,
                        p_holm=adj["H1"] if ok_old else None, decision=dec,
                        detail=f"b2mixed names only, seeds {seeds_present(h1a, 'oodold_empty')}, n={older['n']}, "
                               f"{older['n_drugs']} drugs" + ("" if ok_old else "; provisional estimate"))
    if novel is None:
        d["H1-novel"] = entry("within-drug AUROC", "Novel", decision=msg_nov, detail="no b2mixed ood_empty cell")
    else:
        d["H1-novel"] = entry("within-drug AUROC", "Novel", novel,
                              decision="estimate only (no equivalence test)" if ok_nov else msg_nov,
                              detail=f"b2mixed names only, seeds {seeds_present(h1a, 'ood_empty')}, n={novel['n']}, "
                                     f"{novel['n_drugs']} drugs; upper95 one-sided {_fmt(novel.get('upper95_one_sided'))}")
    pooled = None
    if h1a is not None and "ood_empty" in h1a["evals"] and "oodold_empty" in h1a["evals"]:
        vn = view(h1a["evals"]["ood_empty"], "novel")
        vo = view(h1a["evals"]["oodold_empty"], "older_clean")
        vp = {"y": np.concatenate([vn["y"], vo["y"]]), "p": np.concatenate([vn["p"], vo["p"]]),
              "pb": np.concatenate([vn["pb"], vo["pb"]]),
              "g": np.concatenate([np.char.add("novel:", vn["g"].astype(str)), np.char.add("older:", vo["g"].astype(str))]),
              "partner": np.concatenate([vn["partner"], vo["partner"]]), "dbstate": None}
        pooled = within_stat(vp, boot)
    if pooled is None:
        d["H1-pooled"] = entry("within-drug AUROC", "Novel + Older-clean", decision="pending (0 of 5 seeds)")
    else:
        ok = ok_old and ok_nov
        if not ok:
            dec = msg_old if not ok_old else msg_nov
        else:
            dec = "descriptive, secondary (no pre-registered decision rule)"
        d["H1-pooled"] = entry("within-drug AUROC", "Novel + Older-clean", pooled, p=pooled["p_tost"] if ok else None,
                               decision=dec, detail=f"secondary, outside the Holm family, n={pooled['n']}, "
                                                    f"{pooled['n_drugs']} drugs")

    sel = lambda rows, system: [x for x in rows if x["system"] == system and x["model"] == "biomedbert"
                                and x["split"] == "standard"]
    for hid, system, what in (("H2a", "b2sentence", "test-time masking of the sentence-trained model"),
                              ("H2b", "b2masked", "masked-trained model")):
        ms, sw = sel(masks, system), sel(swaps, system)
        seeds = sorted({x["seed"] for x in ms} & set(SEEDS))
        flips = {k: [x["flip_rate"] for x in sw if x["swap"] == k] for k in KINDS}
        if not ms or not all(flips.values()):
            d[hid] = entry("masked F1 ratio and flip rates", what,
                           decision=f"pending (0 of {len(SEEDS)} seeds)", detail=f"{system} biomedbert masked or swap results missing")
            continue
        ratio = float(np.nanmean([x["ratio"] for x in ms]))
        fl = {k: float(np.mean(v)) for k, v in flips.items()}
        if len(seeds) < len(SEEDS):
            dec = f"pending ({len(seeds)} of {len(SEEDS)} seeds)"
        elif ratio >= 0.90 and all(v < 0.10 for v in fl.values()):
            dec = "supported"
        elif ratio < 0.75 or any(v > 0.25 for v in fl.values()):
            dec = "falsified"
        else:
            dec = "inconclusive"
        detail = f"{system}, seeds {seeds}" + ("; provisional" if len(seeds) < len(SEEDS) else "")
        if hid == "H2b":
            detail += "; " + h2_spread(ms, sw)
        d[hid] = entry("masked F1 ratio and flip rates", what, value={"ratio": ratio, **fl}, decision=dec,
                       detail=detail)

    e3 = h3a["evals"].get("ood_swap_sentence") if h3a else None
    if e3 is None:
        d["H3"] = entry("AUROC", "OOD swap", decision="descriptive only", detail="no b2sentence ood_swap_sentence cell")
    else:
        dr = boot_auroc(e3["y"], e3["p"], e3["g"], None, boot)
        r = {"auroc_within": auroc(e3["y"], e3["p"]), "lo95": interval(dr)[0], "hi95": interval(dr)[1],
             "lo90": float(np.percentile(dr, 5)), "hi90": float(np.percentile(dr, 95)),
             "upper95_one_sided": float(np.percentile(dr, 95))}
        d["H3"] = entry("pooled AUROC", "OOD swap", r, decision="descriptive only",
                        detail=f"b2sentence, seeds {seeds_present(h3a, 'ood_swap_sentence')}, no p-value, outside the Holm family")

    if older is None or novel is None or diff is None:
        d["H4"] = entry("Older-clean minus Novel within-drug AUROC", "cohort comparison",
                        decision=msg_old if not ok_old else msg_nov, detail="a cohort cell is missing")
    else:
        if not (ok_old and ok_nov):
            dec = msg_old if not ok_old else msg_nov
        elif adj["H4"] < 0.05 and older["lo95"] <= HI:
            dec = "supported"
        elif older["lo95"] > HI and novel["upper95_one_sided"] <= HI:
            dec = "falsified"
        else:
            dec = "inconclusive"
        d["H4"] = {"statistic": "Older-clean minus Novel within-drug AUROC", "cohort": "cohort comparison",
                   "value": float(older["auroc_within"] - novel["auroc_within"]),
                   "interval": [float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
                   "interval90": [float(np.percentile(diff, 5)), float(np.percentile(diff, 95))],
                   "upper95_one_sided": float(np.percentile(diff, 95)),
                   "p_tost": ps["H4"], "p_holm": adj["H4"] if ps["H4"] is not None else None, "decision": dec,
                   "detail": f"Older-clean {_fmt(older['auroc_within'])} vs Novel {_fmt(novel['auroc_within'])}; "
                             f"equivalence of the difference within +/-{DIFF_MARGIN:.2f}"}

    ds5 = h5a["evals"].get("ood") if h5a else None
    if ds5 is None:
        d["H5"] = entry("AUROC and MCC", "Novel", decision="pending (0 of 5 seeds)", detail="no contaminated retrieval cell")
    else:
        dr = boot_auroc(ds5["y"], ds5["p"], ds5["g"], None, boot)
        a5, mcc = auroc(ds5["y"], ds5["p"]), extended(ds5["y"], ds5["pb"])["mcc"]
        ok5, msg5 = gate(h5a, "ood")
        r = {"auroc_within": a5, "lo95": interval(dr)[0], "hi95": interval(dr)[1], "lo90": float(np.percentile(dr, 5)),
             "hi90": float(np.percentile(dr, 95)), "upper95_one_sided": float(np.percentile(dr, 95))}
        good = a5 >= 0.75 and mcc >= 0.30
        d["H5"] = entry("AUROC and MCC", "Novel", r, value=[a5, mcc],
                        decision=("supported" if good else "falsified") if ok5 else msg5,
                        detail=("below either threshold: null results uninterpretable" if not good else "") +
                               ("" if ok5 else "; provisional"))

    if krag is None:
        d["H6"] = entry("within-drug AUROC", "Novel", decision=msg_krag, detail="no hybrid k5 c400 retrieval cell")
    else:
        dec = decide_equivalence(krag, adj["H6"]) if ok_krag else msg_krag
        d["H6"] = entry("within-drug AUROC", "Novel", krag, p=krag["p_tost"] if ok_krag else None,
                        p_holm=adj["H6"] if ok_krag else None, decision=dec,
                        detail=f"krag hybrid k5 c400, seeds {seeds_present(h6a, 'ood')}, upper95 one-sided "
                               f"{_fmt(krag.get('upper95_one_sided'))}" + ("" if ok_krag else "; provisional estimate"))
    sens = ood_stat(cache, boot, h1k, h1a, "oodold_empty", "older_clean_sensitivity")
    if sens is None:
        d["H1-sensitivity"] = entry("within-drug AUROC", "Older-clean sensitivity", decision=msg_old,
                                    detail="no b2mixed oodold_empty cell")
    else:
        d["H1-sensitivity"] = entry("within-drug AUROC", "Older-clean sensitivity", sens,
                                    p=sens["p_tost"] if ok_old else None,
                                    decision="sensitivity, not preregistered (no decision rule)" if ok_old else msg_old,
                                    detail=f"b2mixed names only, Older-clean without {', '.join(OLDER_SENSITIVITY_DRUGS)} "
                                           f"(SemEval vocabulary drugs the filter missed), n={sens['n']}, "
                                           f"{sens['n_drugs']} drugs, outside the Holm family")
    order = ["H1", "H1-novel", "H1-pooled", "H1-sensitivity", "H2a", "H2b", "H3", "H4", "H5", "H6"]
    return {h: d[h] for h in order}


def cohort_rows(aggs, boot, cache):
    rows = []
    for gk, a in aggs.items():
        for key in PRIMARY_KEYS:
            if key not in a["evals"]:
                continue
            kind = a["evals"][key]["kind"]
            ok, msg = gate(a, key)
            for cohort, ckind in COHORTS:
                if ckind != kind:
                    continue
                for tier in ("A", "B"):
                    r = ood_stat(cache, boot, gk, a, key, cohort, tier)
                    row = {"group": label(gk), "key": key, "cohort": cohort, "tier": tier,
                           "n_seeds": len(seeds_present(a, key)), "seed_gate": "complete" if ok else msg}
                    if r is None:
                        row["status"] = "not available"
                    else:
                        row.update({k: v for k, v in r.items() if k not in ("draws", "p_tost", "mcc")})
                        row["p_tost"] = r["p_tost"]
                        row["status"] = "ok"
                    rows.append(row)
    return rows


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if math.isnan(o) or math.isinf(o) else round(float(o), 6)
    if isinstance(o, np.integer):
        return int(o)
    return o


POOLED_CI_COLUMNS = {"auroc_lo": "auroc_pooled_lo95", "auroc_hi": "auroc_pooled_hi95",
                     "auroc2_lo": "auroc_pooled2_lo95", "auroc2_hi": "auroc_pooled2_hi95"}


def pooled_ci_rows(rows):
    return [{POOLED_CI_COLUMNS.get(k, k): v for k, v in r.items()} for r in rows]


def md_table(rows, cols):
    if not rows:
        return "none\n"
    fmt = lambda v: "NA" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
    head = "| " + " | ".join(cols) + " |\n| " + " | ".join("---" for _ in cols) + " |\n"
    return head + "".join("| " + " | ".join(fmt(r.get(c)) for c in cols) + " |\n" for r in rows)


def decisions_md(dec, cohorts=None):
    rows = []
    for h, r in dec.items():
        v = r["value"]
        v = ", ".join(f"{k}={x:.3f}" for k, x in v.items()) if isinstance(v, dict) else (
            ", ".join(_fmt(x) for x in v) if isinstance(v, list) else _fmt(v))
        iv = lambda x: "NA" if x is None else f"[{_fmt(x[0])}, {_fmt(x[1])}]"
        rows.append({"id": h, "cohort": r["cohort"], "statistic": r["statistic"], "value": v,
                     "ci90": iv(r["interval90"]), "ci95": iv(r["interval"]), "upper95": _fmt(r["upper95_one_sided"]),
                     "p_tost": _fmt(r["p_tost"]), "p_holm": _fmt(r["p_holm"]), "decision": r["decision"],
                     "detail": r["detail"]})
    txt = ("# Preregistered decisions\n\n" + md_table(rows, ["id", "cohort", "statistic", "value", "ci90", "ci95",
                                                              "upper95", "p_tost", "p_holm", "decision", "detail"]) +
           "\nOOD hypotheses use the within-drug AUROC with two-way cluster bootstrap intervals over OOD drugs and "
           "partners. A decision needs all five seeds (42, 1, 2, 3, 4); otherwise it is pending and the estimate is "
           "provisional. Older-clean is primary for H1; Novel is an estimate with a one-sided 95% upper bound. "
           "The Holm family is H1, H4 and H6; pending tests count as p = 1. H2a is test-time masking of the "
           "sentence-trained model, H2b the masked-trained model; neither is preferred. H3 is descriptive. "
           "H1-novel and H1-pooled are secondary rows. H1-sensitivity is a sensitivity analysis, not preregistered: "
           "Older-clean without five SemEval-vocabulary drugs the filter missed.\n")
    if cohorts is not None:
        keep = [r for r in cohorts if r["key"] in ("ood_empty", "oodold_empty", "ood") and r["group"] in (
            "b2mixed/biomedbert", "krag/biomedbert/hybrid-k5-c400")]
        cols = ["group", "key", "cohort", "tier", "status", "n_seeds", "n", "n_drugs", "n_drugs_contributing", "auroc_within", "auroc_pooled",
                "lo90", "hi90", "lo95", "hi95", "upper95_one_sided", "neg_disagreement_rate",
                "expected_observed_if_true_070"]
        txt += "\n## Label tiers for the primary systems\n\n" + md_table(keep, cols)
    return txt


def evaluate(preds_dir, out_dir, truth, boot=1000, baselines=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = load_jobs(preds_dir, truth)
    aggs = aggregate(jobs)
    swaps, masks = swap_rows(jobs), masking_rows(jobs)
    cache = {}
    cohorts = cohort_rows(aggs, boot, cache)
    t = {"per_job": per_job_rows(jobs, boot), "seeds": seed_rows(aggs, boot, prior_aurocs(baselines)),
         "baselines": baseline_rows(baselines), "swap": swaps, "masking": masks,
         "disjoint": disjoint_rows(jobs), "grid": grid_rows(aggs, boot, truth.test_sid), "ood_cohorts": cohorts,
         "decisions": decide(aggs, swaps, masks, boot, cache)}
    t = clean(t)
    (out_dir / "tables.json").write_text(json.dumps(t, indent=1))
    (out_dir / "decisions.json").write_text(json.dumps(t["decisions"], indent=1))
    metric = ["n", "prevalence", "auroc", "auprc", "f1", "mcc", "balanced_accuracy", "tp", "fp", "fn", "tn"]
    ci = ["auroc_lo", "auroc_hi", "auroc2_lo", "auroc2_hi"]
    pooled_ci = list(POOLED_CI_COLUMNS.values())
    md = "# Revision results\n\n"
    for title, name, cols in (
            ("Per job", "per_job", ["job", "key"] + metric + ["auroc_within"] + pooled_ci),
            ("Seed aggregated", "seeds", ["group", "key", "n_seeds", "seed_auroc_mean", "seed_auroc_sd"] + metric +
             ["auroc_within"] + pooled_ci + ["partner_prior_auroc", "beats_partner_prior"]),
            ("OOD cohorts and label tiers (within-drug AUROC, two-way cluster bootstrap)", "ood_cohorts",
             ["group", "key", "cohort", "tier", "status", "seed_gate", "n", "n_drugs", "n_drugs_contributing", "auroc_within", "auroc_pooled",
              "lo90", "hi90", "lo95", "hi95", "upper95_one_sided", "p_tost", "neg_disagreement_rate",
              "expected_observed_if_true_070"]),
            ("CPU baselines (partner_frequency_prior is the reference a model must beat)", "baselines",
             ["set", "baseline"] + metric + ci),
            ("Name swap", "swap", ["job", "swap", "n", "flip_rate", "mean_abs_dp"]),
            ("Masking ratio", "masking", ["job", "f1_masked", "f1_sentence", "ratio"]),
            ("Drug disjoint", "disjoint", ["job", "key", "subset"] + metric),
            ("Input format by novelty (lo, hi: pair bootstrap on SemEval, drug bootstrap on Novel; lo_clustered, "
             "hi_clustered: clustered by sentence on SemEval, two-way by drug and partner on Novel)", "grid",
             ["group", "format", "novelty", "n", "auroc", "lo", "hi", "lo_clustered", "hi_clustered"])):
        rows = pooled_ci_rows(t[name]) if name in ("per_job", "seeds") else t[name]
        md += f"## {title}\n\n" + md_table(rows, cols) + "\n"
    (out_dir / "tables.md").write_text(md)
    (out_dir / "decisions.md").write_text(decisions_md(t["decisions"], t["ood_cohorts"]))
    return t


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--out", default=str(CORRECTED / "revision"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--baselines", default=str(CORRECTED / "baselines.json"))
    ap.add_argument("--allow-missing-drugbank", action="store_true")
    a = ap.parse_args(argv)
    t = evaluate(a.preds, a.out, load_truth(allow_missing_drugbank=a.allow_missing_drugbank), a.boot,
                 load_baselines(a.baselines))
    print(decisions_md(t["decisions"], t["ood_cohorts"]))


if __name__ == "__main__":
    main()
