import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import evaluate2 as ev
from ddiood import inputs, semeval, stats
from ddiood.prevalence import (all_positive_f1, binary_confusion, multiclass_confusion, prevalence_matched,
                               reference_row)

CORRECTED = ROOT / "results" / "corrected"
PREDS = ROOT / "results" / "revision" / "preds"
CPU = ROOT / "results" / "revision" / "cpu"
OUT = ROOT / "results" / "revision" / "eval"
DB = ROOT / "artifacts" / "ood"
LABELS = ["false", "mechanism", "effect", "advise", "int"]
ID_MATCH_KEYS = ("test_sentence", "test_names", "test_empty", "test_masked", "test")
OOD_MATCH_KEYS = ("ood_empty", "ood_names", "ood", "oodold_empty", "oodold_names")
DROPS = (("b2sentence/biomedbert", "test_sentence", "ood_empty"), ("b2mixed/biomedbert", "test_sentence", "ood_empty"),
         ("b2masked/biomedbert", "test_masked", "ood_empty"), ("b1names/biomedbert", "test_names", "ood_names"),
         ("b2sentence/bertbase", "test_sentence", "ood_empty"), ("b2mixed/bertbase", "test_sentence", "ood_empty"),
         ("b4/pubmedbert-embeddings-logreg", "test", "ood"), ("llm-biomistral-names", "test", "ood"),
         ("llm-qwen-names", "test", "ood"), ("llm-biomistral-rag", "test", "ood"), ("llm-qwen-rag", "test", "ood"))
LLM_JOBS = ("llm-biomistral-names", "llm-qwen-names", "llm-biomistral-rag", "llm-qwen-rag")


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def extra_systems(truth, test):
    out = []
    path = CPU / "b4-lr-s42.json"
    if path.exists():
        d = json.loads(path.read_text())
        if d["ood_hash"] != truth.sets["ood"]["hash"]:
            raise ValueError("B4 probabilities were made on a different OOD set")
        g = truth.sets["ood"]
        out.append({"group": "b4/pubmedbert-embeddings-logreg", "seeds": [42], "source": str(path.relative_to(ROOT)),
                    "evals": {"test": {"kind": "test", "y": np.asarray(truth.test_y), "y5": np.asarray(test["y5"]),
                                       "pred5": np.asarray(d["eval"]["test"]["preds"]),
                                       "p": np.asarray(d["eval"]["test"]["p"]),
                                       "pb": (np.asarray(d["eval"]["test"]["preds"]) != 0).astype(int),
                                       "g": test["sid"]},
                              "ood": {"kind": "ood", "y": np.asarray(g["y"]), "p": np.asarray(d["eval"]["ood"]["p"]),
                                      "pb": (np.asarray(d["eval"]["ood"]["preds"]) != 0).astype(int),
                                      "pred5": np.asarray(d["eval"]["ood"]["preds"]), "g": np.asarray(g["g"])}}})
    path = CORRECTED / "preds" / "krag_hybrid_k5_s42.json"
    rn = CORRECTED / "ood_pairs_random_negatives.csv"
    if path.exists() and rn.exists():
        d = json.loads(path.read_text())
        pairs = inputs.ood_as_pairs(read_csv(rn))
        if inputs.pairs_hash(pairs) == d["ood_hash"]:
            out.append({"group": "krag-schema1/biomedbert/hybrid-k5-c100 (random-negative 444-pair set, superseded)",
                        "seeds": [42], "source": str(path.relative_to(ROOT)), "hard_labels_only": True,
                        "evals": {"test": {"kind": "test", "y": np.asarray(truth.test_y), "y5": np.asarray(test["y5"]),
                                           "pred5": np.asarray(d["test_preds"]), "p": None,
                                           "pb": (np.asarray(d["test_preds"]) != 0).astype(int), "g": test["sid"]},
                                  "ood_random_negatives": {"kind": "ood", "y": np.asarray([p["y"] for p in pairs]),
                                                           "p": None, "pred5": np.asarray(d["ood_preds"]),
                                                           "pb": (np.asarray(d["ood_preds"]) != 0).astype(int),
                                                           "g": np.asarray([p["drug_a"] for p in pairs])}}})
    return out


