import csv
from collections import Counter

import numpy as np

import post8_common as pc
from ddiood.amend7_analysis import OLDER_ARTIFACTS, OLDER_MISSED

AUTHOR_COLUMNS = ["author_label", "notes"]
SHEET_COLUMNS = ["item_id", "cohort", "ood_drug", "partner", "current_label", "evidence", "cooccurrence_sentence",
                 "context_note", "rule_flag"] + AUTHOR_COLUMNS
KEY_COLUMNS = ["item_id", "cohort", "row_index", "ood_drug", "partner", "current_label", "oracle_p_yes", "rule_flag",
               "families", "absence_flag", "patterns", "scope", "ood_drug_not_named", "cooccurrence_also_flags",
               "older_subset", "selected_because"]
NEG_NOTE = "negative: by construction the partner is not named anywhere in this drug's label; judge from knowledge or other sources"


def subset(drug):
    if drug in OLDER_ARTIFACTS:
        return "artifact"
    if drug in OLDER_MISSED:
        return "clean_not_primary"
    return "primary"


def counts(rows, screens, oracle):
    out = {}
    for c in ("novel", "older"):
        y = np.array([int(r["label"]) for r in rows[c]])
        g = np.array([r["ood_drug"] for r in rows[c]])
        f = np.array([0 if s is None else s["flag"] for s in screens[c]])
        a = np.array([0 if s is None else s["absence"] for s in screens[c]])
        p = oracle[c]
        subsets = {"all": np.ones(len(y), bool)}
        if c == "older":
            sub = np.array([subset(d) for d in g])
            subsets["older_clean"] = sub != "artifact"
            subsets["older_primary"] = sub == "primary"
        for name, m in subsets.items():
            pos, neg = m & (y == 1), m & (y == 0)
            fam = Counter(s["families"] for s, mm in zip(screens[c], pos) if mm and s["flag"])
            out[f"{c}/{name}"] = {
                "positives": int(pos.sum()), "negatives": int(neg.sum()), "drugs": int(len(set(g[m]))),
                "rule_flags": int(f[pos].sum()), "families": dict(fam), "absence_flags_not_dropped": int(a[pos].sum()),
                "ood_drug_not_named": int(sum(s["ood_drug_not_named"] for s, mm in zip(screens[c], pos) if mm)),
                "cooccurrence_also_flags": int(sum(s["cooccurrence_also_flags"] for s, mm in zip(screens[c], pos) if mm)),
                "positives_oracle_below_0.5": int((pos & (p < 0.5)).sum()),
                "negatives_oracle_above_0.5": int((neg & (p > 0.5)).sum()),
                "cross_tab_positives": {"flag_and_rejected": int((pos & (f == 1) & (p < 0.5)).sum()),
                                        "flag_not_rejected": int((pos & (f == 1) & (p >= 0.5)).sum()),
                                        "no_flag_rejected": int((pos & (f == 0) & (p < 0.5)).sum()),
                                        "no_flag_not_rejected": int((pos & (f == 0) & (p >= 0.5)).sum())},
                "share_of_rejections_flagged": float((pos & (f == 1) & (p < 0.5)).sum() / max((pos & (p < 0.5)).sum(), 1))}
    return out


def per_drug(rows, screens, oracle, top=15):
    out = {}
    for c in ("novel", "older"):
        by = {}
        for r, s, p in zip(rows[c], screens[c], oracle[c]):
            d = by.setdefault(r["ood_drug"], {"positives": 0, "rule_flags": 0, "oracle_rejected_positives": 0})
            if s is not None:
                d["positives"] += 1
                d["rule_flags"] += s["flag"]
                d["oracle_rejected_positives"] += int(p < 0.5)
        ranked = sorted(by.items(), key=lambda kv: (-kv[1]["rule_flags"], -kv[1]["oracle_rejected_positives"], kv[0]))
        out[c] = {"by_rule_flags": [{"drug": k, **v} for k, v in ranked if v["rule_flags"]][:top],
                  "by_oracle_rejections": [{"drug": k, **v} for k, v in sorted(by.items(), key=lambda kv: (-kv[1]["oracle_rejected_positives"], kv[0]))
                                           if v["oracle_rejected_positives"]][:top],
                  "drugs_with_a_flag": int(sum(1 for v in by.values() if v["rule_flags"]))}
    return out


