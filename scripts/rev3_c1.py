import argparse
import json
from collections import Counter, defaultdict

import numpy as np

import rev3_common as rc
import rev2_m3b as m3b
from amend7_cpu_exp5_dissociation import resolve
from ddiood import amend7_pairs as ap
from ddiood import config, semeval
from ddiood.openfda import LabelStore
from ddiood.rev3_pairlabel import NEGATIVE, POSITIVE, UNDECIDED, PairLabeler
from ddiood.textnorm import canonicalize, normalize

LABELS = ("sem_any", "sem_majority", "fda", "db")
PAIRINGS = [(a, b) for i, a in enumerate(LABELS) for b in LABELS[i + 1:]]
SOURCES = {"both": None, "DDI-DrugBank": "DrugBank", "DDI-MedLine": "MedLine"}
SPLITS = ("train", "test", "pooled")
VARIANTS = ("primary", "self_included", "S1", "S2", "db_both_resolved")
MIN_CLASS = 20
INSTANCE_PAIRINGS = [("sem_instance", "fda"), ("sem_instance", "db"), ("fda", "db")]


def key(name):
    return name.strip().lower()


def ood_blocker(lookup, ood_rows, old_rows):
    blocked = ap.ood_pair_set(ood_rows, old_rows)

    def check(a, b):
        keys = {frozenset((x, z)) for x in {normalize(a), canonicalize(a), lookup[a]["normalized"]}
                for z in {normalize(b), canonicalize(b), lookup[b]["normalized"]}}
        return bool(keys & blocked)
    return check


def build_instances():
    rows = []
    for split in ("train", "test"):
        for r in semeval.load_pairs(split):
            rows.append({"split": split, "source": r["source"], "sentence_id": r["sentence_id"], "a": key(r["drug_a"]),
                         "b": key(r["drug_b"]), "pos": int(r["label_id"] != 0)})
    return rows


def pair_table(lookup, labeler, table, blocker, excl_s2, inst):
    pairs = {}
    for r in inst:
        pairs.setdefault(frozenset((r["a"], r["b"])), (r["a"], r["b"]))
    out = {}
    for k, (a, b) in pairs.items():
        invocab = a in lookup and b in lookup
        e = {"a": a, "b": b, "self": a == b, "invocab": invocab, "same_rxcui": bool(invocab and a != b and lookup[a]["rxcui"] == lookup[b]["rxcui"])}
        e["has_di"] = bool(invocab and (labeler.has_di(a) or labeler.has_di(b)))
        if invocab:
            e["fda"] = labeler.pair_state(a, b)[0]
            e["fda_s1"] = labeler.pair_state(a, b, require_info=False)[0]
            s2 = PairLabeler.__new__(PairLabeler)
            s2.__dict__.update(labeler.__dict__)
            s2.excluded = excl_s2
            e["fda_s2"] = s2.pair_state(a, b, ood_blocked=blocker)[0]
        st, side = resolve(a, b, table, lookup)
        e["db"] = int(st == "positive")
        e["db_resolved_both"] = side == 2
        e["db_state"] = st
        out[k] = e
    return out


def consistency(labeler, table_rows, blocker, excl_s2):
    s2 = PairLabeler.__new__(PairLabeler)
    s2.__dict__.update(labeler.__dict__)
    s2.excluded = excl_s2
    res = {"primary": Counter(), "S2": Counter()}
    for r in table_rows:
        want = POSITIVE if int(r["y"]) == 1 else NEGATIVE
        res["primary"][f"E7_{want}->{labeler.pair_state(r['drug_a'], r['drug_b'])[0]}"] += 1
        res["S2"][f"E7_{want}->{s2.pair_state(r['drug_a'], r['drug_b'], ood_blocked=blocker)[0]}"] += 1
    return {k: dict(sorted(v.items())) for k, v in res.items()}


def sel_instances(inst, pt, split, source, variant):
    out = []
    for r in inst:
        if split != "pooled" and r["split"] != split:
            continue
        if source is not None and r["source"] != source:
            continue
        e = pt[frozenset((r["a"], r["b"]))]
        if not e["invocab"] or not e["has_di"]:
            continue
        if e["self"] and variant != "self_included":
            continue
        out.append((r, e))
    return out


def fda_label(e, variant):
    s = {"S1": e["fda_s1"], "S2": e["fda_s2"]}.get(variant, e["fda"])
    return s


