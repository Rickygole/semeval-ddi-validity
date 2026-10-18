# Tier C-auto sensitivity (post hoc, exploratory)

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

Tier C-auto is tier A without the positives flagged by the rule of criteria.json (families N, L, H); C-auto-broad also drops the absence-of-evidence positives. All negatives are kept. Primary (tier A) values are recomputed by the same code and reproduce decisions.json, e8.json and e7.json.

## Rows per tier

| tier | cohort | positives | negatives | positives dropped |
| --- | --- | --- | --- | --- |
| A | novel | 148 | 290 | 0 |
| A | older_primary | 562 | 1159 | 0 |
| A | older_clean | 599 | 1233 | 0 |
| C-auto | novel | 147 | 290 | 1 |
| C-auto | older_primary | 525 | 1159 | 37 |
| C-auto | older_clean | 561 | 1233 | 38 |
| C-auto-broad | novel | 147 | 290 | 1 |
| C-auto-broad | older_primary | 523 | 1159 | 39 |
| C-auto-broad | older_clean | 559 | 1233 | 40 |

## H1, H1-novel, H4, H6 (two-way bootstrap, 1,000 draws)

| row | tier | n | AUROC | 90% CI | 95% CI | p_TOST | p_Holm | would-be label | DrugBank within | kappa | kappa 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | A | 1832 | 0.452 | [0.395, 0.509] | [0.389, 0.518] | 0.061 | 0.183 | inconclusive | 0.641 | -0.342 | [-0.794, 0.133] |
| H1 | C-auto | 1794 | 0.455 | [0.397, 0.512] | [0.390, 0.524] | 0.054 | 0.162 | inconclusive | 0.644 | -0.316 | [-0.765, 0.187] |
| H1 | C-auto-broad | 1792 | 0.456 | [0.401, 0.512] | [0.391, 0.524] | 0.051 | 0.153 | inconclusive | 0.644 | -0.307 | [-0.748, 0.188] |
| H1-novel | A | 438 | 0.523 | [0.411, 0.626] | [0.397, 0.650] | not tested | NA | estimate only | 0.729 | 0.101 | [-0.486, 0.722] |
| H1-novel | C-auto | 437 | 0.519 | [0.410, 0.625] | [0.393, 0.650] | not tested | NA | estimate only | 0.727 | 0.085 | [-0.504, 0.708] |
| H1-novel | C-auto-broad | 437 | 0.519 | [0.410, 0.625] | [0.393, 0.650] | not tested | NA | estimate only | 0.727 | 0.085 | [-0.504, 0.708] |
| H4 | A |  | -0.071 | [-0.192, 0.045] | [-0.220, 0.068] | 0.339 | 0.339 | inconclusive | NA | NA | NA |
| H4 | C-auto |  | -0.065 | [-0.187, 0.056] | [-0.213, 0.076] | 0.312 | 0.312 | inconclusive | NA | NA | NA |
| H4 | C-auto-broad |  | -0.064 | [-0.185, 0.057] | [-0.213, 0.077] | 0.300 | 0.300 | inconclusive | NA | NA | NA |
| H6 | A | 438 | 0.519 | [0.421, 0.627] | [0.393, 0.647] | 0.102 | 0.204 | inconclusive | 0.729 | 0.084 | [-0.499, 0.682] |
| H6 | C-auto | 437 | 0.521 | [0.420, 0.629] | [0.393, 0.648] | 0.112 | 0.224 | inconclusive | 0.727 | 0.091 | [-0.493, 0.694] |
| H6 | C-auto-broad | 437 | 0.521 | [0.420, 0.629] | [0.393, 0.648] | 0.112 | 0.224 | inconclusive | 0.727 | 0.091 | [-0.493, 0.694] |

## E8 oracle rule

| tier | cohort | within-drug AUROC | 95% CI | grep | bar | statistic | pass | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | novel | 0.974 | [0.916, 1.000] | 1.000 | 0.950 | point | True | fail |
| A | older_primary | 0.957 | [0.921, 0.983] | 1.000 | 0.950 | lower95 | False | fail |
| C-auto | novel | 0.973 | [0.915, 1.000] | 1.000 | 0.950 | point | True | pass |
| C-auto | older_primary | 0.977 | [0.954, 0.993] | 1.000 | 0.950 | lower95 | True | pass |
| C-auto-broad | novel | 0.973 | [0.915, 1.000] | 1.000 | 0.950 | point | True | pass |
| C-auto-broad | older_primary | 0.979 | [0.956, 0.994] | 1.000 | 0.950 | lower95 | True | pass |

