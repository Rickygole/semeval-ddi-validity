import json

import post8_common as pc
from post8_common import ci, f3


def load(name):
    return json.loads((pc.OUT / f"{name}.json").read_text())


def changed_conclusions(sens, e9):
    out = []
    for t in ("C-auto", "C-auto-broad"):
        a, b = sens["e8"]["A"]["decision"], sens["e8"][t]["decision"]
        out.append({"item": "E8 oracle rule", "tier": t, "primary": a, "sensitivity": b, "changed": a != b})
        for h in ("H1", "H4", "H6"):
            a, b = sens["h"]["A"][h]["would_be_label"], sens["h"][t][h]["would_be_label"]
            out.append({"item": f"{h} (would-be label)", "tier": t, "primary": a, "sensitivity": b, "changed": a != b})
    for arm, cells in sens["e7"]["A"].items():
        for cell, e in cells.items():
            b = sens["e7"]["C-auto"][arm][cell]["label"]
            out.append({"item": f"E7 arm {arm} {cell}", "tier": "C-auto", "primary": e["label"], "sensitivity": b, "changed": e["label"] != b})
    for c in ("older_primary", "novel"):
        a, b = e9["tiers"]["A"][c]["n_upper_at_most_0.60"], e9["tiers"]["C-auto"][c]["n_upper_at_most_0.60"]
        out.append({"item": f"E9 {c} checkpoints with 95% upper bound <= 0.60 (of 20)", "tier": "C-auto", "primary": a, "sensitivity": b, "changed": a != b})
    return out


