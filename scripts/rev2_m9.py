import numpy as np
from sklearn.metrics import average_precision_score

import rev2_common as rc
from amend7_cpu_common import cohort_mask
from ddiood import evaluate2 as ev
from ddiood.metrics import extended

DECISIONS = rc.ROOT / "results" / "revision" / "eval" / "decisions.json"


def metrics(y, pred, p):
    y = np.asarray(y, int)
    pb = (np.asarray(pred, int) != 0).astype(int)
    e = extended(y, pb)
    prev = float(y.mean())
    return {"n": int(len(y)), "n_pos": int(y.sum()), "prevalence": prev, "tp": e["tp"], "fp": e["fp"], "fn": e["fn"], "tn": e["tn"],
            "f1": e["binary_f1"], "all_positive_f1": 2 * prev / (1 + prev), "f1_minus_all_positive": e["binary_f1"] - 2 * prev / (1 + prev),
            "precision": e["precision"], "recall": e["recall"], "mcc": e["mcc"], "balanced_accuracy": e["balanced_accuracy"],
            "auprc": float(average_precision_score(y, p)), "auprc_chance": prev, "auroc": ev.auroc(y, p)}


def panel(truth):
    ytest = np.asarray(truth.test_y)
    _, m_old = cohort_mask(truth, "older_clean")
    _, m_nov = cohort_mask(truth, "novel")
    y_old = np.asarray(truth.sets["oodold"]["y"])[m_old]
    y_nov = np.asarray(truth.sets["ood"]["y"])[m_nov]
    rows = []
    for r in rc.panel_files():
        e = r["eval"]
        for where, key, y, m in (("SemEval test, sentence", "test_sentence", ytest, None), ("Novel, names only", "ood_empty", y_nov, m_nov),
                                 ("Older-clean, names only", "oodold_empty", y_old, m_old)):
            pred, p = np.asarray(e[key]["preds"]), np.asarray(e[key]["p"], float)
            if m is not None:
                pred, p = pred[m], p[m]
            rows.append({"checkpoint": r["config"]["name"].replace("a7-panel-", ""), "set": where, "key": key, **metrics(y, pred, p)})
    return rows


def h2(truth):
    ytest = np.asarray(truth.test_y)
    rows, ratios = [], {}
    for system in ("b2sentence", "b2masked"):
        per = []
        for s in rc.SEEDS:
            e = rc.load(rc.PREDS / f"{system}-biomedbert-s{s}.json")["eval"]
            f = {}
            for key in ("test_sentence", "test_masked"):
                m = metrics(ytest, e[key]["preds"], np.asarray(e[key]["p"], float))
                f[key] = m["f1"]
                rows.append({"system": system, "seed": s, "key": key, **m})
            per.append(f["test_masked"] / f["test_sentence"] if f["test_sentence"] else float("nan"))
        ratios[system] = {"seed_mean_ratio": float(np.mean(per)), "per_seed": dict(zip(rc.SEEDS, per))}
    dec = rc.load(DECISIONS)
    ratios["b2sentence"]["decisions_json_H2a"] = dec["H2a"]["value"]["ratio"]
    ratios["b2masked"]["decisions_json_H2b"] = dec["H2b"]["value"]["ratio"]
    ratios["reproduces"] = bool(abs(ratios["b2sentence"]["seed_mean_ratio"] - dec["H2a"]["value"]["ratio"]) < 1e-5
                                and abs(ratios["b2masked"]["seed_mean_ratio"] - dec["H2b"]["value"]["ratio"]) < 1e-3)
    return rows, ratios


COLS = ("n", "prevalence", "tp", "fp", "fn", "tn", "f1", "all_positive_f1", "mcc", "balanced_accuracy", "auprc", "auroc")


def fmt(v):
    return str(v) if isinstance(v, int) else rc.f3(v)


def table(rows, lead):
    L = ["| " + " | ".join(lead + list(COLS)) + " |", "| " + " | ".join(["---"] * (len(lead) + len(COLS))) + " |"]
    for r in rows:
        L.append("| " + " | ".join([str(r[k]) for k in lead] + [fmt(r[c]) for c in COLS]) + " |")
    return L


def md(o):
    L = ["# M9: confusion matrices and threshold-free context for the panel and H2 F1s", "", f"Status: {rc.STATUS}.", "",
         "Positive prediction: 5-class argmax is not `false`. All-positive F1 = 2 prevalence / (1 + prevalence) on the same rows; AUPRC is average precision "
         "of P(interaction), chance = prevalence. Panel checkpoints are one seed each; OOD rows are tier A.", "", "## Amendment 7 panel", ""]
    for where in ("SemEval test, sentence", "Novel, names only", "Older-clean, names only"):
        L += [f"### {where}", ""] + table([r for r in o["panel"] if r["set"] == where], ["checkpoint"]) + [""]
    L += ["## H2 (BiomedBERT, per seed)", ""] + table(o["h2"], ["system", "seed", "key"])
    r = o["h2_ratio"]
    L += ["", f"Masked / sentence F1, mean over seeds: b2sentence {r['b2sentence']['seed_mean_ratio']:.6f} (decisions.json H2a {r['b2sentence']['decisions_json_H2a']}), "
          f"b2masked {r['b2masked']['seed_mean_ratio']:.4f} (H2b {r['b2masked']['decisions_json_H2b']}); reproduces: {r['reproduces']}.", ""]
    return "\n".join(L) + "\n"


def main():
    crit = rc.require_criteria()
    truth = ev.load_truth()
    hr, ratios = h2(truth)
    out = {"status": rc.STATUS, "criteria": crit["m9"], "panel": panel(truth), "h2": hr, "h2_ratio": ratios}
    text = md(out)
    rc.write("m9_confusion", out, text)
    print(text)


if __name__ == "__main__":
    main()