def units(sel, variant):
    by = defaultdict(list)
    for r, e in sel:
        by[frozenset((r["a"], r["b"]))].append((r, e))
    rows = []
    for k, items in by.items():
        e = items[0][1]
        n = len(items)
        npos = sum(r["pos"] for r, _ in items)
        st = fda_label(e, variant)
        if variant == "db_both_resolved" and not e["db_resolved_both"]:
            continue
        rows.append({"key": k, "n": n, "npos": npos, "any": int(npos > 0), "maj": int(2 * npos > n), "half": int(2 * npos == n),
                     "fda_state": st, "fda": int(st == POSITIVE), "db": e["db"], "db_state": e["db_state"],
                     "sources": sorted({r["source"] for r, _ in items}), "self": e["self"], "same_rxcui": e["same_rxcui"],
                     "sent": sorted({r["sentence_id"] for r, _ in items}), "inst": [r["pos"] for r, _ in items],
                     "inst_sent": [r["sentence_id"] for r, _ in items]})
    return rows


def pair_stats(x, y, w):
    N = w.sum(1)
    a = w @ (x & y)
    px = w @ x
    py = w @ y
    with np.errstate(all="ignore"):
        po = (N - px - py + 2 * a) / N
        pe = (px * py + (N - px) * (N - py)) / N ** 2
        kappa = (po - pe) / (1 - pe)
        tpr = a / py
        fpr = (px - a) / (N - py)
        auc_x_for_y = 0.5 * (1 + tpr - fpr)
        tpr2 = a / px
        fpr2 = (py - a) / (N - px)
        auc_y_for_x = 0.5 * (1 + tpr2 - fpr2)
    return {"agreement": po, "kappa": kappa, "auroc_first_for_second": auc_x_for_y, "auroc_second_for_first": auc_y_for_x}


def bootstrap_weights(cluster_ids, unit_cluster, n_boot, seed):
    k = len(cluster_ids)
    rng = np.random.RandomState(seed)
    draws = np.zeros((n_boot, k))
    for b in range(n_boot):
        draws[b] = np.bincount(rng.randint(0, k, k), minlength=k)
    return draws[:, unit_cluster].astype(float)


