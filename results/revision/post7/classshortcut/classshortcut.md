# Class-shortcut test of E7c (post 7)

written 2026-10-16 before any statistic in results/revision/post7/classshortcut was computed; post hoc and exploratory; changes no preregistered decision

## Verdict (Older-primary tier A, pre-stated rule in criteria.json)

- analysis 1 class scorer sufficient: True (definition: atc3)
- analysis 2 class-dependent: ATC-4 False, stem False
- analysis 3 residual 95% interval contains 0.5: False
- class share (rank, joint): 0.226
- verdict: (c) mix

## older_primary:A

rows 1721, drugs 121, positives 562

| system | within-drug AUROC [95%] |
|---|---|
| E7c | 0.695 [0.630, 0.762] |
| E7d | 0.671 [0.601, 0.737] |
| E7e | 0.734 [0.665, 0.802] |
| b2mixed | 0.447 [0.381, 0.517] |
| Qwen names only | 0.610 [0.542, 0.677] |

### 1. Class-sibling scorer (no model)

| definition | pool | score | all drugs | drugs with mates (n) | E7c on those drugs | E7c minus scorer |
|---|---|---|---|---|---|---|
| atc4 | anchors | share | 0.602 [0.559, 0.654] | 0.671 [0.606, 0.740] (70/121) | 0.720 [0.636, 0.805] | 0.093 [0.022, 0.159] |
| atc4 | anchors | conditional | 0.601 [0.559, 0.652] | 0.669 [0.603, 0.738] (70/121) | 0.720 [0.636, 0.805] | 0.093 [0.026, 0.160] |
| atc4 | all_training_drugs | share | 0.605 [0.559, 0.656] | 0.646 [0.583, 0.709] (83/121) | 0.712 [0.637, 0.789] | 0.089 [0.022, 0.155] |
| atc4 | all_training_drugs | conditional | 0.604 [0.560, 0.655] | 0.645 [0.582, 0.709] (83/121) | 0.712 [0.637, 0.789] | 0.090 [0.025, 0.157] |
| stem | anchors | share | 0.579 [0.540, 0.626] | 0.709 [0.627, 0.793] (46/121) | 0.730 [0.630, 0.824] | 0.116 [0.047, 0.189] |
| stem | anchors | conditional | 0.579 [0.539, 0.626] | 0.707 [0.627, 0.792] (46/121) | 0.730 [0.630, 0.824] | 0.116 [0.047, 0.190] |
| stem | all_training_drugs | share | 0.579 [0.539, 0.626] | 0.700 [0.615, 0.784] (48/121) | 0.724 [0.620, 0.819] | 0.116 [0.046, 0.188] |
| stem | all_training_drugs | conditional | 0.578 [0.538, 0.626] | 0.699 [0.617, 0.783] (48/121) | 0.724 [0.620, 0.819] | 0.116 [0.047, 0.190] |
| atc3 | anchors | share | 0.638 [0.583, 0.693] | 0.661 [0.596, 0.722] (103/121) | 0.703 [0.634, 0.775] | 0.057 [-0.012, 0.123] |
| atc3 | anchors | conditional | 0.632 [0.576, 0.687] | 0.654 [0.590, 0.715] (103/121) | 0.703 [0.634, 0.775] | 0.063 [-0.006, 0.133] |
| atc3 | all_training_drugs | share | 0.644 [0.584, 0.699] | 0.656 [0.592, 0.716] (107/121) | 0.700 [0.632, 0.770] | 0.051 [-0.018, 0.118] |
| atc3 | all_training_drugs | conditional | 0.638 [0.580, 0.694] | 0.650 [0.586, 0.709] (107/121) | 0.700 [0.632, 0.770] | 0.057 [-0.014, 0.126] |

### 2. Split by having a training anchor in the same class

