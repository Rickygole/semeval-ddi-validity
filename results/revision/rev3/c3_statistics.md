# C3: statistics

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

## (a) Holm family with the originally registered H1 endpoint

Original endpoint: pooled Novel AUROC 0.529, n = 438, 48 drugs, 95% [0.457, 0.608], 90% [0.465, 0.597], p_TOST 0.045954. Reproduces tables.md: True.

| family | hypothesis | raw p_TOST | Holm adjusted p |
| --- | --- | --- | --- |
| substituted (original H1, amended H4, H6) | H1_original_endpoint | 0.045954 | 0.137862 |
| substituted (original H1, amended H4, H6) | H4 | 0.338661 | 0.338661 |
| substituted (original H1, amended H4, H6) | H6 | 0.101898 | 0.203796 |
| as filed (Older-clean H1, H4, H6) | H1 | 0.060939 | 0.182817 |
| as filed (Older-clean H1, H4, H6) | H4 | 0.338661 | 0.338661 |
| as filed (Older-clean H1, H4, H6) | H6 | 0.101898 | 0.203796 |

Family size sensitivity (Holm adjusted):

| family | adjusted p |
| --- | --- |
| without_H4 | H1_original_endpoint=0.0919, H6=0.1019 |
| without_H6 | H1_original_endpoint=0.0919, H4=0.3387 |

H1 supported by the Holm rule (adjusted p below 0.05 and 90% interval inside [0.40, 0.60]): False.
Unadjusted p_TOST below 0.05: True. 95% interval inside [0.40, 0.60]: False. 90% interval inside [0.40, 0.60]: True.

## (b) Panel between-model to sampling variance ratio, two-way against one-way drug bootstrap

| tier/cohort | bootstrap | drugs | partners | between variance | mean single variance | ratio_old | paired reference | ratio_paired | mean covariance | upper95 <= 0.60 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/older_primary | two_way | 121 | 212 | 0.000608 | 0.001058 | 0.574 | 0.000908 | 0.670 | 0.000151 | 20 |
| A/older_primary | one_way | 121 | 212 | 0.000608 | 0.000349 | 1.743 | 0.000293 | 2.075 | 0.000056 | 20 |
| A/novel | two_way | 48 | 74 | 0.000535 | 0.004651 | 0.115 | 0.004361 | 0.123 | 0.000290 | 3 |
| A/novel | one_way | 48 | 74 | 0.000535 | 0.001365 | 0.392 | 0.001303 | 0.410 | 0.000062 | 17 |
| C-auto/older_primary | two_way | 121 | 212 | 0.000743 | 0.001157 | 0.642 | 0.000988 | 0.752 | 0.000169 | 20 |
| C-auto/older_primary | one_way | 121 | 212 | 0.000743 | 0.000376 | 1.978 | 0.000313 | 2.375 | 0.000063 | 20 |
| C-auto/novel | two_way | 48 | 74 | 0.000543 | 0.004694 | 0.116 | 0.004399 | 0.123 | 0.000295 | 2 |
| C-auto/novel | one_way | 48 | 74 | 0.000543 | 0.001371 | 0.396 | 0.001312 | 0.414 | 0.000059 | 17 |

Reproduction of the stored two-way ratios (results/revision/post8/e9.json):

| tier/cohort | ratio_old | ratio_paired | stored ratio_old | stored ratio_paired |
| --- | --- | --- | --- | --- |
| A/older_primary | True | True | 0.574 | 0.670 |
| A/novel | True | True | 0.115 | 0.123 |
| C-auto/older_primary | True | True | 0.642 | 0.752 |
| C-auto/novel | True | True | 0.116 | 0.123 |

## (c) Spearman rho of SemEval binary F1 against within-drug AUROC

| tier/cohort | stratum | checkpoints | rho | shared-draw two-way 95% | shared-draw one-way 95% | checkpoint bootstrap 95% | permutation p | nested 95% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/older_primary | all | 20 | -0.161 | [-0.468, 0.230] | [-0.433, 0.104] | [-0.635, 0.358] | 0.492 | [-0.673, 0.469] |
| A/older_primary | marker | 10 | -0.479 | [-0.830, 0.225] | [-0.818, -0.115] | [-0.889, 0.274] | 0.171 | [-0.939, 0.543] |
| A/older_primary | pair | 10 | -0.309 | [-0.600, 0.540] | [-0.515, 0.413] | [-0.888, 0.447] | 0.387 | [-0.857, 0.774] |
| A/novel | all | 20 | -0.016 | [-0.370, 0.453] | [-0.336, 0.415] | [-0.511, 0.476] | 0.947 | [-0.565, 0.635] |
| A/novel | marker | 10 | -0.261 | [-0.600, 0.648] | [-0.540, 0.479] | [-0.811, 0.503] | 0.466 | [-0.814, 0.845] |
| A/novel | pair | 10 | -0.030 | [-0.644, 0.648] | [-0.624, 0.657] | [-0.673, 0.696] | 0.946 | [-0.834, 0.862] |
| C-auto/older_primary | all | 20 | -0.167 | [-0.474, 0.241] | [-0.420, 0.113] | [-0.636, 0.365] | 0.466 | [-0.658, 0.470] |
| C-auto/older_primary | marker | 10 | -0.539 | [-0.855, 0.212] | [-0.855, -0.175] | [-0.907, 0.195] | 0.117 | [-0.950, 0.494] |
| C-auto/older_primary | pair | 10 | -0.406 | [-0.576, 0.576] | [-0.467, 0.406] | [-0.961, 0.396] | 0.244 | [-0.851, 0.790] |
| C-auto/novel | all | 20 | 0.007 | [-0.370, 0.455] | [-0.338, 0.413] | [-0.517, 0.512] | 0.980 | [-0.570, 0.638] |
| C-auto/novel | marker | 10 | -0.297 | [-0.612, 0.636] | [-0.564, 0.486] | [-0.912, 0.538] | 0.406 | [-0.824, 0.849] |
| C-auto/novel | pair | 10 | -0.030 | [-0.638, 0.648] | [-0.636, 0.644] | [-0.704, 0.673] | 0.937 | [-0.846, 0.861] |

