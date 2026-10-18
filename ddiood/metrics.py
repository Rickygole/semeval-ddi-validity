import numpy as np
from sklearn.metrics import f1_score


def to_binary(preds):
    return [0 if int(p) == 0 else 1 for p in preds]


def binary_f1(y, preds):
    return float(f1_score(to_binary(y), to_binary(preds), zero_division=0))


def macro_f1(y, preds, n_classes=5):
    return float(f1_score(y, preds, labels=list(range(n_classes)), average="macro", zero_division=0))


def per_class_f1(y, preds, labels):
    s = f1_score(y, preds, labels=list(range(len(labels))), average=None, zero_division=0)
    return {name: round(float(v), 4) for name, v in zip(labels, s)}


def confusion(y, preds):
    y, p = np.array(to_binary(y)), np.array(to_binary(preds))
    tp = int(((y == 1) & (p == 1)).sum())
    fp = int(((y == 0) & (p == 1)).sum())
    fn = int(((y == 1) & (p == 0)).sum())
    tn = int(((y == 0) & (p == 0)).sum())
    return tp, fp, fn, tn


def extended(y, preds):
    tp, fp, fn, tn = confusion(y, preds)
    return {
        "binary_f1": binary_f1(y, preds),
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "specificity": tn / (tn + fp) if tn + fp else 0.0,
        "balanced_accuracy": 0.5 * ((tp / (tp + fn) if tp + fn else 0.0) + (tn / (tn + fp) if tn + fp else 0.0)),
        "mcc": _mcc(tp, fp, fn, tn),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def _mcc(tp, fp, fn, tn):
    d = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    return (tp * tn - fp * fn) / d if d else 0.0


def _summary(stats):
    return {"mean": round(float(np.mean(stats)), 4),
            "lower": round(float(np.percentile(stats, 2.5)), 4),
            "upper": round(float(np.percentile(stats, 97.5)), 4)}


def bootstrap_f1(y, preds, n=1000, seed=42):
    y, p = np.array(to_binary(y)), np.array(to_binary(preds))
    np.random.seed(seed)
    stats = []
    for _ in range(n):
        idx = np.random.randint(0, len(y), len(y))
        stats.append(f1_score(y[idx], p[idx], zero_division=0))
    return _summary(stats)


def bootstrap_drop(y_id, p_id, y_ood, p_ood, n=1000, seed=42):
    a, pa = np.array(to_binary(y_id)), np.array(to_binary(p_id))
    b, pb = np.array(to_binary(y_ood)), np.array(to_binary(p_ood))
    np.random.seed(seed)
    stats = []
    for _ in range(n):
        i = np.random.randint(0, len(a), len(a))
        j = np.random.randint(0, len(b), len(b))
        stats.append(f1_score(a[i], pa[i], zero_division=0) - f1_score(b[j], pb[j], zero_division=0))
    return _summary(stats)


def cluster_bootstrap_f1(y, preds, groups, n=1000, seed=42):
    y, p, g = np.array(to_binary(y)), np.array(to_binary(preds)), np.array(groups)
    uniq = np.unique(g)
    members = {u: np.where(g == u)[0] for u in uniq}
    rng = np.random.RandomState(seed)
    stats = []
    for _ in range(n):
        pick = rng.choice(uniq, len(uniq), replace=True)
        idx = np.concatenate([members[u] for u in pick])
        stats.append(f1_score(y[idx], p[idx], zero_division=0))
    return _summary(stats)