def audit_items(rows, screens, oracle):
    items = []
    for c in ("novel", "older"):
        for i, (r, s, p) in enumerate(zip(rows[c], screens[c], oracle[c])):
            y = int(r["label"])
            why = []
            if y == 1 and p < 0.5:
                why.append("positive_oracle_below_0.5")
            if y == 1 and s["flag"]:
                why.append("positive_rule_flag")
            if y == 0 and p > 0.5:
                why.append("negative_oracle_above_0.5")
            if not why:
                continue
            items.append({"cohort": c, "row_index": i, "ood_drug": r["ood_drug"], "partner": r["semeval_drug"],
                          "current_label": y, "evidence": r["evidence"], "cooccurrence_sentence": r.get("cooccurrence_sentence", ""),
                          "context_note": "" if y == 1 else NEG_NOTE, "rule_flag": "" if s is None else s["flag"],
                          "oracle_p_yes": float(p), "families": "" if s is None else s["families"],
                          "absence_flag": "" if s is None else s["absence"], "patterns": "" if s is None else " ".join(s["patterns"]),
                          "scope": "" if s is None else s["scope"],
                          "ood_drug_not_named": "" if s is None else s["ood_drug_not_named"],
                          "cooccurrence_also_flags": "" if s is None else s["cooccurrence_also_flags"],
                          "older_subset": subset(r["ood_drug"]) if c == "older" else "",
                          "selected_because": " ".join(why)})
    order = np.random.RandomState(42).permutation(len(items))
    items = [items[k] for k in order]
    for n, it in enumerate(items):
        it["item_id"] = f"A{n + 1:03d}"
        it["author_label"] = ""
        it["notes"] = ""
    return items


def write_csv(path, items, cols):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for it in items:
            w.writerow({k: it.get(k, "") for k in cols})


