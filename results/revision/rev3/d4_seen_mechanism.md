# D4: seen-cohort mechanism check

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

Prior (primary): for a partner, the share of positive SemEval train instances among the train instances that contain the partner as either entity. Alternative: the number of positive train instances that contain the partner divided by all positive train instances. A partner with no train instance gets the overall positive share (primary) or 0 (alternative). Priors use all train instances, including the instances of the overlap pairs. Scores are the logit of the seed-mean R2a probability (names only). Bootstrap seed 42, 1,000 draws; the Spearman interval resamples anchor drugs. Raw and adjusted within-drug AUROC use the fast within-drug AUROC of rev2 m4. These are descriptive associations on anchor drugs of which many also act as partners; no mechanism or cause is identified.

SemEval train: 13789 instances, 1570 positive, overall positive share 0.113859; 136 seen pairs (12 partners) have a partner with no train instance.

## View seen_4643 (4643 pairs)

(a) Prior as a scorer

| scorer | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only |
| --- | --- | --- | --- | --- |
| prior_primary | 0.499 | 0.500 | [0.466, 0.535] | [0.476, 0.522] |
| prior_alternative | 0.503 | 0.510 | [0.471, 0.547] | [0.482, 0.536] |
| prior_primary, only pairs whose partner has a train instance (4507 pairs) | 0.499 | 0.500 | [0.464, 0.536] | [0.476, 0.523] |

(b) Within-drug AUROC after partialling out the prior, and (c) Spearman with the prior

| family | raw within | 95% paired two-way | adjusted within | 95% paired two-way | adjusted minus raw | 95% paired two-way | slope on prior | Spearman pooled | 95% anchor bootstrap | mean within-drug Spearman | anchors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | 0.455 | [0.411, 0.494] | 0.455 | [0.411, 0.495] | -0.000 | [-0.017, 0.016] | 2.796 | 0.337 | [0.306, 0.368] | 0.460 | 299 |
| b2sentence | 0.435 | [0.395, 0.473] | 0.434 | [0.394, 0.472] | -0.001 | [-0.009, 0.006] | 0.281 | 0.075 | [0.048, 0.101] | 0.075 | 299 |
| marker | 0.398 | [0.356, 0.437] | 0.399 | [0.358, 0.437] | 0.001 | [-0.004, 0.005] | 0.053 | 0.040 | [0.010, 0.067] | 0.035 | 299 |

## View seen_not_in_semeval_train_4062 (4062 pairs)

(a) Prior as a scorer

| scorer | pooled AUROC | within-drug AUROC | 95% two-way | 95% anchor only |
| --- | --- | --- | --- | --- |
| prior_primary | 0.495 | 0.490 | [0.448, 0.533] | [0.465, 0.517] |
| prior_alternative | 0.475 | 0.482 | [0.437, 0.527] | [0.450, 0.511] |
| prior_primary, only pairs whose partner has a train instance (3926 pairs) | 0.494 | 0.488 | [0.448, 0.531] | [0.463, 0.516] |

(b) Within-drug AUROC after partialling out the prior, and (c) Spearman with the prior

| family | raw within | 95% paired two-way | adjusted within | 95% paired two-way | adjusted minus raw | 95% paired two-way | slope on prior | Spearman pooled | 95% anchor bootstrap | mean within-drug Spearman | anchors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | 0.439 | [0.390, 0.486] | 0.436 | [0.389, 0.483] | -0.003 | [-0.024, 0.017] | 2.613 | 0.334 | [0.300, 0.367] | 0.449 | 294 |
| b2sentence | 0.439 | [0.396, 0.484] | 0.439 | [0.394, 0.481] | -0.000 | [-0.009, 0.008] | 0.273 | 0.084 | [0.054, 0.111] | 0.085 | 294 |
| marker | 0.416 | [0.367, 0.465] | 0.416 | [0.367, 0.464] | 0.000 | [-0.004, 0.004] | 0.033 | 0.036 | [0.006, 0.064] | 0.034 | 294 |