def raw_preds(job_name):
    return json.loads((PREDS / f"{job_name}.json").read_text())["eval"]


def is_llm(a):
    return any(j["cfg"].get("kind") == "llm" for j in a["jobs"])


def glabel(gk, a):
    if is_llm(a):
        return "+".join(j["name"] for j in a["jobs"])
    return ev.label(gk)


def groups_for(e, test):
    return test["sid"] if e["kind"] == "test" else e["g"]


def confusion_tables(jobs, aggs, extras, test):
    per_job, per_group, multi = [], [], []
    for j in jobs:
        raw = raw_preds(j["name"])
        for key, e in j["evals"].items():
            per_job.append({"job": j["name"], "key": key, "n": int(len(e["y"])), **binary_confusion(e["y"], e["pb"])})
            if e["kind"] == "test":
                multi.append({"job": j["name"], "key": key, "labels": LABELS,
                              "matrix_rows_true_cols_pred": multiclass_confusion(test["y5"], raw[key]["preds"])})
    for gk, a in aggs.items():
        for key, e in a["evals"].items():
            per_group.append({"group": glabel(gk, a), "key": key, "n_seeds": len(e["seeds"]), "n": int(len(e["y"])),
                              "vote": "majority of seeds", **binary_confusion(e["y"], e["pb"])})
    for x in extras:
        for key, e in x["evals"].items():
            per_group.append({"group": x["group"], "key": key, "n_seeds": 1, "n": int(len(e["y"])), "vote": "single run",
                              **binary_confusion(e["y"], e["pb"])})
            if e["kind"] == "test":
                multi.append({"job": x["group"], "key": key, "labels": LABELS,
                              "matrix_rows_true_cols_pred": multiclass_confusion(e["y5"], e["pred5"])})
    return {"per_group": per_group, "per_job": per_job, "multiclass_id": multi}


def baseline_reference(bl):
    rows = []
    for name, tag in (("novel", "Novel OOD"), ("older", "Older OOD")):
        s = (bl or {}).get(name) or {}
        for b, r in s.get("baselines", {}).items():
            prev, c = r.get("prevalence"), r.get("confusion", {})
            rows.append({"group": f"baseline/{b}", "key": tag, "n": s["n"], "prevalence": prev, "f1": r.get("binary_f1"),
                         "f1_all_positive": all_positive_f1(prev), "f1_minus_all_positive": r.get("binary_f1") - all_positive_f1(prev),
                         "mcc": r.get("mcc"), "balanced_accuracy": r.get("balanced_accuracy"), "auroc": r.get("auroc"),
                         "auprc": r.get("auprc"), "auprc_minus_prevalence": r.get("auprc") - prev, **c})
    return rows


def reference_tables(aggs, extras, test, bl, boot):
    rows = []
    for gk, a in aggs.items():
        for key, e in a["evals"].items():
            r = reference_row(e["y"], e["p"], e["pb"], groups_for(e, test), boot)
            rows.append({"group": glabel(gk, a), "key": key, "n_seeds": len(e["seeds"]), **r})
    for x in extras:
        for key, e in x["evals"].items():
            r = reference_row(e["y"], e["p"], e["pb"], groups_for(e, test), boot)
            rows.append({"group": x["group"], "key": key, "n_seeds": 1, **r})
    return rows + baseline_reference(bl)


