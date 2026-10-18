import argparse
import csv
import json
import statistics
from pathlib import Path

from . import config, semeval
from .inputs import ood_as_pairs, pairs_hash
from .metrics import (binary_f1, bootstrap_drop, bootstrap_f1, cluster_bootstrap_f1, extended, macro_f1)

PRIMARY = {"B1 name-only": "b1_s42", "B2 sentence-context": "b2_s42", "B3 zero-shot LLM": "b3",
           "B4 retrieval+LR": "b4_s42", "B5 LLM+retrieval": "b5", "KnowledgeRAG-DDI": "krag_hybrid_k5_s42"}

ABLATIONS = {"BM25 only": "krag_bm25_k5_s42", "Dense only": "krag_dense_k5_s42",
             "Hybrid RRF (primary)": "krag_hybrid_k5_s42", "Top-1": "krag_hybrid_k1_s42",
             "Top-3": "krag_hybrid_k3_s42", "Top-5 (primary)": "krag_hybrid_k5_s42",
             "Excl. Clinical Pharmacology": "krag_excl_clinical_pharmacology_k5_s42",
             "Excl. Pharmacokinetics": "krag_excl_pharmacokinetics_k5_s42",
             "Excl. Warnings and Cautions": "krag_excl_warnings_and_cautions_k5_s42",
             "Excl. Mechanism of Action": "krag_excl_mechanism_of_action_k5_s42",
             "Contaminated (DI included)": "krag_contaminated_k5_s42",
             "Partner names masked in passages": "krag_masked_k5_s42"}


def r4(x):
    return None if x is None else round(float(x), 4)


def evaluate(preds_dir, ood_csv):
    P = {p.stem: json.loads(p.read_text()) for p in Path(preds_dir).glob("*.json")}
    y_te = [r["label_id"] for r in semeval.load_pairs("test")]
    ood = ood_as_pairs(list(csv.DictReader(open(ood_csv))))
    y_ood, groups = [p["y"] for p in ood], [p["group"] for p in ood]
    h = pairs_hash(ood)
    for name, r in P.items():
        if r.get("ood_hash") not in (None, h) or len(r["ood_preds"]) != len(ood):
            raise RuntimeError(f"{name}: predictions were made on a different OOD set")
    out = {"n_test": len(y_te), "n_ood": len(y_ood), "n_ood_pos": sum(y_ood), "n_ood_drugs": len(set(groups)),
           "all_positive_reference": {"test": r4(binary_f1(y_te, [1] * len(y_te))),
                                      "ood": r4(binary_f1(y_ood, [1] * len(y_ood)))}}
    t1, t2 = {}, {}
    for name, key in PRIMARY.items():
        if key not in P:
            t1[name] = "missing"
            continue
        r = P[key]
        t1[name] = {
            "id_f1": r4(binary_f1(y_te, r["test_preds"])), "id_macro_f1": r4(macro_f1(y_te, r["test_preds"])),
            "id_ci": bootstrap_f1(y_te, r["test_preds"]),
            "ood_f1": r4(binary_f1(y_ood, r["ood_preds"])), "ood_ci_pairs": bootstrap_f1(y_ood, r["ood_preds"]),
            "ood_ci_drug_cluster": cluster_bootstrap_f1(y_ood, r["ood_preds"], groups),
            "drop": r4(binary_f1(y_te, r["test_preds"]) - binary_f1(y_ood, r["ood_preds"])),
            "drop_ci": bootstrap_drop(y_te, r["test_preds"], y_ood, r["ood_preds"]),
        }
        t2[name] = {"id": {k: r4(v) for k, v in extended(y_te, r["test_preds"]).items()},
                    "ood": {k: r4(v) for k, v in extended(y_ood, r["ood_preds"]).items()}}
    out["table1"], out["table2"] = t1, t2
    seeds = {}
    for sys_key, label in (("b2", "B2 sentence-context"), ("krag_hybrid_k5", "KnowledgeRAG-DDI")):
        runs = {s: P[f"{sys_key}_s{s}"] for s in config.SEEDS if f"{sys_key}_s{s}" in P}
        if not runs:
            continue
        idf = {s: r4(binary_f1(y_te, r["test_preds"])) for s, r in runs.items()}
        odf = {s: r4(binary_f1(y_ood, r["ood_preds"])) for s, r in runs.items()}
        sd = lambda v: r4(statistics.stdev(v)) if len(v) > 1 else None
        seeds[label] = {"id_by_seed": idf, "ood_by_seed": odf,
                        "id_mean": r4(statistics.mean(idf.values())), "id_std": sd(list(idf.values())),
                        "ood_mean": r4(statistics.mean(odf.values())), "ood_std": sd(list(odf.values()))}
    out["multiseed"] = seeds
    if "b2_s42" in P:
        r = P["b2_s42"]
        idx = r.get("ood_sentence_index", [])
        sub_y = [y_ood[i] for i in idx]
        fair = {"id_sentence": r4(binary_f1(y_te, r["test_preds"])),
                "id_names": r4(binary_f1(y_te, r["test_nameonly_preds"])),
                "ood_names": r4(binary_f1(y_ood, r["ood_preds"])),
                "names_only_drop": r4(binary_f1(y_te, r["test_nameonly_preds"]) - binary_f1(y_ood, r["ood_preds"])),
                "ood_sentence_subset_n": len(idx), "ood_sentence_subset_pos": sum(sub_y)}
        if idx:
            fair["ood_sentence"] = r4(binary_f1(sub_y, r["ood_sentence_preds"]))
            fair["ood_names_same_subset"] = r4(binary_f1(sub_y, [r["ood_preds"][i] for i in idx]))
            if "krag_hybrid_k5_s42" in P:
                fair["krag_same_subset"] = r4(binary_f1(sub_y, [P["krag_hybrid_k5_s42"]["ood_preds"][i] for i in idx]))
            fair["all_positive_same_subset"] = r4(binary_f1(sub_y, [1] * len(sub_y)))
        out["fairness_2x2"] = fair
    out["table3"] = {name: ({"id_f1": r4(binary_f1(y_te, P[k]["test_preds"])),
                             "ood_f1": r4(binary_f1(y_ood, P[k]["ood_preds"]))} if k in P else "missing")
                     for name, k in ABLATIONS.items()}
    return out