## E7 arms c, d, e

| arm | cell | tier | within | 95% CI | residual within | 95% CI | partner prior within | paired vs prior | 95% CI | TOST 90% (Older-primary) | kappa | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c | novel/A | A | 0.534 | [0.400, 0.698] | 0.524 | [0.389, 0.678] | 0.489 | 0.045 | [-0.151, 0.261] |  | 0.147 | neither |
| c | novel/A | C-auto | 0.533 | [0.399, 0.698] | 0.525 | [0.388, 0.677] | 0.490 | 0.043 | [-0.159, 0.261] |  | 0.144 | neither |
| c | novel/B | A | 0.533 | [0.351, 0.737] | 0.534 | [0.372, 0.711] | 0.449 | 0.083 | [-0.190, 0.383] |  | NA | neither |
| c | novel/B | C-auto | 0.529 | [0.342, 0.736] | 0.533 | [0.360, 0.708] | 0.450 | 0.079 | [-0.197, 0.382] |  | NA | neither |
| c | older_primary/A | A | 0.695 | [0.630, 0.762] | 0.706 | [0.642, 0.767] | 0.497 | 0.198 | [0.104, 0.286] | [0.638, 0.750] eq=False | 1.284 | signal |
| c | older_primary/A | C-auto | 0.692 | [0.620, 0.763] | 0.700 | [0.629, 0.766] | 0.492 | 0.200 | [0.100, 0.290] | [0.632, 0.752] eq=False | 1.238 | signal |
| c | older_primary/B | A | 0.754 | [0.649, 0.841] | 0.736 | [0.633, 0.821] | 0.448 | 0.307 | [0.151, 0.447] | [0.668, 0.829] eq=False | NA | signal |
| c | older_primary/B | C-auto | 0.750 | [0.642, 0.840] | 0.717 | [0.608, 0.806] | 0.442 | 0.308 | [0.136, 0.461] | [0.662, 0.827] eq=False | NA | signal |
| c | older_clean/A | A | 0.697 | [0.635, 0.758] | 0.712 | [0.645, 0.773] | 0.498 | 0.199 | [0.110, 0.280] |  | 1.398 | signal |
| c | older_clean/A | C-auto | 0.694 | [0.622, 0.758] | 0.706 | [0.634, 0.771] | 0.495 | 0.199 | [0.104, 0.283] |  | 1.350 | signal |
| c | older_clean/B | A | 0.752 | [0.648, 0.834] | 0.739 | [0.647, 0.830] | 0.450 | 0.302 | [0.146, 0.444] |  | NA | signal |
| c | older_clean/B | C-auto | 0.748 | [0.638, 0.837] | 0.720 | [0.618, 0.813] | 0.444 | 0.304 | [0.138, 0.460] |  | NA | signal |
| d | novel/A | A | 0.518 | [0.385, 0.668] | 0.503 | [0.364, 0.673] | 0.489 | 0.029 | [-0.170, 0.249] |  | 0.078 | neither |
| d | novel/A | C-auto | 0.514 | [0.375, 0.663] | 0.501 | [0.359, 0.671] | 0.490 | 0.024 | [-0.185, 0.244] |  | 0.062 | neither |
| d | novel/B | A | 0.563 | [0.382, 0.759] | 0.529 | [0.327, 0.748] | 0.449 | 0.113 | [-0.166, 0.452] |  | NA | neither |
| d | novel/B | C-auto | 0.557 | [0.373, 0.759] | 0.522 | [0.321, 0.739] | 0.450 | 0.107 | [-0.174, 0.452] |  | NA | neither |
| d | older_primary/A | A | 0.671 | [0.601, 0.737] | 0.675 | [0.601, 0.747] | 0.497 | 0.175 | [0.073, 0.264] | [0.614, 0.725] eq=False | 1.130 | signal |
| d | older_primary/A | C-auto | 0.667 | [0.594, 0.735] | 0.667 | [0.582, 0.740] | 0.492 | 0.175 | [0.068, 0.269] | [0.604, 0.724] eq=False | 1.081 | signal |
| d | older_primary/B | A | 0.731 | [0.630, 0.816] | 0.712 | [0.608, 0.802] | 0.448 | 0.283 | [0.115, 0.435] | [0.646, 0.806] eq=False | NA | signal |
| d | older_primary/B | C-auto | 0.728 | [0.614, 0.819] | 0.704 | [0.598, 0.800] | 0.442 | 0.286 | [0.108, 0.448] | [0.635, 0.806] eq=False | NA | signal |
| d | older_clean/A | A | 0.665 | [0.598, 0.730] | 0.671 | [0.597, 0.742] | 0.498 | 0.166 | [0.078, 0.256] |  | 1.167 | signal |
| d | older_clean/A | C-auto | 0.660 | [0.591, 0.728] | 0.662 | [0.583, 0.734] | 0.495 | 0.165 | [0.074, 0.257] |  | 1.111 | signal |
| d | older_clean/B | A | 0.731 | [0.628, 0.813] | 0.714 | [0.613, 0.797] | 0.450 | 0.281 | [0.117, 0.431] |  | NA | signal |
| d | older_clean/B | C-auto | 0.728 | [0.622, 0.812] | 0.702 | [0.599, 0.792] | 0.444 | 0.284 | [0.114, 0.439] |  | NA | signal |
| e | novel/A | A | 0.613 | [0.477, 0.758] | 0.655 | [0.515, 0.787] | 0.489 | 0.124 | [-0.082, 0.334] |  | 0.494 | neither |
| e | novel/A | C-auto | 0.610 | [0.472, 0.758] | 0.651 | [0.512, 0.783] | 0.490 | 0.120 | [-0.092, 0.330] |  | 0.484 | neither |
| e | novel/B | A | 0.664 | [0.485, 0.837] | 0.643 | [0.464, 0.818] | 0.449 | 0.214 | [-0.068, 0.525] |  | NA | neither |
| e | novel/B | C-auto | 0.659 | [0.479, 0.837] | 0.639 | [0.453, 0.823] | 0.450 | 0.209 | [-0.085, 0.522] |  | NA | neither |
| e | older_primary/A | A | 0.734 | [0.665, 0.802] | 0.756 | [0.694, 0.819] | 0.497 | 0.238 | [0.129, 0.335] | [0.676, 0.789] eq=False | 1.545 | signal |
| e | older_primary/A | C-auto | 0.726 | [0.653, 0.796] | 0.740 | [0.672, 0.808] | 0.492 | 0.233 | [0.120, 0.331] | [0.665, 0.784] eq=False | 1.457 | signal |
| e | older_primary/B | A | 0.777 | [0.681, 0.860] | 0.773 | [0.675, 0.855] | 0.448 | 0.330 | [0.176, 0.472] | [0.696, 0.849] eq=False | NA | signal |
| e | older_primary/B | C-auto | 0.774 | [0.666, 0.863] | 0.759 | [0.661, 0.847] | 0.442 | 0.333 | [0.170, 0.482] | [0.688, 0.849] eq=False | NA | signal |
| e | older_clean/A | A | 0.731 | [0.665, 0.792] | 0.753 | [0.690, 0.811] | 0.498 | 0.232 | [0.126, 0.322] |  | 1.632 | signal |
| e | older_clean/A | C-auto | 0.721 | [0.649, 0.786] | 0.739 | [0.675, 0.802] | 0.495 | 0.226 | [0.114, 0.325] |  | 1.541 | signal |
| e | older_clean/B | A | 0.775 | [0.675, 0.859] | 0.769 | [0.677, 0.855] | 0.450 | 0.325 | [0.165, 0.467] |  | NA | signal |
| e | older_clean/B | C-auto | 0.772 | [0.669, 0.859] | 0.754 | [0.657, 0.845] | 0.444 | 0.328 | [0.165, 0.481] |  | NA | signal |

## DrugBank lookup

| cohort | tier | n | n_pos | within-drug AUROC | 95% CI (two-way) | pooled AUROC | 95% CI (two-way) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| novel | A | 438 | 148 | 0.729 | [0.642, 0.808] | 0.767 | [0.691, 0.839] |
| novel | C-auto | 437 | 147 | 0.727 | [0.641, 0.808] | 0.766 | [0.686, 0.839] |
| older_full | A | 1944 | 648 | 0.632 | [0.589, 0.677] | 0.661 | [0.611, 0.708] |
| older_full | C-auto | 1902 | 606 | 0.634 | [0.588, 0.679] | 0.668 | [0.616, 0.717] |
| older_clean | A | 1832 | 599 | 0.641 | [0.595, 0.689] | 0.680 | [0.630, 0.723] |
| older_clean | C-auto | 1794 | 561 | 0.644 | [0.596, 0.695] | 0.687 | [0.638, 0.731] |
| older_primary | A | 1721 | 562 | 0.652 | [0.601, 0.705] | 0.692 | [0.646, 0.735] |
| older_primary | C-auto | 1684 | 525 | 0.655 | [0.606, 0.711] | 0.700 | [0.652, 0.741] |
