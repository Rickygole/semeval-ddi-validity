import numpy as np
from sklearn.metrics import average_precision_score

from .stats import auroc


def all_positive_f1(prevalence):
    return 2 * prevalence / (1 + prevalence) if prevalence else 0.0


def binary_confusion(y, pb):
    y, pb = np.asarray(y).astype(int), np.asarray(pb).astype(int)
    return {"tp": int(((y == 1) & (pb == 1)).sum()), "fp": int(((y == 0) & (pb == 1)).sum()),
            "fn": int(((y == 1) & (pb == 0)).sum()), "tn": int(((y == 0) & (pb == 0)).sum())}


def multiclass_confusion(y, pred, k=5):
    m = np.zeros((k, k), int)
    np.add.at(m, (np.asarray(y, int), np.asarray(pred, int)), 1)
    return m.tolist()


def _from_counts(tp, fp, fn, tn):
    tp, fp, fn, tn = (np.asarray(v, float) for v in (tp, fp, fn, tn))
    with np.errstate(divide="ignore", invalid="ignore"):
        rec = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        spec = np.where(tn + fp > 0, tn / (tn + fp), 0.0)
        f1 = np.where(2 * tp + fp + fn > 0, 2 * tp / (2 * tp + fp + fn), 0.0)
        d = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = np.where(d > 0, (tp * tn - fp * fn) / np.where(d > 0, d, 1), 0.0)
    return {"f1": f1, "mcc": mcc, "balanced_accuracy": 0.5 * (rec + spec)}


def thresholded(y, pb):
    c = binary_confusion(y, pb)
    return {k: float(v) for k, v in _from_counts(c["tp"], c["fp"], c["fn"], c["tn"]).items()}


def cluster_weights(groups, n, seed):
    gi = np.unique(np.asarray(groups), return_inverse=True)[1].ravel()
    G = gi.max() + 1
    rng = np.random.RandomState(seed)
    return np.stack([np.bincount(rng.randint(0, G, G), minlength=G)[gi] for _ in range(n)]).astype(float)


def bootstrap_thresholded(y, pb, groups=None, n=1000, seed=42):
    y, pb = np.asarray(y).astype(int), np.asarray(pb).astype(int)
    groups = np.arange(len(y)) if groups is None else groups
    W = cluster_weights(groups, n, seed)
    tp = W @ ((y == 1) & (pb == 1))
    fp = W @ ((y == 0) & (pb == 1))
    fn = W @ ((y == 1) & (pb == 0))
    tn = W @ ((y == 0) & (pb == 0))
    return _from_counts(tp, fp, fn, tn)


def _auprc(y, p):
    y = np.asarray(y)
    return float(average_precision_score(y, p)) if 0 < y.sum() < len(y) else float("nan")


def reference_row(y, p, pb, groups=None, boot=1000, seed=42):
    y = np.asarray(y).astype(int)
    prev = float(y.mean()) if len(y) else float("nan")
    t = thresholded(y, pb)
    ap = _auprc(y, p) if p is not None else float("nan")
    c = binary_confusion(y, pb)
    row = {"n": int(len(y)), "n_pos": int(y.sum()), "prevalence": prev, "f1": t["f1"],
           "precision": c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0,
           "recall": c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0,
           "specificity": c["tn"] / (c["tn"] + c["fp"]) if c["tn"] + c["fp"] else 0.0,
           "f1_all_positive": all_positive_f1(prev), "f1_minus_all_positive": t["f1"] - all_positive_f1(prev),
           "mcc": t["mcc"], "balanced_accuracy": t["balanced_accuracy"],
           "auroc": auroc(y, p) if p is not None else float("nan"), "auprc": ap,
           "auprc_minus_prevalence": ap - prev, "auprc_over_prevalence": ap / prev if prev else float("nan"), **c}
    if boot:
        d = bootstrap_thresholded(y, pb, groups, boot, seed)
        for k in ("f1", "mcc", "balanced_accuracy"):
            row[f"{k}_lo"], row[f"{k}_hi"] = float(np.percentile(d[k], 2.5)), float(np.percentile(d[k], 97.5))
    return row


def matched_counts(n_pos, n_neg, target):
    prev = n_pos / (n_pos + n_neg)
    if target >= prev:
        return n_pos, int(round(n_pos * (1 - target) / target))
    return int(round(n_neg * target / (1 - target))), n_neg


def matched_indices(y, target, rng):
    y = np.asarray(y).astype(int)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    kp, kn = matched_counts(len(pos), len(neg), target)
    pick = np.concatenate([rng.choice(pos, kp, replace=False), rng.choice(neg, kn, replace=False)])
    return np.sort(pick)


def _metrics(y, p, pb):
    t = thresholded(y, pb)
    prev = float(np.mean(y))
    out = {"prevalence": prev, "f1": t["f1"], "f1_all_positive": all_positive_f1(prev), "mcc": t["mcc"],
           "balanced_accuracy": t["balanced_accuracy"]}
    if p is not None:
        out["auroc"] = auroc(y, p)
        out["auprc"] = _auprc(y, p)
    return out


def prevalence_matched(y, p, pb, target, n=1000, seed=42):
    y, pb = np.asarray(y).astype(int), np.asarray(pb).astype(int)
    p = None if p is None else np.asarray(p, float)
    rng = np.random.RandomState(seed)
    frozen = matched_indices(y, target, rng)
    sub = lambda a, i: None if a is None else a[i]
    out = {"target_prevalence": float(target), "n": int(len(frozen)), "n_pos": int(y[frozen].sum()),
           "frozen": _metrics(y[frozen], sub(p, frozen), pb[frozen])}
    draws = {}
    for _ in range(n):
        i = matched_indices(y, target, rng)
        for k, v in _metrics(y[i], sub(p, i), pb[i]).items():
            draws.setdefault(k, []).append(v)
    out["resampled"] = {k: {"mean": float(np.mean(v)), "lo": float(np.percentile(v, 2.5)),
                            "hi": float(np.percentile(v, 97.5))} for k, v in draws.items()}
    out["n_resamples"] = int(n)
    return out