def sensitivity_md(sens):
    L = ["# Tier C-auto sensitivity (post hoc, exploratory)", "", f"Status: {pc.STATUS}.", "",
         "Tier C-auto is tier A without the positives flagged by the rule of criteria.json (families N, L, H); C-auto-broad also drops the absence-of-evidence positives. All negatives are kept. Primary (tier A) values are recomputed by the same code and reproduce decisions.json, e8.json and e7.json.", "",
         "## Rows per tier", "", "| tier | cohort | positives | negatives | positives dropped |", "| --- | --- | --- | --- | --- |"]
    for t, cs in sens["tiers"].items():
        for c, v in cs.items():
            L.append(f"| {t} | {c} | {v['positives']} | {v['negatives']} | {v['positives_dropped']} |")
    L += ["", "## H1, H1-novel, H4, H6 (two-way bootstrap, 1,000 draws)", "",
          "| row | tier | n | AUROC | 90% CI | 95% CI | p_TOST | p_Holm | would-be label | DrugBank within | kappa | kappa 95% CI |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for h in ("H1", "H1-novel", "H4", "H6"):
        for t in ("A", "C-auto", "C-auto-broad"):
            r = sens["h"][t][h]
            p_tost = f3(r.get("p_tost")) if h != "H1-novel" else "not tested"
            L.append(f"| {h} | {t} | {r.get('n', '')} | {f3(r['value'])} | {ci(r['ci90'])} | {ci(r['ci95'])} | {p_tost} | {f3(r.get('p_holm'))} | "
                     f"{r.get('would_be_label', 'estimate only')} | {f3(r.get('drugbank_within'))} | {f3(r.get('kappa'))} | {ci(r.get('kappa_ci95'))} |")
    L += ["", "## E8 oracle rule", "", "| tier | cohort | within-drug AUROC | 95% CI | grep | bar | statistic | pass | decision |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for t in ("A", "C-auto", "C-auto-broad"):
        e = sens["e8"][t]
        for c in ("novel", "older_primary"):
            w = e[c]["within"]
            L.append(f"| {t} | {c} | {f3(w['value'])} | {ci(w['lo95'], w['hi95'])} | {f3(e[c]['grep'])} | {f3(e[c]['bar'])} | {e[c]['statistic']} | {e[c]['pass']} | {e['decision']} |")
    L += ["", "## E7 arms c, d, e", "",
          "| arm | cell | tier | within | 95% CI | residual within | 95% CI | partner prior within | paired vs prior | 95% CI | TOST 90% (Older-primary) | kappa | label |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm in ("c", "d", "e"):
        for cell in sens["e7"]["A"][arm]:
            for t in ("A", "C-auto"):
                e = sens["e7"][t][arm][cell]
                w, r = e["within"], e["residual_within"]
                pp, pv = e.get("partner_prior_within") or {}, e.get("paired_vs_partner_prior") or {}
                to = e.get("tost_older_primary")
                tos = f"{ci(to['lo90'], to['hi90'])} eq={to['equivalent']}" if to else ""
                L.append(f"| {arm} | {cell} | {t} | {f3(w['value'])} | {ci(w['lo95'], w['hi95'])} | {f3(r['value'])} | {ci(r['lo95'], r['hi95'])} | "
                         f"{f3(pp.get('value'))} | {f3(pv.get('value'))} | {ci(pv.get('lo95'), pv.get('hi95'))} | {tos} | {f3(e.get('kappa'))} | {e['label']} |")
    L += ["", "## DrugBank lookup", "", "| cohort | tier | n | n_pos | within-drug AUROC | 95% CI (two-way) | pooled AUROC | 95% CI (two-way) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in sens["drugbank"]["A"]:
        for t in ("A", "C-auto"):
            r = sens["drugbank"][t][c]
            L.append(f"| {c} | {t} | {r['n']} | {r['n_pos']} | {f3(r['auroc_within'])} | {ci(r['within_ci95'])} | {f3(r['auroc_pooled'])} | {ci(r['pooled_ci95'])} |")
    return "\n".join(L) + "\n"


def main():
    pc.require_criteria()
    screen, sens, e9, red = load("screen"), load("sensitivity"), load("e9"), load("redacted_confound")
    pc.OUT.joinpath("sensitivity.md").write_text(sensitivity_md(sens))
    changes = changed_conclusions(sens, e9)
    cnt = screen["counts"]
    e8a, e8c, e8b = sens["e8"]["A"]["older_primary"], sens["e8"]["C-auto"]["older_primary"], sens["e8"]["C-auto-broad"]["older_primary"]
    out = {"status": pc.STATUS, "checks": {**sens["checks"], **e9["checks"],
                                           "redacted_reconstruction": all(v["match"] for v in red["reconstruction_check"].values())},
           "screen": {k: {x: cnt[k][x] for x in ("positives", "rule_flags", "absence_flags_not_dropped", "positives_oracle_below_0.5",
                                                  "negatives_oracle_above_0.5", "cross_tab_positives")} for k in cnt},
           "reviewer_comparison": screen["reviewer_comparison"], "audit_sheet": screen["audit_sheet"],
           "e8": {t: {c: {"value": sens["e8"][t][c]["within"]["value"], "lo95": sens["e8"][t][c]["within"]["lo95"],
                          "bar": sens["e8"][t][c]["bar"], "pass": sens["e8"][t][c]["pass"]} for c in ("novel", "older_primary")}
                  | {"decision": sens["e8"][t]["decision"]} for t in sens["e8"]},
           "h": {t: {h: {k: sens["h"][t][h].get(k) for k in ("value", "ci90", "ci95", "p_tost", "p_holm", "would_be_label", "kappa", "kappa_ci95")}
                     for h in sens["h"][t]} for t in sens["h"]},
           "e9": {t: {c: {k: e9["tiers"][t][c][k] for k in ("n_upper_at_most_0.60", "ratio_old", "ratio_paired", "paired_within_reference",
                                                             "mean_single_bootstrap_variance", "between_variance", "kappa_hi95_range",
                                                             "kappa_upper95_one_sided_range", "kappa_point_range", "drugbank_within")}
                      for c in e9["tiers"][t]} for t in e9["tiers"]},
           "redacted": {t: {c: {"length_only_within": v["length_only_within"]["value"], "qwen_redacted_within": v["qwen_redacted_within"]["value"],
                                "qwen_minus_length": v["qwen_minus_length"]["value"], "qwen_minus_length_ci95": [v["qwen_minus_length"]["lo95"], v["qwen_minus_length"]["hi95"]],
                                "tokens_removed_mean_positives": v["by_class"]["positives"]["tokens_removed_mean"],
                                "per_drug_neg_minus_pos_tokens_mean": v["by_class"]["per_drug_neg_minus_pos_tokens"]["mean"]}
                            for c, v in red["tiers"][t].items()} for t in red["tiers"]},
           "changed_conclusions": changes, "n_changed": sum(c["changed"] for c in changes)}
    h = sens["h"]
    L = ["# Post 8 summary: label-error screen and tier C-auto (post hoc, exploratory)", "", f"Status: {pc.STATUS}.", "",
         "Nothing here changes a preregistered decision. Tier C-auto is a sensitivity analysis; tier A stays primary. The audit sheet is unadjudicated.", "",
         "## Screen", "",
         f"- Rule flags (N, L, H): Novel {cnt['novel/all']['rule_flags']} of {cnt['novel/all']['positives']}; Older {cnt['older/all']['rule_flags']} of {cnt['older/all']['positives']} "
         f"(Older-clean {cnt['older/older_clean']['rule_flags']} of {cnt['older/older_clean']['positives']}, Older-primary {cnt['older/older_primary']['rule_flags']} of {cnt['older/older_primary']['positives']}). Reviewer: about 69 Older, 2 Novel.",
         f"- Absence-of-evidence positives (not dropped in C-auto): Novel {cnt['novel/all']['absence_flags_not_dropped']}, Older {cnt['older/all']['absence_flags_not_dropped']}.",
         f"- Positives with oracle P(yes) < 0.5: Novel {cnt['novel/all']['positives_oracle_below_0.5']}, Older {cnt['older/all']['positives_oracle_below_0.5']} of 648 (reviewer 142). "
         f"Of the Older rejections, {cnt['older/all']['cross_tab_positives']['flag_and_rejected']} carry a rule flag and {cnt['older/all']['cross_tab_positives']['no_flag_rejected']} do not; "
         f"{cnt['older/all']['cross_tab_positives']['flag_not_rejected']} flagged positives were accepted by the oracle.",
         f"- Negatives with oracle P(yes) > 0.5: Novel {cnt['novel/all']['negatives_oracle_above_0.5']}, Older {cnt['older/all']['negatives_oracle_above_0.5']} (reviewer 52).",
         f"- Audit sheet: {screen['audit_sheet']['rows']} items in label_audit_sheet.csv (scores only in label_audit_key.csv).", "",
         "## Primary next to sensitivity", "",
         "| quantity | tier A (primary) | C-auto | C-auto-broad |", "| --- | --- | --- | --- |",
         f"| E8 Older-primary within-drug, 95% CI | {f3(e8a['within']['value'])} {ci(e8a['within']['lo95'], e8a['within']['hi95'])} | {f3(e8c['within']['value'])} {ci(e8c['within']['lo95'], e8c['within']['hi95'])} | {f3(e8b['within']['value'])} {ci(e8b['within']['lo95'], e8b['within']['hi95'])} |",
         f"| E8 bar (Older-primary lower bound) | {f3(e8a['bar'])} | {f3(e8c['bar'])} | {f3(e8b['bar'])} |",
         f"| E8 Novel point | {f3(sens['e8']['A']['novel']['within']['value'])} | {f3(sens['e8']['C-auto']['novel']['within']['value'])} | {f3(sens['e8']['C-auto-broad']['novel']['within']['value'])} |",
         f"| E8 decision | {sens['e8']['A']['decision']} | {sens['e8']['C-auto']['decision']} | {sens['e8']['C-auto-broad']['decision']} |"]
    for k in ("H1", "H1-novel", "H4", "H6"):
        cells = []
        for t in ("A", "C-auto", "C-auto-broad"):
            r = h[t][k]
            s = f"{f3(r['value'])}, 90% {ci(r['ci90'])}"
            if k != "H1-novel":
                s += f", p_TOST {f3(r['p_tost'])}, Holm {f3(r['p_holm'])}, {r['would_be_label']}"
            cells.append(s)
        L.append(f"| {k} | " + " | ".join(cells) + " |")
    for k in ("H1", "H1-novel", "H6"):
        L.append(f"| {k} kappa, 95% CI | " + " | ".join(f"{f3(h[t][k]['kappa'])} {ci(h[t][k]['kappa_ci95'])}" for t in ("A", "C-auto", "C-auto-broad")) + " |")
    for c in ("older_primary", "novel"):
        A, C = e9["tiers"]["A"][c], e9["tiers"]["C-auto"][c]
        L.append(f"| E9 {c}: upper bounds <= 0.60 (of 20) | {A['n_upper_at_most_0.60']} | {C['n_upper_at_most_0.60']} | not run |")
        L.append(f"| E9 {c}: variance ratio, old / paired reference | {A['ratio_old']:.3f} / {A['ratio_paired']:.3f} | {C['ratio_old']:.3f} / {C['ratio_paired']:.3f} | not run |")
        L.append(f"| E9 {c}: kappa 95% upper bound range (97.5th / 95th percentile) | {ci(A['kappa_hi95_range'])} / {ci(A['kappa_upper95_one_sided_range'])} | {ci(C['kappa_hi95_range'])} / {ci(C['kappa_upper95_one_sided_range'])} | not run |")
    for c in sens["drugbank"]["A"]:
        A, C = sens["drugbank"]["A"][c], sens["drugbank"]["C-auto"][c]
        L.append(f"| DrugBank lookup {c}: within / pooled | {f3(A['auroc_within'])} / {f3(A['auroc_pooled'])} | {f3(C['auroc_within'])} / {f3(C['auroc_pooled'])} | not run |")
    for c in ("novel", "older_primary"):
        A, C = red["tiers"]["A"][c], red["tiers"]["C-auto"][c]
        L.append(f"| Redacted oracle {c}: length-only / Qwen within-drug | {f3(A['length_only_within']['value'])} / {f3(A['qwen_redacted_within']['value'])} | "
                 f"{f3(C['length_only_within']['value'])} / {f3(C['qwen_redacted_within']['value'])} | not run |")
    L += ["", "## Conclusions that change under C-auto", "", "| item | tier | primary | sensitivity | changed |", "| --- | --- | --- | --- | --- |"]
    for c in changes:
        L.append(f"| {c['item']} | {c['tier']} | {c['primary']} | {c['sensitivity']} | {'yes' if c['changed'] else 'no'} |")
    L += ["", f"{out['n_changed']} of {len(changes)} checked labels change. Files: criteria.json, screen.md, label_audit_sheet.csv, label_audit_key.csv, sensitivity.md, e9.md, redacted_confound.md."]
    pc.write("summary", out, "\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
