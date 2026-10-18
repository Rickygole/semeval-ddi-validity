import argparse
import csv
import json
from pathlib import Path

import numpy as np

from sens_common import ROOT, ci, ev, f3, write
from amend7_cpu_common import BOOT_SEED, paired_draws, seed_mean, stats, summarize_draws
from ddiood import drugbank

ART = ROOT / "artifacts"
DEFAULT_ZIP = Path.home() / "Downloads" / "drugbank_all_full_database.xml.zip"
COHORTS = (("novel", "ood", "ood_pairs.csv", "drugbank_validation.csv"),
           ("older_clean", "oodold", "ood_old_pairs.csv", "drugbank_validation_old.csv"))
VARIANTS = (("original", False, "negative"), ("original_one_sided_unresolvable", False, "unresolvable"),
            ("salt_stripped", True, "negative"), ("salt_stripped_one_sided_unresolvable", True, "unresolvable"))


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def unresolved_counts(rows, keep):
    rs = [r for r, k in zip(rows, keep) if k]
    ood = {r["ood_drug"] for r in rs if not r["ood_resolved"]}
    part = {r["semeval_drug"] for r in rs if not r["partner_resolved"]}
    return {"ood_drugs_unresolved": len(ood), "ood_drugs_unresolved_names": sorted(ood),
            "rows_ood_unresolved": sum(not r["ood_resolved"] for r in rs),
            "partner_drugs_unresolved": len(part), "partner_drugs_unresolved_names": sorted(part),
            "rows_partner_unresolved": sum(not r["partner_resolved"] for r in rs),
            "rows_any_side_unresolved": sum(not (r["ood_resolved"] and r["partner_resolved"]) for r in rs),
            "rows_one_side_only": sum(r["ood_resolved"] != r["partner_resolved"] for r in rs),
            "rows_neither_side": sum(not r["ood_resolved"] and not r["partner_resolved"] for r in rs)}


def lookup_metrics(y, labels, g, q, boot, seed):
    score = np.asarray([1.0 if v == "positive" else 0.0 for v in labels])
    d = paired_draws(y, [score], g, q, boot, seed)[0]
    within = summarize_draws(stats.stratified_auroc(y, score, g), d)
    lab = np.asarray(labels)
    res = lab != "unresolvable"
    pos, neg = res & (y == 1), res & (y == 0)
    return {"n": int(len(y)), "n_pos": int(y.sum()), "n_drugs": int(len(set(g.tolist()))),
            "listed": int((lab == "positive").sum()), "not_listed": int((lab == "negative").sum()),
            "unresolvable": int((~res).sum()), "auroc_within": within, "auroc_pooled": ev.auroc(y, score),
            "positive_confirmation_rate": float(score[y == 1].mean()),
            "positive_precision_resolvable": float((lab[pos] == "positive").mean()) if pos.any() else None,
            "pos_resolvable": int(pos.sum()), "neg_resolvable": int(neg.sum()),
            "negative_contradiction_rate": float((lab[neg] == "positive").mean()) if neg.any() else None}