atc4: with 70 drugs (1018 rows), without 51 drugs (703 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.720 [0.636, 0.805] | 0.657 [0.540, 0.762] | 0.063 [-0.074, 0.204] |
| E7d | 0.713 [0.624, 0.788] | 0.610 [0.495, 0.709] | 0.103 [-0.030, 0.244] |
| E7e | 0.776 [0.695, 0.853] | 0.672 [0.550, 0.786] | 0.104 [-0.026, 0.246] |
| b2mixed | 0.412 [0.323, 0.502] | 0.498 [0.388, 0.607] | -0.086 [-0.237, 0.057] |
| Qwen names only | 0.588 [0.498, 0.682] | 0.641 [0.531, 0.744] | -0.052 [-0.197, 0.100] |

E7c drug-averaged per-drug AUROC: with 0.726 (70), without 0.702 (51)

stem: with 46 drugs (661 rows), without 75 drugs (1060 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.730 [0.630, 0.824] | 0.673 [0.586, 0.759] | 0.057 [-0.075, 0.187] |
| E7d | 0.714 [0.604, 0.808] | 0.646 [0.564, 0.729] | 0.068 [-0.075, 0.197] |
| E7e | 0.778 [0.671, 0.863] | 0.708 [0.617, 0.794] | 0.070 [-0.056, 0.193] |
| b2mixed | 0.437 [0.326, 0.551] | 0.453 [0.365, 0.542] | -0.016 [-0.159, 0.118] |
| Qwen names only | 0.637 [0.532, 0.745] | 0.593 [0.503, 0.684] | 0.043 [-0.099, 0.191] |

E7c drug-averaged per-drug AUROC: with 0.716 (46), without 0.716 (75)

### 3. E7c partialled on the class-sibling score within drug

| adjustment | residual within-drug AUROC [95%] | class share | contains 0.5 |
|---|---|---|---|
| rank:joint | 0.651 [0.587, 0.716] | 0.226 | False |
| rank:atc4 | 0.666 [0.604, 0.730] | 0.148 | False |
| rank:stem | 0.663 [0.598, 0.730] | 0.164 | False |
| rank:atc3 | 0.660 [0.596, 0.726] | 0.178 | False |
| linear:joint | 0.647 [0.583, 0.716] | 0.243 | False |
| linear:atc4 | 0.658 [0.593, 0.727] | 0.188 | False |
| linear:stem | 0.659 [0.592, 0.730] | 0.183 | False |
| linear:atc3 | 0.661 [0.599, 0.729] | 0.175 | False |
| post_hoc:rank:joint_plus_embedding_top1 | 0.650 [0.586, 0.718] | 0.228 | False |
| post_hoc:rank:joint_plus_embedding_top3 | 0.651 [0.585, 0.720] | 0.223 | False |

within-drug Spearman of logit E7c with the class score: atc4 0.208, stem 0.184, atc3 0.271

### 4. Mechanism

PK positives 302 (67 drugs), PD or other 260 (90 drugs)

| scorer | PK | PD or other |
|---|---|---|
| E7c | 0.623 [0.526, 0.711] | 0.766 [0.676, 0.845] |
| class_atc4 | 0.575 [0.525, 0.639] | 0.629 [0.565, 0.692] |
| class_stem | 0.557 [0.513, 0.612] | 0.601 [0.545, 0.669] |

E7c PK minus PD: -0.143 [-0.276, -0.025]

post hoc broader PK rule (adds pharmacokinetic, concentration, bioavailability, absorption, plasma or serum level, inducer): PK 349, PD or other 213; E7c PK 0.643 [0.555, 0.725], PD or other 0.770 [0.673, 0.857], difference -0.128 [-0.250, -0.010]

### 5. DrugBank operating point

| quantity | value [95%] |
|---|---|
| drugbank_fpr_pooled | 0.419 [0.356, 0.494] |
| drugbank_tpr_pooled | 0.802 [0.721, 0.870] |
| e7c_tpr_within_at_drugbank_fpr | 0.675 [0.571, 0.778] |
| drugbank_tpr_within_at_its_fpr | 0.650 [0.562, 0.720] |
| e7c_minus_drugbank_tpr_within | 0.025 [-0.075, 0.144] |
| e7c_minus_drugbank_tpr_pooled | -0.127 [-0.239, -0.006] |
| e7c_pauc_to_drugbank_fpr | 0.205 [0.161, 0.277] |
| drugbank_pauc_to_its_fpr | 0.158 [0.122, 0.211] |
| e7c_minus_drugbank_pauc | 0.047 [0.008, 0.096] |
| e7c_pauc_over_fpr | 0.489 [0.423, 0.606] |
| drugbank_pauc_over_fpr | 0.376 [0.333, 0.460] |
| e7c_auroc_from_placements | 0.695 [0.630, 0.762] |
| drugbank_auroc_from_placements | 0.652 [0.601, 0.705] |

### 6. Non-constant partner priors

partner training positive rate: within 0.495 [0.432, 0.555]; partners in training 192/212; distinct-partner mean 0.336, sd 0.097, range 0.067 to 0.647

- class-conditional partner rate, atc4: 0.601 [0.559, 0.652]
- class-conditional partner rate, stem: 0.579 [0.539, 0.626]
- class-conditional partner rate, atc3: 0.632 [0.576, 0.687]
- frozen BiomedBERT name similarity, top1: 0.595 [0.528, 0.665]
- frozen BiomedBERT name similarity, top3: 0.579 [0.504, 0.646]
- frozen BiomedBERT name similarity, top5: 0.570 [0.496, 0.639]

## older_primary:B

rows 1122, drugs 121, positives 451

| system | within-drug AUROC [95%] |
|---|---|
| E7c | 0.754 [0.649, 0.841] |
| E7d | 0.731 [0.630, 0.816] |
| E7e | 0.777 [0.681, 0.860] |
| b2mixed | 0.396 [0.298, 0.508] |
| Qwen names only | 0.663 [0.552, 0.769] |

### 1. Class-sibling scorer (no model)

| definition | pool | score | all drugs | drugs with mates (n) | E7c on those drugs | E7c minus scorer |
|---|---|---|---|---|---|---|
| atc4 | anchors | share | 0.613 [0.557, 0.675] | 0.685 [0.605, 0.766] (70/121) | 0.784 [0.654, 0.889] | 0.142 [0.041, 0.242] |
| atc4 | anchors | conditional | 0.611 [0.556, 0.672] | 0.682 [0.601, 0.762] (70/121) | 0.784 [0.654, 0.889] | 0.144 [0.042, 0.244] |
| atc4 | all_training_drugs | share | 0.618 [0.560, 0.684] | 0.666 [0.587, 0.750] (83/121) | 0.772 [0.644, 0.870] | 0.136 [0.034, 0.237] |
| atc4 | all_training_drugs | conditional | 0.615 [0.559, 0.679] | 0.662 [0.585, 0.744] (83/121) | 0.772 [0.644, 0.870] | 0.139 [0.037, 0.239] |
| stem | anchors | share | 0.596 [0.542, 0.659] | 0.724 [0.626, 0.830] (46/121) | 0.799 [0.647, 0.915] | 0.158 [0.052, 0.260] |
| stem | anchors | conditional | 0.594 [0.540, 0.658] | 0.719 [0.623, 0.824] (46/121) | 0.799 [0.647, 0.915] | 0.160 [0.055, 0.261] |
| stem | all_training_drugs | share | 0.597 [0.544, 0.660] | 0.721 [0.623, 0.823] (48/121) | 0.788 [0.630, 0.905] | 0.157 [0.052, 0.260] |
| stem | all_training_drugs | conditional | 0.595 [0.542, 0.659] | 0.716 [0.619, 0.819] (48/121) | 0.788 [0.630, 0.905] | 0.159 [0.055, 0.260] |
| atc3 | anchors | share | 0.648 [0.571, 0.723] | 0.664 [0.581, 0.745] (103/121) | 0.746 [0.637, 0.840] | 0.106 [-0.010, 0.222] |
| atc3 | anchors | conditional | 0.642 [0.561, 0.718] | 0.657 [0.567, 0.739] (103/121) | 0.746 [0.637, 0.840] | 0.113 [-0.003, 0.232] |
| atc3 | all_training_drugs | share | 0.663 [0.582, 0.737] | 0.668 [0.586, 0.745] (107/121) | 0.755 [0.647, 0.843] | 0.091 [-0.023, 0.198] |
| atc3 | all_training_drugs | conditional | 0.652 [0.576, 0.725] | 0.657 [0.580, 0.728] (107/121) | 0.755 [0.647, 0.843] | 0.102 [-0.009, 0.212] |

### 2. Split by having a training anchor in the same class

atc4: with 70 drugs (665 rows), without 51 drugs (457 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.784 [0.654, 0.889] | 0.708 [0.525, 0.846] | 0.075 [-0.104, 0.291] |
| E7d | 0.782 [0.665, 0.883] | 0.651 [0.474, 0.806] | 0.131 [-0.077, 0.331] |
| E7e | 0.817 [0.692, 0.910] | 0.716 [0.557, 0.859] | 0.101 [-0.083, 0.293] |
| b2mixed | 0.363 [0.251, 0.508] | 0.448 [0.276, 0.627] | -0.085 [-0.283, 0.137] |
| Qwen names only | 0.653 [0.506, 0.793] | 0.678 [0.515, 0.831] | -0.025 [-0.229, 0.190] |

E7c drug-averaged per-drug AUROC: with 0.785 (57), without 0.679 (37)

stem: with 46 drugs (422 rows), without 75 drugs (700 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.799 [0.647, 0.915] | 0.720 [0.587, 0.838] | 0.079 [-0.106, 0.253] |
| E7d | 0.799 [0.652, 0.914] | 0.679 [0.558, 0.792] | 0.120 [-0.068, 0.292] |
| E7e | 0.839 [0.708, 0.933] | 0.731 [0.608, 0.854] | 0.108 [-0.073, 0.266] |
| b2mixed | 0.422 [0.272, 0.593] | 0.377 [0.241, 0.524] | 0.046 [-0.172, 0.276] |
| Qwen names only | 0.697 [0.545, 0.838] | 0.638 [0.494, 0.776] | 0.059 [-0.141, 0.252] |

E7c drug-averaged per-drug AUROC: with 0.755 (39), without 0.736 (55)

### 3. E7c partialled on the class-sibling score within drug

| adjustment | residual within-drug AUROC [95%] | class share | contains 0.5 |
|---|---|---|---|
| rank:joint | 0.713 [0.611, 0.803] | 0.162 | False |
| rank:atc4 | 0.725 [0.622, 0.815] | 0.114 | False |
| rank:stem | 0.721 [0.620, 0.810] | 0.132 | False |
| rank:atc3 | 0.724 [0.619, 0.815] | 0.118 | False |
| linear:joint | 0.703 [0.592, 0.801] | 0.202 | False |
| linear:atc4 | 0.716 [0.610, 0.808] | 0.151 | False |
| linear:stem | 0.708 [0.597, 0.802] | 0.181 | False |
| linear:atc3 | 0.718 [0.608, 0.815] | 0.144 | False |
| post_hoc:rank:joint_plus_embedding_top1 | 0.710 [0.610, 0.801] | 0.172 | False |
| post_hoc:rank:joint_plus_embedding_top3 | 0.713 [0.611, 0.802] | 0.162 | False |

within-drug Spearman of logit E7c with the class score: atc4 0.200, stem 0.191, atc3 0.247

### 4. Mechanism

PK positives 255 (59 drugs), PD or other 196 (74 drugs)

| scorer | PK | PD or other |
|---|---|---|
| E7c | 0.674 [0.529, 0.803] | 0.823 [0.715, 0.913] |
| class_atc4 | 0.608 [0.538, 0.702] | 0.617 [0.545, 0.704] |
| class_stem | 0.581 [0.520, 0.670] | 0.609 [0.535, 0.695] |

E7c PK minus PD: -0.149 [-0.323, 0.006]

post hoc broader PK rule (adds pharmacokinetic, concentration, bioavailability, absorption, plasma or serum level, inducer): PK 287, PD or other 164; E7c PK 0.711 [0.571, 0.824], PD or other 0.814 [0.687, 0.913], difference -0.103 [-0.255, 0.060]

### 5. DrugBank operating point

| quantity | value [95%] |
|---|---|
| drugbank_fpr_pooled | 0.000 [0.000, 0.000] |
| drugbank_tpr_pooled | 1.000 [1.000, 1.000] |
| e7c_tpr_within_at_drugbank_fpr | 0.496 [0.411, 0.693] |
| drugbank_tpr_within_at_its_fpr | 1.000 [1.000, 1.000] |
| e7c_minus_drugbank_tpr_within | -0.504 [-0.589, -0.307] |
| e7c_minus_drugbank_tpr_pooled | -0.504 [-0.589, -0.307] |
| e7c_pauc_to_drugbank_fpr | 0.000 [0.000, 0.000] |
| drugbank_pauc_to_its_fpr | 0.000 [0.000, 0.000] |
| e7c_minus_drugbank_pauc | 0.000 [0.000, 0.000] |
| e7c_pauc_over_fpr | NA [NA, NA] |
| drugbank_pauc_over_fpr | NA [NA, NA] |
| e7c_auroc_from_placements | 0.754 [0.649, 0.841] |
| drugbank_auroc_from_placements | 1.000 [1.000, 1.000] |

### 6. Non-constant partner priors

partner training positive rate: within 0.496 [0.393, 0.597]; partners in training 184/204; distinct-partner mean 0.336, sd 0.091, range 0.071 to 0.647

- class-conditional partner rate, atc4: 0.611 [0.556, 0.672]
- class-conditional partner rate, stem: 0.594 [0.540, 0.658]
- class-conditional partner rate, atc3: 0.642 [0.561, 0.718]
- frozen BiomedBERT name similarity, top1: 0.619 [0.521, 0.720]
- frozen BiomedBERT name similarity, top3: 0.617 [0.518, 0.713]
- frozen BiomedBERT name similarity, top5: 0.605 [0.502, 0.707]

## novel:A

rows 438, drugs 48, positives 148

| system | within-drug AUROC [95%] |
|---|---|
| E7c | 0.534 [0.400, 0.698] |
| E7d | 0.518 [0.385, 0.668] |
| E7e | 0.613 [0.477, 0.758] |
| b2mixed | 0.523 [0.397, 0.650] |
| Qwen names only | 0.579 [0.440, 0.713] |

### 1. Class-sibling scorer (no model)

| definition | pool | score | all drugs | drugs with mates (n) | E7c on those drugs | E7c minus scorer |
|---|---|---|---|---|---|---|
| atc4 | anchors | share | 0.499 [0.469, 0.540] | 0.497 [0.357, 0.640] (11/48) | 0.614 [0.295, 0.897] | 0.034 [-0.099, 0.175] |
| atc4 | anchors | conditional | 0.499 [0.469, 0.540] | 0.497 [0.357, 0.640] (11/48) | 0.614 [0.295, 0.897] | 0.034 [-0.099, 0.175] |
| atc4 | all_training_drugs | share | 0.513 [0.474, 0.579] | 0.538 [0.414, 0.689] (16/48) | 0.574 [0.324, 0.828] | 0.021 [-0.114, 0.163] |
| atc4 | all_training_drugs | conditional | 0.513 [0.474, 0.579] | 0.538 [0.414, 0.689] (16/48) | 0.574 [0.324, 0.828] | 0.021 [-0.114, 0.163] |
| stem | anchors | share | 0.499 [0.476, 0.520] | 0.495 [0.300, 0.717] (9/48) | 0.500 [0.153, 0.895] | 0.034 [-0.109, 0.208] |
| stem | anchors | conditional | 0.498 [0.475, 0.518] | 0.484 [0.286, 0.695] (9/48) | 0.500 [0.153, 0.895] | 0.036 [-0.102, 0.208] |
| stem | all_training_drugs | share | 0.499 [0.476, 0.520] | 0.495 [0.300, 0.717] (9/48) | 0.500 [0.153, 0.895] | 0.034 [-0.109, 0.208] |
| stem | all_training_drugs | conditional | 0.498 [0.475, 0.518] | 0.484 [0.286, 0.695] (9/48) | 0.500 [0.153, 0.895] | 0.036 [-0.102, 0.208] |
| atc3 | anchors | share | 0.531 [0.451, 0.612] | 0.542 [0.435, 0.652] (34/48) | 0.554 [0.395, 0.736] | 0.003 [-0.133, 0.148] |
| atc3 | anchors | conditional | 0.518 [0.436, 0.604] | 0.525 [0.412, 0.638] (34/48) | 0.554 [0.395, 0.736] | 0.015 [-0.123, 0.166] |
| atc3 | all_training_drugs | share | 0.541 [0.453, 0.633] | 0.552 [0.442, 0.659] (37/48) | 0.541 [0.388, 0.711] | -0.007 [-0.138, 0.132] |
| atc3 | all_training_drugs | conditional | 0.532 [0.441, 0.626] | 0.541 [0.426, 0.660] (37/48) | 0.541 [0.388, 0.711] | 0.001 [-0.133, 0.147] |

### 2. Split by having a training anchor in the same class

atc4: with 11 drugs (98 rows), without 37 drugs (340 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.614 [0.295, 0.897] | 0.510 [0.365, 0.673] | 0.104 [-0.237, 0.423] |
| E7d | 0.532 [0.237, 0.880] | 0.514 [0.356, 0.680] | 0.019 [-0.332, 0.392] |
| E7e | 0.602 [0.317, 0.869] | 0.616 [0.459, 0.793] | -0.014 [-0.326, 0.299] |
| b2mixed | 0.550 [0.264, 0.828] | 0.515 [0.360, 0.668] | 0.034 [-0.292, 0.361] |
| Qwen names only | 0.643 [0.264, 0.896] | 0.560 [0.417, 0.704] | 0.084 [-0.317, 0.368] |

E7c drug-averaged per-drug AUROC: with 0.568 (11), without 0.550 (37)

stem: with 9 drugs (66 rows), without 39 drugs (372 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.500 [0.153, 0.895] | 0.538 [0.395, 0.700] | -0.038 [-0.425, 0.352] |
| E7d | 0.370 [0.083, 0.876] | 0.538 [0.394, 0.699] | -0.169 [-0.524, 0.336] |
| E7e | 0.707 [0.346, 1.000] | 0.600 [0.460, 0.762] | 0.107 [-0.310, 0.451] |
| b2mixed | 0.522 [0.143, 0.834] | 0.523 [0.387, 0.660] | -0.002 [-0.394, 0.355] |
| Qwen names only | 0.511 [0.140, 0.863] | 0.588 [0.442, 0.728] | -0.077 [-0.455, 0.297] |

E7c drug-averaged per-drug AUROC: with 0.598 (9), without 0.544 (39)

### 3. E7c partialled on the class-sibling score within drug

| adjustment | residual within-drug AUROC [95%] | class share | contains 0.5 |
|---|---|---|---|
| rank:joint | 0.535 [0.400, 0.678] | 0.000 | True |
| rank:atc4 | 0.534 [0.398, 0.686] | 0.000 | True |
| rank:stem | 0.534 [0.400, 0.698] | 0.000 | True |
| rank:atc3 | 0.535 [0.404, 0.679] | 0.000 | True |
| linear:joint | 0.522 [0.393, 0.678] | 0.353 | True |
| linear:atc4 | 0.536 [0.402, 0.693] | 0.000 | True |
| linear:stem | 0.535 [0.400, 0.698] | 0.000 | True |
| linear:atc3 | 0.517 [0.383, 0.677] | 0.510 | True |
| post_hoc:rank:joint_plus_embedding_top1 | 0.542 [0.409, 0.685] | 0.000 | True |
| post_hoc:rank:joint_plus_embedding_top3 | 0.552 [0.421, 0.696] | 0.000 | True |

within-drug Spearman of logit E7c with the class score: atc4 0.151, stem 0.018, atc3 0.262

### 4. Mechanism

PK positives 82 (35 drugs), PD or other 66 (28 drugs)

| scorer | PK | PD or other |
|---|---|---|
| E7c | 0.543 [0.367, 0.724] | 0.522 [0.316, 0.749] |
| class_atc4 | 0.498 [0.456, 0.559] | 0.501 [0.464, 0.558] |
| class_stem | 0.507 [0.490, 0.535] | 0.490 [0.445, 0.513] |

E7c PK minus PD: 0.021 [-0.249, 0.282]

post hoc broader PK rule (adds pharmacokinetic, concentration, bioavailability, absorption, plasma or serum level, inducer): PK 92, PD or other 56; E7c PK 0.553 [0.386, 0.724], PD or other 0.500 [0.284, 0.766], difference 0.053 [-0.232, 0.321]

### 5. DrugBank operating point

| quantity | value [95%] |
|---|---|
| drugbank_fpr_pooled | 0.366 [0.239, 0.494] |
| drugbank_tpr_pooled | 0.899 [0.794, 0.967] |
| e7c_tpr_within_at_drugbank_fpr | 0.420 [0.210, 0.670] |
| drugbank_tpr_within_at_its_fpr | 0.704 [0.570, 0.817] |
| e7c_minus_drugbank_tpr_within | -0.283 [-0.501, -0.009] |
| e7c_minus_drugbank_tpr_pooled | -0.479 [-0.699, -0.217] |
| e7c_pauc_to_drugbank_fpr | 0.095 [0.048, 0.215] |
| drugbank_pauc_to_its_fpr | 0.169 [0.105, 0.259] |
| e7c_minus_drugbank_pauc | -0.073 [-0.135, 0.027] |
| e7c_pauc_over_fpr | 0.261 [0.159, 0.512] |
| drugbank_pauc_over_fpr | 0.461 [0.370, 0.610] |
| e7c_auroc_from_placements | 0.534 [0.400, 0.698] |
| drugbank_auroc_from_placements | 0.729 [0.642, 0.808] |

### 6. Non-constant partner priors

partner training positive rate: within 0.485 [0.354, 0.624]; partners in training 66/74; distinct-partner mean 0.337, sd 0.073, range 0.067 to 0.464

- class-conditional partner rate, atc4: 0.499 [0.469, 0.540]
- class-conditional partner rate, stem: 0.498 [0.475, 0.518]
- class-conditional partner rate, atc3: 0.518 [0.436, 0.604]
- frozen BiomedBERT name similarity, top1: 0.450 [0.311, 0.599]
- frozen BiomedBERT name similarity, top3: 0.485 [0.345, 0.626]
- frozen BiomedBERT name similarity, top5: 0.488 [0.347, 0.630]

## novel:B

rows 316, drugs 48, positives 133

| system | within-drug AUROC [95%] |
|---|---|
| E7c | 0.533 [0.351, 0.737] |
| E7d | 0.563 [0.382, 0.759] |
| E7e | 0.664 [0.485, 0.837] |
| b2mixed | 0.533 [0.357, 0.714] |
| Qwen names only | 0.577 [0.397, 0.736] |

### 1. Class-sibling scorer (no model)

| definition | pool | score | all drugs | drugs with mates (n) | E7c on those drugs | E7c minus scorer |
|---|---|---|---|---|---|---|
| atc4 | anchors | share | 0.495 [0.438, 0.566] | 0.479 [0.250, 0.694] (11/48) | 0.585 [0.259, 0.967] | 0.038 [-0.158, 0.236] |
| atc4 | anchors | conditional | 0.495 [0.438, 0.566] | 0.479 [0.250, 0.694] (11/48) | 0.585 [0.259, 0.967] | 0.038 [-0.158, 0.236] |
| atc4 | all_training_drugs | share | 0.519 [0.453, 0.632] | 0.553 [0.352, 0.760] (16/48) | 0.556 [0.214, 0.870] | 0.014 [-0.192, 0.226] |
| atc4 | all_training_drugs | conditional | 0.519 [0.453, 0.632] | 0.553 [0.352, 0.760] (16/48) | 0.556 [0.214, 0.870] | 0.014 [-0.192, 0.226] |
| stem | anchors | share | 0.493 [0.460, 0.513] | 0.375 [0.065, 1.000] (9/48) | 0.650 [0.000, 1.000] | 0.040 [-0.147, 0.247] |
| stem | anchors | conditional | 0.492 [0.459, 0.513] | 0.350 [0.000, 1.000] (9/48) | 0.650 [0.000, 1.000] | 0.041 [-0.144, 0.247] |
| stem | all_training_drugs | share | 0.493 [0.460, 0.513] | 0.375 [0.065, 1.000] (9/48) | 0.650 [0.000, 1.000] | 0.040 [-0.147, 0.247] |
| stem | all_training_drugs | conditional | 0.492 [0.459, 0.513] | 0.350 [0.000, 1.000] (9/48) | 0.650 [0.000, 1.000] | 0.041 [-0.144, 0.247] |
| atc3 | anchors | share | 0.526 [0.427, 0.628] | 0.538 [0.385, 0.691] (34/48) | 0.584 [0.382, 0.790] | 0.007 [-0.194, 0.227] |
| atc3 | anchors | conditional | 0.511 [0.403, 0.620] | 0.516 [0.363, 0.676] (34/48) | 0.584 [0.382, 0.790] | 0.022 [-0.178, 0.231] |
| atc3 | all_training_drugs | share | 0.549 [0.451, 0.664] | 0.566 [0.432, 0.707] (37/48) | 0.551 [0.342, 0.760] | -0.016 [-0.225, 0.209] |
| atc3 | all_training_drugs | conditional | 0.544 [0.432, 0.669] | 0.559 [0.408, 0.718] (37/48) | 0.551 [0.342, 0.760] | -0.011 [-0.222, 0.216] |

### 2. Split by having a training anchor in the same class

atc4: with 11 drugs (75 rows), without 37 drugs (241 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.585 [0.259, 0.967] | 0.515 [0.294, 0.736] | 0.070 [-0.316, 0.476] |
| E7d | 0.468 [0.137, 0.930] | 0.596 [0.382, 0.803] | -0.128 [-0.528, 0.363] |
| E7e | 0.681 [0.264, 0.971] | 0.658 [0.457, 0.865] | 0.023 [-0.461, 0.346] |
| b2mixed | 0.532 [0.175, 0.942] | 0.533 [0.321, 0.741] | -0.001 [-0.428, 0.418] |
| Qwen names only | 0.691 [0.250, 0.941] | 0.537 [0.336, 0.736] | 0.155 [-0.324, 0.488] |

E7c drug-averaged per-drug AUROC: with 0.581 (10), without 0.564 (30)

stem: with 9 drugs (45 rows), without 39 drugs (271 rows)

| system | with | without | with minus without |
|---|---|---|---|
| E7c | 0.650 [0.000, 1.000] | 0.526 [0.331, 0.728] | 0.124 [-0.548, 0.600] |
| E7d | 0.600 [0.000, 1.000] | 0.561 [0.370, 0.764] | 0.039 [-0.565, 0.571] |
| E7e | 0.900 [0.214, 1.000] | 0.650 [0.467, 0.831] | 0.250 [-0.470, 0.523] |
| b2mixed | 0.450 [0.000, 1.000] | 0.538 [0.357, 0.728] | -0.088 [-0.655, 0.554] |
| Qwen names only | 0.400 [0.000, 1.000] | 0.587 [0.400, 0.757] | -0.187 [-0.693, 0.462] |

E7c drug-averaged per-drug AUROC: with 0.683 (5), without 0.552 (35)

### 3. E7c partialled on the class-sibling score within drug

| adjustment | residual within-drug AUROC [95%] | class share | contains 0.5 |
|---|---|---|---|
| rank:joint | 0.536 [0.350, 0.734] | 0.000 | True |
| rank:atc4 | 0.533 [0.340, 0.727] | 0.000 | True |
| rank:stem | 0.533 [0.351, 0.737] | 0.000 | True |
| rank:atc3 | 0.538 [0.354, 0.736] | 0.000 | True |
| linear:joint | 0.503 [0.318, 0.697] | 0.917 | True |
| linear:atc4 | 0.538 [0.347, 0.736] | 0.000 | True |
| linear:stem | 0.533 [0.351, 0.737] | 0.000 | True |
| linear:atc3 | 0.500 [0.310, 0.702] | 1.000 | True |
| post_hoc:rank:joint_plus_embedding_top1 | 0.536 [0.350, 0.725] | 0.000 | True |
| post_hoc:rank:joint_plus_embedding_top3 | 0.546 [0.357, 0.742] | 0.000 | True |

within-drug Spearman of logit E7c with the class score: atc4 0.135, stem 0.031, atc3 0.153

### 4. Mechanism

PK positives 77 (32 drugs), PD or other 56 (26 drugs)

| scorer | PK | PD or other |
|---|---|---|
| E7c | 0.528 [0.292, 0.768] | 0.539 [0.246, 0.880] |
| class_atc4 | 0.502 [0.419, 0.616] | 0.484 [0.427, 0.500] |
| class_stem | 0.500 [0.473, 0.528] | 0.484 [0.415, 0.500] |

E7c PK minus PD: -0.011 [-0.419, 0.356]

post hoc broader PK rule (adds pharmacokinetic, concentration, bioavailability, absorption, plasma or serum level, inducer): PK 85, PD or other 48; E7c PK 0.543 [0.324, 0.771], PD or other 0.515 [0.217, 0.892], difference 0.029 [-0.381, 0.408]

### 5. DrugBank operating point

| quantity | value [95%] |
|---|---|
| drugbank_fpr_pooled | 0.000 [0.000, 0.000] |
| drugbank_tpr_pooled | 1.000 [1.000, 1.000] |
| e7c_tpr_within_at_drugbank_fpr | 0.257 [0.135, 0.590] |
| drugbank_tpr_within_at_its_fpr | 1.000 [1.000, 1.000] |
| e7c_minus_drugbank_tpr_within | -0.743 [-0.865, -0.410] |
| e7c_minus_drugbank_tpr_pooled | -0.743 [-0.865, -0.410] |
| e7c_pauc_to_drugbank_fpr | 0.000 [0.000, 0.000] |
| drugbank_pauc_to_its_fpr | 0.000 [0.000, 0.000] |
| e7c_minus_drugbank_pauc | 0.000 [0.000, 0.000] |
| e7c_pauc_over_fpr | NA [NA, NA] |
| drugbank_pauc_over_fpr | NA [NA, NA] |
| e7c_auroc_from_placements | 0.533 [0.351, 0.737] |
| drugbank_auroc_from_placements | 1.000 [1.000, 1.000] |

### 6. Non-constant partner priors

partner training positive rate: within 0.508 [0.310, 0.691]; partners in training 66/74; distinct-partner mean 0.337, sd 0.073, range 0.067 to 0.464

- class-conditional partner rate, atc4: 0.495 [0.438, 0.566]
- class-conditional partner rate, stem: 0.492 [0.459, 0.513]
- class-conditional partner rate, atc3: 0.511 [0.403, 0.620]
- frozen BiomedBERT name similarity, top1: 0.460 [0.256, 0.662]
- frozen BiomedBERT name similarity, top3: 0.501 [0.294, 0.712]
- frozen BiomedBERT name similarity, top5: 0.488 [0.283, 0.694]

## 7. Aliases

| Older drug | training drug | ratio | LCS | judged alias |
|---|---|---|---|---|
| aminolevulinic acid | ethacrynic acid | 0.529 | 8 | False |
| aminolevulinic acid | fenofibric acid | 0.588 | 7 | False |
| aminolevulinic acid | folic acid | 0.621 | 7 | False |
| aminolevulinic acid | mefenamic acid | 0.545 | 7 | False |
| aminolevulinic acid | para-aminobenzoic acid | 0.683 | 7 | False |
| aminolevulinic acid | valproic acid | 0.562 | 7 | False |
| avanafil | vardenafil | 0.778 | 5 | False |
| axitinib | imatinib | 0.75 | 5 | False |
| belatacept | abatacept | 0.842 | 7 | True |
| bicalutamide | flutamide | 0.762 | 8 | False |
| bicalutamide | nilutamide | 0.818 | 8 | False |
| dutasteride | finasteride | 0.727 | 8 | False |
| eletriptan hydrobromide | frovatriptan | 0.636 | 7 | False |
| eletriptan hydrobromide | naratriptan | 0.667 | 7 | False |
| eletriptan hydrobromide | sumatriptan | 0.667 | 7 | False |
| eletriptan hydrobromide | sumatriptan succinate | 0.667 | 7 | False |
| enzalutamide | flutamide | 0.762 | 8 | False |
| enzalutamide | nilutamide | 0.818 | 8 | False |
| fomepizole | omeprazole | 0.8 | 4 | False |
| iloperidone | droperidol | 0.667 | 7 | False |
| iloperidone | haloperidol | 0.727 | 8 | False |
| iloperidone | risperidone | 0.818 | 8 | False |
| iopromide | disopyramide | 0.762 | 4 | False |
| iopromide | disopyramide phosphate | 0.762 | 4 | False |
| lanreotide | octreotide | 0.7 | 7 | False |
| lanthanum carbonate | lithium carbonate | 0.833 | 12 | False |
| lisdexamfetamine dimesylate | ketamine | 0.583 | 7 | False |
| lurasidone | ziprasidone | 0.762 | 8 | False |
| pasireotide | octreotide | 0.667 | 7 | False |
| pimecrolimus | everolimus | 0.727 | 7 | False |
| pimecrolimus | tacrolimus | 0.727 | 8 | False |
| pitavastatin | fluvastatin | 0.696 | 8 | False |
| pitavastatin | lovastatin | 0.727 | 8 | False |
| pitavastatin | pravastatin | 0.87 | 9 | False |
| pitavastatin | simvastatin | 0.783 | 8 | False |
| posaconazole | fluconazole | 0.696 | 8 | False |
| posaconazole | itraconazole | 0.75 | 9 | False |
| posaconazole | ketoconazole | 0.75 | 8 | False |
| posaconazole | miconazole | 0.727 | 8 | False |
| posaconazole | voriconazole | 0.75 | 8 | False |
| pralatrexate | methotrexate | 0.583 | 7 | False |
| rabeprazole | aripiprazole | 0.696 | 7 | False |
| rabeprazole | lansoprazole | 0.696 | 7 | False |
| rabeprazole | omeprazole | 0.762 | 8 | False |
| ranolazine | hydralazine | 0.762 | 6 | False |
| repaglinide | nateglinide | 0.727 | 7 | False |
| rifaximin | rifampin | 0.824 | 4 | False |
| risedronate | alendronate | 0.727 | 7 | False |
| risedronate | ibandronate | 0.727 | 7 | False |
| rizatriptan benzoate | frovatriptan | 0.783 | 8 | False |
| rizatriptan benzoate | naratriptan | 0.818 | 8 | False |
| rizatriptan benzoate | sumatriptan | 0.727 | 8 | False |
| rizatriptan benzoate | sumatriptan succinate | 0.727 | 8 | False |
| temsirolimus | everolimus | 0.727 | 7 | False |
| temsirolimus | tacrolimus | 0.727 | 7 | False |
| teriflunomide | leflunomide | 0.833 | 9 | True |
| tetrabenazine | perphenazine | 0.72 | 7 | False |
| tetrabenazine | terbinafine | 0.75 | 3 | False |
| tinidazole | metronidazole | 0.783 | 8 | False |
| vilazodone | nefazodone | 0.7 | 7 | False |
| vilazodone | trazodone | 0.737 | 7 | False |
| vilazodone | trazodone hydrochloride | 0.737 | 7 | False |
| vorinostat | orlistat | 0.778 | 4 | False |
| zoledronic acid | ethacrynic acid | 0.667 | 8 | False |
| zoledronic acid | fenofibric acid | 0.6 | 7 | False |
| zoledronic acid | folic acid | 0.72 | 7 | False |
| zoledronic acid | mefenamic acid | 0.621 | 7 | False |
| zoledronic acid | para-aminobenzoic acid | 0.486 | 7 | False |
| zoledronic acid | valproic acid | 0.714 | 7 | False |
| zolmitriptan | amitriptyline | 0.64 | 7 | False |
| zolmitriptan | amitriptyline hcl | 0.64 | 7 | False |
| zolmitriptan | frovatriptan | 0.667 | 7 | False |
| zolmitriptan | naratriptan | 0.609 | 7 | False |
| zolmitriptan | sumatriptan | 0.696 | 7 | False |
| zolmitriptan | sumatriptan succinate | 0.696 | 7 | False |

red-team alias partner present among training drugs: teriflunomide: True, balsalazide disodium: True, lisdexamfetamine dimesylate: False

Older-primary tier A: none_removed 0.695 [0.630, 0.762] (121 drugs); red_team_removed 0.697 [0.627, 0.761] (118 drugs); all_confirmed_removed 0.695 [0.629, 0.762] (117 drugs)
Older-primary tier B: none_removed 0.754 [0.649, 0.841] (121 drugs); red_team_removed 0.758 [0.658, 0.846] (118 drugs); all_confirmed_removed 0.753 [0.648, 0.836] (117 drugs)

## Red-team named drugs

Release note: the per-drug table derived from DrugBank ATC codes is removed from the public copy. Rerun scripts/post7_classshortcut.py with a licensed DrugBank copy to regenerate it.