def matched_tables(aggs, extras, truth, n):
    ood_prev = float(np.mean(truth.sets["ood"]["y"]))
    id_prev = float(np.mean(truth.test_y))
    cells = [(glabel(gk, a), key, e) for gk, a in aggs.items() for key, e in a["evals"].items()]
    cells += [(x["group"], key, e) for x in extras for key, e in x["evals"].items()]
    rows = []
    for group, key, e in cells:
        if key in ID_MATCH_KEYS:
            target, direction = ood_prev, "SemEval test resampled to Novel OOD prevalence"
        elif key in OOD_MATCH_KEYS:
            target, direction = id_prev, "OOD resampled to SemEval test prevalence"
        else:
            continue
        m = prevalence_matched(e["y"], e["p"], e["pb"], target, n)
        raw = reference_row(e["y"], e["p"], e["pb"], None, 0)
        rows.append({"group": group, "key": key, "direction": direction, "original_prevalence": raw["prevalence"],
                     "original_f1": raw["f1"], "original_mcc": raw["mcc"], **m})
    drops = []
    index = {(r["group"], r["key"]): r for r in rows}
    for group, idk, oodk in DROPS:
        a, b = index.get((group, idk)), index.get((group, oodk))
        if a is None or b is None:
            continue
        drops.append({"group": group, "id_key": idk, "ood_key": oodk,
                      "id_f1_original": a["original_f1"], "id_f1_at_ood_prevalence": a["resampled"]["f1"]["mean"],
                      "ood_f1": b["original_f1"], "f1_drop_original": a["original_f1"] - b["original_f1"],
                      "f1_drop_prevalence_matched": a["resampled"]["f1"]["mean"] - b["original_f1"],
                      "id_mcc": a["original_mcc"], "ood_mcc": b["original_mcc"],
                      "f1_all_positive_id": all_positive_f1(a["original_prevalence"]),
                      "f1_all_positive_ood": all_positive_f1(b["original_prevalence"])})
    return {"target_ood_prevalence": ood_prev, "target_id_prevalence": id_prev, "n_resamples": n,
            "cells": rows, "drops": drops}


def drugbank_tables(truth, boot):
    out = []
    files = {"ood": DB / "drugbank_validation.csv", "oodold": DB / "drugbank_validation_old.csv"}
    for cohort, tag in (("novel", "ood"), ("older_full", "oodold"), ("older_clean", "oodold")):
        if not files[tag].exists():
            out.append({"cohort": cohort, "status": f"missing {files[tag].name}"})
            continue
        db = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in read_csv(files[tag])}
        s = truth.sets[tag]
        m = np.ones(len(s["y"]), bool) if cohort != "older_clean" else s["clean"]
        pairs = [p for p, keep in zip(s["pairs"], m) if keep]
        y = np.asarray([p["y"] for p in pairs])
        state = [db.get((p["drug_a"], p["drug_b"]), "missing") for p in pairs]
        score = np.asarray([1.0 if v == "positive" else 0.0 for v in state])
        g = np.asarray([p["drug_a"] for p in pairs])
        q = np.asarray([p["drug_b"] for p in pairs])
        r = reference_row(y, score, score.astype(int), g, boot)
        lo, hi = ev.interval(ev.boot_auroc(y, score, g, q, boot))
        out.append({"cohort": cohort, "tier": "A", "status": "ok", "n_drugs": int(len(set(g))),
                    "listed": int(sum(v == "positive" for v in state)),
                    "not_listed": int(sum(v == "negative" for v in state)),
                    "unresolvable": int(sum(v in ("unresolvable", "missing") for v in state)),
                    "auroc_within": stats.stratified_auroc(y, score, g), "auroc2_lo": lo, "auroc2_hi": hi, **r})
    return out


def load_test():
    semeval.download()
    rows = semeval.load_pairs("test")
    return {"y5": [r["label_id"] for r in rows], "sid": np.asarray([r["sentence_id"] for r in rows])}


def fmt_ci(r, k):
    v, lo, hi = r.get(k), r.get(f"{k}_lo"), r.get(f"{k}_hi")
    if v is None:
        return "NA"
    return f"{v:.3f}" if lo is None else f"{v:.3f} [{lo:.3f}, {hi:.3f}]"


def write(name, obj, md):
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1))
    (OUT / f"{name}.md").write_text(md)


def llm_section(rows, cols, title):
    keep = [r for r in rows if r.get("group") in LLM_JOBS]
    if not keep:
        return ""
    return f"\n## {title}\n\n" + ev.md_table(ev.clean(keep), cols)


