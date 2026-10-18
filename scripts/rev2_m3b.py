import argparse
import json
import pickle
import re
import zipfile
from pathlib import Path

import numpy as np

import rev2_common as rc
from amend7_cpu_common import BOOT_SEED, cohort_arrays, fast_within_auroc, paired_draws
from amend7_cpu_exp5_dissociation import pair_key, resolve
from ddiood import config, drugbank, semeval
from ddiood import evaluate2 as ev

DEFAULT_ZIP = Path.home() / "Downloads" / "drugbank_all_full_database.xml.zip"
BASELINES = rc.ROOT / "results" / "corrected" / "baselines.json"
BASELINE_SCORES = rc.ROOT / "results" / "corrected" / "baseline_scores.json"
EXP5 = rc.ROOT / "results" / "revision" / "amend7" / "cpu" / "exp5_dissociation.json"


def header(path):
    path = str(path)
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        name = [n for n in z.namelist() if n.endswith(".xml")][0]
        head = z.open(name).read(4096).decode("utf-8", "replace")
    else:
        head = open(path, "rb").read(4096).decode("utf-8", "replace")
    m = re.search(r"<drugbank\b[^>]*>", head)
    tag = m.group(0) if m else ""
    ver = re.search(r'\bversion="([^"]+)"', tag)
    exp = re.search(r'\bexported-on="([^"]+)"', tag)
    return {"file": Path(path).name, "version": ver.group(1) if ver else None, "exported_on": exp.group(1) if exp else None,
            "root_element": tag}


def load_table(path, cache):
    if cache and Path(cache).exists():
        return pickle.loads(Path(cache).read_bytes())
    table = drugbank.load_interactions(path)
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        Path(cache).write_bytes(pickle.dumps(table))
    return table


def rates(states, sides):
    states, sides = np.asarray(states), np.asarray(sides)
    n = len(states)
    listed = int((states == "positive").sum())
    res = int((states != "unresolvable").sum())
    both = int((sides == 2).sum())
    lb = int(((states == "positive") & (sides == 2)).sum())
    return {"n": n, "resolvable": res, "both_resolved": both, "listed": listed,
            "listed_share_of_all": listed / n if n else None, "ci95_all": rc.wilson(listed, n),
            "listed_share_of_resolvable": listed / res if res else None, "ci95_resolvable": rc.wilson(listed, res),
            "listed_share_of_both_resolved": lb / both if both else None, "ci95_both_resolved": rc.wilson(lb, both)}


def random_pairs(lookup, table, n, seed, one_per_cui):
    keys = sorted(lookup)
    if one_per_cui:
        seen, kept = set(), []
        for k in keys:
            if lookup[k]["rxcui"] not in seen:
                seen.add(lookup[k]["rxcui"])
                kept.append(k)
        keys = kept
    rng = np.random.RandomState(seed)
    st, sd, drawn = [], [], 0
    while len(st) < n:
        i, j = rng.randint(0, len(keys), 2)
        drawn += 1
        a, b = keys[i], keys[j]
        if lookup[a]["rxcui"] == lookup[b]["rxcui"]:
            continue
        s, side = resolve(a, b, table, lookup)
        st.append(s)
        sd.append(side)
    return {"n_names": len(keys), "draws_including_rejected": drawn, **rates(st, sd)}


def auroc_row(name, y, s, groups, boot, seed):
    lo, hi = ev.interval(ev.boot_auroc(y, s, groups, None, boot, seed))
    pos, neg = y == 1, y == 0
    tpr = float(s[pos].mean()) if pos.any() else None
    fpr = float(s[neg].mean()) if neg.any() else None
    return {"subset": name, "n": int(len(y)), "n_pos": int(y.sum()), "n_neg": int(neg.sum()), "listed": int(s.sum()),
            "tpr_listed_share_of_positives": tpr, "fpr_listed_share_of_negatives": fpr,
            "auroc": ev.auroc(y, s) if pos.any() and neg.any() else None, "ci95": [lo, hi]}


