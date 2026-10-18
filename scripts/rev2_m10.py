import argparse

import numpy as np
from sklearn.metrics import f1_score

import rev2_common as rc
from ddiood import config, semeval
from ddiood.gpu_jobs import MODELS

POSITIVE = (1, 2, 3, 4)
SYSTEMS = (("b2sentence", "biomedbert", rc.SEEDS), ("b2mixed", "biomedbert", rc.SEEDS), ("b2sentence", "bertbase", rc.SEEDS),
           ("b2mixed", "bertbase", rc.SEEDS), ("b2sentence", "biobert", (42,)), ("b2mixed", "biobert", (42,)))
PUBLISHED = {"source": "Gu et al. 2021, Domain-Specific Language Model Pretraining for Biomedical Natural Language Processing, arXiv 2007.15779 (published in ACM Transactions on Computing for Healthcare), Table 6 (read from the arXiv PDF on 2026-10-17)",
             "metric": "micro F1 (Table 3 lists DDI: relation extraction, train 25296, dev 2496, test 5716, micro F1)",
             "split": "the original DDI 2013 corpus with a train/dev/test split of 624/90/191 files",
             "rows": {"PubMedBERT (uncased)": 82.36, "BioBERT (cased)": 80.88, "BERT (uncased)": 80.04, "BERT (cased)": 79.34,
                      "RoBERTa (cased)": 79.52, "SciBERT (uncased)": 81.06, "SciBERT (cased)": 81.22, "ClinicalBERT (cased)": 78.20,
                      "BlueBERT (cased)": 77.78},
             "not_verified": "The BioBERT paper (Lee et al. 2020) itself was not checked for a DDI figure"}


def micro(gold, pred, w=None):
    gold, pred = np.asarray(gold), np.asarray(pred)
    w = np.ones(len(gold)) if w is None else w
    tp = float((w * ((pred == gold) & (gold > 0))).sum())
    p = float((w * (pred > 0)).sum())
    g = float((w * (gold > 0)).sum())
    return tp, p, g


def f1_from(tp, p, g, extra_fn=0.0):
    den = p + g + extra_fn
    return 2 * tp / den if den else 0.0


def boot(gold, pred, sid, n, seed, extra_fn):
    codes = np.unique(sid, return_inverse=True)[1].ravel()
    G = codes.max() + 1
    rng = np.random.RandomState(seed)
    a, b = [], []
    for _ in range(n):
        w = np.bincount(rng.randint(0, G, G), minlength=G)[codes].astype(float)
        tp, p, g = micro(gold, pred, w)
        a.append(f1_from(tp, p, g))
        b.append(f1_from(tp, p, g, extra_fn * w.sum() / len(w)))
    return np.asarray(a), np.asarray(b)


def evaluate(gold, pred, sid, nboot, extra_fn):
    tp, p, g = micro(gold, pred)
    sk = float(f1_score(gold, pred, labels=list(POSITIVE), average="micro", zero_division=0))
    a, b = boot(gold, pred, sid, nboot, 42, extra_fn)
    per = f1_score(gold, pred, labels=list(POSITIVE), average=None, zero_division=0)
    return {"micro_f1_4class": f1_from(tp, p, g), "sklearn_micro_f1": sk, "ci95": rc.pct(a),
            "micro_f1_official_set_bound": f1_from(tp, p, g, extra_fn), "ci95_official_set_bound": rc.pct(b),
            "precision": tp / p if p else 0.0, "recall": tp / g if g else 0.0, "tp": int(tp), "predicted_positive": int(p), "gold_positive": int(g),
            "per_class_f1": {config.LABELS[c]: float(v) for c, v in zip(POSITIVE, per)},
            "binary_f1": float(f1_score((gold > 0).astype(int), (pred > 0).astype(int), zero_division=0))}


def agg(vals):
    v = np.asarray(vals, float)
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None, "min": float(v.min()), "max": float(v.max()), "n_seeds": int(len(v))}


