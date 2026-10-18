import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev
from amend7_cpu_common import cohort_arrays, drugbank_score, logit, seed_mean, single

OUT = ROOT / "results" / "revision" / "post7"
CRITERIA = OUT / "criteria.json"
BOOT_SEED = {"novel": 1042, "older_clean": 42}
COHORTS = ("older_clean", "novel")
TIERS = ("A", "B")
LO, HI = 0.40, 0.60
STATUS = "post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision"


def require_criteria():
    if not CRITERIA.exists():
        raise SystemExit("results/revision/post7/criteria.json must be written before this analysis runs")
    return json.loads(CRITERIA.read_text())


def codes(x):
    return np.unique(np.asarray(x), return_inverse=True)[1].ravel()


def heaviside(diff):
    return (diff > 0).astype(float) + 0.5 * (diff == 0)


def within_design(y, g, q):
    y = np.asarray(y)
    gd, qd = codes(g), codes(q)
    I, J = [], []
    for d in range(gd.max() + 1):
        rows = np.where(gd == d)[0]
        pos, neg = rows[y[rows] == 1], rows[y[rows] == 0]
        if len(pos) and len(neg):
            I.append(np.repeat(pos, len(neg)))
            J.append(np.tile(neg, len(pos)))
    I = np.concatenate(I) if I else np.zeros(0, int)
    J = np.concatenate(J) if J else np.zeros(0, int)
    return {"kind": "within", "i": I, "j": J, "d": gd[I], "qi": qd[I], "qj": qd[J],
            "nd": int(gd.max() + 1), "nq": int(qd.max() + 1)}


def partner_design(y, g, q):
    y = np.asarray(y)
    gd, qd = codes(g), codes(q)
    I, J = [], []
    for p in range(qd.max() + 1):
        rows = np.where(qd == p)[0]
        pos, neg = rows[y[rows] == 1], rows[y[rows] == 0]
        if len(pos) and len(neg):
            I.append(np.repeat(pos, len(neg)))
            J.append(np.tile(neg, len(pos)))
    I = np.concatenate(I) if I else np.zeros(0, int)
    J = np.concatenate(J) if J else np.zeros(0, int)
    return {"kind": "partner", "i": I, "j": J, "p": qd[I], "di": gd[I], "dj": gd[J],
            "nd": int(gd.max() + 1), "nq": int(qd.max() + 1)}


def tetrad_design(y, g, q):
    y = np.asarray(y)
    gd, qd = codes(g), codes(q)
    cell = {(int(a), int(b)): i for i, (a, b) in enumerate(zip(gd, qd))}
    pos_by_drug = {}
    pos_by_partner = {}
    for i, (a, b) in enumerate(zip(gd, qd)):
        if y[i] == 1:
            pos_by_drug.setdefault(int(a), []).append(int(b))
            pos_by_partner.setdefault(int(b), []).append(int(a))
    seen = set()
    A, B, C, D = [], [], [], []
    for n2 in np.where(y == 0)[0]:
        d2, p1 = int(gd[n2]), int(qd[n2])
        for d1 in pos_by_partner.get(p1, ()):
            for p2 in pos_by_drug.get(d2, ()):
                n1 = cell.get((d1, p2))
                if n1 is None or y[n1] != 0 or d1 == d2 or p1 == p2:
                    continue
                key = frozenset([(d1, p1), (d2, p2)])
                if key in seen:
                    continue
                seen.add(key)
                A.append(cell[(d1, p1)])
                B.append(cell[(d2, p2)])
                C.append(n1)
                D.append(int(n2))
    A, B, C, D = (np.asarray(v, int) for v in (A, B, C, D))
    return {"kind": "tetrad", "a": A, "b": B, "c": C, "e": D, "d1": gd[A], "d2": gd[B], "p1": qd[A], "p2": qd[B],
            "nd": int(gd.max() + 1), "nq": int(qd.max() + 1)}


def comparisons(design, s):
    s = np.asarray(s, float)
    if design["kind"] == "tetrad":
        return heaviside(s[design["a"]] + s[design["b"]] - s[design["c"]] - s[design["e"]])
    return heaviside(s[design["i"]] - s[design["j"]])


