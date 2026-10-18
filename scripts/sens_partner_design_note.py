import json

from sens_common import ROOT, OUT, ci, f3, write

EXP7 = ROOT / "results" / "revision" / "amend7" / "cpu" / "exp7_below_chance.json"
PRIMARY = "b2mixed-biomedbert"
FEATS = (("iii_partner_prior_loo_rate", "leave-one-drug-out partner positive rate (test labels)"),
         ("b_partner_popularity_loo_positives", "leave-one-drug-out partner positive count (test labels)"),
         ("iii2_partner_prior_vocab_di", "label-free partner prior (share of vocabulary Drug Interactions sections naming the partner)"))


def share(raw, part):
    gap = 0.5 - raw
    return (part - raw) / gap if gap > 0 else None


def main():
    d = json.loads(EXP7.read_text())["causes"]
    out = {"source": "results/revision/amend7/cpu/exp7_below_chance.json", "primary_system": PRIMARY, "cohorts": {}}
    for cohort in ("older_clean", "novel"):
        out["cohorts"][cohort] = {}
        for tier in ("A", "B"):
            c = d[cohort][tier]
            s = c["systems"][PRIMARY]
            raw = s["raw_within_auroc"]["value"]
            rows = {}
            for k, _ in FEATS:
                f = c["features"][k]
                b = s["by_feature"][k]
                part = b["partialled_within_auroc"]["value"]
                rows[k] = {"feature_within_auroc": f["within_auroc"]["value"], "feature_within_auroc_ci95": f["within_auroc"]["ci95"],
                           "mean_pos": f["mean_pos"], "mean_neg": f["mean_neg"],
                           "primary_spearman_within": b["within_drug_spearman"]["value"],
                           "primary_spearman_within_ci95": b["within_drug_spearman"]["ci95"],
                           "primary_partialled_within_auroc": part,
                           "primary_partialled_within_auroc_ci95": b["partialled_within_auroc"]["ci95"],
                           "change_in_auroc": part - raw, "share_of_gap_below_0_5": share(raw, part)}
            joint = s["by_feature"].get("joint a+b+c+e", {}).get("partialled_within_auroc", {}).get("value")
            dbs = c["systems"]["DrugBank lookup"]
            out["cohorts"][cohort][tier] = {"n": c["n"], "n_pos": c["n_pos"], "n_drugs": c["n_drugs"],
                                            "primary_raw_within_auroc": raw, "primary_raw_within_auroc_ci95": s["raw_within_auroc"]["ci95"],
                                            "primary_joint_abce_partialled": joint, "features": rows,
                                            "drugbank_raw_within_auroc": dbs["raw_within_auroc"]["value"],
                                            "drugbank_partialled_on_iii": dbs["by_feature"]["iii_partner_prior_loo_rate"]["partialled_within_auroc"]["value"]}
    oc = out["cohorts"]["older_clean"]["A"]
    iii = oc["features"]["iii_partner_prior_loo_rate"]
    pop = oc["features"]["b_partner_popularity_loo_positives"]
    free = oc["features"]["iii2_partner_prior_vocab_di"]
    ocb = out["cohorts"]["older_clean"]["B"]["features"]["iii_partner_prior_loo_rate"]
    nv = out["cohorts"]["novel"]["A"]
    nvi = nv["features"]["iii_partner_prior_loo_rate"]
    md = ["# Partner matching builds an anti-signal into the OOD sets", "",
          "Post hoc note. Every number is read from `results/revision/amend7/cpu/exp7_below_chance.json` by "
          "`scripts/sens_partner_design_note.py`; shares are computed from those values. No decision changes.", "",
          "## The design", "",
          "Negatives are partner matched: each negative reuses a positive's partner with a different OOD drug whose label never "
          "names it (`docs/PREREGISTRATION.md`, frozen evaluation sets). The partner of a negative is therefore, by construction, "
          "a positive partner of some other drug in the cohort, while the partner of a positive need not be. Within a drug, the "
          "partner's positive rate among the other drugs of the cohort is then higher for negatives than for positives.", "",
          "## The size of the anti-signal", "",
          f"On Older-clean (tier A, n = {oc['n']}, {oc['n_drugs']} drugs) the leave-one-drug-out partner positive rate has "
          f"within-drug AUROC {f3(iii['feature_within_auroc'])} {ci(iii['feature_within_auroc_ci95'])}: its mean is "
          f"{f3(iii['mean_pos'])} for positives and {f3(iii['mean_neg'])} for negatives. On tier B it is {f3(ocb['feature_within_auroc'])} "
          f"{ci(ocb['feature_within_auroc_ci95'])}, and on Novel tier A {f3(nvi['feature_within_auroc'])} {ci(nvi['feature_within_auroc_ci95'])}. "
          f"The partner positive count gives {f3(pop['feature_within_auroc'])} {ci(pop['feature_within_auroc_ci95'])}. A label-free partner prior "
          f"(how often vocabulary Drug Interactions sections name the partner) sits at {f3(free['feature_within_auroc'])} "
          f"{ci(free['feature_within_auroc_ci95'])}, so the anti-signal is a property of the test labels, not of the partners.", "",
          "Any scorer whose output rises with how often a partner is a positive in this cohort is pushed below 0.5 within drug "
          "by construction. A model that learned that some partners interact often, and applied that to these pairs, would "
          "score below chance without any error about the OOD drug.", "",
          "## How much of the 0.452 it can account for", "",
          f"Primary system {PRIMARY}, five-seed mean, names only, Older-clean tier A: raw within-drug AUROC {f3(oc['primary_raw_within_auroc'])} "
          f"{ci(oc['primary_raw_within_auroc_ci95'])}, a gap of {f3(0.5 - oc['primary_raw_within_auroc'])} below chance. "
          "exp7 removes the within-drug linear association with each feature and recomputes the AUROC (partialled).", "",
          "| feature | Spearman with the model, within drug | 95% CI | partialled AUROC | 95% CI | change | share of the gap below 0.5 |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for k, label in FEATS:
        r = oc["features"][k]
        md.append(f"| {label} | {f3(r['primary_spearman_within'])} | {ci(r['primary_spearman_within_ci95'])} | "
                  f"{f3(r['primary_partialled_within_auroc'])} | {ci(r['primary_partialled_within_auroc_ci95'])} | "
                  f"{r['change_in_auroc']:+.3f} | {f3(r['share_of_gap_below_0_5'])} |")
    md += ["", f"Joint partialling on the preregistered causes a, b, c and e gives {f3(oc['primary_joint_abce_partialled'])}.", "",
           f"Partialling on the test-label partner rate moves the primary system from {f3(oc['primary_raw_within_auroc'])} to "
           f"{f3(iii['primary_partialled_within_auroc'])}, {f3(iii['share_of_gap_below_0_5'])} of the gap below 0.5, and its interval "
           f"{ci(iii['primary_partialled_within_auroc_ci95'])} then covers 0.5. This is an upper estimate of what the design explains: "
           f"the model's within-drug Spearman with the feature is only {f3(iii['primary_spearman_within'])} "
           f"{ci(iii['primary_spearman_within_ci95'])}, and the feature is built from the test labels, so partialling on it also "
           f"removes label information. The same partialling takes the DrugBank lookup from {f3(oc['drugbank_raw_within_auroc'])} "
           f"to {f3(oc['drugbank_partialled_on_iii'])}, which shows how strongly a label-derived regressor can move any scorer. "
           f"The label-free prior explains none of it ({f3(free['primary_partialled_within_auroc'])}), and the partner count "
           f"{f3(pop['share_of_gap_below_0_5'])} of the gap.", "",
           f"On Novel the primary system is {f3(nv['primary_raw_within_auroc'])} raw and "
           f"{f3(nvi['primary_partialled_within_auroc'])} partialled on the same feature, so there is no below-chance result to explain.", "",
           "Reading: partner matching makes below-chance scores the expected outcome for a partner-popularity-sensitive scorer, and "
           f"can account for up to {f3(iii['share_of_gap_below_0_5'])} of the Older-clean deficit under the most generous partialling. It is reported "
           "as a design property of the evaluation sets, not as a confirmed cause; exp7's preregistered verdict for cause b stays rejected.", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "partner_design_note.md").write_text("\n".join(md))
    write("partner_design_note", out)
    print("\n".join(md))


if __name__ == "__main__":
    main()