def markdown(res):
    L = [f"OOD set: {res['n_ood']} pairs ({res['n_ood_pos']} positive) over {res['n_ood_drugs']} novel drugs. "
         f"All-positive reference F1: test {res['all_positive_reference']['test']}, OOD {res['all_positive_reference']['ood']}.", "",
         "| System | ID F1 | ID 95% CI | OOD F1 | OOD 95% CI (pairs) | OOD 95% CI (drug clusters) | Drop | Drop 95% CI |",
         "|---|---|---|---|---|---|---|---|"]
    for name, r in res["table1"].items():
        if r == "missing":
            L.append(f"| {name} | not run | | | | | | |")
            continue
        ci = lambda c: f"[{c['lower']:.4f}, {c['upper']:.4f}]"
        L.append(f"| {name} | {r['id_f1']:.4f} | {ci(r['id_ci'])} | {r['ood_f1']:.4f} | {ci(r['ood_ci_pairs'])} | "
                 f"{ci(r['ood_ci_drug_cluster'])} | {r['drop']:.4f} | {ci(r['drop_ci'])} |")
    L += ["", "| System | Split | F1 | Precision | Recall | Specificity | Balanced acc. | MCC |", "|---|---|---|---|---|---|---|---|"]
    for name, r in res["table2"].items():
        for split in ("id", "ood"):
            e = r[split]
            L.append(f"| {name} | {split} | {e['binary_f1']:.4f} | {e['precision']:.4f} | {e['recall']:.4f} | "
                     f"{e['specificity']:.4f} | {e['balanced_accuracy']:.4f} | {e['mcc']:.4f} |")
    if res.get("multiseed"):
        L += ["", "| System | ID F1 by seed | ID mean (std) | OOD F1 by seed | OOD mean (std) |", "|---|---|---|---|---|"]
        for name, s in res["multiseed"].items():
            L.append(f"| {name} | {s['id_by_seed']} | {s['id_mean']} ({s['id_std']}) | {s['ood_by_seed']} | {s['ood_mean']} ({s['ood_std']}) |")
    if res.get("fairness_2x2"):
        L += ["", "B2 fairness check: " + json.dumps(res["fairness_2x2"])]
    L += ["", "| Ablation | ID F1 | OOD F1 |", "|---|---|---|"]
    for name, r in res["table3"].items():
        L.append(f"| {name} | not run | |" if r == "missing" else f"| {name} | {r['id_f1']:.4f} | {r['ood_f1']:.4f} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default=str(config.RESULTS / "corrected" / "preds"))
    ap.add_argument("--ood", default=str(config.RESULTS / "corrected" / "ood_pairs.csv"))
    ap.add_argument("--out", default=str(config.RESULTS / "corrected"))
    a = ap.parse_args()
    res = evaluate(a.preds, a.ood)
    Path(a.out, "tables.json").write_text(json.dumps(res, indent=1))
    Path(a.out, "tables.md").write_text(markdown(res))
    print(markdown(res))