def decomposition(y, s, com, sel, label):
    y, s, com = y[sel], s[sel], com[sel]
    pos, neg = y == 1, y == 0
    out = {"set": label, "n": int(len(y))}
    for name, m in (("co-mentioned", com), ("not co-mentioned", ~com)):
        out[name] = {"n": int(m.sum()), "n_pos": int((m & pos).sum()), "n_neg": int((m & neg).sum()),
                     "share_of_all_positives": float((m & pos).sum() / pos.sum()), "share_of_all_negatives": float((m & neg).sum() / neg.sum()),
                     "positive_rate": float(y[m].mean()), "tpr": float(s[m & pos].mean()), "fpr": float(s[m & neg].mean())}
        out[name]["auroc"] = 0.5 * (1 + out[name]["tpr"] - out[name]["fpr"])
    c, nc = out["co-mentioned"], out["not co-mentioned"]
    tpr = c["share_of_all_positives"] * c["tpr"] + nc["share_of_all_positives"] * nc["tpr"]
    fpr = c["share_of_all_negatives"] * c["fpr"] + nc["share_of_all_negatives"] * nc["fpr"]
    out["pooled"] = {"tpr": tpr, "fpr": fpr, "auroc": 0.5 * (1 + tpr - fpr), "auroc_direct": ev.auroc(y, s)}
    out["counterfactual_pooled_auroc_if_negatives_had_positive_mix"] = 0.5 * (1 + tpr - (c["share_of_all_positives"] * c["fpr"] + nc["share_of_all_positives"] * nc["fpr"]))
    return out


def string_match(truth, boot):
    bl = rc.load(BASELINES)
    sc = rc.load(BASELINE_SCORES)
    out = {"pooled_from_baselines_json": {}, "within_drug": {}}
    for cohort in ("novel", "older"):
        b = bl[cohort]["baselines"]["non_di_label_string_match"]
        out["pooled_from_baselines_json"][cohort] = {"n": bl[cohort]["n"], "n_pos": bl[cohort]["n_pos"], "auroc": b["auroc"],
                                                     "ci95": [b["auroc_ci95"]["lower"], b["auroc_ci95"]["upper"]],
                                                     "bootstrap": bl["bootstrap"], "auprc": b["auprc"], "binary_f1": b["binary_f1"],
                                                     "mcc": b["mcc"], "confusion": b["confusion"],
                                                     "cohort_note": "Novel 438 pairs; 'older' is the full Older cohort (1944 pairs), not Older-clean"}
    for cohort, key in (("novel", "novel"), ("older_clean", "older")):
        c = cohort_arrays(truth, cohort, "A")
        s = np.asarray(sc[key]["non_di_label_string_match"], float)
        if len(s) != len(c["mask"]):
            raise ValueError("baseline scores do not align with the cohort")
        s = s[c["mask"]]
        d = paired_draws(c["y"], [s], c["g"], c["q"], boot, BOOT_SEED[cohort])[0]
        out["within_drug"][cohort] = {"n": int(len(s)), "n_drugs": int(len(set(c["g"]))), "auroc_within": fast_within_auroc(c["y"], s, c["g"]),
                                      "ci95": rc.pct(d), "pooled_auroc": ev.auroc(c["y"], s)}
    return out


