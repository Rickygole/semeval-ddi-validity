import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import amend7_analysis as aa
from ddiood.amend7_pairs import read_csv
from ddiood.drugbank import strip_salt
from amend7_cpu_common import seed_mean, single
from post7_classshortcut_classes import OUT, classes, load_atc

CRITERIA = OUT / "criteria.json"
PREDS7 = ROOT / "runs" / "preds"
DEFS = ("atc4", "stem", "atc3")
CELLS = (("older_primary", "A"), ("older_primary", "B"), ("novel", "A"), ("novel", "B"))
SYSTEMS = ("E7c", "E7d", "E7e", "b2mixed", "Qwen names only")
PK_RE = re.compile(r"cyp|p-gp|p-glycoprotein|transporter|\bauc\b|\bc\s?max|exposure|clearance|metaboli", re.I)
PK_BROAD_RE = re.compile(PK_RE.pattern + r"|pharmacokinetic|concentration|bioavailab|absor|plasma level|serum level|\binducer", re.I)
RED_TEAM_ALIASES = {"teriflunomide": "leflunomide", "balsalazide disodium": "mesalamine",
                    "lisdexamfetamine dimesylate": "amphetamine"}
OWN_ALIASES = {"belatacept": "abatacept: belatacept is abatacept (CTLA4-Ig) with two amino acid substitutions"}
RED_TEAM_HIGH = ("adalimumab", "golimumab", "certolizumab pegol", "apixaban", "tapentadol", "trandolapril", "regorafenib")
RED_TEAM_LOW = ("avanafil", "axitinib", "cabozantinib", "teriflunomide", "rabeprazole")
TOPK = (1, 3, 5)


def require_criteria():
    if not CRITERIA.exists():
        raise SystemExit("results/revision/post7/classshortcut/criteria.json must be written before this analysis runs")
    return json.loads(CRITERIA.read_text())


def codes(x):
    return np.unique(np.asarray(x), return_inverse=True)[1].ravel()


class Graph:
    def __init__(self, rows):
        self.anchors = {r["drug_a"] for r in rows}
        self.drugs = self.anchors | {r["drug_b"] for r in rows}
        self.pos = defaultdict(set)
        self.any = defaultdict(set)
        for r in rows:
            a, b = r["drug_a"], r["drug_b"]
            self.any[a].add(b)
            self.any[b].add(a)
            if int(r["y"]) == 1:
                self.pos[a].add(b)
                self.pos[b].add(a)


def members(pool, atc, definition):
    mem = defaultdict(set)
    for t in pool:
        for lab in classes(t, atc, definition):
            mem[lab].add(t)
    return mem


def mates_of(d, mem, atc, definition):
    out = set()
    for lab in classes(d, atc, definition):
        out |= mem.get(lab, set())
    return out - {d}


def class_scores(g, q, graph, atc, definition, pool):
    mem = members(pool, atc, definition)
    share = np.zeros(len(g))
    cond = np.zeros(len(g))
    nm = np.zeros(len(g), int)
    for i, (d, x) in enumerate(zip(g, q)):
        mates = mates_of(d, mem, atc, definition)
        nm[i] = len(mates)
        if mates:
            k = sum(x in graph.pos[a] for a in mates)
            den = sum(x in graph.any[a] for a in mates)
            share[i] = k / len(mates)
            cond[i] = k / den if den else 0.0
    return share, cond, nm


def resamples(g, q, n, seed):
    c1, c2 = codes(g), codes(q)
    k1, k2 = c1.max() + 1, c2.max() + 1
    rng = np.random.RandomState(seed)
    for _ in range(n):
        w1 = np.bincount(rng.randint(0, k1, k1), minlength=k1)
        w2 = np.bincount(rng.randint(0, k2, k2), minlength=k2)
        rep = w1[c1] * w2[c2]
        idx = np.repeat(np.arange(len(rep)), rep)
        if len(idx) == 0:
            continue
        r = np.arange(len(idx)) - np.repeat(np.cumsum(rep) - rep, rep)
        copy = r // w2[c2][idx]
        yield idx, c1[idx] * (w1.max() + 1) + copy


def run_metrics(c, fns, n, seed):
    base = (np.arange(len(c["y"])), codes(c["g"]))
    point = {k: f(*base) for k, f in fns.items()}
    store = {k: [] for k in fns}
    for idx, st in resamples(c["g"], c["q"], n, seed):
        for k, f in fns.items():
            v = f(idx, st)
            if v == v:
                store[k].append(v)
    return {k: aa.summ(point[k], store[k]) if point[k] == point[k] else aa.summ(float("nan"), []) for k in fns}


