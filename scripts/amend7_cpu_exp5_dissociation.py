import argparse
import json
import pickle
from collections import Counter
from pathlib import Path

import numpy as np

from amend7_cpu_common import (BOOT_SEED, ci, cohort_arrays, drugbank_score, ev, f3, paired_draws,
                               seed_mean, single, stats, summarize_draws, write)
from ddiood import config, drugbank, semeval

CLASSES = ("false", "mechanism", "effect", "advise", "int")


def load_table(path, cache):
    if cache and Path(cache).exists():
        return pickle.loads(Path(cache).read_bytes())
    table = drugbank.load_interactions(path)
    if cache:
        Path(cache).write_bytes(pickle.dumps(table))
    return table


def forms(d, lookup):
    out = {drugbank._norm(d)}
    if d in lookup:
        out |= {drugbank._norm(lookup[d]["normalized"]), drugbank._norm(lookup[d]["canonicalized"])}
    return out


def resolve(a, b, table, lookup):
    fa, fb = forms(a, lookup), forms(b, lookup)
    ea = next((table[n] for n in fa if n in table), None)
    eb = next((table[n] for n in fb if n in table), None)
    if ea is None and eb is None:
        return "unresolvable", 0
    side = 2 if ea is not None and eb is not None else 1
    if (ea and fb & ea) or (eb and fa & eb):
        return "positive", side
    return "negative", side


def pair_key(a, b):
    return tuple(sorted((a, b)))


def class_rows(test, state, sides, comention, sel_name, sel):
    rows = []
    for cls in CLASSES + ("any positive",):
        m = sel & (np.array([r["label"] != "false" for r in test]) if cls == "any positive"
                   else np.array([r["label"] == cls for r in test]))
        st, sd = state[m], sides[m]
        resolvable = st != "unresolvable"
        both = sd == 2
        rows.append({"subset": sel_name, "label": cls, "n": int(m.sum()),
                     "unresolvable": int((~resolvable).sum()), "one_side_resolved": int((sd == 1).sum()),
                     "both_resolved": int(both.sum()), "listed": int((st == "positive").sum()),
                     "listed_share_of_resolvable": float((st[resolvable] == "positive").mean()) if resolvable.any() else None,
                     "listed_share_of_both_resolved": float((st[both] == "positive").mean()) if both.any() else None,
                     "n_pairs_comentioned_in_train": int(comention[m].sum())})
    return rows


def auroc_row(name, y, s, groups, boot):
    d = ev.boot_auroc(y, s, groups, None, boot)
    lo, hi = ev.interval(d)
    return {"subset": name, "n": int(len(y)), "n_pos": int(np.sum(y)), "auroc": ev.auroc(y, s), "ci95": [lo, hi]}


