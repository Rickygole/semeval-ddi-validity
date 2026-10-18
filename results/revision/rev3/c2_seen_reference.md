# C2: reference rows for the R2a seen cohort

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

DrugBank release: version 5.1, exported on 2026-03-05.

Overlap with SemEval train: {"match_rule": "unordered pair, each name lowercased and stripped, against every SemEval 2013 train pair", "n_pairs": 4643, "n_in_semeval_train": 581, "n_in_semeval_train_with_a_positive_instance": 213, "n_positive_and_semeval_positive": 206, "n_not_in_semeval_train": 4062, "n_positive_not_in_semeval_train": 1134, "n_drugs_both_anchor_and_partner": 175, "n_anchor_drugs": 299, "n_partner_drugs": 313}

## Cohort seen

4643 pairs, 1542 positive, 299 anchor drugs, 313 partner drugs, 175 drugs act as both anchor and partner.

| row | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only |
| --- | --- | --- | --- | --- |
| drugbank_lookup | 0.633 | 0.611 | [0.585, 0.639] | [0.596, 0.627] |
| label_string_match | 0.831 | 0.837 | [0.802, 0.867] | [0.812, 0.861] |
| partner_prior_label_free_anchor_section_excluded | 0.488 | 0.501 | [0.459, 0.537] | [0.473, 0.528] |
| partner_prior_with_anchor_section (circular for these pairs) | 0.506 | 0.515 | [0.475, 0.551] | [0.486, 0.542] |
| partner_rate_leave_one_drug_out | 0.067 | 0.061 | [0.034, 0.095] | [0.053, 0.070] |
| partner_rate_not_left_out (circular reference) | 0.518 | 0.511 | [0.476, 0.549] | [0.485, 0.539] |

## Cohort seen_not_in_semeval_train

4062 pairs, 1134 positive, 299 anchor drugs, 313 partner drugs, 175 drugs act as both anchor and partner.

| row | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only |
| --- | --- | --- | --- | --- |
| drugbank_lookup | 0.627 | 0.613 | [0.586, 0.647] | [0.596, 0.633] |
| label_string_match | 0.826 | 0.833 | [0.793, 0.871] | [0.803, 0.861] |
| partner_prior_label_free_anchor_section_excluded | 0.475 | 0.489 | [0.441, 0.533] | [0.457, 0.518] |
| partner_prior_with_anchor_section (circular for these pairs) | 0.494 | 0.505 | [0.455, 0.548] | [0.473, 0.533] |
| partner_rate_leave_one_drug_out (from the 4,062 pairs) | 0.290 | 0.285 | [0.233, 0.333] | [0.264, 0.306] |
| partner_rate_leave_one_drug_out (from all 4,643 pairs) | 0.066 | 0.062 | [0.034, 0.098] | [0.052, 0.073] |
| partner_rate_not_left_out (circular reference) | 0.578 | 0.572 | [0.533, 0.615] | [0.546, 0.600] |

DrugBank: {"listed": 3258, "unresolvable": 2, "one_side_resolved": 287}

label_string_match is 0 for every negative by construction (E7 negatives are not named anywhere in the anchor label). Rows marked circular include the anchor's own label or the pair's own training label. No comparison with the Novel or Older rows is made.