def auc_fn(y, s, sub=None):
    y, s = np.asarray(y), np.asarray(s, float)

    def f(idx, st):
        if sub is None:
            return aa.fast_within(y[idx], s[idx], st)
        m = sub[idx]
        if not m.any():
            return float("nan")
        return aa.fast_within(y[idx][m], s[idx][m], st[m])
    return f


def diff_fn(a, b):
    return lambda idx, st: a(idx, st) - b(idx, st)


def placements(y, s, st):
    st = codes(st)
    dense = np.unique(np.asarray(s, float), return_inverse=True)[1].ravel()
    K = int(dense.max()) + 1
    key = st.astype(np.int64) * K + dense
    neg = y == 0
    kn = np.sort(key[neg])
    nneg = np.bincount(st[neg], minlength=st.max() + 1)
    pos = np.where(y == 1)[0]
    kp = key[pos]
    right = np.searchsorted(kn, kp, "right")
    gt = np.searchsorted(kn, st[pos].astype(np.int64) * K + K - 1, "right") - right
    eq = right - np.searchsorted(kn, kp, "left")
    nn = nneg[st[pos]]
    ok = nn > 0
    nn = nn[ok].astype(float)
    return gt[ok] / nn, (gt[ok] + eq[ok]) / nn, nn


def tpr_at(lo, hi, w, t):
    with np.errstate(invalid="ignore", divide="ignore"):
        ramp = np.where(hi > lo, np.clip((t - lo) / np.where(hi > lo, hi - lo, 1), 0, 1), (t >= lo).astype(float))
    return float((w * ramp).sum() / w.sum()) if w.sum() else float("nan")


def pauc_at(lo, hi, w, t):
    width = np.where(hi > lo, hi - lo, 1)
    v = np.where(t <= lo, 0.0, np.where(t >= hi, t - (lo + hi) / 2, (t - lo) ** 2 / (2 * width)))
    return float((w * v).sum() / w.sum()) if w.sum() else float("nan")


def db_point(y, db):
    return float(db[y == 0].mean()), float(db[y == 1].mean())


def operating_fns(y, s, db):
    def get(idx, st):
        yy = y[idx]
        fpr, tpr = db_point(yy, db[idx])
        e = placements(yy, s[idx], st)
        d = placements(yy, db[idx], st)
        return fpr, tpr, e, d

    def mk(which):
        def f(idx, st):
            fpr, tpr, e, d = get(idx, st)
            vals = {"drugbank_fpr_pooled": fpr, "drugbank_tpr_pooled": tpr,
                    "e7c_tpr_within_at_drugbank_fpr": tpr_at(*e, fpr), "drugbank_tpr_within_at_its_fpr": tpr_at(*d, fpr),
                    "e7c_pauc_to_drugbank_fpr": pauc_at(*e, fpr), "drugbank_pauc_to_its_fpr": pauc_at(*d, fpr),
                    "e7c_auroc_from_placements": pauc_at(*e, 1.0), "drugbank_auroc_from_placements": pauc_at(*d, 1.0)}
            vals["e7c_minus_drugbank_tpr_within"] = vals["e7c_tpr_within_at_drugbank_fpr"] - vals["drugbank_tpr_within_at_its_fpr"]
            vals["e7c_minus_drugbank_tpr_pooled"] = vals["e7c_tpr_within_at_drugbank_fpr"] - tpr
            vals["e7c_minus_drugbank_pauc"] = vals["e7c_pauc_to_drugbank_fpr"] - vals["drugbank_pauc_to_its_fpr"]
            vals["e7c_pauc_over_fpr"] = vals["e7c_pauc_to_drugbank_fpr"] / fpr if fpr > 0 else float("nan")
            vals["drugbank_pauc_over_fpr"] = vals["drugbank_pauc_to_its_fpr"] / fpr if fpr > 0 else float("nan")
            return vals[which]
        return f
    names = ("drugbank_fpr_pooled", "drugbank_tpr_pooled", "e7c_tpr_within_at_drugbank_fpr", "drugbank_tpr_within_at_its_fpr",
             "e7c_minus_drugbank_tpr_within", "e7c_minus_drugbank_tpr_pooled", "e7c_pauc_to_drugbank_fpr",
             "drugbank_pauc_to_its_fpr", "e7c_minus_drugbank_pauc", "e7c_pauc_over_fpr", "drugbank_pauc_over_fpr",
             "e7c_auroc_from_placements", "drugbank_auroc_from_placements")
    return {k: mk(k) for k in names}