def md(o):
    L = ["# M10: standard SemEval 2013 DDI evaluation", "", f"Status: {rc.STATUS}.", "",
         "Metric: micro-averaged F1 over mechanism, effect, advise and int, from the stored 5-class argmax predictions on `test_sentence` "
         f"(the predictions store class ids, so this is computed directly). Repository test set: {o['test']['n_scored']} pairs, {o['test']['positives_scored']} positive "
         f"(entity types drug and drug_n, `config.ENTITY_TYPES`). Official DDI 2013 extraction test set: {o['test']['n_official']} pairs, {o['test']['positives_official']} positive; "
         f"{o['test']['n_official'] - o['test']['n_scored']} pairs (entity types brand and group, {o['test']['positives_official'] - o['test']['positives_scored']} of them positive) were never scored. "
         "The 'official-set bound' counts those unscored positives as false negatives: it is what these predictions would score on the 5,716-pair set, a lower bound for a model "
         "that scored those pairs, not an estimate of it. 95% intervals: sentence-cluster bootstrap, 1,000 draws, seed 42.", "",
         "## Per seed", "", "| system | model | seed | micro F1 (2810 pairs) | 95% CI | official-set bound | 95% CI | precision | recall | mechanism | effect | advise | int | binary F1 |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["rows"]:
        pc = r["per_class_f1"]
        L.append(f"| {r['system']} | {r['model']} | {r['seed']} | {rc.f3(r['micro_f1_4class'])} | {rc.ci(r['ci95'])} | {rc.f3(r['micro_f1_official_set_bound'])} | "
                 f"{rc.ci(r['ci95_official_set_bound'])} | {rc.f3(r['precision'])} | {rc.f3(r['recall'])} | {rc.f3(pc['mechanism'])} | {rc.f3(pc['effect'])} | "
                 f"{rc.f3(pc['advise'])} | {rc.f3(pc['int'])} | {rc.f3(r['binary_f1'])} |")
    L += ["", "## Over seeds", "", "| system | model | pretrained | seeds | micro F1 mean | SD | range | official-set bound mean | binary F1 mean |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["summary"]:
        m, b, bf = r["micro_f1_4class"], r["micro_f1_official_set_bound"], r["binary_f1"]
        L.append(f"| {r['system']} | {r['model']} | {r['repo']} | {m['n_seeds']} | {rc.f3(m['mean'])} | {rc.f3(m['sd'])} | [{rc.f3(m['min'])}, {rc.f3(m['max'])}] | {rc.f3(b['mean'])} | {rc.f3(bf['mean'])} |")
    L += ["", "## Amendment 7 panel (one seed each, test_sentence)", "", "| checkpoint | micro F1 | 95% CI | official-set bound | binary F1 |", "| --- | --- | --- | --- | --- |"]
    L += [f"| {r['name']} | {rc.f3(r['micro_f1_4class'])} | {rc.ci(r['ci95'])} | {rc.f3(r['micro_f1_official_set_bound'])} | {rc.f3(r['binary_f1'])} |" for r in o["panel"]]
    p = o["published"]
    L += ["", "## Published figures", "", f"Source: {p['source']}. Metric: {p['metric']}. Split: {p['split']}.", "",
          "| model | DDI micro F1 (Table 6) |", "| --- | --- |"]
    L += [f"| {k} | {v:.2f} |" for k, v in p["rows"].items()]
    L += ["", "The comparison is not like-for-like: BLURB trains on all four entity types with its own 624/90/191-file split and scores all 5,716 test pairs, "
          "while the repository models were trained and scored on drug and drug_n pairs only, with at most five epochs of fine-tuning and no entity dummification. "
          f"{p['not_verified']}.", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    crit = rc.require_criteria()
    semeval.download()
    test = semeval.load_pairs("test")
    full = semeval.load_pairs("test", entity_types={"drug", "drug_n", "brand", "group"})
    gold = np.asarray([r["label_id"] for r in test])
    sid = np.asarray([r["sentence_id"] for r in test])
    extra = int(sum(r["label_id"] > 0 for r in full) - (gold > 0).sum())
    rows, summary = [], []
    for system, model, seeds in SYSTEMS:
        per = []
        for s in seeds:
            r = rc.load(rc.PREDS / f"{system}-{model}-s{s}.json")
            pred = np.asarray(r["eval"]["test_sentence"]["preds"], int)
            if len(pred) != len(gold):
                raise ValueError("prediction length differs from the test set")
            e = {"system": system, "model": model, "seed": s, **evaluate(gold, pred, sid, a.boot, extra)}
            rows.append(e)
            per.append(e)
        summary.append({"system": system, "model": model, "repo": MODELS[model],
                        **{k: agg([e[k] for e in per]) for k in ("micro_f1_4class", "micro_f1_official_set_bound", "binary_f1")}})
    panel = []
    for r in rc.panel_files():
        pred = np.asarray(r["eval"]["test_sentence"]["preds"], int)
        panel.append({"name": r["config"]["name"], "repo": r["config"].get("repo"), **evaluate(gold, pred, sid, a.boot, extra)})
    out = {"status": rc.STATUS, "criteria": crit["m10"], "five_class_predictions_stored": True,
           "test": {"n_scored": int(len(test)), "positives_scored": int((gold > 0).sum()), "n_official": int(len(full)),
                    "positives_official": int(sum(r["label_id"] > 0 for r in full)), "unscored_positives": extra},
           "rows": rows, "summary": summary, "panel": panel, "published": PUBLISHED}
    text = md(out)
    rc.write("m10_semeval_standard", out, text)
    print(text)


if __name__ == "__main__":
    main()
