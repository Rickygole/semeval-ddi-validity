import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import beta

import post8_common as pc
import post8_e9 as e9
import post8_sensitivity as ps
from ddiood import amend7_analysis as aa
from ddiood import evaluate2 as ev

ADJ = pc.OUT / "model_adjudication.csv"
KEY = pc.OUT / "label_audit_key.csv"
TIER = "C-adjudicated"
DISCLOSURE = "automated model adjudication, not a human audit"
CORRECTIONS = [
    "rule_flag and current_label were stripped from the copy of label_audit_sheet.csv used for judging; items were judged from the text only",
    "each of the 76 negative rows, which carry no evidence text, was judged against the ood_drug Drug Interactions section in artifacts/amend7/di_sections.json, from the supplied text only and never from background knowledge",
]


def cp(k, n, a=0.05):
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": (k / n) if n else None, "ci95_exact": cp(k, n)}


def load():
    a = pd.read_csv(ADJ, dtype=str)
    k = pd.read_csv(KEY)
    if len(a) != 255 or set(a.item_id) != set(k.item_id):
        raise ValueError("adjudication file does not cover the 255 key items")
    if not set(a.adjudication) <= {"yes", "no", "unsure"}:
        raise ValueError("adjudication values must be yes, no or unsure")
    return k.merge(a, on="item_id", how="left")


def agreement_current(m):
    y = m.current_label.astype(int)
    adj = m.adjudication
    conf = (adj == "yes") & (y == 1) | (adj == "no") & (y == 0)
    dec = adj != "unsure"
    tab = pd.crosstab(adj, y).reindex(index=["yes", "no", "unsure"], columns=[1, 0], fill_value=0)
    return {"table_rows_adjudication_cols_current_label": {r: {str(c): int(tab.loc[r, c]) for c in tab.columns} for r in tab.index},
            "unsure_as_not_confirming": rate(conf.sum(), len(m)),
            "decided_only": rate(conf[dec].sum(), dec.sum()), "n_unsure": int((~dec).sum())}


def error_block(sub, wrong):
    adj = sub.adjudication
    dec = adj != "unsure"
    e = (adj == wrong)
    u = (adj == "unsure")
    return {"n": int(len(sub)), "n_wrong": int(e.sum()), "n_unsure": int(u.sum()),
            "primary_decided_only": rate(e.sum(), dec.sum()),
            "unsure_as_correct": rate(e.sum(), len(sub)),
            "unsure_as_error": rate((e | u).sum(), len(sub))}


def error_rates(m):
    pos = m[m.current_label == 1]
    neg = m[m.current_label == 0]
    out = {"flagged_positives": error_block(pos, "no"), "flagged_negatives": error_block(neg, "yes"), "positives_by_selection": {},
           "positives_by_cohort": {}, "negatives_by_cohort": {}}
    for s, g in pos.groupby("selected_because"):
        out["positives_by_selection"][s] = error_block(g, "no")
    for c, g in pos.groupby("cohort"):
        out["positives_by_cohort"][c] = error_block(g, "no")
    for c, g in neg.groupby("cohort"):
        out["negatives_by_cohort"][c] = error_block(g, "yes")
    return out


def agreement_rule(m):
    pos = m[m.current_label == 1].copy()
    f = pos.rule_flag.astype(float).astype(int)
    adj = pos.adjudication
    dec = adj != "unsure"
    agree = (f == 1) & (adj == "no") | (f == 0) & (adj == "yes")
    tab = pd.crosstab(adj, f).reindex(index=["yes", "no", "unsure"], columns=[1, 0], fill_value=0)
    return {"scope": "the 179 positives; rule_flag 1 means the post8 rule calls the positive a non-interaction",
            "table_rows_adjudication_cols_rule_flag": {r: {str(c): int(tab.loc[r, c]) for c in tab.columns} for r in tab.index},
            "agreement_decided_only": rate(agree[dec].sum(), dec.sum()),
            "flagged_judged_no": rate(((f == 1) & (adj == "no")).sum(), ((f == 1) & dec).sum()),
            "judged_no_flagged": rate(((f == 1) & (adj == "no")).sum(), (adj == "no").sum())}


def agreement_oracle(m):
    o = np.where(m.oracle_p_yes.astype(float) >= 0.5, "yes", "no")
    adj = m.adjudication
    dec = adj != "unsure"
    agree = adj == o
    out = {"threshold": 0.5, "all_items_decided_only": rate(agree[dec].sum(), dec.sum())}
    for lab, g in m.assign(o=o).groupby("current_label"):
        d = g.adjudication != "unsure"
        out[f"current_label_{lab}_decided_only"] = rate((g.adjudication == g.o)[d].sum(), d.sum())
    return out


