import csv
import random
from urllib.parse import quote

import numpy as np

from .stats import kappa

INTERACTS = ("yes", "no", "unsure")
BASIS = ("named", "class-level", "none")
SHEET_FIELDS = ["item_id", "novel_drug", "partner", "openfda_label_query", "drug_interactions_section",
                "annotator", "interacts", "basis", "notes"]
DASHES = {chr(0x2013): "-", chr(0x2014): "-"}


def clean_text(s):
    for k, v in DASHES.items():
        s = s.replace(k, v)
    return " ".join(s.split())


def label_query(drug):
    return "https://api.fda.gov/drug/label.json?search=openfda.generic_name%3A%22" + quote(drug) + "%22&limit=1"


def _round_robin(rows, n, rng):
    by = {}
    for r in rows:
        by.setdefault(r["ood_drug"], []).append(r)
    drugs = sorted(by)
    rng.shuffle(drugs)
    for d in drugs:
        rng.shuffle(by[d])
    out = []
    while len(out) < n and any(by.values()):
        for d in drugs:
            if by[d] and len(out) < n:
                out.append(by[d].pop())
    if len(out) < n:
        raise ValueError(f"only {len(out)} rows available, {n} requested")
    return out


def sample(rows, n_pos=50, n_neg=50, seed=42):
    rng = random.Random(seed)
    pos = sorted((r for r in rows if str(r["label"]) == "1"), key=lambda r: (r["ood_drug"], r["semeval_drug"]))
    neg = sorted((r for r in rows if str(r["label"]) == "0"), key=lambda r: (r["ood_drug"], r["semeval_drug"]))
    items = _round_robin(pos, n_pos, rng) + _round_robin(neg, n_neg, rng)
    rng.shuffle(items)
    return [{"item_id": f"Q{i + 1:03d}", **r} for i, r in enumerate(items)]


def sheet_rows(items, di_text):
    return [{"item_id": it["item_id"], "novel_drug": it["ood_drug"], "partner": it["semeval_drug"],
             "openfda_label_query": label_query(it["ood_drug"]),
             "drug_interactions_section": clean_text(di_text.get(it["ood_drug"], "")),
             "annotator": "", "interacts": "", "basis": "", "notes": ""} for it in items]


def key_rows(items):
    return [{"item_id": it["item_id"], "novel_drug": it["ood_drug"], "partner": it["semeval_drug"],
             "fda_label": int(it["label"])} for it in items]


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def validate(rows, expected_ids):
    errors = []
    ids = [r.get("item_id", "") for r in rows]
    if sorted(ids) != sorted(expected_ids):
        errors.append("item ids do not match the sheet")
    for r in rows:
        v = (r.get("interacts") or "").strip().lower()
        b = (r.get("basis") or "").strip().lower()
        if v not in INTERACTS:
            errors.append(f"{r.get('item_id')}: interacts is {v!r}, expected one of {INTERACTS}")
        if b not in BASIS:
            errors.append(f"{r.get('item_id')}: basis is {b!r}, expected one of {BASIS}")
    return errors


def _answers(rows):
    return {r["item_id"]: ((r["interacts"] or "").strip().lower(), (r["basis"] or "").strip().lower()) for r in rows}


def bootstrap_kappa(a, b, n=1000, seed=42):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0:
        return None, None
    rng = np.random.RandomState(seed)
    draws = []
    for _ in range(n):
        i = rng.randint(0, len(a), len(a))
        draws.append(kappa(a[i], b[i]))
    d = np.asarray(draws, float)
    d = d[~np.isnan(d)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def _agreement(pred, gold):
    pred, gold = np.asarray(pred), np.asarray(gold)
    if len(pred) == 0:
        return None
    tp = int(((pred == 1) & (gold == 1)).sum())
    tn = int(((pred == 0) & (gold == 0)).sum())
    fp = int(((pred == 1) & (gold == 0)).sum())
    fn = int(((pred == 0) & (gold == 1)).sum())
    return {"n": int(len(pred)), "agreement": float((pred == gold).mean()), "kappa": float(kappa(pred, gold)),
            "label1_annot_yes": tp, "label0_annot_no": tn, "label0_annot_yes": fp, "label1_annot_no": fn}


def report(rows1, rows2, key, n_boot=1000, seed=42):
    ids = [r["item_id"] for r in key]
    for name, rows in (("annotator_1", rows1), ("annotator_2", rows2)):
        err = validate(rows, ids)
        if err:
            raise ValueError(f"{name}: " + "; ".join(err[:10]))
    a1, a2 = _answers(rows1), _answers(rows2)
    gold = {r["item_id"]: int(r["fda_label"]) for r in key}
    v1 = [a1[i][0] for i in ids]
    v2 = [a2[i][0] for i in ids]
    keep = [i for i in ids if a1[i][0] != "unsure" and a2[i][0] != "unsure"]
    k1, k2 = [a1[i][0] for i in keep], [a2[i][0] for i in keep]
    lo, hi = bootstrap_kappa(k1, k2, n_boot, seed)
    lo3, hi3 = bootstrap_kappa(v1, v2, n_boot, seed)
    agree = [i for i in keep if a1[i][0] == a2[i][0]]
    tier_c = [{"item_id": i, "consensus": int(a1[i][0] == "yes"), "fda_label": gold[i],
               "basis_1": a1[i][1], "basis_2": a2[i][1]} for i in agree]
    cats = list(INTERACTS)
    table = [[sum(1 for i in ids if a1[i][0] == x and a2[i][0] == y) for y in cats] for x in cats]
    out = {"n_items": len(ids), "n_label_positive": sum(gold.values()), "n_label_negative": len(ids) - sum(gold.values()),
           "n_unsure_either": len(ids) - len(keep), "n_both_decided": len(keep),
           "kappa_yes_no": float(kappa(k1, k2)) if keep else None, "kappa_yes_no_ci95": [lo, hi],
           "percent_agreement_yes_no": float(np.mean(np.asarray(k1) == np.asarray(k2))) if keep else None,
           "kappa_three_category": float(kappa(v1, v2)), "kappa_three_category_ci95": [lo3, hi3],
           "annotator_table_rows_1_cols_2": {"categories": cats, "counts": table},
           "n_disagreements_excluded": len(keep) - len(agree), "tier_c_size": len(tier_c),
           "tier_c_positive": sum(t["consensus"] for t in tier_c),
           "tier_c_class_level_positive": sum(1 for t in tier_c if t["consensus"] == 1 and "class-level" in
                                              (t["basis_1"], t["basis_2"])),
           "agreement_with_fda_label": {
               "annotator_1": _agreement([int(a1[i][0] == "yes") for i in ids if a1[i][0] != "unsure"],
                                         [gold[i] for i in ids if a1[i][0] != "unsure"]),
               "annotator_2": _agreement([int(a2[i][0] == "yes") for i in ids if a2[i][0] != "unsure"],
                                         [gold[i] for i in ids if a2[i][0] != "unsure"]),
               "consensus_tier_c": _agreement([t["consensus"] for t in tier_c], [t["fda_label"] for t in tier_c])},
           "bootstrap": {"resamples": n_boot, "seed": seed, "unit": "item"}}
    return out, tier_c
