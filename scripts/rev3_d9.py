import argparse
import json
import pickle
from pathlib import Path

import numpy as np

import rev3_common as rc
import rev2_common as r2
import rev2_m3b as m3b
from amend7_cpu_exp5_dissociation import resolve
from ddiood import config, drugbank, semeval

SOURCES = (("pooled", None), ("DDI-DrugBank", "DrugBank"), ("DDI-MedLine", "MedLine"))
CLASSES = (("negatives", 0), ("positives", 1))
CONVENTIONS = (("self_pairs_excluded", True), ("self_pairs_included", False))
STORED_CHECKS = (
    ("MedLine negatives, self pairs excluded, listed over resolvable", "self_pairs_excluded", "negatives", "DDI-MedLine", "listed_share_of_resolvable",
     {"listed": 101, "resolvable": 196, "value": 0.515, "ci95": [0.446, 0.584]}),
    ("pooled negatives, self pairs excluded, listed over resolvable (0.763 in the abstract)", "self_pairs_excluded", "negatives", "pooled",
     "listed_share_of_resolvable", {"resolvable": 2108, "value": 0.763}),
    ("pooled positives, listed over resolvable (0.727)", "self_pairs_excluded", "positives", "pooled", "listed_share_of_resolvable",
     {"resolvable": 362, "value": 0.727}),
    ("DDI-DrugBank negatives, self pairs excluded, listed over all pairs (0.785, the AUROC table false positive rate)",
     "self_pairs_excluded", "negatives", "DDI-DrugBank", "listed_share_of_all", {"value": 0.785}),
    ("DDI-DrugBank positives, listed over all pairs (0.763, the AUROC table true positive rate)", "self_pairs_excluded", "positives",
     "DDI-DrugBank", "listed_share_of_all", {"value": 0.763}),
)


def load_cached_table(zip_path, cache):
    path = Path(zip_path)
    st = path.stat()
    key = f"{st.st_size}:{int(st.st_mtime)}"
    if Path(cache).exists():
        obj = pickle.loads(Path(cache).read_bytes())
        if isinstance(obj, dict) and set(obj) == {"source_key", "table"}:
            if obj["source_key"] == key:
                return obj["table"], "cache with matching source key"
        elif isinstance(obj, dict) and obj and "source_key" not in obj:
            return obj, "cache of bare table, source not recorded"
    return drugbank.load_interactions(str(path)), "parsed from the zip, nothing written"


def counts(states, sides):
    r = m3b.rates(states, sides)
    return {"n": r["n"], "resolvable": r["resolvable"], "listed": r["listed"],
            "listed_share_of_resolvable": r["listed_share_of_resolvable"], "ci95_resolvable": r["ci95_resolvable"],
            "listed_share_of_all": r["listed_share_of_all"], "ci95_all": r["ci95_all"]}


def instance_rows(y, source, selfpair, state, sides):
    out = {}
    for conv, drop in CONVENTIONS:
        for cname, cv in CLASSES:
            for sname, src in SOURCES:
                m = (y == cv) & (np.ones(len(y), bool) if src is None else source == src)
                removed = int((m & selfpair).sum()) if drop else 0
                if drop:
                    m = m & ~selfpair
                out[(conv, cname, sname)] = {**counts(state[m], sides[m]), "n_self_pairs_removed": removed}
    return out


def pair_rows(test, y, source, selfpair, state, sides, keys):
    out, both_classes = {}, 0
    cls_of = {}
    for i, k in enumerate(keys):
        cls_of.setdefault(k, set()).add(int(y[i]))
    both_classes = sum(1 for v in cls_of.values() if len(v) == 2)
    for conv, drop in CONVENTIONS:
        for cname, cv in CLASSES:
            for sname, src in SOURCES:
                seen, idx = set(), []
                for i, k in enumerate(keys):
                    if y[i] != cv or (src is not None and source[i] != src) or (drop and selfpair[i]) or k in seen:
                        continue
                    seen.add(k)
                    idx.append(i)
                idx = np.array(idx, int)
                out[(conv, cname, sname)] = counts(state[idx], sides[idx]) if len(idx) else {"n": 0}
    return out, both_classes


def reproduce(rows):
    out = []
    for label, conv, cname, sname, field, want in STORED_CHECKS:
        got = rows[(conv, cname, sname)]
        entry = {"value": label, "stored": want, "recomputed": {"listed": got["listed"], "resolvable": got["resolvable"], "n": got["n"],
                                                                   "value": got[field],
                                                                   "ci95": got["ci95_resolvable"] if field.endswith("resolvable") else got["ci95_all"]}}
        ok = got[field] is not None and round(got[field], 3) == want["value"]
        for k in ("listed", "resolvable"):
            if k in want:
                ok = ok and got[k] == want[k]
        if "ci95" in want:
            ci = entry["recomputed"]["ci95"]
            ok = ok and ci is not None and [round(ci[0], 3), round(ci[1], 3)] == want["ci95"]
        entry["match"] = bool(ok)
        out.append(entry)
    return out