def within_center_rank(x, g):
    gc = codes(g)
    dense = rankdata(x, method="dense")
    r = rankdata(gc.astype(np.int64) * (len(x) + 1) + dense)
    size = np.bincount(gc)
    r = r - (np.cumsum(size) - size)[gc]
    return r - (np.bincount(gc, weights=r) / size)[gc]


def demean(x, g):
    gc = codes(g)
    x = np.asarray(x, float)
    return x - (np.bincount(gc, weights=x) / np.bincount(gc))[gc]


def residualize(s, X, g, kind):
    tr = within_center_rank if kind == "rank" else demean
    yv = tr(s, g)
    M = np.column_stack([tr(x, g) for x in X])
    keep = M.std(0) > 0
    if not keep.any():
        return yv, [0.0] * M.shape[1]
    beta = np.zeros(M.shape[1])
    beta[keep] = np.linalg.lstsq(M[:, keep], yv, rcond=None)[0]
    return np.round(yv - M @ beta, 10), beta.tolist()


def within_spearman(a, b, g):
    ra, rb = within_center_rank(a, g), within_center_rank(b, g)
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / den) if den > 0 else float("nan")


def class_share(e7c, resid):
    if e7c is None or resid is None or e7c == 0.5:
        return None
    return float(min(1.0, max(0.0, 1 - (resid - 0.5) / (e7c - 0.5))))


def build_truth():
    corr, oa = ROOT / "results" / "corrected", ROOT / "artifacts" / "ood"
    rows = {"ood": read_csv(corr / "ood_pairs.csv"), "oodold": read_csv(corr / "ood_old_pairs.csv")}
    db_rows = {"ood": read_csv(oa / "drugbank_validation.csv"), "oodold": read_csv(oa / "drugbank_validation_old.csv")}
    truth = aa.Truth(rows["ood"], rows["oodold"], db_rows["ood"], db_rows["oodold"])
    pairs = {t: [{"ood_drug": r["ood_drug"], "semeval_drug": r["semeval_drug"]} for r in rows[t]] for t in rows}
    db = {t: aa.drugbank_scores(pairs[t], db_rows[t]) for t in rows}
    return truth, rows, db


def load_systems():
    out, seeds = {}, {}
    for tag in ("ood", "oodold"):
        s = {}
        for arm, name in (("c", "E7c"), ("d", "E7d"), ("e", "E7e")):
            key = aa.KEYS[arm][1 if tag == "ood" else 2]
            avg = aa.seed_average(PREDS7, arm, key)
            s[name] = avg["p"]
            seeds[f"{name}:{key}"] = avg["seeds"]
        s["b2mixed"], nb = seed_mean("b2mixed-biomedbert", f"{tag}_empty")
        seeds[f"b2mixed:{tag}_empty"] = nb
        s["Qwen names only"] = single("llm-qwen-names", tag)
        out[tag] = s
    return out, seeds


def embedding_scores(g, q, graph):
    idx_path = OUT / "name_embeddings_index.json"
    if not idx_path.exists():
        return None, "name_embeddings.npy not found; run scripts/post7_classshortcut_embed.py"
    names = json.loads(idx_path.read_text())["names"]
    V = np.load(OUT / "name_embeddings.npy")
    pos = {n: i for i, n in enumerate(names)}
    out = {k: np.full(len(g), -1.0) for k in TOPK}
    for i, (d, x) in enumerate(zip(g, q)):
        ps = [p for p in graph.pos.get(x, ()) if p in pos and p != d]
        if not ps or d not in pos:
            continue
        sims = np.sort(V[[pos[p] for p in ps]] @ V[pos[d]])[::-1]
        for k in TOPK:
            out[k][i] = float(sims[:k].mean())
    return out, None


def alias_candidates(drugs, train_drugs):
    out = []
    for d in sorted(drugs):
        ds = strip_salt(d)
        for t in sorted(train_drugs):
            ts = strip_salt(t)
            sm = difflib.SequenceMatcher(None, ds, ts)
            lcs = sm.find_longest_match(0, len(ds), 0, len(ts)).size
            r = sm.ratio()
            if r >= 0.75 or lcs >= 7:
                judged = d in RED_TEAM_ALIASES and RED_TEAM_ALIASES[d] == t or d in OWN_ALIASES and t == OWN_ALIASES[d].split(":")[0]
                out.append({"older_drug": d, "training_drug": t, "ratio": round(r, 3), "longest_common_substring": lcs,
                            "judged_alias": bool(judged)})
    return out