def keep_masks(m, rows):
    keep = {"ood": np.ones(len(rows["novel"]), bool), "oodold": np.ones(len(rows["older"]), bool)}
    drop = m[(m.current_label == 1) & (m.adjudication == "no")]
    for _, r in drop.iterrows():
        x = rows[r.cohort][int(r.row_index)]
        if x["ood_drug"] != r.ood_drug or x["semeval_drug"] != r.partner or str(x["label"]) != "1":
            raise ValueError(f"{r.item_id}: key row_index does not match the frozen pair")
        keep[pc.TAGS[r.cohort]][int(r.row_index)] = False
    return keep, drop


def e9_counts(keep, rows, n):
    base, _, (db_ood, db_old) = pc.a7_truth()
    ytest = ev.load_truth().test_y
    models = e9.load_panel(pc.PREDS, ytest)
    db = {"ood": aa.drugbank_scores(rows["novel"], db_ood), "oodold": aa.drugbank_scores(rows["older"], db_old)}
    tr = pc.TruthC(base, keep)
    out = {}
    for c in ("older_primary", "novel"):
        b = e9.cohort_block(tr, c, models, db, n)
        out[c] = {k: b[k] for k in ("n_rows", "n_pos", "n_upper_at_most_0.60", "n_models", "drugbank_within", "drugbank_lo95",
                                     "drugbank_hi95", "kappa_hi95_range", "kappa_upper95_one_sided_range", "ratio_old", "ratio_paired")}
    return out


def e7_older_primary(e7):
    out = {}
    for arm in ("c", "d", "e"):
        for cell in ("older_primary/A", "older_primary/B"):
            e = e7[arm][cell]
            out[f"{arm} {cell}"] = {"within": e["within"], "residual_within": e["residual_within"],
                                    "paired_vs_partner_prior": e.get("paired_vs_partner_prior"),
                                    "tost_older_primary": e.get("tost_older_primary"), "kappa": e.get("kappa"), "label": e["label"]}
    return out


def conclusions(ref, new):
    ch = []
    for h in ("H1", "H4", "H6"):
        for t in ("A", "C-auto"):
            ch.append({"item": f"{h} would-be label", "vs": t, "reference": ref["h"][t][h].get("would_be_label"),
                       "adjudicated": new["h"][h].get("would_be_label")})
    for t in ("A", "C-auto"):
        ch.append({"item": "E8 decision", "vs": t, "reference": ref["e8"][t]["decision"], "adjudicated": new["e8"]["decision"]})
        for c in ("novel", "older_primary"):
            ch.append({"item": f"E8 {c} pass", "vs": t, "reference": ref["e8"][t][c]["pass"], "adjudicated": new["e8"][c]["pass"]})
        for arm in ("c", "d", "e"):
            for cell in ref["e7"][t][arm]:
                ch.append({"item": f"E7 {arm} {cell} label", "vs": t, "reference": ref["e7"][t][arm][cell]["label"],
                           "adjudicated": new["e7"][arm][cell]["label"]})
                ro, no = ref["e7"][t][arm][cell].get("tost_older_primary"), new["e7"][arm][cell].get("tost_older_primary")
                if ro and no:
                    ch.append({"item": f"E7 {arm} {cell} TOST equivalence", "vs": t, "reference": ro.get("equivalent"),
                               "adjudicated": no.get("equivalent")})
        for c in ("older_primary", "novel"):
            ch.append({"item": f"E9 {c} count upper95 <= 0.60", "vs": t, "reference": ref["e9"][t][c]["n_upper_at_most_0.60"],
                       "adjudicated": new["e9"][c]["n_upper_at_most_0.60"]})
    for c in ch:
        c["changed"] = c["reference"] != c["adjudicated"]
    return ch


def pr(r):
    return f"{r['k']}/{r['n']} = {pc.f3(r['rate'])} {pc.ci(r['ci95_exact'])}"


