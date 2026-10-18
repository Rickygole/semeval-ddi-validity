import argparse
import csv
import json
import sys
from pathlib import Path

from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import stats

POST8 = ROOT / "results" / "revision" / "post8"
LABELS = ("yes", "no", "unsure")


def cp(k, n, a=0.05):
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": (k / n) if n else None, "ci95_exact": cp(k, n)}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_items(preds_path):
    d = json.loads(Path(preds_path).read_text())
    items = d["eval"]["items"]
    for x in items:
        if x["decision"] not in LABELS:
            raise ValueError(f"{x['item_id']}: decision {x['decision']} is not yes, no or unsure")
    return d, items


def confusion(items):
    tab = {a: {"1": 0, "0": 0} for a in LABELS}
    for x in items:
        tab[x["decision"]][str(x["current_label"])] += 1
    return tab


def agreement_current(items):
    conf = [(x["decision"] == "yes" and x["current_label"] == 1) or (x["decision"] == "no" and x["current_label"] == 0)
            for x in items]
    dec = [x["decision"] != "unsure" for x in items]
    k_dec = sum(c for c, d in zip(conf, dec) if d)
    return {"table_rows_decision_cols_current_label": confusion(items),
            "unsure_as_not_confirming": rate(sum(conf), len(items)), "decided_only": rate(k_dec, sum(dec)),
            "n_unsure": int(len(items) - sum(dec))}


def error_block(items, wrong):
    e = sum(x["decision"] == wrong for x in items)
    u = sum(x["decision"] == "unsure" for x in items)
    n = len(items)
    return {"n": n, "n_wrong": int(e), "n_unsure": int(u), "primary_decided_only": rate(e, n - u),
            "unsure_as_correct": rate(e, n), "unsure_as_error": rate(e + u, n)}


def class_errors(items):
    pos = [x for x in items if x["current_label"] == 1]
    neg = [x for x in items if x["current_label"] == 0]
    return {"positives_judged_no": error_block(pos, "no"), "negatives_judged_yes": error_block(neg, "yes")}


def by(items, field):
    keys = sorted({x[field] for x in items})
    return {k: class_errors([x for x in items if x[field] == k]) for k in keys}


def agreement_earlier(items, earlier):
    prior = {r["item_id"]: r["adjudication"] for r in earlier}
    rows = [(x, prior[x["item_id"]]) for x in items if x["item_id"] in prior]
    if len(rows) != len(items):
        raise ValueError(f"{len(items) - len(rows)} audit items have no earlier adjudication")

    def block(sel):
        a = [x["decision"] for x, _ in sel]
        b = [p for _, p in sel]
        both = [(u, v) for u, v in zip(a, b) if u != "unsure" and v != "unsure"]
        tab = {u: {v: 0 for v in LABELS} for u in LABELS}
        for u, v in zip(a, b):
            tab[u][v] += 1
        return {"n": len(sel), "table_rows_new_cols_earlier": tab, "agreement_three_way": rate(sum(u == v for u, v in zip(a, b)), len(a)),
                "agreement_both_decided": rate(sum(u == v for u, v in both), len(both)),
                "kappa_three_way": stats.kappa(a, b) if a else None,
                "kappa_both_decided": stats.kappa([u for u, _ in both], [v for _, v in both]) if both else None}

    return {"all": block(rows), "current_label_1": block([r for r in rows if r[0]["current_label"] == 1]),
            "current_label_0": block([r for r in rows if r[0]["current_label"] == 0])}


def attach_selection(items, key_rows):
    why = {r["item_id"]: r["selected_because"] for r in key_rows}
    return [{**x, "selected_because": why.get(x["item_id"], "random_sample")} for x in items]


