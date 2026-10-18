import json

from post7_common import OUT, STATUS, ci, f3, require_criteria, write


def load(name):
    return json.loads((OUT / f"{name}.json").read_text())


def pick(rows, **kw):
    return next(r for r in rows if all(r.get(k) == v for k, v in kw.items()))


def main():
    require_criteria()
    cal, cov, par = load("calibration"), load("coverage"), load("partner")
    k2 = pick(cal["kappa"], id="H1", tier="A", scheme="two_way")
    k1 = pick(cal["kappa"], id="H1", tier="A", scheme="one_way_drug")
    h1 = {s: pick(cal["intervals"], id="H1", tier="A", scheme=s) for s in ("two_way", "one_way_drug", "partner_only")}
    bay = pick(cal["bayes"], id="H1", tier="A", model="Bayesian bootstrap over drugs (primary)")
    bay2 = pick(cal["bayes"], id="H1", tier="A", model="two-way Bayesian bootstrap over drugs and partners (secondary)")
    covsum = {(s["design"], s["scheme"]): s for s in cov["summary"]}
    prim = par["decomposition"]["older_clean:A"]
    b2 = prim["systems"]["b2mixed"]
    pop = par["simulation"]["older_clean:A"]["features"]["label-free popularity"]
    loo = par["simulation"]["older_clean:A"]["features"]["leave-one-drug-out partner positive rate (label-derived contrast)"]
    out = {"status": STATUS,
           "kappa_H1": {"two_way": k2, "one_way_drug": k1},
           "H1_intervals": h1, "H1_bayes": {"primary": bay, "secondary": bay2},
           "coverage_summary": cov["summary"], "coverage_reps": cov["reps"], "coverage_boot": cov["boot"],
           "partner_primary": par["primary"], "validity": prim["validity"]}
    L = ["# Post hoc analyses after Amendment 7: summary", "", f"Status: {STATUS}. Criteria: `criteria.json`.", "",
         "## Headline framing row", "",
         f"H1 kappa against the DrugBank lookup (Older-clean, tier A, two-way bootstrap with paired DrugBank draws): {f3(k2['kappa'])}, "
         f"95% {ci(k2['kappa_ci95'])}; upper bound {f3(k2['kappa_upper95'])}. b2mixed carries at most {f3(k2['kappa_upper95'])} of the "
         f"within-drug signal of the DrugBank lookup (AUROC {f3(k2['drugbank'])}) at 95% confidence. Under the one-way drug bootstrap "
         f"the kappa interval is {ci(k1['kappa_ci95'])}.", "",
         "## 1. Interval calibration", "",
         f"* Two-way (preregistered): H1 {f3(h1['two_way']['value'])}, 90% {ci(h1['two_way']['ci90'])}, 95% {ci(h1['two_way']['ci95'])}, p_TOST {f3(h1['two_way']['p_tost'])}.",
         f"* One-way drug (sensitivity): 90% {ci(h1['one_way_drug']['ci90'])}, 95% {ci(h1['one_way_drug']['ci95'])}, p_TOST {f3(h1['one_way_drug']['p_tost'])} "
         f"(Holm {f3(h1['one_way_drug']['p_holm_family_H1_H4_H6'])}). The 95% interval lies below 0.5: {h1['one_way_drug']['ci95_below_0.5']}. "
         "Under this bootstrap the model is significantly below chance on Older-clean, that is, it carries inverted information; "
         "this is not support for equivalence and it changes no preregistered decision.",
         f"* Partner-only: 90% {ci(h1['partner_only']['ci90'])}, 95% {ci(h1['partner_only']['ci95'])}.",
         f"* Bayesian bootstrap over drugs: P(0.40 <= AUROC <= 0.60) = {f3(bay['p_in_rope'])} ({bay['verdict']}), and P(AUROC < 0.5) = {f3(bay['p_below'])}. "
         f"With Dirichlet weights on partners as well: {f3(bay2['p_in_rope'])} ({bay2['verdict']}), P(AUROC < 0.5) = {f3(bay2['p_below'])}.", "",
         f"Coverage simulation ({cov['reps']} replicates, {cov['boot']} draws each):", "",
         "| design | bootstrap | 90% coverage range | half-width ratio range | labels | adequate |", "| --- | --- | --- | --- | --- | --- |"]
    for (d, s), v in covsum.items():
        L.append(f"| {d} | {s} | {ci(v['coverage90_range'])} | {ci(v['ratio_range'])} | {v['labels']} | {v['adequate']} |")
    L += ["", "In the simulation the partner effects are independent of the labels; the real design links partners to labels through "
          "partner matching (negatives reuse other drugs' positive partners), which the simulation does not reproduce. The one-way drug "
          "bootstrap is near nominal there (one Older-clean tier B scenario at 0.865, just under the 0.87 bar) and the two-way bootstrap "
          "covers 0.989 to 1.000 with 1.5 to 2.2 times the nominal half-width.", "", "## 2. Partner structure", "",
          f"Validity (DrugBank lookup, Older-clean tier A): partner-stratified {f3(prim['validity']['partner_stratified']['drugbank_tier_A_value'])} "
          f"(lower 95% {f3(prim['validity']['partner_stratified']['drugbank_tier_A_lower95_two_way'])}, valid {prim['validity']['partner_stratified']['valid']}); "
          f"tetrad {f3(prim['validity']['tetrad']['drugbank_tier_A_value'])} (lower 95% {f3(prim['validity']['tetrad']['drugbank_tier_A_lower95_two_way'])}, "
          f"valid {prim['validity']['tetrad']['valid']}).", "",
          f"* b2mixed Older-clean tier A: within-drug {f3(b2['within']['value'])}; partner-stratified {f3(b2['partner_stratified']['value'])} "
          f"{ci(b2['partner_stratified']['two_way']['ci95'])}, explained {b2['partner_stratified']['two_way']['verdict']['explained']}; "
          f"tetrad {f3(b2['tetrad']['value'])} {ci(b2['tetrad']['two_way']['ci95'])}, explained {b2['tetrad']['two_way']['verdict']['explained']}.",
          f"* Popularity-only scorer: feature within-drug AUROC {f3(pop['feature_within_auroc'])}; at b2mixed's within-drug Spearman "
          f"({f3(pop['b2mixed_within_spearman'])}) it gives {f3(pop['matched_auroc'])}; share of the gap reproduced {f3(pop['share_of_gap_reproduced'])}; "
          f"popularity explains: {pop['popularity_explains']}. No popularity sensitivity reaches {f3(par['simulation']['older_clean:A']['b2mixed_within_auroc'])}: "
          f"the scorer's AUROC range is {ci(pop['auroc_equal_to_b2mixed'].get('auroc_range_over_lambda'))}.",
          f"* Label-derived contrast (leave-one-drug-out partner positive rate, no decision): at b2mixed's Spearman with it ({f3(loo['b2mixed_within_spearman'])}) "
          f"a scorer of that rate gives {f3(loo['matched_auroc'])} (share {f3(loo['share_of_gap_reproduced'])}).", "",
          "Every verdict above is post hoc and exploratory. H1, H4 and H6 stay inconclusive and H5 stays falsified."]
    write("summary", out, "\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