def cell_analysis(name, tier, truth, rows, db, S, graph, atc, n, emb_ok):
    c = truth.cohort(name, tier)
    tag, m = c["tag"], c["mask"]
    y, g, q = c["y"], c["g"], c["q"]
    seed = aa.BOOT_SEED[name]
    sysv = {k: np.asarray(S[tag][k], float)[m] for k in SYSTEMS if S[tag][k] is not None}
    e7c = sysv["E7c"]
    fullg, fullq = truth.sets[tag]["g"], truth.sets[tag]["q"]
    cs, nmates = {}, {}
    for dfn in DEFS:
        for pool_name, pool in (("anchors", graph.anchors), ("all_training_drugs", graph.drugs)):
            share, cond, nm = class_scores(fullg, fullq, graph, atc, dfn, pool)
            cs[(dfn, pool_name, "share")] = share[m]
            cs[(dfn, pool_name, "conditional")] = cond[m]
            nmates[(dfn, pool_name)] = nm[m]
    res = {"n_rows": int(len(y)), "n_drugs": int(len(set(g))), "n_positives": int(y.sum())}

    fns = {"E7c": auc_fn(y, e7c)}
    for k, v in sysv.items():
        fns[k] = auc_fn(y, v)
    for (dfn, pool_name, kind), v in cs.items():
        key = f"class:{dfn}:{pool_name}:{kind}"
        fns[key] = auc_fn(y, v)
        has = nmates[(dfn, pool_name)] > 0
        fns[key + ":drugs_with_mates"] = auc_fn(y, v, has)
        fns["E7c:drugs_with_mates:" + f"{dfn}:{pool_name}"] = auc_fn(y, e7c, has)
        fns[f"E7c_minus_{key}"] = diff_fn(fns["E7c"], fns[key])
    for dfn in ("atc4", "stem"):
        has = nmates[(dfn, "anchors")] > 0
        for k, v in sysv.items():
            fns[f"split:{dfn}:with:{k}"] = auc_fn(y, v, has)
            fns[f"split:{dfn}:without:{k}"] = auc_fn(y, v, ~has)
            fns[f"split:{dfn}:with_minus_without:{k}"] = diff_fn(fns[f"split:{dfn}:with:{k}"], fns[f"split:{dfn}:without:{k}"])
    X = [cs[(d, "anchors", "share")] for d in DEFS]
    resid = {}
    for kind in ("rank", "linear"):
        r, beta = residualize(aa.logit(e7c), X, g, kind)
        resid[f"{kind}:joint"] = (r, beta)
        fns[f"residual:{kind}:joint"] = auc_fn(y, r)
        for i, d in enumerate(DEFS):
            r1, b1 = residualize(aa.logit(e7c), [X[i]], g, kind)
            resid[f"{kind}:{d}"] = (r1, b1)
            fns[f"residual:{kind}:{d}"] = auc_fn(y, r1)
    evid = np.asarray([r["evidence"] for r in rows[tag]], dtype=object)[m]
    pk = np.asarray([bool(PK_RE.search(e or "")) for e in evid]) & (y == 1)
    pd_ = (y == 1) & ~pk
    pkb = np.asarray([bool(PK_BROAD_RE.search(e or "")) for e in evid]) & (y == 1)
    pdb = (y == 1) & ~pkb
    for lab, msk in (("PK", pk), ("PD_or_other", pd_), ("broad_PK", pkb), ("broad_PD_or_other", pdb)):
        sub = (y == 0) | msk
        fns[f"mechanism:{lab}:E7c"] = auc_fn(y, e7c, sub)
        fns[f"mechanism:{lab}:class_atc4"] = auc_fn(y, cs[("atc4", "anchors", "share")], sub)
        fns[f"mechanism:{lab}:class_stem"] = auc_fn(y, cs[("stem", "anchors", "share")], sub)
    fns["mechanism:PK_minus_PD:E7c"] = diff_fn(fns["mechanism:PK:E7c"], fns["mechanism:PD_or_other:E7c"])
    fns["mechanism:broad_PK_minus_PD:E7c"] = diff_fn(fns["mechanism:broad_PK:E7c"], fns["mechanism:broad_PD_or_other:E7c"])
    dbv = np.asarray(db[tag], float)[m]
    fns.update({f"drugbank:{k}": f for k, f in operating_fns(y, e7c, dbv).items()})
    rate = np.full(len(fullq), np.nan)
    for i, x in enumerate(fullq):
        if graph.any.get(x):
            rate[i] = len(graph.pos[x]) / len(graph.any[x])
    rate = rate[m]
    rate_filled = np.where(np.isnan(rate), np.nanmean(rate) if (~np.isnan(rate)).any() else 0.0, rate)
    fns["prior:partner_training_rate"] = auc_fn(y, rate_filled)
    emb = None
    if emb_ok:
        emb, _ = embedding_scores(fullg, fullq, graph)
        for k in TOPK:
            fns[f"prior:embedding_top{k}"] = auc_fn(y, emb[k][m])
        for k in (1, 3):
            r, beta = residualize(aa.logit(e7c), X + [emb[k][m]], g, "rank")
            resid[f"post_hoc:rank:joint_plus_embedding_top{k}"] = (r, beta)
            fns[f"residual:post_hoc:rank:joint_plus_embedding_top{k}"] = auc_fn(y, r)
    stats = run_metrics({"y": y, "g": g, "q": q}, fns, n, seed)

    res["systems"] = {k: stats[k] for k in sysv}
    res["class_scorer"] = {}
    for (dfn, pool_name, kind) in cs:
        key = f"class:{dfn}:{pool_name}:{kind}"
        has = nmates[(dfn, pool_name)] > 0
        res["class_scorer"][key] = {"all_drugs": stats[key], "drugs_with_mates": stats[key + ":drugs_with_mates"],
                                     "E7c_on_drugs_with_mates": stats[f"E7c:drugs_with_mates:{dfn}:{pool_name}"],
                                     "E7c_minus_scorer_all_drugs": stats[f"E7c_minus_{key}"],
                                     "n_drugs_with_mates": int(len(set(g[has]))), "n_drugs": int(len(set(g)))}
    res["split"] = {}
    for dfn in ("atc4", "stem"):
        has = nmates[(dfn, "anchors")] > 0
        res["split"][dfn] = {"n_drugs_with": int(len(set(g[has]))), "n_drugs_without": int(len(set(g[~has]))),
                             "n_rows_with": int(has.sum()), "n_rows_without": int((~has).sum()),
                             "drugs_without": sorted(set(g[~has].tolist())),
                             "systems": {k: {"with": stats[f"split:{dfn}:with:{k}"], "without": stats[f"split:{dfn}:without:{k}"],
                                             "with_minus_without": stats[f"split:{dfn}:with_minus_without:{k}"]} for k in sysv}}
    res["partial"] = {"E7c_within": stats["E7c"],
                      "within_spearman_logitE7c_vs_class": {d: within_spearman(aa.logit(e7c), X[i], g) for i, d in enumerate(DEFS)}}
    for key, (_, beta) in resid.items():
        st_ = stats[f"residual:{key}"]
        res["partial"][key] = {"residual_within": st_, "beta": beta,
                               "class_share": class_share(stats["E7c"]["value"], st_["value"]),
                               "contains_0.5": None if st_["lo95"] is None else bool(st_["lo95"] <= 0.5 <= st_["hi95"])}
    res["mechanism"] = {"n_pk_positives": int(pk.sum()), "n_pd_or_other_positives": int(pd_.sum()),
                        "n_drugs_with_pk_positive": int(len(set(g[pk]))), "n_drugs_with_pd_positive": int(len(set(g[pd_]))),
                        "E7c": {"PK": stats["mechanism:PK:E7c"], "PD_or_other": stats["mechanism:PD_or_other:E7c"],
                                "PK_minus_PD": stats["mechanism:PK_minus_PD:E7c"]},
                        "class_atc4": {"PK": stats["mechanism:PK:class_atc4"], "PD_or_other": stats["mechanism:PD_or_other:class_atc4"]},
                        "class_stem": {"PK": stats["mechanism:PK:class_stem"], "PD_or_other": stats["mechanism:PD_or_other:class_stem"]},
                        "post_hoc_broad_rule": {"regex": PK_BROAD_RE.pattern, "n_pk_positives": int(pkb.sum()),
                                                "n_pd_or_other_positives": int(pdb.sum()),
                                                "E7c": {"PK": stats["mechanism:broad_PK:E7c"], "PD_or_other": stats["mechanism:broad_PD_or_other:E7c"],
                                                        "PK_minus_PD": stats["mechanism:broad_PK_minus_PD:E7c"]},
                                                "class_atc4": {"PK": stats["mechanism:broad_PK:class_atc4"], "PD_or_other": stats["mechanism:broad_PD_or_other:class_atc4"]}}}
    res["drugbank_operating_point"] = {k.split(":", 1)[1]: v for k, v in stats.items() if k.startswith("drugbank:")}
    ok = ~np.isnan(rate)
    res["partner_prior"] = {"partner_training_rate": {"within": stats["prior:partner_training_rate"],
                                                      "n_partners": int(len(set(q))), "n_partners_in_training": int(len(set(q[ok]))),
                                                      "distinct_partner_values": {"mean": float(np.mean(list({x: r for x, r in zip(q[ok], rate[ok])}.values()))) if ok.any() else None,
                                                                                  "sd": float(np.std(list({x: r for x, r in zip(q[ok], rate[ok])}.values()))) if ok.any() else None,
                                                                                  "min": float(rate[ok].min()) if ok.any() else None,
                                                                                  "max": float(rate[ok].max()) if ok.any() else None}},
                            "class_conditional_rate": {d: res["class_scorer"][f"class:{d}:anchors:conditional"]["all_drugs"] for d in DEFS}}
    if emb is not None:
        res["partner_prior"]["embedding"] = {f"top{k}": stats[f"prior:embedding_top{k}"] for k in TOPK}
        res["partner_prior"]["embedding_n_rows_scored"] = int((emb[3][m] > -1).sum())
    per_drug = {}
    for d in sorted(set(g.tolist())):
        sel = g == d
        if y[sel].min() == y[sel].max():
            continue
        per_drug[d] = {"E7c": aa.fast_within(y[sel], e7c[sel], np.zeros(sel.sum(), int)),
                       "class_atc4": aa.fast_within(y[sel], cs[("atc4", "anchors", "share")][sel], np.zeros(sel.sum(), int)),
                       "class_stem": aa.fast_within(y[sel], cs[("stem", "anchors", "share")][sel], np.zeros(sel.sum(), int)),
                       "mates_atc4": int(nmates[("atc4", "anchors")][sel][0]), "mates_stem": int(nmates[("stem", "anchors")][sel][0]),
                       "mates_atc3": int(nmates[("atc3", "anchors")][sel][0]),
                       "n_pos": int(y[sel].sum()), "n_neg": int((1 - y[sel]).sum())}
    res["per_drug"] = per_drug
    for dfn in ("atc4", "stem"):
        w = [v["E7c"] for v in per_drug.values() if v[f"mates_{dfn}"] > 0]
        wo = [v["E7c"] for v in per_drug.values() if v[f"mates_{dfn}"] == 0]
        res["split"][dfn]["E7c_drug_averaged"] = {"with": float(np.mean(w)) if w else None, "without": float(np.mean(wo)) if wo else None,
                                                  "n_with": len(w), "n_without": len(wo)}
    return res


