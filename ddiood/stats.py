import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

TOST_MARGIN = (0.40, 0.60)


def auroc(y, s):
    y = np.asarray(y)
    if y.min() == y.max():
        return float("nan")
    return float(roc_auc_score(y, s))


def auprc(y, s):
    y = np.asarray(y)
    if y.sum() == 0:
        return float("nan")
    return float(average_precision_score(y, s))


def prevalence(y):
    return float(np.mean(y))


def _codes(g):
    return np.unique(np.asarray(g), return_inverse=True)[1]


def _expand(w):
    return np.repeat(np.arange(len(w)), w)


def stratified_auroc(y, s, g=None):
    y, s = np.asarray(y), np.asarray(s, dtype=float)
    if g is None:
        return auroc(y, s)
    g = np.asarray(g)
    wins, total = 0.0, 0.0
    for k in np.unique(g):
        m = g == k
        pos, neg = s[m & (y == 1)], s[m & (y == 0)]
        if len(pos) == 0 or len(neg) == 0:
            continue
        diff = pos[:, None] - neg[None, :]
        wins += float((diff > 0).sum() + 0.5 * (diff == 0).sum())
        total += len(pos) * len(neg)
    return wins / total if total else float("nan")


def two_way_samples(metric, y, s, g1, g2, n=1000, seed=42, strat=None):
    y, s = np.asarray(y), np.asarray(s)
    c1, c2 = _codes(g1), _codes(g2)
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = _expand(rep)
        if len(idx) == 0:
            continue
        if strat is None:
            v = metric(y[idx], s[idx])
        else:
            r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
            copy = r // w2[c2][idx]
            v = metric(y[idx], s[idx], _codes(strat)[idx] * (w1.max() + 1) + copy)
        if not np.isnan(v):
            out.append(v)
    return np.array(out)


def one_way_samples(metric, y, s, g, n=1000, seed=42):
    y, s = np.asarray(y), np.asarray(s)
    c = _codes(g)
    k = c.max() + 1
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        w = np.bincount(rng.randint(0, k, k), minlength=k)
        idx = _expand(w[c])
        v = metric(y[idx], s[idx])
        if not np.isnan(v):
            out.append(v)
    return np.array(out)


def interval(samples, level=0.95):
    a = (1 - level) / 2 * 100
    return {"mean": float(np.mean(samples)), "lower": float(np.percentile(samples, a)),
            "upper": float(np.percentile(samples, 100 - a)), "n_valid": int(len(samples))}


def two_way_bootstrap(metric, y, s, g1, g2, n=1000, seed=42, level=0.95):
    return interval(two_way_samples(metric, y, s, g1, g2, n, seed), level)


def one_way_bootstrap(metric, y, s, g, n=1000, seed=42, level=0.95):
    return interval(one_way_samples(metric, y, s, g, n, seed), level)


def tost_decision(samples, margin=TOST_MARGIN, alpha=0.05):
    ci = interval(samples, 1 - 2 * alpha)
    lo, hi = margin
    return {"equivalent": bool(ci["lower"] > lo and ci["upper"] < hi), "lower90": ci["lower"],
            "upper90": ci["upper"], "margin": [lo, hi], "alpha": alpha}


def tost_auroc(y, s, g1, g2, n=1000, seed=42, margin=TOST_MARGIN, alpha=0.05):
    return tost_decision(two_way_samples(auroc, y, s, g1, g2, n, seed), margin, alpha)


def holm(pvals, alpha=0.05):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * p[i])
        adj[i] = min(1.0, run)
    return {"adjusted": adj.tolist(), "reject": (adj <= alpha).tolist()}


def seed_average(score_lists):
    return np.mean(np.vstack([np.asarray(s, dtype=float) for s in score_lists]), axis=0)


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    cats = np.unique(np.concatenate([a, b]))
    po = float(np.mean(a == b))
    pe = float(sum(np.mean(a == c) * np.mean(b == c) for c in cats))
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)