def score(preds_path, earlier_path, key_path):
    d, items = load_items(preds_path)
    items = attach_selection(items, read_csv(key_path))
    audit = [x for x in items if x["set"] == "audit"]
    rand = [x for x in items if x["set"] == "random"]
    ids = [x["item_id"] for x in audit]
    res = {"status": "post hoc, descriptive; automated model adjudication from the Drug Interactions section only, not a human audit",
           "smoke": d.get("smoke"), "model": d.get("model"), "prompt_sha256": d.get("prompt_sha256"), "n_items": len(items), "n_audit": len(audit),
           "n_random": len(rand), "n_unique_prompts": d.get("n_unique_prompts"), "n_pairs_in_both_sets": d.get("n_pairs_in_both_sets"),
           "answer_mass": d.get("answer"), "non_answers_by_prompt": (d.get("answer") or {}).get("non_answers"),
           "non_answer_items": int(sum(x["non_answer"] for x in items)),
           "multi_chunk_items": int(sum(x["n_chunks"] > 1 for x in items)),
           "decisions": {s: {a: int(sum(x["decision"] == a for x in grp)) for a in LABELS}
                         for s, grp in (("audit", audit), ("random", rand))}}
    if audit:
        res["audit"] = {"scope": "the 255 flagged items; selected for suspected errors, so these are not population rates",
                        "agreement_with_current_label": agreement_current(audit), "errors": class_errors(audit),
                        "positives_by_selection": by([x for x in audit if x["current_label"] == 1], "selected_because"),
                        "by_cohort": by(audit, "cohort")}
        if earlier_path:
            res["audit"]["agreement_with_earlier_model_adjudication"] = agreement_earlier(audit, read_csv(earlier_path))
    if rand:
        res["random"] = {"scope": "random sample, 75 and 50 per class from Older primary and Novel; the population estimates by stratum",
                         "agreement_with_current_label": {c: agreement_current([x for x in rand if x["cohort"] == c])
                                                          for c in sorted({x["cohort"] for x in rand})},
                         "errors_by_cohort": by(rand, "cohort"), "errors_unweighted_pool_by_class": class_errors(rand),
                         "pool_note": "an unweighted pool of the strata samples, not a population rate",
                         "note": "intervals treat each stratum sample as binomial and ignore the finite-population correction, so they are conservative"}
    return res


def f3(v):
    return "NA" if v is None else f"{v:.3f}"


def rate_cell(r):
    lo, hi = r["ci95_exact"]
    return f"{r['k']}/{r['n']} = {f3(r['rate'])} [{f3(lo)}, {f3(hi)}]"


def error_rows(label, ce):
    rows = []
    for name, b in ce.items():
        rows.append(f"| {label} | {name} | {b['n']} | {b['n_unsure']} | {rate_cell(b['primary_decided_only'])} | "
                    f"{rate_cell(b['unsure_as_correct'])} | {rate_cell(b['unsure_as_error'])} |")
    return rows


def markdown(res):
    md = ["# R2b: open-model label adjudication (OLMo-2-1124-7B-Instruct, Drug Interactions section only)", "", res["status"], "", "SMOKE RUN, tiny stand-in model, not a result" if res["smoke"] else "Full run.", "",
          f"Items {res['n_items']} (audit {res['n_audit']}, random {res['n_random']}); non-answers {res['non_answer_items']} items "
          f"({res['non_answers_by_prompt']} prompts, chunks included); "
          f"multi-chunk items {res['multi_chunk_items']}; decisions {json.dumps(res['decisions'])}.", "",
          "| set | stratum and error type | n | unsure | wrong, unsure excluded | wrong, unsure as correct | wrong or unsure |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    if "audit" in res:
        md += error_rows("audit (all)", res["audit"]["errors"])
        for s, ce in res["audit"]["positives_by_selection"].items():
            md += error_rows(f"audit positives, {s}", {"positives_judged_no": ce["positives_judged_no"]})
        for c, ce in res["audit"]["by_cohort"].items():
            md += error_rows(f"audit {c}", ce)
    if "random" in res:
        for c, ce in res["random"]["errors_by_cohort"].items():
            md += error_rows(f"random {c}", ce)
        md += error_rows("random unweighted pool, not a population rate", res["random"]["errors_unweighted_pool_by_class"])
    if "audit" in res and "agreement_with_earlier_model_adjudication" in res["audit"]:
        md += ["", "## Agreement with the earlier model adjudication (255 audit items)", "",
               "| subset | n | three-way agreement | both decided | kappa three-way | kappa both decided |", "| --- | --- | --- | --- | --- | --- |"]
        for k, v in res["audit"]["agreement_with_earlier_model_adjudication"].items():
            md.append(f"| {k} | {v['n']} | {rate_cell(v['agreement_three_way'])} | {rate_cell(v['agreement_both_decided'])} | "
                      f"{f3(v['kappa_three_way'])} | {f3(v['kappa_both_decided'])} |")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--earlier", default=str(POST8 / "model_adjudication.csv"))
    ap.add_argument("--key", default=str(POST8 / "label_audit_key.csv"))
    ap.add_argument("--out", default=str(ROOT / "results" / "revision" / "rev2_colab"))
    a = ap.parse_args()
    res = score(a.preds, a.earlier, a.key)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "r2b.json").write_text(json.dumps(res, indent=1))
    (out / "r2b.md").write_text(markdown(res))
    print(out / "r2b.md")


if __name__ == "__main__":
    main()
