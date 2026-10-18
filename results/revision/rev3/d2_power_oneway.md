# D2: panel power under the one-way drug bootstrap

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

Tier A. The one-way bootstrap resamples anchor drugs only, so the panel is treated as scoring the same partners every time. The two-way rows are recomputed with the same code and are a reproduction of C3(d), not a new result. beta is AUROC per standard deviation of SemEval F1; tau is extra between-model SD.

| tier/cohort | stratum | bootstrap | setting | mean sampling SD | tau | observed rho | smallest beta, power >= 0.80 | expected rho there | power at observed |rho| | max power on grid | size at beta 0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/older_primary | all | one_way | tau_0 | 0.0187 | 0.0000 | -0.161 | 0.015 | 0.621 | 0.168 | 1.000 | 0.071 |
| A/older_primary | all | one_way | tau_observed_between_sd | 0.0187 | 0.0247 | -0.161 | 0.025 | 0.600 | 0.115 | 1.000 | 0.062 |
| A/older_primary | all | two_way | tau_0 | 0.0325 | 0.0000 | -0.161 | 0.025 | 0.598 | 0.134 | 1.000 | 0.065 |
| A/older_primary | all | two_way | tau_observed_between_sd | 0.0325 | 0.0247 | -0.161 | 0.035 | 0.629 | 0.129 | 1.000 | 0.062 |
| A/older_primary | marker | one_way | tau_0 | 0.0187 | 0.0000 | -0.479 | 0.02 | 0.764 | 0.400 | 1.000 | 0.123 |
| A/older_primary | marker | one_way | tau_observed_between_sd | 0.0187 | 0.0276 | -0.479 | 0.04 | 0.773 | 0.354 | 1.000 | 0.069 |
| A/older_primary | marker | two_way | tau_0 | 0.0321 | 0.0000 | -0.479 | 0.035 | 0.757 | 0.392 | 1.000 | 0.109 |
| A/older_primary | marker | two_way | tau_observed_between_sd | 0.0321 | 0.0276 | -0.479 | 0.05 | 0.772 | 0.362 | 0.997 | 0.084 |
| A/older_primary | pair | one_way | tau_0 | 0.0187 | 0.0000 | -0.309 | 0.045 | 0.751 | 0.167 | 0.976 | 0.084 |
| A/older_primary | pair | one_way | tau_observed_between_sd | 0.0187 | 0.0229 | -0.309 | 0.075 | 0.752 | 0.155 | 0.848 | 0.065 |
| A/older_primary | pair | two_way | tau_0 | 0.0330 | 0.0000 | -0.309 | 0.08 | 0.753 | 0.163 | 0.813 | 0.079 |
| A/older_primary | pair | two_way | tau_observed_between_sd | 0.0330 | 0.0229 | -0.309 | not reached | NA | 0.156 | 0.721 | 0.071 |
| A/novel | all | one_way | tau_0 | 0.0369 | 0.0000 | -0.016 | 0.03 | 0.612 | 0.046 | 1.000 | 0.041 |
| A/novel | all | one_way | tau_observed_between_sd | 0.0369 | 0.0231 | -0.016 | 0.035 | 0.598 | 0.046 | 1.000 | 0.042 |
| A/novel | all | two_way | tau_0 | 0.0682 | 0.0000 | -0.016 | 0.055 | 0.608 | 0.057 | 0.981 | 0.055 |
| A/novel | all | two_way | tau_observed_between_sd | 0.0682 | 0.0231 | -0.016 | 0.055 | 0.586 | 0.059 | 0.976 | 0.057 |
| A/novel | marker | one_way | tau_0 | 0.0352 | 0.0000 | -0.261 | 0.04 | 0.760 | 0.123 | 0.999 | 0.048 |
| A/novel | marker | one_way | tau_observed_between_sd | 0.0352 | 0.0264 | -0.261 | 0.05 | 0.755 | 0.123 | 0.994 | 0.049 |
| A/novel | marker | two_way | tau_0 | 0.0672 | 0.0000 | -0.261 | 0.075 | 0.757 | 0.148 | 0.879 | 0.072 |
| A/novel | marker | two_way | tau_observed_between_sd | 0.0672 | 0.0264 | -0.261 | 0.08 | 0.753 | 0.146 | 0.824 | 0.071 |
| A/novel | pair | one_way | tau_0 | 0.0386 | 0.0000 | -0.030 | not reached | NA | 0.077 | 0.728 | 0.071 |
| A/novel | pair | one_way | tau_observed_between_sd | 0.0386 | 0.0203 | -0.030 | not reached | NA | 0.075 | 0.668 | 0.072 |
| A/novel | pair | two_way | tau_0 | 0.0692 | 0.0000 | -0.030 | not reached | NA | 0.073 | 0.451 | 0.071 |
| A/novel | pair | two_way | tau_observed_between_sd | 0.0692 | 0.0203 | -0.030 | not reached | NA | 0.071 | 0.437 | 0.072 |

Two-way power curves reproduce c3_statistics.json to 6 decimals: False.

| tier/cohort | stratum | setting | curve matches | max abs power difference | smallest beta matches |
| --- | --- | --- | --- | --- | --- |
| A/older_primary | all | tau_0 | False | 0.012000 | True |
| A/older_primary | all | tau_observed_between_sd | False | 0.018600 | False |
| A/older_primary | marker | tau_0 | False | 0.009600 | True |
| A/older_primary | marker | tau_observed_between_sd | False | 0.010800 | False |
| A/older_primary | pair | tau_0 | False | 0.014400 | True |
| A/older_primary | pair | tau_observed_between_sd | False | 0.019000 | True |
| A/novel | all | tau_0 | False | 0.014800 | True |
| A/novel | all | tau_observed_between_sd | False | 0.014800 | True |
| A/novel | marker | tau_0 | False | 0.014400 | True |
| A/novel | marker | tau_observed_between_sd | False | 0.016000 | True |
| A/novel | pair | tau_0 | False | 0.017000 | True |
| A/novel | pair | tau_observed_between_sd | False | 0.008600 | True |