def alias_analysis(truth, S, graph, n):
    c0 = truth.cohort("older_primary", "A")
    cands = alias_candidates(set(c0["g"].tolist()), graph.drugs)
    confirmed = sorted(set(RED_TEAM_ALIASES) | set(OWN_ALIASES))
    out = {"candidates": cands, "red_team": RED_TEAM_ALIASES, "own_confirmed": OWN_ALIASES,
           "red_team_alias_partner_in_training": {d: t in graph.drugs for d, t in RED_TEAM_ALIASES.items()}, "cells": {}}
    for name, tier in CELLS:
        if name != "older_primary":
            continue
        cell = {}
        for lab, drop in (("none_removed", ()), ("red_team_removed", tuple(RED_TEAM_ALIASES)), ("all_confirmed_removed", tuple(confirmed))):
            c = truth.cohort(name, tier, drop=drop)
            p = np.asarray(S[c["tag"]]["E7c"], float)[c["mask"]]
            st = run_metrics(c, {"E7c": auc_fn(c["y"], p)}, n, aa.BOOT_SEED[name])["E7c"]
            cell[lab] = {"E7c": st, "n_drugs": int(len(set(c["g"]))), "n_rows": int(len(c["y"]))}
        cell["drop_red_team"] = cell["none_removed"]["E7c"]["value"] - cell["red_team_removed"]["E7c"]["value"]
        cell["drop_all"] = cell["none_removed"]["E7c"]["value"] - cell["all_confirmed_removed"]["E7c"]["value"]
        out["cells"][tier] = cell
    return out


