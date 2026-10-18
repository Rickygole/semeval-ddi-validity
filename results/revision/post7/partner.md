# Partner structure and the below-chance Older-clean result

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

The partner-stratified and tetrad statistics are a decomposition of the within-drug AUROC by partner structure. They do not replace H1, whose preregistered statistic and decision are unchanged. The leave-one-drug-out partialling of experiment 7 drives the DrugBank lookup to 0.398 within drug, which shows that adjustment is broken; it is not used here as an explanation.

## 2a. Validity first: does the DrugBank lookup keep its signal?

| cohort | statistic | DrugBank tier A | two-way 95% lower bound | valid decomposition |
| --- | --- | --- | --- | --- |
| older_clean | partner_stratified | 0.699 | 0.627 | True |
| older_clean | tetrad | 0.691 | 0.577 | True |
| novel | partner_stratified | 0.785 | 0.680 | True |
| novel | tetrad | 0.885 | 0.702 | True |

## 2a. Decomposition by system

W is the within-drug AUROC (the H1 statistic), P the partner-stratified AUROC (primary), T the tetrad AUROC (secondary). Intervals are two-way cluster bootstrap 95% (one-way drug in brackets after the slash). W - P and W - T are paired. Explained: the statistic's 95% interval contains 0.5, |S - 0.5| <= |W - 0.5| - 0.03, and the statistic is valid.

### older_clean, tier A (n = 1832, 128 drugs; comparisons: within 5162, partner 10643, tetrads 1975 over 125 drugs)

| system | W | W 95% CI | P | P 95% CI two-way / one-way | W - P | 95% CI | P explained (two-way / one-way) | T | T 95% CI two-way / one-way | W - T | 95% CI | T explained (two-way / one-way) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup | 0.641 | [0.595, 0.689] / [0.611, 0.670] | 0.699 | [0.627, 0.764] / [0.649, 0.745] | -0.058 | [-0.123, 0.012] |  | 0.691 | [0.577, 0.802] / [0.619, 0.759] | -0.050 | [-0.140, 0.041] |  |
| b2mixed | 0.452 | [0.389, 0.518] / [0.412, 0.495] | 0.461 | [0.368, 0.543] / [0.386, 0.528] | -0.009 | [-0.102, 0.090] | False / False | 0.375 | [0.233, 0.541] / [0.290, 0.465] | 0.077 | [-0.068, 0.204] | False / False |
| Qwen names only | 0.602 | [0.533, 0.667] / [0.557, 0.645] | 0.717 | [0.640, 0.790] / [0.660, 0.768] | -0.115 | [-0.205, -0.018] | False / False | 0.758 | [0.619, 0.882] / [0.683, 0.830] | -0.157 | [-0.297, -0.008] | False / False |
| b1names | 0.463 | [0.398, 0.521] / [0.423, 0.504] | 0.451 | [0.358, 0.535] / [0.378, 0.514] | 0.012 | [-0.079, 0.106] | False / False | 0.348 | [0.220, 0.497] / [0.271, 0.424] | 0.114 | [-0.033, 0.226] | False / False |
| b2sentence | 0.453 | [0.391, 0.518] / [0.413, 0.491] | 0.427 | [0.358, 0.500] / [0.372, 0.481] | 0.026 | [-0.061, 0.111] | False / False | 0.433 | [0.269, 0.595] / [0.342, 0.537] | 0.020 | [-0.130, 0.170] | False / False |

### older_clean, tier B (n = 1191, 128 drugs; comparisons: within 1706, partner 5092, tetrads 172 over 66 drugs)

| system | W | W 95% CI | P | P 95% CI two-way / one-way | W - P | 95% CI | P explained (two-way / one-way) | T | T 95% CI two-way / one-way | W - T | 95% CI | T explained (two-way / one-way) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 0.000 | [0.000, 0.000] |  | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 0.000 | [0.000, 0.000] |  |
| b2mixed | 0.397 | [0.289, 0.514] / [0.333, 0.464] | 0.395 | [0.278, 0.492] / [0.307, 0.483] | 0.002 | [-0.128, 0.151] | False / False | 0.227 | [0.000, 0.551] / [0.107, 0.350] | 0.170 | [-0.144, 0.400] | False / False |
| Qwen names only | 0.660 | [0.543, 0.767] / [0.593, 0.723] | 0.860 | [0.783, 0.920] / [0.817, 0.902] | -0.200 | [-0.329, -0.070] | False / False | 0.936 | [0.629, 1.000] / [0.824, 1.000] | -0.276 | [-0.438, 0.019] | False / False |
| b1names | 0.419 | [0.320, 0.531] / [0.355, 0.486] | 0.387 | [0.290, 0.494] / [0.305, 0.474] | 0.032 | [-0.100, 0.168] | False / False | 0.233 | [0.021, 0.602] / [0.112, 0.393] | 0.187 | [-0.199, 0.424] | False / False |
| b2sentence | 0.393 | [0.296, 0.501] / [0.333, 0.452] | 0.395 | [0.301, 0.503] / [0.321, 0.473] | -0.002 | [-0.139, 0.138] | False / False | 0.337 | [0.044, 0.681] / [0.193, 0.519] | 0.056 | [-0.301, 0.345] | False / False |