## (d) Power by simulation

beta is AUROC per standard deviation of SemEval F1; tau is extra between-model SD. Detectable rho is the mean observed Spearman rho at the smallest beta of the plan grid (0 to 0.08) with power at least 0.80.

| tier/cohort | stratum | setting | mean sampling SD | tau | smallest beta, power >= 0.80 | expected rho there | power at observed |rho| | max power on grid | size at beta 0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/older_primary | all | tau_0 | 0.0325 | 0.0000 | 0.025 | 0.598 | 0.134 | 1.000 | 0.066 |
| A/older_primary | all | tau_observed_between_sd | 0.0325 | 0.0247 | 0.03 | 0.575 | 0.126 | 1.000 | 0.062 |
| A/older_primary | marker | tau_0 | 0.0321 | 0.0000 | 0.035 | 0.757 | 0.390 | 1.000 | 0.119 |
| A/older_primary | marker | tau_observed_between_sd | 0.0321 | 0.0276 | 0.045 | 0.738 | 0.358 | 0.996 | 0.083 |
| A/older_primary | pair | tau_0 | 0.0330 | 0.0000 | 0.08 | 0.753 | 0.170 | 0.805 | 0.080 |
| A/older_primary | pair | tau_observed_between_sd | 0.0330 | 0.0229 | not reached | NA | 0.158 | 0.719 | 0.071 |
| A/novel | all | tau_0 | 0.0682 | 0.0000 | 0.055 | 0.606 | 0.060 | 0.976 | 0.057 |
| A/novel | all | tau_observed_between_sd | 0.0682 | 0.0231 | 0.055 | 0.583 | 0.059 | 0.971 | 0.057 |
| A/novel | marker | tau_0 | 0.0672 | 0.0000 | 0.075 | 0.758 | 0.146 | 0.881 | 0.074 |
| A/novel | marker | tau_observed_between_sd | 0.0672 | 0.0264 | 0.08 | 0.753 | 0.142 | 0.827 | 0.075 |
| A/novel | pair | tau_0 | 0.0692 | 0.0000 | not reached | NA | 0.074 | 0.451 | 0.080 |
| A/novel | pair | tau_observed_between_sd | 0.0692 | 0.0203 | not reached | NA | 0.069 | 0.439 | 0.068 |
| C-auto/older_primary | all | tau_0 | 0.0340 | 0.0000 | 0.025 | 0.580 | 0.142 | 1.000 | 0.075 |
| C-auto/older_primary | all | tau_observed_between_sd | 0.0340 | 0.0273 | 0.035 | 0.601 | 0.131 | 1.000 | 0.059 |
| C-auto/older_primary | marker | tau_0 | 0.0337 | 0.0000 | 0.035 | 0.743 | 0.459 | 1.000 | 0.115 |
| C-auto/older_primary | marker | tau_observed_between_sd | 0.0337 | 0.0298 | 0.05 | 0.750 | 0.439 | 0.992 | 0.085 |
| C-auto/older_primary | pair | tau_0 | 0.0344 | 0.0000 | not reached | NA | 0.234 | 0.791 | 0.073 |
| C-auto/older_primary | pair | tau_observed_between_sd | 0.0344 | 0.0261 | not reached | NA | 0.232 | 0.682 | 0.066 |
| C-auto/novel | all | tau_0 | 0.0685 | 0.0000 | 0.055 | 0.607 | 0.059 | 0.982 | 0.058 |
| C-auto/novel | all | tau_observed_between_sd | 0.0685 | 0.0233 | 0.055 | 0.584 | 0.062 | 0.977 | 0.061 |
| C-auto/novel | marker | tau_0 | 0.0674 | 0.0000 | 0.075 | 0.757 | 0.173 | 0.879 | 0.080 |
| C-auto/novel | marker | tau_observed_between_sd | 0.0674 | 0.0263 | 0.08 | 0.753 | 0.163 | 0.832 | 0.075 |
| C-auto/novel | pair | tau_0 | 0.0696 | 0.0000 | not reached | NA | 0.073 | 0.455 | 0.074 |
| C-auto/novel | pair | tau_observed_between_sd | 0.0696 | 0.0209 | not reached | NA | 0.069 | 0.436 | 0.067 |