def block(vecs, w_point, w_boot, small, pairings=PAIRINGS):
    out = {}
    for a, b in pairings:
        x, y = vecs[a], vecs[b]
        pt = pair_stats(x, y, w_point[None, :])
        bs = pair_stats(x, y, w_boot)
        row = {}
        for m in pt:
            v = float(pt[m][0])
            d = bs[m][~np.isnan(bs[m])]
            skip = small[a] or small[b]
            row[m] = {"value": v, "ci95": None if skip or not len(d) else [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
                      "n_draws": int(len(d))}
        row["small_cell"] = bool(small[a] or small[b])
        out[f"{a}|{b}"] = row
    return out


def summarize(units_, view, seed, n_boot):
    n = len(units_)
    base = {"n_pairs": n}
    dec = [u for u in units_ if u["fda_state"] != UNDECIDED]
    und = [u for u in units_ if u["fda_state"] == UNDECIDED]
    base["n_fda_decided"] = len(dec)
    base["n_fda_undecided"] = len(und)
    base["undecided_sem_any_rate"] = float(np.mean([u["any"] for u in und])) if und else None
    base["undecided_db_listed_rate"] = float(np.mean([u["db"] for u in und])) if und else None
    base["n_pairs_in_both_source_folders"] = int(sum(1 for u in dec if len(u["sources"]) > 1))
    base["n_same_rxcui_different_names"] = int(sum(u["same_rxcui"] for u in dec))
    base["n_half_positive_pairs"] = int(sum(u["half"] for u in dec))
    base["n_self_pairs"] = int(sum(u["self"] for u in dec))
    base["db_unresolvable_decided"] = int(sum(u["db_state"] == "unresolvable" for u in dec))
    if view == "pair":
        U = dec
        if len(U) < 4:
            return {**base, "pairings": None}
        vecs = {"sem_any": np.array([u["any"] for u in U], bool), "sem_majority": np.array([u["maj"] for u in U], bool),
                "fda": np.array([u["fda"] for u in U], bool), "db": np.array([u["db"] for u in U], bool)}
        cross = Counter((int(u["any"]), u["fda"], u["db"]) for u in U)
        base["crosstab_any_fda_db"] = {f"{a}{f}{d}": cross.get((a, f, d), 0) for a in (0, 1) for f in (0, 1) for d in (0, 1)}
        crossm = Counter((int(u["maj"]), u["fda"], u["db"]) for u in U)
        base["crosstab_majority_fda_db"] = {f"{a}{f}{d}": crossm.get((a, f, d), 0) for a in (0, 1) for f in (0, 1) for d in (0, 1)}
        base["label_counts"] = {k: int(v.sum()) for k, v in vecs.items()}
        small = {k: bool(min(v.sum(), (~v).sum()) < MIN_CLASS) for k, v in vecs.items()}
        w_boot = bootstrap_weights(range(len(U)), np.arange(len(U)), n_boot, seed)
        base["pairings"] = block(vecs, np.ones(len(U)), w_boot, small)
        return base
    inst = [(i, u) for u in dec for i in range(len(u["inst"]))]
    if len(inst) < 4:
        return {**base, "pairings": None}
    sem = np.array([u["inst"][i] for i, u in inst], bool)
    vecs = {"sem_instance": sem, "fda": np.array([u["fda"] for _, u in inst], bool), "db": np.array([u["db"] for _, u in inst], bool)}
    sents = sorted({u["inst_sent"][i] for i, u in inst})
    sidx = {s: j for j, s in enumerate(sents)}
    cl = np.array([sidx[u["inst_sent"][i]] for i, u in inst])
    base["n_instances"] = len(inst)
    base["n_sentences"] = len(sents)
    base["label_counts"] = {k: int(v.sum()) for k, v in vecs.items()}
    small = {k: bool(min(v.sum(), (~v).sum()) < MIN_CLASS) for k, v in vecs.items()}
    w_boot = bootstrap_weights(sents, cl, n_boot, seed)
    base["pairings"] = block(vecs, np.ones(len(inst)), w_boot, small, INSTANCE_PAIRINGS)
    return base


def run(inst, pt, n_boot):
    res = {}
    for variant in VARIANTS:
        res[variant] = {}
        for split in SPLITS:
            for sname, src in SOURCES.items():
                sel = sel_instances(inst, pt, split, src, variant)
                us = units(sel, "S2" if variant == "S2" else variant)
                tag = f"{split}/{sname}"
                res[variant][tag] = {"pair": summarize(us, "pair", 42, n_boot)}
                if variant == "primary":
                    res[variant][tag]["instance"] = summarize(us, "instance", 42, n_boot)
    return res


def funnel(inst, pt):
    out = {}
    for split in SPLITS:
        rows = [r for r in inst if split == "pooled" or r["split"] == split]
        ks = {frozenset((r["a"], r["b"])) for r in rows}
        ents = [pt[k] for k in ks]
        selfs = [e for e in ents if e["self"]]
        ns = [e for e in ents if not e["self"]]
        iv = [e for e in ns if e["invocab"]]
        di = [e for e in iv if e["has_di"]]
        out[split] = {"instances": len(rows), "unique_pairs": len(ks), "self_pairs": len(selfs), "non_self_pairs": len(ns),
                      "self_pairs_in_vocab_with_di": int(sum(e["invocab"] and e["has_di"] for e in selfs)),
                      "both_names_in_vocabulary": len(iv), "at_least_one_di_section": len(di),
                      "fda_positive": sum(e["fda"] == POSITIVE for e in di), "fda_negative": sum(e["fda"] == NEGATIVE for e in di),
                      "fda_undecided": sum(e["fda"] == UNDECIDED for e in di),
                      "db_unresolvable": sum(e["db_state"] == "unresolvable" for e in di)}
    return out


def md(res):
    L = ["# C1: model-free same-pair dissociation", "", f"Status: {rc.STATUS}.", "",
         f"DrugBank release: version {res['drugbank_release']['version']}, exported on {res['drugbank_release']['exported_on']} (`{res['drugbank_release']['file']}`).", "",
         "## Funnel", ""]
    f = res["funnel"]
    keys = list(f["pooled"])
    L += rc.table(["step"] + list(f), [[k] + [f[s][k] for s in f] for k in keys]) + [""]
    L += ["## Consistency gate on the 4,643 E7 pairs", "", "```", json.dumps(res["consistency_gate"], indent=1), "```", ""]
    for variant in VARIANTS:
        L += [f"## Pair view, variant {variant}", ""]
        rows = []
        for tag, v in res["results"][variant].items():
            p = v["pair"]
            if not p.get("pairings"):
                rows.append([tag, p["n_pairs"], p["n_fda_decided"], "too few"])
                continue
            lc = p["label_counts"]
            rows.append([tag, p["n_pairs"], p["n_fda_decided"], p["n_fda_undecided"], lc["sem_any"], lc["sem_majority"], lc["fda"], lc["db"]])
        L += rc.table(["stratum", "pairs", "FDA decided", "FDA undecided", "SemEval any +", "SemEval majority +", "FDA +", "DrugBank listed"], rows) + [""]
        rows = []
        for tag, v in res["results"][variant].items():
            p = v["pair"]
            if not p.get("pairings"):
                continue
            for pr, x in p["pairings"].items():
                rows.append([tag, pr, rc.f3(x["agreement"]["value"]), rc.ci(x["agreement"]["ci95"]), rc.f3(x["kappa"]["value"]), rc.ci(x["kappa"]["ci95"]),
                             rc.f3(x["auroc_first_for_second"]["value"]), rc.ci(x["auroc_first_for_second"]["ci95"]),
                             rc.f3(x["auroc_second_for_first"]["value"]), rc.ci(x["auroc_second_for_first"]["ci95"]), "small" if x["small_cell"] else ""])
        L += rc.table(["stratum", "labels (first|second)", "agreement", "95%", "kappa", "95%", "AUROC first for second", "95%", "AUROC second for first", "95%", "note"], rows) + [""]
    L += ["## Instance view, primary", ""]
    rows = []
    for tag, v in res["results"]["primary"].items():
        p = v["instance"]
        if not p.get("pairings"):
            continue
        for pr, x in p["pairings"].items():
            rows.append([tag, p["n_instances"], pr, rc.f3(x["agreement"]["value"]), rc.ci(x["agreement"]["ci95"]), rc.f3(x["kappa"]["value"]), rc.ci(x["kappa"]["ci95"]),
                         rc.f3(x["auroc_first_for_second"]["value"]), rc.ci(x["auroc_first_for_second"]["ci95"]),
                         rc.f3(x["auroc_second_for_first"]["value"]), rc.ci(x["auroc_second_for_first"]["ci95"])])
    L += rc.table(["stratum", "instances", "labels", "agreement", "95%", "kappa", "95%", "AUROC first for second", "95%", "AUROC second for first", "95%"], rows) + [""]
    L += ["## Cross-tabulations, primary, pooled, both sources", ""]
    p = res["results"]["primary"]["pooled/both"]["pair"]
    L += ["SemEval any, FDA, DrugBank (digits in that order):", ""] + rc.table(["cell", "pairs"], list(p["crosstab_any_fda_db"].items())) + [""]
    L += ["SemEval majority, FDA, DrugBank:", ""] + rc.table(["cell", "pairs"], list(p["crosstab_majority_fda_db"].items())) + [""]
    return "\n".join(L) + "\n"


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--drugbank", default=str(m3b.DEFAULT_ZIP))
    ap_.add_argument("--boot", type=int, default=1000)
    a = ap_.parse_args()
    rc.RUNS.mkdir(parents=True, exist_ok=True)
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    found = json.loads((config.ARTIFACTS / "labels" / "coverage.json").read_text())["vocab_label_found"]
    ood = ap.read_csv(rc.ROOT / "results" / "corrected" / "ood_pairs.csv")
    old = ap.read_csv(rc.ROOT / "results" / "corrected" / "ood_old_pairs.csv")
    report = json.loads((rc.ROOT / "artifacts" / "amend7" / "train_pairs_report.json").read_text())
    excl = set(report["audit"]["excluded_vocab"])
    blocker = ood_blocker(lookup, ood, old)
    table = m3b.load_table(a.drugbank, str(rc.RUNS / "drugbank_table.pkl"))
    header = m3b.header(a.drugbank)
    semeval.download()
    inst = build_instances()
    labeler = PairLabeler(lookup, found, LabelStore(offline=True))
    pt = pair_table(lookup, labeler, table, blocker, excl, inst)
    train_rows = ap.read_rows(rc.ROOT / "artifacts" / "amend7" / "train_pairs.csv")
    gate = consistency(labeler, train_rows, blocker, excl)
    res = {"drugbank_release": header, "n_boot": a.boot, "seed": 42, "min_class_for_interval": MIN_CLASS,
           "n_semeval_instances": len(inst), "funnel": funnel(inst, pt), "consistency_gate": gate,
           "n_excluded_vocab_s2": len(excl), "results": run(inst, pt, a.boot)}
    with open(rc.RUNS / "c1_pairs.csv", "w") as f:
        f.write("a,b,self,invocab,has_di,fda,fda_s1,fda_s2,db,db_state\n")
        for e in pt.values():
            f.write(f"{e['a']},{e['b']},{int(e['self'])},{int(e['invocab'])},{int(e['has_di'])},{e.get('fda','')},{e.get('fda_s1','')},{e.get('fda_s2','')},{e['db']},{e['db_state']}\n")
    rc.write("c1_dissociation", res, md(res))
    print(rc.OUT / "c1_dissociation.md")


if __name__ == "__main__":
    main()