def verdict(primary):
    best_def, sufficient = None, False
    for d in DEFS:
        cs = primary["class_scorer"][f"class:{d}:anchors:share"]
        e7c = primary["systems"]["E7c"]["value"]
        diff = cs["E7c_minus_scorer_all_drugs"]
        ok = cs["all_drugs"]["value"] >= e7c or (diff["lo95"] is not None and diff["lo95"] <= 0 <= diff["hi95"])
        if ok:
            sufficient, best_def = True, d
    dependent = {}
    for d in ("atc4", "stem"):
        s = primary["split"][d]["systems"]["E7c"]
        w = s["with_minus_without"]
        wo = s["without"]
        dependent[d] = bool(w["value"] is not None and w["value"] >= 0.10 and w["lo95"] is not None and w["lo95"] > 0
                            and wo["lo95"] is not None and wo["lo95"] <= 0.5 <= wo["hi95"])
    part = primary["partial"]["rank:joint"]
    explains = bool(part["contains_0.5"])
    share = part["class_share"]
    lo = part["residual_within"]["lo95"]
    if explains and (sufficient or any(dependent.values())):
        v = "b"
    elif lo is not None and lo > 0.5 and share is not None and share <= 0.25 and not sufficient:
        v = "a"
    else:
        v = "c"
    return {"analysis_1_sufficient": sufficient, "analysis_1_qualifying_definition": best_def,
            "analysis_2_dependent": dependent, "analysis_3_shortcut_explains": explains, "class_share_primary": share,
            "verdict": v, "verdict_text": {"a": "genuine specific-drug knowledge", "b": "drug-class transfer shortcut",
                                           "c": "mix"}[v]}