def kappa_rows(m, h1_auc):
    a = m["auroc_within"]["value"]
    return {"auc_drugbank_within": a, "kappa_margin_0_1": 0.1 / (a - 0.5) if a > 0.5 else None,
            "h1_auroc_within": h1_auc, "kappa_observed": (h1_auc - 0.5) / (a - 0.5) if a > 0.5 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugbank", default=str(DEFAULT_ZIP))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    truth = ev.load_truth()
    lookup = json.loads((ART / "vocab" / "drug_lookup.json").read_text())
    table = drugbank.load_interactions(a.drugbank)
    out = {"status": "sensitivity analysis, post hoc; the preregistered DrugBank validation files and every decision are unchanged",
           "drugbank_file": Path(a.drugbank).name, "boot": a.boot,
           "method": "ddiood.drugbank.validate rerun on the frozen pair files with the same name lookup. 'original' is the "
                     "preregistered resolution; 'salt_stripped' adds salt and hydrate words removed from a name as a fallback "
                     "form (ddiood.drugbank.SALT_WORDS) when the exact forms do not resolve. 'one_sided_unresolvable' labels a "
                     "pair unresolvable instead of negative when only one side resolves. The lookup score is 1 for a DrugBank "
                     "positive and 0 otherwise. Positive confirmation rate is the share of FDA positives DrugBank lists, with "
                     "unresolvable pairs counted as not listed, as in results/revision/eval/drugbank_lookup.md. Within-drug "
                     "AUROC intervals use the two-way cluster bootstrap (Novel seed 1042, Older seed 42). kappa_margin_0_1 is "
                     "0.1 / (AUROC_DrugBank - 0.5), the H1 equivalence margin as a share of the DrugBank headroom; "
                     "kappa_observed is (AUROC_H1 - 0.5) / (AUROC_DrugBank - 0.5) with the five-seed mixed-input BiomedBERT score.",
           "cohorts": {}}
    md = ["# DrugBank name resolution: salt forms and one-sided pairs", "",
          "Sensitivity analysis, post hoc. The preregistered files `artifacts/ood/drugbank_validation*.csv` are not changed.", ""]
    for cohort, tag, pair_file, db_file in COHORTS:
        pairs = read_csv(ART / "ood" / pair_file)
        s = truth.sets[tag]
        keep_truth = np.ones(len(s["y"]), bool) if cohort == "novel" else s["clean"]
        if [(p["drug_a"], p["drug_b"]) for p in s["pairs"]] != [(p["ood_drug"], p["semeval_drug"]) for p in pairs]:
            raise ValueError(f"{pair_file} order differs from the evaluation truth")
        keep = list(keep_truth)
        y = np.asarray([int(p["label"]) for p, k in zip(pairs, keep) if k])
        g = np.asarray([p["ood_drug"] for p, k in zip(pairs, keep) if k])
        q = np.asarray([p["semeval_drug"] for p, k in zip(pairs, keep) if k])
        seed = BOOT_SEED["novel" if cohort == "novel" else "older_clean"]
        saved = read_csv(ART / "ood" / db_file)
        h1_key = "ood_empty" if tag == "ood" else "oodold_empty"
        p_h1, n_seeds = seed_mean("b2mixed-biomedbert", h1_key)
        h1_auc = stats.stratified_auroc(y, np.asarray(p_h1)[np.asarray(keep_truth)], g) if n_seeds == 5 else None
        c = {"n_rows": int(len(y)), "variants": {}}
        for name, strip, one in VARIANTS:
            rows, _ = drugbank.validate(pairs, table, lookup, strip_salts=strip, one_sided=one, detail=True)
            if name == "original":
                c["original_reproduces_saved_csv"] = [r["drugbank_label"] for r in rows] == [r["drugbank_label"] for r in saved]
                affected = {r["ood_drug"] for r in rows if not r["ood_resolved"]}
            labels = [r["drugbank_label"] for r, k in zip(rows, keep) if k]
            m = lookup_metrics(y, labels, g, q, a.boot, seed)
            c["variants"][name] = {"resolution": unresolved_counts(rows, keep), "lookup": m, "kappa": kappa_rows(m, h1_auc)}
        ex = ~np.isin(g, sorted(affected))
        rows, _ = drugbank.validate(pairs, table, lookup, detail=True)
        labels = np.asarray([r["drugbank_label"] for r, k in zip(rows, keep) if k])
        m = lookup_metrics(y[ex], list(labels[ex]), g[ex], q[ex], a.boot, seed)
        h1_ex = stats.stratified_auroc(y[ex], np.asarray(p_h1)[np.asarray(keep_truth)][ex], g[ex]) if n_seeds == 5 else None
        c["variants"]["original_excluding_unresolved_ood_drugs"] = {"excluded_ood_drugs": sorted(affected), "lookup": m,
                                                                    "kappa": kappa_rows(m, h1_ex)}
        anyside = np.asarray([r["ood_resolved"] and r["partner_resolved"] for r, k in zip(rows, keep) if k])
        m = lookup_metrics(y[anyside], list(labels[anyside]), g[anyside], q[anyside], a.boot, seed)
        h1_rows = stats.stratified_auroc(y[anyside], np.asarray(p_h1)[np.asarray(keep_truth)][anyside], g[anyside]) if n_seeds == 5 else None
        c["variants"]["original_excluding_rows_with_an_unresolved_side"] = {"lookup": m, "kappa": kappa_rows(m, h1_rows)}
        out["cohorts"][cohort] = c
        md += [f"## {cohort}", "", f"{c['n_rows']} rows. Original resolution reproduces the saved `{db_file}`: {c['original_reproduces_saved_csv']}.", "",
               "| variant | OOD drugs unresolved | rows, OOD side unresolved | partners unresolved | rows, partner unresolved | rows, one side only | listed | not listed | unresolvable |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for name, v in c["variants"].items():
            if "resolution" not in v:
                continue
            r, m = v["resolution"], v["lookup"]
            md.append(f"| {name} | {r['ood_drugs_unresolved']} | {r['rows_ood_unresolved']} | {r['partner_drugs_unresolved']} | "
                      f"{r['rows_partner_unresolved']} | {r['rows_one_side_only']} | {m['listed']} | {m['not_listed']} | {m['unresolvable']} |")
        md += ["", "| variant | n | drugs | lookup AUROC within | 95% CI | pooled | positive confirmation | positive precision (resolvable) | negative contradiction | kappa margin 0.1 | H1 AUROC | kappa observed |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for name, v in c["variants"].items():
            m, k = v["lookup"], v["kappa"]
            md.append(f"| {name} | {m['n']} | {m['n_drugs']} | {f3(m['auroc_within']['value'])} | {ci(m['auroc_within']['ci95'])} | "
                      f"{f3(m['auroc_pooled'])} | {f3(m['positive_confirmation_rate'])} | {f3(m['positive_precision_resolvable'])} | "
                      f"{f3(m['negative_contradiction_rate'])} | {f3(k['kappa_margin_0_1'])} | {f3(k['h1_auroc_within'])} | {f3(k['kappa_observed'])} |")
        for name in ("original", "salt_stripped"):
            r = c["variants"][name]["resolution"]
            md += ["", f"Unresolved OOD drugs, {name}: {', '.join(r['ood_drugs_unresolved_names']) or 'none'}."]
        md.append("")
    write("drugbank_salts", out, "\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