def flat(rows):
    return [{"convention": c, "class": cn, "scope": s, **v} for (c, cn, s), v in rows.items()]


def md(o):
    L = ["# D9: DrugBank listing rates of SemEval 2013 test pairs under one convention", "", f"Status: {rc.STATUS}.", "",
         f"DrugBank release: version {o['drugbank_release']['version']}, exported on {o['drugbank_release']['exported_on']}. Resolution is the experiment 5 rule "
         "(`resolve`), unresolvable pairs are those where neither name maps to a DrugBank entry. Self pairs: the two names are equal after lowercase and strip "
         "(`drugbank._norm`), as in m3b. Primary number: share listed among resolvable pairs, Wilson 95%. The Wilson intervals treat instances as independent; "
         "sentence clustering is not applied.", ""]
    for title, key in (("Instance rows (the SemEval test rows, as m3b)", "instances"), ("Distinct unordered pairs (reference)", "unique_pairs")):
        L += [f"## {title}", ""]
        if key == "unique_pairs":
            L += [f"A distinct pair is counted in each class in which it has an instance; {o['pairs_with_both_classes']} pairs have both classes.", ""]
        rows = []
        for r in o[key]:
            if not r["n"]:
                continue
            rows.append([r["convention"], r["class"], r["scope"], r["n"], r["resolvable"], r["listed"], rc.f3(r["listed_share_of_resolvable"]),
                         rc.ci(r["ci95_resolvable"]), rc.f3(r["listed_share_of_all"]), rc.ci(r["ci95_all"]), r.get("n_self_pairs_removed", "")])
        L += rc.table(["convention", "class", "scope", "n", "resolvable", "listed", "listed / resolvable", "Wilson 95%", "listed / all", "Wilson 95%",
                       "self pairs removed"], rows) + [""]
    L += ["## Reproduction of stored values", ""]
    L += rc.table(["value", "recomputed (listed, resolvable, n)", "recomputed value", "stored", "match"],
                  [[r["value"], f"{r['recomputed']['listed']}, {r['recomputed']['resolvable']}, {r['recomputed']['n']}", rc.f3(r["recomputed"]["value"]),
                    json.dumps(r["stored"]), r["match"]] for r in o["reproduction"]]) + [""]
    L += ["## Which row each existing value uses", ""]
    L += rc.table(["existing value", "row", "denominator"], [[m["value"], m["row"], m["denominator"]] for m in o["denominator_map"]]) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(m3b.DEFAULT_ZIP))
    a = ap.parse_args()
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    semeval.download()
    test = semeval.load_pairs("test")
    table, table_source = load_cached_table(a.drugbank, str(rc.RUNS / "drugbank_table.pkl"))
    res = [resolve(r["drug_a"], r["drug_b"], table, lookup) for r in test]
    state, sides = np.array([x[0] for x in res]), np.array([x[1] for x in res])
    y = np.array([int(r["label_id"] != 0) for r in test])
    source = np.array([r["source"] for r in test])
    selfpair = np.array([drugbank._norm(r["drug_a"]) == drugbank._norm(r["drug_b"]) for r in test])
    keys = [tuple(sorted((r["drug_a"], r["drug_b"]))) for r in test]
    inst = instance_rows(y, source, selfpair, state, sides)
    uniq, both = pair_rows(test, y, source, selfpair, state, sides, keys)
    head = m3b.header(a.drugbank) if Path(a.drugbank).exists() else rc.load(rc.OUT / "c2_seen_reference.json")["drugbank_release"]
    dmap = [
        {"value": "0.763 (negatives)", "row": "self_pairs_excluded / negatives / pooled", "denominator": "resolvable pairs"},
        {"value": "0.727", "row": "self_pairs_excluded / positives / pooled", "denominator": "resolvable pairs (positives have no self pairs)"},
        {"value": "0.785", "row": "self_pairs_excluded / negatives / DDI-DrugBank", "denominator": "all pairs, unresolvable counted as not listed"},
        {"value": "0.763 (true positive rate)", "row": "self_pairs_excluded / positives / DDI-DrugBank", "denominator": "all pairs; equal to the resolvable denominator here"}]
    out = {"drugbank_release": head, "table_source": table_source, "n_table_names": len(table), "n_test_rows": len(test), "n_self_pairs": int(selfpair.sum()),
           "self_pairs_by_source": {s: int((selfpair & (source == s)).sum()) for s in ("DrugBank", "MedLine")},
           "instances": flat(inst), "unique_pairs": flat(uniq), "pairs_with_both_classes": both, "reproduction": reproduce(inst),
           "denominator_map": dmap}
    rc.write("d9_listing_conventions", out, md(out))
    print(md(out))


if __name__ == "__main__":
    main()