def f3(v):
    return "NA" if v is None or (isinstance(v, float) and v != v) else f"{v:.3f}"


def ci(s):
    return f"{f3(s['value'])} [{f3(s['lo95'])}, {f3(s['hi95'])}]"


def markdown(res):
    L = ["# Class-shortcut test of E7c (post 7)", "", res["status"], ""]
    v = res["verdict"]
    L += ["## Verdict (Older-primary tier A, pre-stated rule in criteria.json)", "",
          f"- analysis 1 class scorer sufficient: {v['analysis_1_sufficient']} (definition: {v['analysis_1_qualifying_definition']})",
          f"- analysis 2 class-dependent: ATC-4 {v['analysis_2_dependent']['atc4']}, stem {v['analysis_2_dependent']['stem']}",
          f"- analysis 3 residual 95% interval contains 0.5: {v['analysis_3_shortcut_explains']}",
          f"- class share (rank, joint): {f3(v['class_share_primary'])}",
          f"- verdict: ({v['verdict']}) {v['verdict_text']}", ""]
    for key, cell in res["cells"].items():
        L += [f"## {key}", "", f"rows {cell['n_rows']}, drugs {cell['n_drugs']}, positives {cell['n_positives']}", ""]
        L += ["| system | within-drug AUROC [95%] |", "|---|---|"]
        L += [f"| {k} | {ci(s)} |" for k, s in cell["systems"].items()]
        L += ["", "### 1. Class-sibling scorer (no model)", "",
              "| definition | pool | score | all drugs | drugs with mates (n) | E7c on those drugs | E7c minus scorer |", "|---|---|---|---|---|---|---|"]
        for k, s in cell["class_scorer"].items():
            _, d, pool, kind = k.split(":")
            L.append(f"| {d} | {pool} | {kind} | {ci(s['all_drugs'])} | {ci(s['drugs_with_mates'])} ({s['n_drugs_with_mates']}/{s['n_drugs']}) | "
                     f"{ci(s['E7c_on_drugs_with_mates'])} | {ci(s['E7c_minus_scorer_all_drugs'])} |")
        L += ["", "### 2. Split by having a training anchor in the same class", ""]
        for d, sp in cell["split"].items():
            L += [f"{d}: with {sp['n_drugs_with']} drugs ({sp['n_rows_with']} rows), without {sp['n_drugs_without']} drugs ({sp['n_rows_without']} rows)", "",
                  "| system | with | without | with minus without |", "|---|---|---|---|"]
            L += [f"| {k} | {ci(s['with'])} | {ci(s['without'])} | {ci(s['with_minus_without'])} |" for k, s in sp["systems"].items()]
            da = sp["E7c_drug_averaged"]
            L += ["", f"E7c drug-averaged per-drug AUROC: with {f3(da['with'])} ({da['n_with']}), without {f3(da['without'])} ({da['n_without']})", ""]
        L += ["### 3. E7c partialled on the class-sibling score within drug", "",
              "| adjustment | residual within-drug AUROC [95%] | class share | contains 0.5 |", "|---|---|---|---|"]
        for k, p in cell["partial"].items():
            if k in ("E7c_within", "within_spearman_logitE7c_vs_class"):
                continue
            L.append(f"| {k} | {ci(p['residual_within'])} | {f3(p['class_share'])} | {p['contains_0.5']} |")
        sp = cell["partial"]["within_spearman_logitE7c_vs_class"]
        L += ["", "within-drug Spearman of logit E7c with the class score: " + ", ".join(f"{k} {f3(x)}" for k, x in sp.items()), ""]
        mech = cell["mechanism"]
        L += ["### 4. Mechanism", "",
              f"PK positives {mech['n_pk_positives']} ({mech['n_drugs_with_pk_positive']} drugs), PD or other {mech['n_pd_or_other_positives']} ({mech['n_drugs_with_pd_positive']} drugs)", "",
              "| scorer | PK | PD or other |", "|---|---|---|"]
        for k in ("E7c", "class_atc4", "class_stem"):
            L.append(f"| {k} | {ci(mech[k]['PK'])} | {ci(mech[k]['PD_or_other'])} |")
        b = mech["post_hoc_broad_rule"]
        L += ["", f"E7c PK minus PD: {ci(mech['E7c']['PK_minus_PD'])}", "",
              f"post hoc broader PK rule (adds pharmacokinetic, concentration, bioavailability, absorption, plasma or serum level, inducer): "
              f"PK {b['n_pk_positives']}, PD or other {b['n_pd_or_other_positives']}; E7c PK {ci(b['E7c']['PK'])}, PD or other {ci(b['E7c']['PD_or_other'])}, "
              f"difference {ci(b['E7c']['PK_minus_PD'])}", "", "### 5. DrugBank operating point", "",
              "| quantity | value [95%] |", "|---|---|"]
        L += [f"| {k} | {ci(s)} |" for k, s in cell["drugbank_operating_point"].items()]
        pp = cell["partner_prior"]
        L += ["", "### 6. Non-constant partner priors", "",
              f"partner training positive rate: within {ci(pp['partner_training_rate']['within'])}; partners in training "
              f"{pp['partner_training_rate']['n_partners_in_training']}/{pp['partner_training_rate']['n_partners']}; "
              f"distinct-partner mean {f3(pp['partner_training_rate']['distinct_partner_values']['mean'])}, "
              f"sd {f3(pp['partner_training_rate']['distinct_partner_values']['sd'])}, "
              f"range {f3(pp['partner_training_rate']['distinct_partner_values']['min'])} to {f3(pp['partner_training_rate']['distinct_partner_values']['max'])}", ""]
        L += [f"- class-conditional partner rate, {d}: {ci(s)}" for d, s in pp["class_conditional_rate"].items()]
        if "embedding" in pp:
            L += [f"- frozen BiomedBERT name similarity, {k}: {ci(s)}" for k, s in pp["embedding"].items()]
        L.append("")
    al = res["aliases"]
    L += ["## 7. Aliases", "", "| Older drug | training drug | ratio | LCS | judged alias |", "|---|---|---|---|---|"]
    L += [f"| {c['older_drug']} | {c['training_drug']} | {c['ratio']} | {c['longest_common_substring']} | {c['judged_alias']} |" for c in al["candidates"]]
    L += ["", "red-team alias partner present among training drugs: " + ", ".join(f"{k}: {v}" for k, v in al["red_team_alias_partner_in_training"].items()), ""]
    for tier, cell in al["cells"].items():
        L += [f"Older-primary tier {tier}: " + "; ".join(f"{k} {ci(cell[k]['E7c'])} ({cell[k]['n_drugs']} drugs)" for k in ("none_removed", "red_team_removed", "all_confirmed_removed"))]
    L += ["", "## Red-team named drugs (seed-averaged per-drug AUROC, Older-primary tier A)", "",
          "| drug | group | E7c | class ATC-4 | class stem | mates ATC-4 | mates stem |", "|---|---|---|---|---|---|---|"]
    pdg = res["cells"]["older_primary:A"]["per_drug"]
    for grp, ds in (("high", RED_TEAM_HIGH), ("low", RED_TEAM_LOW)):
        for d in ds:
            r = pdg.get(d)
            if r:
                L.append(f"| {d} | {grp} | {f3(r['E7c'])} | {f3(r['class_atc4'])} | {f3(r['class_stem'])} | {r['mates_atc4']} | {r['mates_stem']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    crit = require_criteria()
    truth, rows, db = build_truth()
    S, seeds = load_systems()
    graph = Graph(read_csv(ROOT / "artifacts" / "amend7" / "train_pairs.csv"))
    atc = load_atc()
    emb_ok = (OUT / "name_embeddings.npy").exists()
    res = {"status": crit["status"], "bootstrap_draws": a.boot, "seeds": seeds, "pk_regex": PK_RE.pattern,
           "embedding_available": emb_ok, "cells": {}}
    for name, tier in CELLS:
        res["cells"][f"{name}:{tier}"] = cell_analysis(name, tier, truth, rows, db, S, graph, atc, a.boot, emb_ok)
    res["aliases"] = alias_analysis(truth, S, graph, a.boot)
    res["verdict"] = verdict(res["cells"]["older_primary:A"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "classshortcut.json").write_text(json.dumps(aa.clean(res), indent=1) + "\n")
    (OUT / "classshortcut.md").write_text(markdown(aa.clean(res)))
    print(json.dumps(aa.clean(res["verdict"]), indent=1))


if __name__ == "__main__":
    main()