def markdown(out):
    L = [f"# Label audit: {DISCLOSURE}", "", f"Status: {pc.STATUS}.", "",
         f"Disclosure: this is an {DISCLOSURE}. One automated adjudicator read each of the 255 items of label_audit_sheet.csv blind to the key, following AUDIT_GUIDELINES.md. "
         "It is a third automated source, not a reference standard, and no agreement with a human standard is claimed.", "",
         "Corrections applied before judging:", ""]
    L += [f"* {c}." for c in CORRECTIONS]
    L += ["", "The sheet is a list of suspect items (positives the oracle scored below 0.5 or the rule flagged, negatives the oracle scored above 0.5), not a random sample, so the rates below describe those strata only and not the whole set.", "",
          "## Counts", "", "| adjudication | current label 1 | current label 0 |", "| --- | --- | --- |"]
    t = out["agreement_current_label"]["table_rows_adjudication_cols_current_label"]
    for r in ("yes", "no", "unsure"):
        L.append(f"| {r} | {t[r]['1']} | {t[r]['0']} |")
    a = out["agreement_current_label"]
    L += ["", f"Agreement with the current label: {pr(a['unsure_as_not_confirming'])} with unsure counted as not confirming; {pr(a['decided_only'])} on decided items.", "",
          "## Estimated label error rate (exact Clopper-Pearson 95% intervals)", "",
          "| stratum | decided only | unsure as correct | unsure as error | unsure |", "| --- | --- | --- | --- | --- |"]
    er = out["error_rates"]
    def row(name, b):
        L.append(f"| {name} | {pr(b['primary_decided_only'])} | {pr(b['unsure_as_correct'])} | {pr(b['unsure_as_error'])} | {b['n_unsure']} |")
    row("flagged positives (judged no)", er["flagged_positives"])
    for s, b in er["positives_by_selection"].items():
        row(f"positives, {s}", b)
    for c, b in er["positives_by_cohort"].items():
        row(f"positives, {c}", b)
    row("flagged negatives (judged yes)", er["flagged_negatives"])
    for c, b in er["negatives_by_cohort"].items():
        row(f"negatives, {c}", b)
    ru, orc = out["agreement_rule"], out["agreement_oracle"]
    rt = ru["table_rows_adjudication_cols_rule_flag"]
    L += ["", "## Agreement with the post8 rule and with the oracle", "",
          "Post8 rule, on the 179 positives (flag 1 means the rule calls the positive a non-interaction):", "",
          "| adjudication | rule flag 1 | rule flag 0 |", "| --- | --- | --- |"]
    for r in ("yes", "no", "unsure"):
        L.append(f"| {r} | {rt[r]['1']} | {rt[r]['0']} |")
    L += ["", f"Agreement on decided items: {pr(ru['agreement_decided_only'])}. Flagged items judged no: {pr(ru['flagged_judged_no'])}. Items judged no that the rule flagged: {pr(ru['judged_no_flagged'])}.", "",
          f"Oracle (P(yes) at least 0.5 read as yes), decided items: all {pr(orc['all_items_decided_only'])}; current label 1 {pr(orc['current_label_1_decided_only'])}; current label 0 {pr(orc['current_label_0_decided_only'])}.", "",
          f"## Tier {TIER}", "",
          f"Tier {TIER} is tier A without the positives adjudicated no; unsure items are kept and nothing is flipped. All negatives are kept, including any adjudicated yes. Reference values for tiers A and C-auto are read from sensitivity.json and e9.json, which reproduce the primary files.", "",
          "| cohort | positives | negatives | positives dropped |", "| --- | --- | --- | --- |"]
    for c, v in out["tier"]["counts"].items():
        L.append(f"| {c} | {v['positives']} | {v['negatives']} | {v['positives_dropped']} |")
    L += ["", "### H1, H1-novel, H4, H6", "", "| row | tier | n | AUROC | 95% CI | p_TOST | p_Holm | would-be label | kappa | kappa 95% CI |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for h in ("H1", "H1-novel", "H4", "H6"):
        for tname, src in (("A", out["reference"]["h"]["A"]), ("C-auto", out["reference"]["h"]["C-auto"]), (TIER, out["tier"]["h"])):
            r = src[h]
            L.append(f"| {h} | {tname} | {r.get('n', '')} | {pc.f3(r['value'])} | {pc.ci(r['ci95'])} | {pc.f3(r.get('p_tost')) if h != 'H1-novel' else 'not tested'} | "
                     f"{pc.f3(r.get('p_holm'))} | {r.get('would_be_label', 'estimate only')} | {pc.f3(r.get('kappa'))} | {pc.ci(r.get('kappa_ci95'))} |")
    L += ["", "### E8 oracle rule", "", "| tier | cohort | within-drug AUROC | 95% CI | statistic | pass | decision |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for tname, src in (("A", out["reference"]["e8"]["A"]), ("C-auto", out["reference"]["e8"]["C-auto"]), (TIER, out["tier"]["e8"])):
        for c in ("novel", "older_primary"):
            w = src[c]["within"]
            L.append(f"| {tname} | {c} | {pc.f3(w['value'])} | {pc.ci(w['lo95'], w['hi95'])} | {src[c]['statistic']} | {src[c]['pass']} | {src['decision']} |")
    L += ["", "### E7 arms c, d, e, Older-primary", "", "| arm and cell | tier | within | 95% CI | residual within | 95% CI | paired vs prior | 95% CI | TOST 90% | kappa | label |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key in out["tier"]["e7_older_primary"]:
        arm, cell = key.split(" ")
        for tname, e in (("A", out["reference"]["e7"]["A"][arm][cell]), ("C-auto", out["reference"]["e7"]["C-auto"][arm][cell]), (TIER, out["tier"]["e7"][arm][cell])):
            pv = e.get("paired_vs_partner_prior") or {}
            tt = e.get("tost_older_primary")
            ts = f"{pc.ci(tt.get('lo90'), tt.get('hi90'))} eq={tt.get('equivalent')}" if tt else ""
            L.append(f"| {key} | {tname} | {pc.f3(e['within']['value'])} | {pc.ci(e['within']['lo95'], e['within']['hi95'])} | {pc.f3(e['residual_within']['value'])} | "
                     f"{pc.ci(e['residual_within']['lo95'], e['residual_within']['hi95'])} | {pc.f3(pv.get('value'))} | {pc.ci(pv.get('lo95'), pv.get('hi95'))} | {ts} | {pc.f3(e.get('kappa'))} | {e['label']} |")
    L += ["", "### E9 count", "", "| cohort | tier | rows | positives | checkpoints with upper 95% bound at most 0.60 | of |", "| --- | --- | --- | --- | --- | --- |"]
    for c in ("older_primary", "novel"):
        for tname, b in (("A", out["reference"]["e9"]["A"][c]), ("C-auto", out["reference"]["e9"]["C-auto"][c]), (TIER, out["tier"]["e9"][c])):
            L.append(f"| {c} | {tname} | {b['n_rows']} | {b['n_pos']} | {b['n_upper_at_most_0.60']} | {b['n_models']} |")
    ch = [c for c in out["conclusions"] if c["changed"]]
    L += ["", "## Conclusions", ""]
    if ch:
        L += ["| item | compared with | reference | C-adjudicated |", "| --- | --- | --- | --- |"]
        L += [f"| {c['item']} | {c['vs']} | {c['reference']} | {c['adjudicated']} |" for c in ch]
    else:
        L.append("No compared conclusion changes.")
    L += ["", f"{len(ch)} of {len(out['conclusions'])} compared conclusions differ from the reference tier named in each row."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    pc.require_criteria()
    m = load()
    rows = pc.load_rows()
    keep, drop = keep_masks(m, rows)
    out = {"status": pc.STATUS, "disclosure": DISCLOSURE, "corrections_applied": CORRECTIONS, "boot": a.boot,
           "adjudication_counts": {f"{r}|current_{y}": int(((m.adjudication == r) & (m.current_label == y)).sum())
                                   for r in ("yes", "no", "unsure") for y in (1, 0)},
           "agreement_current_label": agreement_current(m), "error_rates": error_rates(m),
           "agreement_rule": agreement_rule(m), "agreement_oracle": agreement_oracle(m)}
    sens = json.loads((pc.OUT / "sensitivity.json").read_text())
    e9ref = json.loads((pc.OUT / "e9.json").read_text())["tiers"]
    out["reference"] = {"h": sens["h"], "e8": sens["e8"], "e7": sens["e7"], "e9": e9ref}
    truth = ev.load_truth()
    a7, _, (db_ood, db_old) = pc.a7_truth()
    db_scores = {"ood": aa.drugbank_scores(rows["novel"], db_ood), "oodold": aa.drugbank_scores(rows["older"], db_old)}
    tc = pc.TruthC(a7, keep)
    e7 = ps.e7_rows(tc, db_scores, a.boot)
    out["tier"] = {"name": TIER, "dropped_items": sorted(drop.item_id.tolist()), "counts": ps.counts_by_cohort(a7, keep),
                   "h": ps.h_family(truth, keep, a.boot), "e8": ps.e8_rows(tc, a.boot), "e7": e7,
                   "e7_older_primary": e7_older_primary(e7), "e9": e9_counts(keep, rows, a.boot)}
    out["conclusions"] = conclusions(out["reference"], out["tier"])
    out["n_conclusions_changed"] = sum(c["changed"] for c in out["conclusions"])
    md = markdown(out)
    out.pop("reference")
    pc.write("adjudication", out, md)
    print(json.dumps({"error_rates": {k: out["error_rates"][k]["primary_decided_only"] for k in ("flagged_positives", "flagged_negatives")},
                      "counts": out["tier"]["counts"], "n_conclusions_changed": out["n_conclusions_changed"]}, indent=1))


if __name__ == "__main__":
    main()
