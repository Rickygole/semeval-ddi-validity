import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import evaluate2 as ev
from ddiood import stats

PREDS = ROOT / "results" / "revision" / "preds"
OUT = ROOT / "results" / "revision" / "amend7" / "cpu"
DBDIR = ROOT / "artifacts" / "ood"
SEEDS = (42, 1, 2, 3, 4)
BOOT_SEED = {"novel": 1042, "older_clean": 42}


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def seed_mean(system, key, preds=PREDS, seeds=SEEDS):
    ps = []
    for s in seeds:
        f = Path(preds) / f"{system}-s{s}.json"
        if f.exists():
            ps.append(np.asarray(json.loads(f.read_text())["eval"][key]["p"], float))
    if not ps:
        return None, 0
    return np.mean(ps, axis=0), len(ps)


def single(job, key, preds=PREDS):
    f = Path(preds) / f"{job}.json"
    if not f.exists():
        return None
    return np.asarray(json.loads(f.read_text())["eval"][key]["p"], float)


def drugbank_score(truth, tag):
    name = "drugbank_validation.csv" if tag == "ood" else "drugbank_validation_old.csv"
    db = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in read_csv(DBDIR / name)}
    return np.asarray([1.0 if db.get((p["drug_a"], p["drug_b"])) == "positive" else 0.0
                       for p in truth.sets[tag]["pairs"]])


def cohort_mask(truth, cohort, tier="A"):
    tag = "ood" if cohort == "novel" else "oodold"
    s = truth.sets[tag]
    m = np.ones(len(s["y"]), bool)
    if cohort == "older_clean":
        m &= s["clean"]
    if tier == "B":
        m &= s["dbstate"] == 1
    return tag, m


def cohort_arrays(truth, cohort, tier="A"):
    tag, m = cohort_mask(truth, cohort, tier)
    s = truth.sets[tag]
    return {"tag": tag, "mask": m, "y": np.asarray(s["y"])[m], "g": np.asarray(s["g"])[m],
            "q": np.asarray(s["partner"])[m], "dbstate": None if s["dbstate"] is None else s["dbstate"][m]}


def fast_within_auroc(y, s, strata):
    y = np.asarray(y)
    st = stats._codes(strata)
    dense = np.unique(np.asarray(s, float), return_inverse=True)[1].ravel()
    r = rankdata(st.astype(np.int64) * (dense.max() + 1) + dense)
    size = np.bincount(st)
    offset = (np.cumsum(size) - size)[st]
    npos = np.bincount(st, weights=y.astype(float), minlength=len(size))
    nneg = size - npos
    u = np.bincount(st, weights=(r - offset) * y, minlength=len(size)) - npos * (npos + 1) / 2
    total = float((npos * nneg).sum())
    return float(u.sum() / total) if total else float("nan")


def paired_draws(y, scores, g1, g2, n=1000, seed=42):
    y = np.asarray(y)
    scores = [np.asarray(s, float) for s in scores]
    c1, c2 = stats._codes(g1), stats._codes(g2)
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = stats._expand(rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        copy = r // w2[c2][idx]
        strata = c1[idx] * (w1.max() + 1) + copy
        v = [fast_within_auroc(y[idx], s[idx], strata) for s in scores]
        if not any(np.isnan(v)):
            out.append(v)
    return np.asarray(out).T if out else np.zeros((len(scores), 0))


def summarize_draws(est, d):
    d = np.asarray(d)
    if not len(d):
        return {"value": est, "ci95": None, "ci90": None, "n_draws": 0}
    return {"value": est, "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "ci90": [float(np.percentile(d, 5)), float(np.percentile(d, 95))], "n_draws": int(len(d))}


def within(y, s, g, q, n=1000, seed=42):
    d = paired_draws(y, [s], g, q, n, seed)[0]
    return summarize_draws(stats.stratified_auroc(y, s, g), d)


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def write(name, obj, md):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1))
    (OUT / f"{name}.md").write_text(md)


def f3(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "NA"
    return f"{v:.3f}"


def ci(c):
    return "NA" if not c else f"[{f3(c[0])}, {f3(c[1])}]"
