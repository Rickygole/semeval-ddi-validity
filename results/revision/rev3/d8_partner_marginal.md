# D8: consequence of the partner anti-correlation for the evaluated systems

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

For each pair (anchor A, partner y) the other pairs of y are those of the same cohort with anchor A removed (the exclusion of `rev3_c2.lodo_scores`). The leave-one-drug-out rate is the smoothed positive rate (pos + 1) / (n + 2) of those pairs; the partner-marginal score is the unweighted mean of the system's stored score (probability, or 0 or 1 for DrugBank) over the same pairs. Pairs with no other pair of the partner are dropped and counted. Intervals: 95% percentile, 1000 draws; the Spearman intervals resample partner drugs (seed 42), the within-drug AUROC intervals are the two-way cluster bootstrap of `aa.draws` with the cohort seed, scores held fixed across draws. The partner-marginal score is a scorer only in the sense that the partner-matched label construction would reward it; no causal statement is made.

## older_clean

1832 pairs, 599 positive, 128 anchor drugs, 212 partner drugs.

| system | seeds | pairs used | pair-level Spearman | 95% CI | partner-level Spearman | 95% CI | partners | marginal-score within-drug AUROC | 95% CI | own within-drug AUROC | LOO-rate within-drug AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup |  | 1832 | 0.185 | [0.074, 0.275] | 0.129 | [0.023, 0.240] | 212 | 0.441 | [0.378, 0.500] | 0.641 | 0.092 |
| stored b2mixed |  | 1832 | -0.082 | [-0.197, 0.032] | 0.031 | [-0.115, 0.185] | 212 | 0.523 | [0.464, 0.583] | 0.452 | 0.092 |
| stored b2sentence |  | 1832 | -0.030 | [-0.157, 0.092] | 0.012 | [-0.136, 0.148] | 212 | 0.522 | [0.464, 0.577] | 0.453 | 0.092 |
| Qwen names only |  | 1832 | -0.136 | [-0.229, -0.036] | -0.100 | [-0.239, 0.041] | 212 | 0.474 | [0.406, 0.545] | 0.602 | 0.092 |
| R2a b2mixed | [42, 1, 2, 3, 4] | 1832 | -0.058 | [-0.177, 0.059] | 0.048 | [-0.092, 0.189] | 212 | 0.526 | [0.466, 0.588] | 0.454 | 0.092 |
| R2a b2sentence | [42, 1, 2, 3, 4] | 1832 | -0.021 | [-0.142, 0.097] | 0.020 | [-0.131, 0.157] | 212 | 0.528 | [0.468, 0.584] | 0.472 | 0.092 |
| R2a marker | [42, 1, 2, 3, 4] | 1832 | -0.092 | [-0.223, 0.043] | 0.066 | [-0.073, 0.209] | 212 | 0.532 | [0.473, 0.589] | 0.407 | 0.092 |

## novel

438 pairs, 148 positive, 48 anchor drugs, 74 partner drugs.

| system | seeds | pairs used | pair-level Spearman | 95% CI | partner-level Spearman | 95% CI | partners | marginal-score within-drug AUROC | 95% CI | own within-drug AUROC | LOO-rate within-drug AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup |  | 438 | 0.170 | [0.036, 0.304] | -0.003 | [-0.058, 0.057] | 74 | 0.365 | [0.241, 0.492] | 0.729 | 0.022 |
| stored b2mixed |  | 438 | -0.062 | [-0.160, 0.055] | 0.019 | [-0.031, 0.086] | 74 | 0.511 | [0.387, 0.638] | 0.523 | 0.022 |
| stored b2sentence |  | 438 | -0.137 | [-0.236, -0.034] | -0.123 | [-0.256, -0.096] | 74 | 0.518 | [0.380, 0.674] | 0.490 | 0.022 |
| Qwen names only |  | 438 | 0.050 | [-0.051, 0.162] | 0.189 | [0.173, 0.358] | 74 | 0.493 | [0.355, 0.631] | 0.579 | 0.022 |
| R2a b2mixed | [42, 1, 2, 3, 4] | 438 | -0.008 | [-0.108, 0.109] | 0.085 | [0.047, 0.188] | 74 | 0.482 | [0.343, 0.621] | 0.483 | 0.022 |
| R2a b2sentence | [42, 1, 2, 3, 4] | 438 | -0.063 | [-0.162, 0.061] | 0.025 | [-0.025, 0.101] | 74 | 0.509 | [0.358, 0.656] | 0.511 | 0.022 |
| R2a marker | [42, 1, 2, 3, 4] | 438 | -0.065 | [-0.200, 0.056] | 0.041 | [-0.008, 0.125] | 74 | 0.546 | [0.423, 0.678] | 0.494 | 0.022 |

## seen

4643 pairs, 1542 positive, 299 anchor drugs, 313 partner drugs.

| system | seeds | pairs used | pair-level Spearman | 95% CI | partner-level Spearman | 95% CI | partners | marginal-score within-drug AUROC | 95% CI | own within-drug AUROC | LOO-rate within-drug AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup |  | 4643 | 0.046 | [-0.018, 0.109] | 0.203 | [0.088, 0.294] | 313 | 0.479 | [0.443, 0.515] | 0.611 | 0.061 |
| R2a b2mixed | [42, 1, 2, 3, 4] | 4643 | -0.109 | [-0.178, -0.027] | -0.008 | [-0.122, 0.098] | 313 | 0.513 | [0.475, 0.550] | 0.455 | 0.061 |
| R2a b2sentence | [42, 1, 2, 3, 4] | 4643 | -0.122 | [-0.192, -0.044] | -0.079 | [-0.176, 0.026] | 313 | 0.523 | [0.486, 0.555] | 0.435 | 0.061 |
| R2a marker | [42, 1, 2, 3, 4] | 4643 | -0.050 | [-0.133, 0.032] | 0.006 | [-0.098, 0.125] | 313 | 0.515 | [0.479, 0.549] | 0.398 | 0.061 |