def md(o):
    h = o["drugbank_release"]
    L = ["# M3b: DrugBank listing rates, SemEval source split and the string-match baseline", "", f"Status: {rc.STATUS}.", "",
         f"DrugBank release: version {h['version']}, exported on {h['exported_on']} (`{h['file']}`). Resolution is the experiment 5 rule.", "",
         "## (a) Listing rate of random vocabulary pairs against SemEval pairs", "",
         "Random: 10,000 unordered pairs of SemEval vocabulary names (keys of `artifacts/vocab/drug_lookup.json`) with different RxCUI, "
         "RandomState(1). Wilson 95% intervals.", "",
         "| set | n | resolvable | listed / all | listed / resolvable | 95% CI | listed / both resolved | 95% CI |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, r in o["listing_rates"].items():
        L.append(f"| {name} | {r['n']} | {r['resolvable']} | {rc.f3(r['listed_share_of_all'])} | {rc.f3(r['listed_share_of_resolvable'])} | "
                 f"{rc.ci(r['ci95_resolvable'])} | {rc.f3(r['listed_share_of_both_resolved'])} | {rc.ci(r['ci95_both_resolved'])} |")
    L += ["", "## (b) DrugBank lookup AUROC on SemEval test by source document", "",
          "Pooled AUROC against the binary SemEval label; unresolvable counted as not listed; sentence-cluster bootstrap, 1,000 draws, seed 42. "
          "For a 0/1 score AUROC = 0.5 (1 + TPR - FPR).", "",
          "| subset | n | positives | listed | TPR | FPR | AUROC | 95% CI |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["by_source"]:
        L.append(f"| {r['subset']} | {r['n']} | {r['n_pos']} | {r['listed']} | {rc.f3(r['tpr_listed_share_of_positives'])} | "
                 f"{rc.f3(r['fpr_listed_share_of_negatives'])} | {rc.f3(r['auroc'])} | {rc.ci(r['ci95'])} |")
    s = o["string_match"]
    L += ["", "## (c) Label string-match baseline", "",
          "`non_di_label_string_match`: 1 if the partner is named anywhere outside the Drug Interactions section of the OOD drug's label.", "",
          "| cohort | statistic | n | AUROC | 95% CI | source |", "| --- | --- | --- | --- | --- | --- |"]
    for c, r in s["pooled_from_baselines_json"].items():
        L.append(f"| {'Novel' if c == 'novel' else 'Older (full, 1944)'} | pooled | {r['n']} | {rc.f3(r['auroc'])} | {rc.ci(r['ci95'])} | baselines.json, two-way cluster bootstrap |")
    for c, r in s["within_drug"].items():
        L.append(f"| {c} | within-drug | {r['n']} | {rc.f3(r['auroc_within'])} | {rc.ci(r['ci95'])} | recomputed, two-way paired_draws (pooled on these rows {rc.f3(r['pooled_auroc'])}) |")
    L += ["", "## (d) Why both co-mention subgroups exceed the overall value", ""]
    for d in o["subgroups"]:
        c, nc, p = d["co-mentioned"], d["not co-mentioned"], d["pooled"]
        L += [f"Set: {d['set']} (n = {d['n']}).", "",
              "| subgroup | n | positives | negatives | share of all positives | share of all negatives | TPR | FPR | AUROC |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
              f"| co-mentioned in a SemEval train sentence | {c['n']} | {c['n_pos']} | {c['n_neg']} | {rc.f3(c['share_of_all_positives'])} | {rc.f3(c['share_of_all_negatives'])} | {rc.f3(c['tpr'])} | {rc.f3(c['fpr'])} | {rc.f3(c['auroc'])} |",
              f"| not co-mentioned | {nc['n']} | {nc['n_pos']} | {nc['n_neg']} | {rc.f3(nc['share_of_all_positives'])} | {rc.f3(nc['share_of_all_negatives'])} | {rc.f3(nc['tpr'])} | {rc.f3(nc['fpr'])} | {rc.f3(nc['auroc'])} |",
              f"| pooled | {d['n']} | | | | | {rc.f3(p['tpr'])} | {rc.f3(p['fpr'])} | {rc.f3(p['auroc'])} |", "",
              f"If the negatives had the positives' co-mention mix, the pooled AUROC would be {rc.f3(d['counterfactual_pooled_auroc_if_negatives_had_positive_mix'])}.", ""]
    L += [o["subgroup_explanation"], ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(DEFAULT_ZIP))
    ap.add_argument("--cache", default=None)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--n-random", type=int, default=10000)
    a = ap.parse_args()
    crit = rc.require_criteria()
    head = header(a.drugbank)
    table = load_table(a.drugbank, a.cache)
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    semeval.download()
    test, train = semeval.load_pairs("test"), semeval.load_pairs("train")
    truth = ev.load_truth()
    y = np.asarray(truth.test_y)
    if [int(r["label_id"] != 0) for r in test] != list(y):
        raise ValueError("SemEval test order differs from the evaluation truth")
    res = [resolve(r["drug_a"], r["drug_b"], table, lookup) for r in test]
    state = np.array([x[0] for x in res])
    sides = np.array([x[1] for x in res])
    score = (state == "positive").astype(float)
    selfpair = np.array([drugbank._norm(r["drug_a"]) == drugbank._norm(r["drug_b"]) for r in test])
    source = np.array([r["source"] for r in test])
    sid = np.array([r["sentence_id"] for r in test])
    train_pairs = {pair_key(r["drug_a"], r["drug_b"]) for r in train}
    com = np.array([pair_key(r["drug_a"], r["drug_b"]) in train_pairs for r in test])
    lr = {"random vocabulary pairs (names)": random_pairs(lookup, table, a.n_random, 1, False),
          "random vocabulary pairs (one name per RxCUI)": random_pairs(lookup, table, a.n_random, 1, True)}
    for name, m in (("SemEval test negatives", y == 0), ("SemEval test positives", y == 1),
                    ("SemEval test negatives, no self pairs", (y == 0) & ~selfpair), ("SemEval test positives, no self pairs", (y == 1) & ~selfpair)):
        lr[name] = rates(state[m], sides[m])
    for src in ("DrugBank", "MedLine"):
        for lab, v in (("negatives", 0), ("positives", 1)):
            m = (source == src) & (y == v)
            lr[f"SemEval test {lab}, DDI-{src}"] = rates(state[m], sides[m])
    by_source = []
    for src_name, ms in (("all sources", np.ones(len(y), bool)), ("DDI-DrugBank documents", source == "DrugBank"), ("DDI-MedLine abstracts", source == "MedLine")):
        for sp_name, mp in (("all pairs", np.ones(len(y), bool)), ("no self pairs", ~selfpair)):
            m = ms & mp
            r = auroc_row(f"{src_name}, {sp_name}", y[m], score[m], sid[m], a.boot, 42)
            r["n_self_pairs_removed"] = int((ms & selfpair).sum()) if sp_name == "no self pairs" else 0
            by_source.append(r)
    sub = [decomposition(y, score, com, np.ones(len(y), bool), "all 2810 SemEval test pairs, self pairs kept, unresolvable as not listed (the experiment 5 set behind 0.525, 0.591 and 0.529)"),
           decomposition(y, score, com, ~selfpair, "2521 pairs without self pairs")]
    d0 = sub[0]
    c, nc = d0["co-mentioned"], d0["not co-mentioned"]
    expl = (f"The three values use the same set: all 2,810 SemEval test pairs with the 289 self pairs kept and unresolvable pairs counted as not listed, "
            f"pooled AUROC of the 0/1 lookup, sentence bootstrap (Amendment 7 experiment 5). Both subgroups beat the pooled value because co-mention "
            f"is associated with both the label and the score (Simpson's paradox). Co-mentioned pairs are rarely positive ({c['n_pos']} of {c['n']}, "
            f"{rc.f3(c['positive_rate'])}) but are listed often (FPR {rc.f3(c['fpr'])}); not co-mentioned pairs are positive more often "
            f"({rc.f3(nc['positive_rate'])}) and listed less (FPR {rc.f3(nc['fpr'])}). Pooling weights the TPR by where the positives are "
            f"({rc.f3(nc['share_of_all_positives'])} of positives are not co-mentioned, so pooled TPR {rc.f3(d0['pooled']['tpr'])} sits near the "
            f"low subgroup TPR {rc.f3(nc['tpr'])}) and the FPR by where the negatives are ({rc.f3(c['share_of_all_negatives'])} of negatives are "
            f"co-mentioned, which pulls pooled FPR up to {rc.f3(d0['pooled']['fpr'])}). The pooled TPR minus FPR, {rc.f3(d0['pooled']['tpr'] - d0['pooled']['fpr'])}, "
            f"is smaller than in either subgroup ({rc.f3(c['tpr'] - c['fpr'])} and {rc.f3(nc['tpr'] - nc['fpr'])}), so 0.5 (1 + TPR - FPR) is "
            f"{rc.f3(d0['pooled']['auroc'])} overall against {rc.f3(c['auroc'])} and {rc.f3(nc['auroc'])}.")
    out = {"status": rc.STATUS, "criteria": crit["m3b"], "drugbank_release": head, "listing_rates": lr, "by_source": by_source,
           "n_self_pairs": int(selfpair.sum()), "self_pairs_by_source": {s: int((selfpair & (source == s)).sum()) for s in ("DrugBank", "MedLine")},
           "self_pairs_comentioned": int((selfpair & com).sum()), "string_match": string_match(truth, a.boot), "subgroups": sub,
           "subgroup_explanation": expl}
    e5 = {r["subset"]: r for r in rc.load(EXP5)["auroc"]}
    out["check_exp5"] = {"all": abs(by_source[0]["auroc"] - e5["all pairs, unresolvable counted as not listed"]["auroc"]) < 6e-4,
                         "co": abs(sub[0]["co-mentioned"]["auroc"] - e5["co-mentioned in SemEval train"]["auroc"]) < 6e-4,
                         "not_co": abs(sub[0]["not co-mentioned"]["auroc"] - e5["not co-mentioned in SemEval train"]["auroc"]) < 6e-4}
    text = md(out)
    rc.write("m3b_drugbank", out, text)
    print(text)
    print(out["check_exp5"])


if __name__ == "__main__":
    main()