### novel, tier A (n = 438, 48 drugs; comparisons: within 757, partner 1046, tetrads 152 over 46 drugs)

| system | W | W 95% CI | P | P 95% CI two-way / one-way | W - P | 95% CI | P explained (two-way / one-way) | T | T 95% CI two-way / one-way | W - T | 95% CI | T explained (two-way / one-way) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup | 0.729 | [0.642, 0.808] / [0.675, 0.779] | 0.785 | [0.680, 0.880] / [0.725, 0.843] | -0.057 | [-0.158, 0.056] |  | 0.885 | [0.702, 1.000] / [0.803, 0.962] | -0.156 | [-0.301, 0.020] |  |
| b2mixed | 0.523 | [0.397, 0.650] / [0.458, 0.585] | 0.540 | [0.374, 0.686] / [0.427, 0.662] | -0.017 | [-0.186, 0.155] | False / False | 0.480 | [0.120, 0.825] / [0.333, 0.696] | 0.043 | [-0.299, 0.358] | False / False |
| Qwen names only | 0.579 | [0.440, 0.713] / [0.503, 0.651] | 0.663 | [0.543, 0.787] / [0.576, 0.741] | -0.084 | [-0.248, 0.102] | False / False | 0.664 | [0.297, 0.940] / [0.477, 0.802] | -0.086 | [-0.354, 0.275] | False / False |
| b1names | 0.514 | [0.384, 0.635] / [0.443, 0.584] | 0.533 | [0.394, 0.658] / [0.453, 0.627] | -0.020 | [-0.179, 0.138] | False / False | 0.546 | [0.182, 0.859] / [0.362, 0.725] | -0.032 | [-0.331, 0.317] | False / False |
| b2sentence | 0.490 | [0.370, 0.612] / [0.429, 0.554] | 0.507 | [0.376, 0.633] / [0.414, 0.590] | -0.017 | [-0.166, 0.136] | False / False | 0.566 | [0.204, 0.888] / [0.375, 0.729] | -0.076 | [-0.405, 0.306] | False / False |

### novel, tier B (n = 316, 48 drugs; comparisons: within 366, partner 619, tetrads 35 over 29 drugs)

| system | W | W 95% CI | P | P 95% CI two-way / one-way | W - P | 95% CI | P explained (two-way / one-way) | T | T 95% CI two-way / one-way | W - T | 95% CI | T explained (two-way / one-way) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 0.000 | [0.000, 0.000] |  | 1.000 | [1.000, 1.000] / [1.000, 1.000] | 0.000 | [0.000, 0.000] |  |
| b2mixed | 0.533 | [0.357, 0.714] / [0.440, 0.627] | 0.535 | [0.339, 0.712] / [0.384, 0.679] | -0.002 | [-0.231, 0.242] | False / False | 0.571 | [0.000, 1.000] / [0.212, 0.875] | -0.039 | [-0.564, 0.589] | False / False |
| Qwen names only | 0.577 | [0.397, 0.736] / [0.471, 0.667] | 0.733 | [0.594, 0.861] / [0.609, 0.835] | -0.157 | [-0.368, 0.072] | False / False | 0.657 | [0.000, 1.000] / [0.333, 0.895] | -0.081 | [-0.483, 0.588] | False / False |
| b1names | 0.530 | [0.341, 0.724] / [0.423, 0.635] | 0.525 | [0.370, 0.691] / [0.406, 0.643] | 0.005 | [-0.223, 0.220] | False / False | 0.771 | [0.000, 1.000] / [0.368, 0.976] | -0.241 | [-0.601, 0.481] | False / False |
| b2sentence | 0.475 | [0.308, 0.644] / [0.411, 0.541] | 0.473 | [0.311, 0.624] / [0.353, 0.597] | 0.002 | [-0.198, 0.235] | False / False | 0.429 | [0.000, 1.000] / [0.138, 0.750] | 0.047 | [-0.575, 0.562] | False / False |

## 2b. Popularity-only scorer on the frozen designs

Scorer s = lambda z(pop) + e, z the normal scores of partner popularity (share of vocabulary Drug Interactions sections naming the partner), e standard normal, 300 replicates per lambda. The label-derived leave-one-drug-out partner positive rate is run the same way as a contrast and carries no decision.