def main():
    crit, rows, rule, screens = pc.screens_for_run()
    oracle = pc.oracle_scores(rows)
    cnt = counts(rows, screens, oracle)
    drugs = per_drug(rows, screens, oracle)
    items = audit_items(rows, screens, oracle)
    pc.OUT.mkdir(parents=True, exist_ok=True)
    write_csv(pc.OUT / "label_audit_sheet.csv", items, SHEET_COLUMNS)
    write_csv(pc.OUT / "label_audit_key.csv", items, KEY_COLUMNS)
    flagged = []
    for c in ("novel", "older"):
        for i, (r, s) in enumerate(zip(rows[c], screens[c])):
            if s is not None and (s["flag"] or s["absence"]):
                flagged.append({"cohort": c, "row_index": i, "ood_drug": r["ood_drug"], "partner": r["semeval_drug"],
                                "flag": s["flag"], "absence": s["absence"], "families": s["families"], "patterns": s["patterns"],
                                "scope": s["scope"], "heading": s["heading"], "evidence": r["evidence"]})
    sel = Counter(w for it in items for w in it["selected_because"].split())
    out = {"status": pc.STATUS, "rule": "criteria.json rule (families N, L, H); absence family reported, not dropped",
           "oracle_row_order": "ood_hash and ood_old_hash of a7-qwen-oracle.json equal the frozen pair hashes; partner_in_context is 0 on every negative and at least 0.99 on positives",
           "counts": cnt, "per_drug": drugs, "flagged_items": flagged,
           "reviewer_comparison": {
               "older_positives_oracle_below_0.5": {"reviewer": "142 of 648", "here": f"{cnt['older/all']['positives_oracle_below_0.5']} of {cnt['older/all']['positives']}"},
               "older_rule_flags": {"reviewer": "about 69 of 648", "here": f"{cnt['older/all']['rule_flags']} of {cnt['older/all']['positives']}"},
               "novel_rule_flags": {"reviewer": "2 of 148", "here": f"{cnt['novel/all']['rule_flags']} of {cnt['novel/all']['positives']}"},
               "negatives_oracle_above_0.5": {"reviewer": "52", "here": cnt["novel/all"]["negatives_oracle_above_0.5"] + cnt["older/all"]["negatives_oracle_above_0.5"],
                                              "novel": cnt["novel/all"]["negatives_oracle_above_0.5"], "older": cnt["older/all"]["negatives_oracle_above_0.5"]}},
           "audit_sheet": {"rows": len(items), "selected_because": dict(sel),
                           "by_cohort": dict(Counter(it["cohort"] for it in items)),
                           "files": ["label_audit_sheet.csv", "label_audit_key.csv"], "shuffle": "numpy RandomState(42).permutation",
                           "adjudicated": 0}}
    L = ["# Label-error screen (post hoc, exploratory)", "", f"Status: {pc.STATUS}.", "",
         "Rule: results/revision/post8/criteria.json (non-interaction N, laboratory test L, heading H) applied to each positive's evidence sentence, in clauses that name the partner. The absence-of-evidence family is reported and not dropped.", "",
         "| cohort | positives | negatives | rule flags | families | absence (not dropped) | positives with oracle P < 0.5 | flagged and rejected | rejected, not flagged | flagged, not rejected | negatives with oracle P > 0.5 |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, v in cnt.items():
        ct = v["cross_tab_positives"]
        L.append(f"| {k} | {v['positives']} | {v['negatives']} | {v['rule_flags']} | {v['families']} | {v['absence_flags_not_dropped']} | "
                 f"{v['positives_oracle_below_0.5']} | {ct['flag_and_rejected']} | {ct['no_flag_rejected']} | {ct['flag_not_rejected']} | {v['negatives_oracle_above_0.5']} |")
    L += ["", "## Reviewer comparison", ""]
    for k, v in out["reviewer_comparison"].items():
        L.append(f"- {k}: reviewer {v['reviewer']}; here {v['here']}")
    L += ["", "## Drugs with the most rule flags", "", "| cohort | drug | positives | rule flags | oracle-rejected positives |", "| --- | --- | --- | --- | --- |"]
    for c in ("older", "novel"):
        for d in drugs[c]["by_rule_flags"]:
            L.append(f"| {c} | {d['drug']} | {d['positives']} | {d['rule_flags']} | {d['oracle_rejected_positives']} |")
    L += ["", "## Drugs with the most oracle-rejected positives", "", "| cohort | drug | positives | oracle-rejected | rule flags |", "| --- | --- | --- | --- | --- |"]
    for c in ("older", "novel"):
        for d in drugs[c]["by_oracle_rejections"]:
            L.append(f"| {c} | {d['drug']} | {d['positives']} | {d['oracle_rejected_positives']} | {d['rule_flags']} |")
    L += ["", "## Flagged positives", "", "| cohort | drug | partner | flag | absence | families | patterns |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for x in flagged:
        L.append(f"| {x['cohort']} | {x['ood_drug']} | {x['partner']} | {x['flag']} | {x['absence']} | {x['families']} | {' '.join(x['patterns'])} |")
    L += ["", f"Audit sheet: label_audit_sheet.csv, {len(items)} items ({dict(sel)}), shuffled with seed 42; the author fills author_label (yes, no or unsure) and notes. Scores are only in label_audit_key.csv. Nothing has been adjudicated."]
    pc.write("screen", out, "\n".join(L) + "\n")
    print({k: (v["rule_flags"], v["positives_oracle_below_0.5"], v["negatives_oracle_above_0.5"]) for k, v in cnt.items()}, len(items))


if __name__ == "__main__":
    main()