def weight_matrix(design, W1, W2):
    k = design["kind"]
    if k == "within":
        return W1[:, design["d"]] * W2[:, design["qi"]] * W2[:, design["qj"]]
    if k == "partner":
        return W2[:, design["p"]] * W1[:, design["di"]] * W1[:, design["dj"]]
    return W1[:, design["d1"]] * W1[:, design["d2"]] * W2[:, design["p1"]] * W2[:, design["p2"]]


def estimate(design, s):
    h = comparisons(design, s)
    return float(h.mean()) if len(h) else float("nan")


def draws(design, H, W1, W2):
    H = np.atleast_2d(H)
    M = weight_matrix(design, W1, W2)
    den = M.sum(1)
    num = M @ H.T
    with np.errstate(invalid="ignore", divide="ignore"):
        v = num / den[:, None]
    return v.T, den > 0


def evaluate2_weights(nd, nq, n, seed):
    rng = np.random.RandomState(seed)
    W1 = np.empty((n, nd))
    W2 = np.empty((n, nq))
    for b in range(n):
        W1[b] = np.bincount(rng.randint(0, nd, nd), minlength=nd)
        W2[b] = np.bincount(rng.randint(0, nq, nq), minlength=nq)
    return W1, W2


def multinomial_weights(rng, k, n):
    return rng.multinomial(k, np.full(k, 1.0 / k), size=n).astype(float)


def scheme_weights(scheme, nd, nq, n, seed):
    if scheme == "two_way":
        return evaluate2_weights(nd, nq, n, seed)
    rng = np.random.RandomState(seed)
    if scheme == "one_way_drug":
        W1 = np.empty((n, nd))
        for b in range(n):
            W1[b] = np.bincount(rng.randint(0, nd, nd), minlength=nd)
        return W1, np.ones((n, nq))
    if scheme == "partner_only":
        W2 = np.empty((n, nq))
        for b in range(n):
            W2[b] = np.bincount(rng.randint(0, nq, nq), minlength=nq)
        return np.ones((n, nd)), W2
    raise ValueError(scheme)


def tost_p(d, lo=LO, hi=HI):
    d = np.asarray(d)
    if not len(d):
        return None
    n = len(d)
    return float(max((1 + (d <= lo).sum()) / (n + 1), (1 + (d >= hi).sum()) / (n + 1)))


def summarize(est, d, lo=LO, hi=HI):
    d = np.asarray(d)
    d = d[~np.isnan(d)]
    if not len(d):
        return {"value": est, "ci90": None, "ci95": None, "p_tost": None, "n_draws": 0}
    return {"value": est, "ci90": [float(np.percentile(d, 5)), float(np.percentile(d, 95))],
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_tost": tost_p(d, lo, hi), "n_draws": int(len(d))}


def systems(truth):
    out = {}
    for cohort, tag in (("older_clean", "oodold"), ("novel", "ood")):
        out[cohort] = {
            "DrugBank lookup": drugbank_score(truth, tag),
            "b2mixed": seed_mean("b2mixed-biomedbert", f"{tag}_empty")[0],
            "Qwen names only": single("llm-qwen-names", tag),
            "b1names": seed_mean("b1names-biomedbert", f"{tag}_names")[0],
            "b2sentence": seed_mean("b2sentence-biomedbert", f"{tag}_empty")[0],
        }
        if cohort == "novel":
            out[cohort]["krag"] = seed_mean("krag-hybrid-k5-c400-biomedbert", "ood")[0]
    return out


def additive_scale(name, p):
    return np.asarray(p, float) if name == "DrugBank lookup" else logit(p)


def cell(truth, cohort, tier):
    c = cohort_arrays(truth, cohort, tier)
    return c


def write(name, obj, md):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1) + "\n")
    (OUT / f"{name}.md").write_text(md)


def f3(v):
    if v is None or (isinstance(v, float) and v != v):
        return "NA"
    return f"{v:.3f}"


def ci(c):
    return "NA" if not c else f"[{f3(c[0])}, {f3(c[1])}]"