def main():
    global PREDS, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--resamples", type=int, default=1000)
    ap.add_argument("--preds", default=str(PREDS))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    PREDS, OUT = Path(a.preds).resolve(), Path(a.out).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    truth = ev.load_truth()
    test = load_test()
    jobs = ev.load_jobs(PREDS, truth)
    aggs = ev.aggregate(jobs)
    extras = extra_systems(truth, test)
    bl = ev.load_baselines(CORRECTED / "baselines.json")
    sources = {"preds": PREDS.name if not PREDS.is_relative_to(ROOT) else str(PREDS.relative_to(ROOT)), "jobs": [j["name"] for j in jobs],
               "extra": [x.get("source") for x in extras], "ood_hash": truth.sets["ood"]["hash"],
               "ood_old_hash": truth.sets["oodold"]["hash"]}

    conf = confusion_tables(jobs, aggs, extras, test)
    md = ("# Confusion matrices\n\nGenerated by `scripts/revision_metrics.py`. A pair is predicted positive when the "
          "argmax of the five SemEval classes is not `false`. Seed-aggregated systems use the majority vote of their "
          "seeds. Rows marked superseded were made on the earlier 444-pair random-negative set and carry hard labels only."
          "\n\n## Binary, every system and evaluation set\n\n" +
          ev.md_table(ev.clean(conf["per_group"]), ["group", "key", "n_seeds", "vote", "n", "tp", "fp", "fn", "tn"]) +
          "\n## Five-class, SemEval test (rows true, columns predicted: " + ", ".join(LABELS) + ")\n\n")
    for m in conf["multiclass_id"]:
        if (m["job"].endswith("-s42") or "/" in m["job"] or m["job"] in LLM_JOBS) and not m["key"].startswith("swap"):
            md += f"### {m['job']}, {m['key']}\n\n" + ev.md_table(
                [{"true": LABELS[i], **{LABELS[k]: v for k, v in enumerate(row)}} for i, row in
                 enumerate(m["matrix_rows_true_cols_pred"])], ["true"] + LABELS) + "\n"
    md += llm_section(conf["per_group"], ["group", "key", "n", "tp", "fp", "fn", "tn"],
                      "LLM baselines, binary (single run each, label-word probabilities)")
    md += "\nPer-seed binary and five-class matrices for every job are in `confusion.json`.\n"
    write("confusion", {"sources": sources, **conf}, md)

    ref = reference_tables(aggs, extras, test, bl, a.boot)
    cols = ["group", "key", "n_seeds", "n", "prevalence", "f1", "f1_all_positive", "f1_minus_all_positive", "mcc_ci",
            "ba_ci", "auroc", "auprc", "auprc_minus_prevalence", "tp", "fp", "fn", "tn"]
    view = [{**r, "mcc_ci": fmt_ci(r, "mcc"), "ba_ci": fmt_ci(r, "balanced_accuracy")} for r in ref]
    md = ("# Prevalence-referenced metrics\n\nGenerated by `scripts/revision_metrics.py`. Every F1 is paired with the "
          "F1 of an all-positive classifier at the same prevalence (2p / (1 + p)), and every AUPRC with its prevalence, "
          "which is the AUPRC of an uninformative ranking. MCC and balanced accuracy carry 95% cluster bootstrap "
          f"intervals ({a.boot} resamples, seed 42) over SemEval sentences or OOD drugs. Cells whose pairs are all "
          "positive (`ood_sentence`, `oodold_sentence`) have no AUROC, AUPRC or MCC by definition and measure recall only."
          "\n\n" + ev.md_table(ev.clean(view), cols) +
          llm_section(view, cols, "LLM baselines (single run each, label-word probabilities)"))
    write("prevalence_reference", {"sources": sources, "rows": ref}, md)

    mt = matched_tables(aggs, extras, truth, a.resamples)
    flat = []
    for r in mt["cells"]:
        rs = r["resampled"]
        g = lambda k: "NA" if k not in rs or rs[k]["mean"] is None or np.isnan(rs[k]["mean"]) else \
            f"{rs[k]['mean']:.3f} [{rs[k]['lo']:.3f}, {rs[k]['hi']:.3f}]"
        flat.append({"group": r["group"], "key": r["key"], "direction": r["direction"],
                     "original_prevalence": r["original_prevalence"], "original_f1": r["original_f1"],
                     "target_prevalence": r["target_prevalence"], "n": r["n"], "n_pos": r["n_pos"],
                     "frozen_f1": r["frozen"]["f1"], "f1": g("f1"), "f1_all_positive": r["frozen"]["f1_all_positive"],
                     "mcc": g("mcc"), "balanced_accuracy": g("balanced_accuracy"), "auroc": g("auroc"), "auprc": g("auprc")})
    md = ("# Prevalence-matched evaluation (tracker E9)\n\nGenerated by `scripts/revision_metrics.py`. SemEval test cells "
          f"keep all 371 positives and draw negatives without replacement so that prevalence equals the Novel OOD "
          f"prevalence ({mt['target_ood_prevalence']:.4f}); OOD cells keep all negatives and draw positives so that "
          f"prevalence equals the SemEval test prevalence ({mt['target_id_prevalence']:.4f}). `frozen_f1` is the first "
          f"draw (seed 42); the other columns give the mean and the 2.5 and 97.5 percentiles over {mt['n_resamples']} draws. "
          "AUROC does not depend on prevalence and is shown as a check.\n\n" +
          ev.md_table(ev.clean(flat), ["group", "key", "direction", "original_prevalence", "original_f1", "target_prevalence", "n",
                             "n_pos", "frozen_f1", "f1", "f1_all_positive", "mcc", "balanced_accuracy", "auroc", "auprc"]) +
          "\n## In-distribution to OOD drop with and without prevalence matching\n\n" +
          ev.md_table(ev.clean(mt["drops"]), ["group", "id_key", "ood_key", "id_f1_original", "id_f1_at_ood_prevalence", "ood_f1",
                                    "f1_drop_original", "f1_drop_prevalence_matched", "id_mcc", "ood_mcc",
                                    "f1_all_positive_id", "f1_all_positive_ood"]))
    md += llm_section(flat, ["group", "key", "direction", "original_prevalence", "original_f1", "target_prevalence",
                             "frozen_f1", "f1", "f1_all_positive", "mcc", "balanced_accuracy", "auroc", "auprc"],
                      "LLM baselines (single run each)")
    write("prevalence_matched", {"sources": sources, **mt}, md)

    db = drugbank_tables(truth, a.boot)
    md = ("# DrugBank lookup reference (tracker E5)\n\nGenerated by `scripts/revision_metrics.py` from "
          "`artifacts/ood/drugbank_validation.csv` and `drugbank_validation_old.csv`, which `python -m ddiood.pipeline "
          "drugbank` writes from a local DrugBank copy (not redistributed). The lookup predicts an interaction when "
          "DrugBank lists the pair; unresolvable pairs count as not listed. Labels are tier A (FDA label). The lookup is "
          "circular on tier B, which is defined by agreement with DrugBank, so no tier B row is given. AUROC intervals "
          "are two-way cluster bootstrap over OOD drugs and partners; MCC and balanced accuracy intervals resample OOD drugs.\n\n" +
          ev.md_table(ev.clean([{**r, "mcc_ci": fmt_ci(r, "mcc"), "ba_ci": fmt_ci(r, "balanced_accuracy")} for r in db]),
                      ["cohort", "tier", "status", "n", "n_pos", "n_drugs", "listed", "not_listed", "unresolvable",
                       "prevalence", "auroc", "auroc2_lo", "auroc2_hi", "auroc_within", "auprc", "f1", "f1_all_positive",
                       "mcc_ci", "ba_ci", "precision", "recall", "specificity", "tp", "fp", "fn", "tn"]))
    write("drugbank_lookup", {"sources": sources, "rows": db}, md)
    print(json.dumps({"jobs": len(jobs), "groups": len(aggs), "extra": [x["group"] for x in extras],
                      "drugbank": [(r["cohort"], r.get("auroc"), r.get("mcc")) for r in db]}, default=str))


if __name__ == "__main__":
    main()
