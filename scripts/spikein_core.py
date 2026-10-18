import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev
from ddiood import stats

OUT = ROOT / "results" / "revision" / "spikein"
CRITERIA = OUT / "criteria.json"
LO, HI = 0.40, 0.60
KAPPA_MARGIN = 0.25
SIGMA = 0.1
W_GRID = np.round(np.linspace(0, 1, 101), 2)
OBSERVED_P = {"H4": 0.3387, "H6": 0.1019}
BASE_ID = {"b2mixed": 1, "noise": 2}


def load_criteria():
    return json.loads(CRITERIA.read_text())


def codes(x):
    return np.unique(np.asarray(x), return_inverse=True)[1].ravel()


def two_way_indices(g, q, n, seed):
    c1, c2 = codes(g), codes(q)
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = stats._expand(rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        yield idx, c1[idx] * (w1.max() + 1) + r // w2[c2][idx]


def one_way_indices(g, n, seed):
    c1 = codes(g)
    k1 = c1.max() + 1
    rng = np.random.RandomState(seed)
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        rep = w1[c1]
        idx = stats._expand(rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        yield idx, c1[idx] * (w1.max() + 1) + r


def dense(scores):
    scores = np.atleast_2d(np.asarray(scores, float))
    return np.vstack([np.unique(s, return_inverse=True)[1].ravel() for s in scores]).astype(np.int64)


def batched_within(y, dranks, strata):
    y = np.asarray(y, float)
    st = codes(strata).astype(np.int64)
    n = len(y)
    size = np.bincount(st)
    npos = np.bincount(st, weights=y, minlength=len(size))
    total = float((npos * (size - npos)).sum())
    if total == 0:
        return np.full(len(dranks), np.nan)
    key = st[None, :] * (int(dranks.max()) + 2) + dranks
    order = np.argsort(key, axis=1, kind="stable")
    ks = np.take_along_axis(key, order, axis=1)
    ys = y[order]
    pos = np.broadcast_to(np.arange(n), ks.shape)
    newg = np.ones(ks.shape, bool)
    newg[:, 1:] = ks[:, 1:] != ks[:, :-1]
    start = np.maximum.accumulate(np.where(newg, pos, 0), axis=1)
    endg = np.ones(ks.shape, bool)
    endg[:, :-1] = ks[:, :-1] != ks[:, 1:]
    end = np.flip(np.minimum.accumulate(np.flip(np.where(endg, pos, n), axis=1), axis=1), axis=1)
    mid = (start + end) / 2.0 + 1.0
    offset = np.concatenate([[0], np.cumsum(size)[:-1]])
    off_sorted = offset[np.sort(st)]
    u = ((mid - off_sorted[None, :]) * ys).sum(axis=1) - float((npos * (npos + 1) / 2).sum())
    return u / total


def point_within(y, scores, g):
    return batched_within(y, dense(scores), g)


def draws(y, scores, g, q=None, n=300, seed=42, chunk=600):
    y = np.asarray(y)
    dr = dense(scores)
    gen = one_way_indices(g, n, seed) if q is None else two_way_indices(g, q, n, seed)
    out = []
    for idx, strata in gen:
        col = np.concatenate([batched_within(y[idx], dr[i:i + chunk][:, idx], strata)
                              for i in range(0, len(dr), chunk)])
        out.append(col)
    a = np.asarray(out).T
    ok = ~np.isnan(a).any(axis=0)
    return a[:, ok]


def tost_p_rows(d):
    n = d.shape[1]
    return np.maximum((1 + (d <= LO).sum(1)) / (n + 1), (1 + (d >= HI).sum(1)) / (n + 1))


def auroc_decisions(d):
    lo90, hi90 = np.percentile(d, 5, axis=1), np.percentile(d, 95, axis=1)
    lo95, hi95 = np.percentile(d, 2.5, axis=1), np.percentile(d, 97.5, axis=1)
    eq = (lo90 > LO) & (hi90 < HI)
    fal = lo95 > HI
    dec = np.where(fal, "falsified", np.where(eq, "equivalent", "inconclusive"))
    p = tost_p_rows(d)
    holm = np.array([holm_decision(pi, l) for pi, l in zip(p, lo95)])
    return {"decision": dec, "holm": holm, "p_tost": p, "lo90": lo90, "hi90": hi90, "lo95": lo95, "hi95": hi95,
            "detected": lo95 > 0.5}


def holm_decision(p, lo95):
    adj = ev.holm({"H1": float(p), **OBSERVED_P})
    d = ev.decide_equivalence({"lo95": float(lo95)}, adj["H1"])
    return {"supported": "equivalent"}.get(d, d)


def kappa_decisions(d, ddb):
    k = (d - 0.5) / (ddb[None, :] - 0.5)
    lo, hi = np.percentile(k, 2.5, axis=1), np.percentile(k, 97.5, axis=1)
    dec = np.where(lo > KAPPA_MARGIN, "falsified", np.where(hi <= KAPPA_MARGIN, "equivalent", "inconclusive"))
    return {"decision": dec, "lo95": lo, "hi95": hi}


def norm_rank(x):
    return rankdata(x) / len(x)


def blend(w, r_db, r_base, z):
    return w * r_db + (1 - w) * (r_base + SIGMA * z)


def rep_components(rng, db, base_rank, base):
    n = len(db)
    r_db = norm_rank(np.asarray(db, float) + 0.5 * rng.random(n))
    r_base = norm_rank(rng.standard_normal(n)) if base == "noise" else base_rank
    return r_db, r_base, rng.standard_normal(n)


def calibrate(y, g, db, base_scores, base, cohort_id, targets, n_cal=100):
    a_db = float(stats.stratified_auroc(y, db, g))
    base_rank = None if base_scores is None else norm_rank(base_scores)
    ks = np.zeros((n_cal, len(W_GRID)))
    for j in range(n_cal):
        rng = np.random.default_rng([BASE_ID[base], cohort_id, 999, j, 1])
        r_db, r_base, z = rep_components(rng, db, base_rank, base)
        s = np.vstack([blend(w, r_db, r_base, z) for w in W_GRID])
        ks[j] = (point_within(y, s, g) - 0.5) / (a_db - 0.5)
    curve = np.maximum.accumulate(ks.mean(0))
    se = ks.std(0, ddof=1) / np.sqrt(n_cal)
    tol_lo, tol_hi = 3 * se[0], 3 * se[-1]
    ws, clamped = [], []
    for t in targets:
        if t < curve[0] - tol_lo or t > curve[-1] + tol_hi:
            ws.append(None)
        elif t < curve[0]:
            ws.append(0.0)
            clamped.append(t)
        elif t > curve[-1]:
            ws.append(1.0)
            clamped.append(t)
        else:
            ws.append(float(np.interp(t, curve, W_GRID)))
    return {"a_db": a_db, "curve": curve.tolist(), "w": ws, "clamped": clamped,
            "endpoint_se": [float(se[0]), float(se[-1])]}


def make_scores(db, base_scores, base, cohort_id, grid_index, w, reps):
    base_rank = None if base_scores is None else norm_rank(base_scores)
    out = []
    for r in range(reps):
        rng = np.random.default_rng([BASE_ID[base], cohort_id, grid_index, r, 0])
        out.append(blend(w, *rep_components(rng, db, base_rank, base)))
    return np.vstack(out)


def crossing_up(grid, p, level):
    grid, p = np.asarray(grid, float), np.asarray(p, float)
    hit = np.where(p >= level)[0]
    if not len(hit):
        return None, None
    i = int(hit[0])
    if i == 0:
        return float(grid[0]), float(grid[0])
    x = grid[i - 1] + (level - p[i - 1]) * (grid[i] - grid[i - 1]) / (p[i] - p[i - 1])
    return float(grid[i]), float(x)


def crossing_down(grid, p, level):
    grid, p = np.asarray(grid, float), np.asarray(p, float)
    hit = np.where(p >= level)[0]
    if not len(hit):
        return None, None
    i = int(hit[-1])
    if i == len(grid) - 1:
        return float(grid[i]), float(grid[i])
    x = grid[i] + (p[i] - level) * (grid[i + 1] - grid[i]) / (p[i] - p[i + 1])
    return float(grid[i]), float(x)


def shares(dec):
    dec = np.asarray(dec)
    return {k: float(np.mean(dec == k)) for k in ("falsified", "equivalent", "inconclusive")}


def evaluate_scores(y, g, q, s, db, seed, n_boot):
    d2 = draws(y, np.vstack([s, db[None, :]]), g, q, n_boot, seed)
    d1 = draws(y, s, g, None, n_boot, seed)
    two, ddb = d2[:-1], d2[-1]
    a = auroc_decisions(two)
    k = kappa_decisions(two, ddb)
    o = auroc_decisions(d1)
    est = point_within(y, s, g)
    a_db = float(stats.stratified_auroc(y, db, g))
    return {"est": est, "kappa_est": (est - 0.5) / (a_db - 0.5), "a_db": a_db, "two": a, "kappa": k, "one": o,
            "n_draws": int(two.shape[1]), "n_draws_one": int(d1.shape[1])}


def summarize(r):
    return {"realised_auroc_mean": float(np.mean(r["est"])), "realised_auroc_sd": float(np.std(r["est"], ddof=1)),
            "realised_kappa_mean": float(np.mean(r["kappa_est"])), "realised_kappa_sd": float(np.std(r["kappa_est"], ddof=1)),
            "mean_lo90": float(np.mean(r["two"]["lo90"])), "mean_hi90": float(np.mean(r["two"]["hi90"])),
            "mean_lo95": float(np.mean(r["two"]["lo95"])), "mean_hi95": float(np.mean(r["two"]["hi95"])),
            "mean_p_tost": float(np.mean(r["two"]["p_tost"])),
            "auroc_rule": shares(r["two"]["decision"]), "auroc_rule_holm": shares(r["two"]["holm"]),
            "auroc_rule_one_way": shares(r["one"]["decision"]), "kappa_rule": shares(r["kappa"]["decision"]),
            "mean_kappa_lo95": float(np.mean(r["kappa"]["lo95"])), "mean_kappa_hi95": float(np.mean(r["kappa"]["hi95"])),
            "p_detected": float(np.mean(r["two"]["detected"])), "p_detected_one_way": float(np.mean(r["one"]["detected"])),
            "n_draws": r["n_draws"], "n_draws_one_way": r["n_draws_one"]}
