# D3: R2a on the seen pairs that are in SemEval train

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

Overlap: {'match_rule': 'unordered pair, each name lowercased and stripped, against every SemEval 2013 train pair', 'n_pairs': 4643, 'n_in_semeval_train': 581, 'n_in_semeval_train_with_a_positive_instance': 213, 'n_positive_and_semeval_positive': 206, 'n_not_in_semeval_train': 4062, 'n_positive_not_in_semeval_train': 1134, 'n_drugs_both_anchor_and_partner': 175, 'n_anchor_drugs': 299, 'n_partner_drugs': 313}

Within-drug AUROC by anchor drug, seed mean over the seeds present, bootstrap seed 42, 1,000 draws. Anchor drugs with one class only do not contribute to the within-drug AUROC; their number is shown.

## Cohort seen

4643 pairs, 1542 positive, 299 anchor drugs (298 with both classes), 313 partner drugs, 175 drugs act as both anchor and partner.

| family | input | seeds | complete | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only | per-seed within |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | names_only | 42,1,2,3,4 | True | 0.444 | 0.455 | [0.411, 0.494] | [0.433, 0.478] | 0.460, 0.458, 0.464, 0.457, 0.451 |
| b2mixed | names_text_b1 | 42,1,2,3,4 | True | 0.446 | 0.464 | [0.422, 0.504] | [0.441, 0.488] | 0.478, 0.462, 0.468, 0.461, 0.440 |
| b2sentence | names_only | 42,1,2,3,4 | True | 0.437 | 0.435 | [0.395, 0.473] | [0.414, 0.458] | 0.425, 0.466, 0.472, 0.457, 0.446 |
| b2sentence | names_text_b1 | 42,1,2,3,4 | True | 0.426 | 0.429 | [0.391, 0.466] | [0.407, 0.451] | 0.430, 0.484, 0.486, 0.457, 0.441 |
| marker | names_only | 42,1,2,3,4 | True | 0.406 | 0.398 | [0.356, 0.437] | [0.375, 0.423] | 0.418, 0.438, 0.425, 0.396, 0.417 |

## Cohort seen_not_in_semeval_train

4062 pairs, 1134 positive, 299 anchor drugs (267 with both classes), 313 partner drugs, 175 drugs act as both anchor and partner.

| family | input | seeds | complete | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only | per-seed within |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | names_only | 42,1,2,3,4 | True | 0.422 | 0.439 | [0.390, 0.486] | [0.414, 0.466] | 0.442, 0.441, 0.443, 0.439, 0.450 |
| b2mixed | names_text_b1 | 42,1,2,3,4 | True | 0.426 | 0.450 | [0.404, 0.495] | [0.426, 0.479] | 0.457, 0.443, 0.456, 0.445, 0.443 |
| b2sentence | names_only | 42,1,2,3,4 | True | 0.444 | 0.439 | [0.396, 0.484] | [0.416, 0.464] | 0.437, 0.469, 0.487, 0.459, 0.457 |
| b2sentence | names_text_b1 | 42,1,2,3,4 | True | 0.438 | 0.441 | [0.395, 0.485] | [0.417, 0.466] | 0.441, 0.493, 0.492, 0.465, 0.455 |
| marker | names_only | 42,1,2,3,4 | True | 0.425 | 0.416 | [0.367, 0.465] | [0.389, 0.447] | 0.428, 0.456, 0.441, 0.409, 0.420 |

## Cohort seen_in_semeval_train

581 pairs, 408 positive, 184 anchor drugs (73 with both classes), 158 partner drugs, 73 drugs act as both anchor and partner.

| family | input | seeds | complete | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only | per-seed within |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | names_only | 42,1,2,3,4 | True | 0.627 | 0.590 | [0.433, 0.742] | [0.524, 0.654] | 0.588, 0.586, 0.571, 0.573, 0.545 |
| b2mixed | names_text_b1 | 42,1,2,3,4 | True | 0.626 | 0.583 | [0.425, 0.737] | [0.510, 0.660] | 0.595, 0.581, 0.545, 0.607, 0.523 |
| b2sentence | names_only | 42,1,2,3,4 | True | 0.500 | 0.446 | [0.279, 0.601] | [0.358, 0.530] | 0.492, 0.389, 0.431, 0.424, 0.475 |
| b2sentence | names_text_b1 | 42,1,2,3,4 | True | 0.492 | 0.459 | [0.304, 0.602] | [0.384, 0.528] | 0.480, 0.549, 0.487, 0.547, 0.436 |
| marker | names_only | 42,1,2,3,4 | True | 0.442 | 0.419 | [0.265, 0.573] | [0.351, 0.492] | 0.449, 0.546, 0.420, 0.455, 0.395 |

Existing r2a.json two-way points and intervals reproduced for 10 rows: True.