def grid(truth, test, sid, db_test, boot):
    systems = {
        "DrugBank lookup": {"semeval": db_test, "novel": drugbank_score(truth, "ood"), "older_clean": drugbank_score(truth, "oodold"),
                            "n_seeds": None},
        "b1names-biomedbert (names only)": {"semeval": seed_mean("b1names-biomedbert", "test_names")[0],
                                            "novel": seed_mean("b1names-biomedbert", "ood_names")[0],
                                            "older_clean": seed_mean("b1names-biomedbert", "oodold_names")[0],
                                            "n_seeds": seed_mean("b1names-biomedbert", "test_names")[1]},
        "llm-qwen-names (names only)": {"semeval": single("llm-qwen-names", "test"), "novel": single("llm-qwen-names", "ood"),
                                        "older_clean": single("llm-qwen-names", "oodold"), "n_seeds": 1},
        "b2sentence-biomedbert (sentence model; OOD has no sentence)": {
            "semeval": seed_mean("b2sentence-biomedbert", "test_sentence")[0],
            "novel": seed_mean("b2sentence-biomedbert", "ood_empty")[0],
            "older_clean": seed_mean("b2sentence-biomedbert", "oodold_empty")[0],
            "n_seeds": seed_mean("b2sentence-biomedbert", "test_sentence")[1]}}
    y = np.asarray(truth.test_y)
    rows = []
    for name, sc in systems.items():
        r = auroc_row("SemEval test", y, sc["semeval"], sid, boot)
        rows.append({"system": name, "labels": "SemEval 2013 test (sentence-level)", "tier": "A", "statistic": "pooled AUROC",
                     "n": r["n"], "n_drugs": None, "value": r["auroc"], "ci95": r["ci95"], "n_seeds": sc["n_seeds"],
                     "interval": "sentence-cluster bootstrap"})
    for cohort in ("novel", "older_clean"):
        for tier in ("A", "B"):
            c = cohort_arrays(truth, cohort, tier)
            names = list(systems)
            scores = [systems[n][cohort][c["mask"]] for n in names]
            d = paired_draws(c["y"], scores, c["g"], c["q"], boot, BOOT_SEED[cohort])
            for i, n in enumerate(names):
                s = summarize_draws(stats.stratified_auroc(c["y"], scores[i], c["g"]), d[i])
                rows.append({"system": n, "labels": f"{cohort} pair labels", "tier": tier, "statistic": "within-drug AUROC",
                             "n": int(len(c["y"])), "n_drugs": int(len(set(c["g"]))), "value": s["value"], "ci95": s["ci95"],
                             "n_seeds": systems[n]["n_seeds"], "interval": "two-way cluster bootstrap over OOD drugs and partners",
                             "note": "circular: tier B is defined by DrugBank agreement" if tier == "B" and n == "DrugBank lookup" else ""})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(config.DRUGBANK_XML))
    ap.add_argument("--cache", default=None)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    table = load_table(a.drugbank, a.cache)
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    semeval.download()
    test, train = semeval.load_pairs("test"), semeval.load_pairs("train")
    truth = ev.load_truth()
    if [int(r["label_id"] != 0) for r in test] != list(truth.test_y):
        raise ValueError("SemEval test order differs from the evaluation truth")
    res = [resolve(r["drug_a"], r["drug_b"], table, lookup) for r in test]
    state = np.array([x[0] for x in res])
    sides = np.array([x[1] for x in res])
    train_pairs = {pair_key(r["drug_a"], r["drug_b"]) for r in train}
    comention = np.array([pair_key(r["drug_a"], r["drug_b"]) in train_pairs for r in test])
    selfpair = np.array([r["drug_a"] == r["drug_b"] for r in test])
    sid = np.array([r["sentence_id"] for r in test])
    y = np.asarray(truth.test_y)
    score = (state == "positive").astype(float)
    every = np.ones(len(test), bool)
    by_class = []
    for name, sel in (("all", every), ("pair co-mentioned in a SemEval train sentence", comention),
                      ("pair not co-mentioned in SemEval train", ~comention), ("both drugs resolved in DrugBank", sides == 2)):
        by_class += class_rows(test, state, sides, comention, name, sel)
    aucs = []
    for name, sel in (("all pairs, unresolvable counted as not listed", every), ("both drugs resolved", sides == 2),
                      ("co-mentioned in SemEval train", comention), ("not co-mentioned in SemEval train", ~comention),
                      ("both resolved and co-mentioned in train", (sides == 2) & comention),
                      ("both resolved and not co-mentioned in train", (sides == 2) & ~comention),
                      ("excluding self pairs", ~selfpair)):
        aucs.append(auroc_row(name, y[sel], score[sel], sid[sel], a.boot))
    keys = [pair_key(r["drug_a"], r["drug_b"]) for r in test]
    lab = {}
    for k, v in zip(keys, y):
        lab.setdefault(k, set()).add(int(v))
    counts = Counter(keys)
    multi = [k for k in lab if counts[k] > 1]
    conflict = [k for k in multi if len(lab[k]) == 2]
    dedup = {}
    for k, st, v in zip(keys, state, y):
        dedup.setdefault(k, (st, set()))[1].add(int(v))
    neg_only = [st for st, v in dedup.values() if v == {0} and st != "unresolvable"]
    pos_only = [st for st, v in dedup.values() if v == {1} and st != "unresolvable"]
    distinct = {"n_distinct_pairs": len(dedup), "n_pairs_with_repeat_instances": len(multi),
                "n_repeat_pairs_with_conflicting_labels": len(conflict),
                "distinct_negative_only_pairs_resolvable": len(neg_only),
                "distinct_negative_only_listed_share": float(np.mean([s == "positive" for s in neg_only])) if neg_only else None,
                "distinct_positive_only_pairs_resolvable": len(pos_only),
                "distinct_positive_only_listed_share": float(np.mean([s == "positive" for s in pos_only])) if pos_only else None}
    neg = y == 0
    pos = y == 1
    resolvable = state != "unresolvable"
    headline = {"n_test_pairs": int(len(test)), "n_negative": int(neg.sum()), "n_positive": int(pos.sum()),
                "unresolvable": int((~resolvable).sum()), "one_side_resolved": int((sides == 1).sum()),
                "both_resolved": int((sides == 2).sum()), "self_pairs": int(selfpair.sum()),
                "negatives_listed": int((neg & (state == "positive")).sum()),
                "negatives_resolvable": int((neg & resolvable).sum()),
                "negatives_listed_share_of_resolvable": float((state[neg & resolvable] == "positive").mean()),
                "negatives_listed_share_of_both_resolved": float((state[neg & (sides == 2)] == "positive").mean()),
                "positives_listed_share_of_resolvable": float((state[pos & resolvable] == "positive").mean()),
                "positives_listed_share_of_both_resolved": float((state[pos & (sides == 2)] == "positive").mean())}
    g = grid(truth, test, sid, score, a.boot)
    out = {"status": "Amendment 7 experiment 5, exploratory, post hoc",
           "method": "DrugBank lookup as in ddiood.drugbank.validate (names and RxNorm normalized forms from artifacts/vocab/drug_lookup.json; "
                     "listed if either drug's DrugBank interaction list names the other) applied to the 2,810 SemEval 2013 test pairs; "
                     "unresolvable means neither drug was found; AUROC intervals resample sentences (1,000 draws); "
                     "co-mention means the unordered pair also occurs in a SemEval train sentence (every test pair co-occurs in its own test sentence by construction)",
           "drugbank_source": Path(a.drugbank).name, "headline": headline, "by_class": by_class, "auroc": aucs,
           "distinct_pairs": distinct, "grid_2x2": g}
    h = headline
    md = ["# Experiment 5: double dissociation (DrugBank lookup on SemEval 2013 test)", "",
          f"n = {h['n_test_pairs']} test pairs ({h['n_positive']} positive, {h['n_negative']} negative); "
          f"{h['unresolvable']} unresolvable (neither drug in DrugBank), {h['one_side_resolved']} with one drug resolved, "
          f"{h['both_resolved']} with both resolved; {h['self_pairs']} self pairs.", "",
          f"SemEval negatives that DrugBank lists as interacting: {h['negatives_listed']} of {h['negatives_resolvable']} resolvable "
          f"({f3(h['negatives_listed_share_of_resolvable'])}); {f3(h['negatives_listed_share_of_both_resolved'])} when both drugs resolve. "
          f"Positives listed: {f3(h['positives_listed_share_of_resolvable'])} of resolvable, {f3(h['positives_listed_share_of_both_resolved'])} with both resolved.", "",
          "## By SemEval label", "", "| subset | label | n | unresolvable | one side | both resolved | listed | listed / resolvable | listed / both resolved | co-mentioned in train |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in by_class:
        md.append(f"| {r['subset']} | {r['label']} | {r['n']} | {r['unresolvable']} | {r['one_side_resolved']} | {r['both_resolved']} | "
                  f"{r['listed']} | {f3(r['listed_share_of_resolvable'])} | {f3(r['listed_share_of_both_resolved'])} | {r['n_pairs_comentioned_in_train']} |")
    md += ["", "## Lookup AUROC against SemEval labels", "", "| subset | n | n_pos | AUROC | 95% CI |", "| --- | --- | --- | --- | --- |"]
    md += [f"| {r['subset']} | {r['n']} | {r['n_pos']} | {f3(r['auroc'])} | {ci(r['ci95'])} |" for r in aucs]
    d = distinct
    md += ["", f"Distinct unordered pairs: {d['n_distinct_pairs']}; {d['n_pairs_with_repeat_instances']} occur more than once, "
               f"{d['n_repeat_pairs_with_conflicting_labels']} of them with both a positive and a negative instance. "
               f"Among distinct pairs labelled only negative and resolvable ({d['distinct_negative_only_pairs_resolvable']}), "
               f"DrugBank lists {f3(d['distinct_negative_only_listed_share'])}; among only-positive ({d['distinct_positive_only_pairs_resolvable']}), "
               f"{f3(d['distinct_positive_only_listed_share'])}.",
           "", "## 2x2 figure data", "", "| system | labels | tier | statistic | n | drugs | value | 95% CI | note |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    md += [f"| {r['system']} | {r['labels']} | {r['tier']} | {r['statistic']} | {r['n']} | {r['n_drugs'] or ''} | {f3(r['value'])} | "
           f"{ci(r['ci95'])} | {r.get('note', '')} |" for r in g]
    write("exp5_dissociation", out, "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