| cell | feature | feature within-drug AUROC | b2mixed W | b2mixed within-drug Spearman | scorer AUROC at matched Spearman | share of gap | AUROC equal to b2mixed reachable | scorer AUROC range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| older_clean:A | label-free popularity | 0.506 | 0.452 | 0.257 | 0.501 | -0.019 | False | [0.493, 0.506] |
| older_clean:A | leave-one-drug-out partner positive rate (label-derived contrast) | 0.088 | 0.452 | 0.055 | 0.476 | 0.504 | True between lambda [0.0, 0.25] | [0.088, 0.912] |
| older_clean:B | label-free popularity | 0.534 | 0.397 | 0.228 | 0.506 | -0.061 | False | [0.466, 0.534] |
| older_clean:B | leave-one-drug-out partner positive rate (label-derived contrast) | 0.053 | 0.397 | 0.068 | 0.464 | 0.351 | True between lambda [0.0, 0.25] | [0.053, 0.947] |
| novel:A | label-free popularity | 0.522 | 0.523 | 0.225 | 0.506 | 0.253 | False | [0.477, 0.523] |
| novel:A | leave-one-drug-out partner positive rate (label-derived contrast) | 0.028 | 0.523 | -0.046 | 0.525 | 1.102 | True between lambda [-0.25, 0.0] | [0.028, 0.972] |
| novel:B | label-free popularity | 0.536 | 0.533 | 0.281 | 0.512 | 0.376 | True between lambda [1.0, 2.0] | [0.458, 0.542] |
| novel:B | leave-one-drug-out partner positive rate (label-derived contrast) | 0.025 | 0.533 | -0.030 | 0.521 | 0.631 | True between lambda [-0.25, 0.0] | [0.025, 0.975] |

Curve for Older-clean tier A:

| feature | lambda | mean within-drug AUROC | SD | mean within-drug Spearman |
| --- | --- | --- | --- | --- |
| label-free popularity | -inf | 0.494 | 0.000 | -1.000 |
| label-free popularity | -5.0 | 0.493 | 0.004 | -0.963 |
| label-free popularity | -2.0 | 0.495 | 0.008 | -0.858 |
| label-free popularity | -1.0 | 0.496 | 0.013 | -0.660 |
| label-free popularity | -0.5 | 0.498 | 0.015 | -0.407 |
| label-free popularity | -0.25 | 0.498 | 0.017 | -0.216 |
| label-free popularity | 0.0 | 0.500 | 0.016 | 0.002 |
| label-free popularity | 0.25 | 0.500 | 0.016 | 0.215 |
| label-free popularity | 0.5 | 0.503 | 0.016 | 0.408 |
| label-free popularity | 1.0 | 0.504 | 0.012 | 0.662 |
| label-free popularity | 2.0 | 0.505 | 0.008 | 0.858 |
| label-free popularity | 5.0 | 0.506 | 0.004 | 0.963 |
| label-free popularity | +inf | 0.506 | 0.000 | 1.000 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -inf | 0.912 | 0.000 | -1.000 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -5.0 | 0.905 | 0.003 | -0.963 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -2.0 | 0.869 | 0.006 | -0.853 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -1.0 | 0.786 | 0.011 | -0.649 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -0.5 | 0.677 | 0.014 | -0.395 |
| leave-one-drug-out partner positive rate (label-derived contrast) | -0.25 | 0.594 | 0.018 | -0.210 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 0.0 | 0.500 | 0.018 | 0.000 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 0.25 | 0.406 | 0.016 | 0.210 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 0.5 | 0.325 | 0.015 | 0.394 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 1.0 | 0.215 | 0.011 | 0.648 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 2.0 | 0.130 | 0.007 | 0.854 |
| leave-one-drug-out partner positive rate (label-derived contrast) | 5.0 | 0.095 | 0.003 | 0.963 |
| leave-one-drug-out partner positive rate (label-derived contrast) | +inf | 0.088 | 0.000 | 1.000 |

## 2c. Decomposition of the b2mixed gap from 0.5

| cell | W - 0.5 | partner component W - P (two-way 95%) | residual P - 0.5 | tetrad component W - T (two-way 95%) | residual T - 0.5 | popularity component (one-way drug 95%) | residual after popularity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| older_clean:A | -0.048 | -0.009 [-0.102, 0.090] | -0.039 | 0.077 [-0.068, 0.204] | -0.125 | 0.001 [0.000, 0.001] | -0.049 [-0.089, -0.006] |
| older_clean:B | -0.103 | 0.002 [-0.128, 0.151] | -0.105 | 0.170 [-0.144, 0.400] | -0.273 | 0.006 [0.005, 0.008] | -0.110 [-0.173, -0.042] |
| novel:A | 0.023 | -0.017 [-0.186, 0.155] | 0.040 | 0.043 [-0.299, 0.358] | -0.020 | 0.006 [0.003, 0.008] | 0.017 [-0.048, 0.080] |
| novel:B | 0.033 | -0.002 [-0.231, 0.242] | 0.035 | -0.039 [-0.564, 0.589] | 0.071 | 0.012 [0.005, 0.017] | 0.020 [-0.073, 0.117] |
