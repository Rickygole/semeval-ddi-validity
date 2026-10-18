# C1: model-free same-pair dissociation

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

DrugBank release: version 5.1, exported on 2026-03-05 (`drugbank_all_full_database.xml.zip`).

## Funnel

| step | train | test | pooled |
| --- | --- | --- | --- |
| instances | 13789 | 2810 | 16599 |
| unique_pairs | 7934 | 1844 | 9230 |
| self_pairs | 354 | 113 | 408 |
| non_self_pairs | 7580 | 1731 | 8822 |
| self_pairs_in_vocab_with_di | 201 | 52 | 215 |
| both_names_in_vocabulary | 6612 | 1119 | 7258 |
| at_least_one_di_section | 5480 | 979 | 6059 |
| fda_positive | 621 | 128 | 674 |
| fda_negative | 2083 | 343 | 2320 |
| fda_undecided | 2776 | 508 | 3065 |
| db_unresolvable | 4 | 0 | 4 |

## Consistency gate on the 4,643 E7 pairs

```
{
 "primary": {
  "E7_negative->negative": 3101,
  "E7_positive->positive": 1542
 },
 "S2": {
  "E7_negative->negative": 3101,
  "E7_positive->positive": 1542
 }
}
```

## Pair view, variant primary

| stratum | pairs | FDA decided | FDA undecided | SemEval any + | SemEval majority + | FDA + | DrugBank listed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 5480 | 2704 | 2776 | 390 | 185 | 621 | 2206 |
| train/DDI-DrugBank | 5331 | 2654 | 2677 | 373 | 182 | 611 | 2167 |
| train/DDI-MedLine | 198 | 73 | 125 | 18 | 4 | 20 | 61 |
| test/both | 979 | 471 | 508 | 40 | 28 | 128 | 407 |
| test/DDI-DrugBank | 940 | 446 | 494 | 29 | 22 | 121 | 386 |
| test/DDI-MedLine | 44 | 27 | 17 | 11 | 7 | 9 | 23 |
| pooled/both | 6059 | 2994 | 3065 | 421 | 201 | 674 | 2441 |
| pooled/DDI-DrugBank | 5886 | 2930 | 2956 | 393 | 193 | 660 | 2392 |
| pooled/DDI-MedLine | 241 | 99 | 142 | 29 | 11 | 28 | 83 |

| stratum | labels (first|second) | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | sem_any|sem_majority | 0.924 | [0.914, 0.934] | 0.607 | [0.556, 0.655] | 0.959 | [0.954, 0.965] | 0.737 | [0.712, 0.762] |  |
| train/both | sem_any|fda | 0.844 | [0.829, 0.857] | 0.492 | [0.447, 0.533] | 0.714 | [0.693, 0.735] | 0.806 | [0.782, 0.826] |  |
| train/both | sem_any|db | 0.309 | [0.293, 0.326] | 0.047 | [0.036, 0.058] | 0.556 | [0.544, 0.568] | 0.569 | [0.555, 0.582] |  |
| train/both | sem_majority|fda | 0.795 | [0.780, 0.810] | 0.232 | [0.188, 0.272] | 0.587 | [0.570, 0.604] | 0.742 | [0.705, 0.775] |  |
| train/both | sem_majority|db | 0.241 | [0.224, 0.257] | 0.017 | [0.010, 0.024] | 0.522 | [0.513, 0.532] | 0.552 | [0.530, 0.573] |  |
| train/both | fda|db | 0.390 | [0.373, 0.409] | 0.091 | [0.077, 0.105] | 0.601 | [0.587, 0.615] | 0.586 | [0.574, 0.598] |  |
| train/DDI-DrugBank | sem_any|sem_majority | 0.928 | [0.917, 0.937] | 0.621 | [0.571, 0.667] | 0.961 | [0.956, 0.966] | 0.744 | [0.718, 0.770] |  |
| train/DDI-DrugBank | sem_any|fda | 0.845 | [0.830, 0.858] | 0.493 | [0.447, 0.536] | 0.713 | [0.691, 0.735] | 0.812 | [0.786, 0.833] |  |
| train/DDI-DrugBank | sem_any|db | 0.307 | [0.290, 0.324] | 0.047 | [0.036, 0.058] | 0.557 | [0.545, 0.570] | 0.571 | [0.556, 0.584] |  |
| train/DDI-DrugBank | sem_majority|fda | 0.795 | [0.779, 0.810] | 0.234 | [0.190, 0.277] | 0.588 | [0.571, 0.605] | 0.745 | [0.706, 0.778] |  |
| train/DDI-DrugBank | sem_majority|db | 0.241 | [0.225, 0.258] | 0.018 | [0.010, 0.025] | 0.523 | [0.513, 0.532] | 0.554 | [0.532, 0.573] |  |
| train/DDI-DrugBank | fda|db | 0.390 | [0.371, 0.407] | 0.090 | [0.076, 0.104] | 0.601 | [0.587, 0.615] | 0.585 | [0.573, 0.597] |  |
| train/DDI-MedLine | sem_any|sem_majority | 0.808 | NA | 0.301 | NA | 0.899 | NA | 0.611 | NA | small |
| train/DDI-MedLine | sem_any|fda | 0.726 | NA | 0.289 | NA | 0.640 | NA | 0.650 | NA | small |
| train/DDI-MedLine | sem_any|db | 0.329 | NA | -0.002 | NA | 0.498 | NA | 0.498 | NA | small |
| train/DDI-MedLine | sem_majority|fda | 0.726 | NA | 0.083 | NA | 0.531 | NA | 0.620 | NA | small |
| train/DDI-MedLine | sem_majority|db | 0.192 | NA | -0.012 | NA | 0.483 | NA | 0.455 | NA | small |
| train/DDI-MedLine | fda|db | 0.438 | NA | 0.138 | NA | 0.664 | NA | 0.613 | NA | small |
| test/both | sem_any|sem_majority | 0.975 | [0.960, 0.987] | 0.810 | [0.688, 0.905] | 0.986 | [0.978, 0.993] | 0.850 | [0.773, 0.919] |  |
| test/both | sem_any|fda | 0.762 | [0.722, 0.796] | 0.234 | [0.141, 0.317] | 0.592 | [0.554, 0.627] | 0.734 | [0.654, 0.806] |  |
| test/both | sem_any|db | 0.200 | [0.163, 0.234] | 0.002 | [-0.020, 0.022] | 0.504 | [0.465, 0.536] | 0.506 | [0.450, 0.561] |  |
| test/both | sem_majority|fda | 0.758 | [0.718, 0.794] | 0.190 | [0.106, 0.273] | 0.572 | [0.540, 0.605] | 0.754 | [0.665, 0.839] |  |
| test/both | sem_majority|db | 0.178 | [0.142, 0.214] | -0.001 | [-0.020, 0.015] | 0.498 | [0.464, 0.526] | 0.496 | [0.426, 0.561] |  |
| test/both | fda|db | 0.382 | [0.340, 0.427] | 0.073 | [0.040, 0.107] | 0.603 | [0.560, 0.641] | 0.561 | [0.533, 0.587] |  |
| test/DDI-DrugBank | sem_any|sem_majority | 0.984 | [0.971, 0.993] | 0.855 | [0.731, 0.945] | 0.992 | [0.985, 0.997] | 0.879 | [0.795, 0.950] |  |
| test/DDI-DrugBank | sem_any|fda | 0.767 | [0.729, 0.800] | 0.225 | [0.147, 0.317] | 0.586 | [0.554, 0.624] | 0.779 | [0.702, 0.854] |  |
| test/DDI-DrugBank | sem_any|db | 0.182 | [0.148, 0.220] | -0.001 | [-0.021, 0.017] | 0.499 | [0.462, 0.529] | 0.498 | [0.426, 0.560] |  |
| test/DDI-DrugBank | sem_majority|fda | 0.756 | [0.717, 0.789] | 0.168 | [0.091, 0.248] | 0.563 | [0.533, 0.595] | 0.764 | [0.673, 0.851] |  |
| test/DDI-DrugBank | sem_majority|db | 0.166 | [0.132, 0.202] | -0.006 | [-0.025, 0.011] | 0.490 | [0.454, 0.522] | 0.475 | [0.385, 0.558] |  |
| test/DDI-DrugBank | fda|db | 0.379 | [0.336, 0.422] | 0.069 | [0.034, 0.104] | 0.599 | [0.553, 0.639] | 0.558 | [0.529, 0.585] |  |
| test/DDI-MedLine | sem_any|sem_majority | 0.852 | NA | 0.675 | NA | 0.900 | NA | 0.818 | NA | small |
| test/DDI-MedLine | sem_any|fda | 0.630 | NA | 0.211 | NA | 0.611 | NA | 0.602 | NA | small |
| test/DDI-MedLine | sem_any|db | 0.481 | NA | 0.083 | NA | 0.592 | NA | 0.548 | NA | small |
| test/DDI-MedLine | sem_majority|fda | 0.778 | NA | 0.471 | NA | 0.722 | NA | 0.757 | NA | small |
| test/DDI-MedLine | sem_majority|db | 0.407 | NA | 0.115 | NA | 0.652 | NA | 0.600 | NA | small |
| test/DDI-MedLine | fda|db | 0.481 | NA | 0.160 | NA | 0.696 | NA | 0.611 | NA | small |
| pooled/both | sem_any|sem_majority | 0.927 | [0.918, 0.936] | 0.611 | [0.562, 0.657] | 0.961 | [0.956, 0.965] | 0.739 | [0.714, 0.763] |  |
| pooled/both | sem_any|fda | 0.845 | [0.831, 0.857] | 0.486 | [0.440, 0.527] | 0.711 | [0.689, 0.732] | 0.804 | [0.781, 0.825] |  |
| pooled/both | sem_any|db | 0.305 | [0.290, 0.321] | 0.043 | [0.033, 0.053] | 0.552 | [0.540, 0.564] | 0.565 | [0.550, 0.579] |  |
| pooled/both | sem_majority|fda | 0.801 | [0.786, 0.814] | 0.239 | [0.198, 0.279] | 0.590 | [0.574, 0.606] | 0.750 | [0.716, 0.781] |  |
| pooled/both | sem_majority|db | 0.239 | [0.225, 0.254] | 0.016 | [0.008, 0.022] | 0.520 | [0.511, 0.529] | 0.548 | [0.526, 0.568] |  |
| pooled/both | fda|db | 0.386 | [0.369, 0.402] | 0.088 | [0.075, 0.101] | 0.598 | [0.585, 0.612] | 0.585 | [0.574, 0.596] |  |
| pooled/DDI-DrugBank | sem_any|sem_majority | 0.932 | [0.922, 0.941] | 0.626 | [0.576, 0.670] | 0.963 | [0.958, 0.968] | 0.746 | [0.720, 0.770] |  |
| pooled/DDI-DrugBank | sem_any|fda | 0.847 | [0.833, 0.859] | 0.487 | [0.445, 0.527] | 0.709 | [0.689, 0.730] | 0.814 | [0.789, 0.833] |  |
| pooled/DDI-DrugBank | sem_any|db | 0.299 | [0.283, 0.316] | 0.042 | [0.032, 0.052] | 0.551 | [0.539, 0.563] | 0.566 | [0.552, 0.580] |  |
| pooled/DDI-DrugBank | sem_majority|fda | 0.801 | [0.786, 0.814] | 0.239 | [0.199, 0.277] | 0.589 | [0.574, 0.605] | 0.754 | [0.717, 0.786] |  |
| pooled/DDI-DrugBank | sem_majority|db | 0.237 | [0.223, 0.252] | 0.015 | [0.008, 0.022] | 0.520 | [0.510, 0.528] | 0.548 | [0.526, 0.568] |  |
| pooled/DDI-DrugBank | fda|db | 0.384 | [0.367, 0.401] | 0.086 | [0.073, 0.100] | 0.597 | [0.583, 0.610] | 0.583 | [0.571, 0.595] |  |
| pooled/DDI-MedLine | sem_any|sem_majority | 0.818 | NA | 0.464 | NA | 0.898 | NA | 0.690 | NA | small |
| pooled/DDI-MedLine | sem_any|fda | 0.707 | [0.626, 0.798] | 0.286 | [0.091, 0.485] | 0.644 | [0.544, 0.752] | 0.641 | [0.544, 0.742] |  |
| pooled/DDI-MedLine | sem_any|db | 0.374 | NA | 0.022 | NA | 0.526 | NA | 0.517 | NA | small |
| pooled/DDI-MedLine | sem_majority|fda | 0.747 | NA | 0.237 | NA | 0.597 | NA | 0.699 | NA | small |
| pooled/DDI-MedLine | sem_majority|db | 0.253 | NA | 0.021 | NA | 0.529 | NA | 0.540 | NA | small |
| pooled/DDI-MedLine | fda|db | 0.444 | NA | 0.141 | NA | 0.669 | NA | 0.613 | NA | small |

## Pair view, variant self_included

| stratum | pairs | FDA decided | FDA undecided | SemEval any + | SemEval majority + | FDA + | DrugBank listed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 5681 | 2704 | 2977 | 390 | 185 | 621 | 2206 |
| train/DDI-DrugBank | 5521 | 2654 | 2867 | 373 | 182 | 611 | 2167 |
| train/DDI-MedLine | 231 | 73 | 158 | 18 | 4 | 20 | 61 |
| test/both | 1031 | 471 | 560 | 40 | 28 | 128 | 407 |
| test/DDI-DrugBank | 982 | 446 | 536 | 29 | 22 | 121 | 386 |
| test/DDI-MedLine | 55 | 27 | 28 | 11 | 7 | 9 | 23 |
| pooled/both | 6274 | 2994 | 3280 | 421 | 201 | 674 | 2441 |
| pooled/DDI-DrugBank | 6086 | 2930 | 3156 | 393 | 193 | 660 | 2392 |
| pooled/DDI-MedLine | 284 | 99 | 185 | 29 | 11 | 28 | 83 |

| stratum | labels (first|second) | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | sem_any|sem_majority | 0.924 | [0.914, 0.934] | 0.607 | [0.556, 0.655] | 0.959 | [0.954, 0.965] | 0.737 | [0.712, 0.762] |  |
| train/both | sem_any|fda | 0.844 | [0.829, 0.857] | 0.492 | [0.447, 0.533] | 0.714 | [0.693, 0.735] | 0.806 | [0.782, 0.826] |  |
| train/both | sem_any|db | 0.309 | [0.293, 0.326] | 0.047 | [0.036, 0.058] | 0.556 | [0.544, 0.568] | 0.569 | [0.555, 0.582] |  |
| train/both | sem_majority|fda | 0.795 | [0.780, 0.810] | 0.232 | [0.188, 0.272] | 0.587 | [0.570, 0.604] | 0.742 | [0.705, 0.775] |  |
| train/both | sem_majority|db | 0.241 | [0.224, 0.257] | 0.017 | [0.010, 0.024] | 0.522 | [0.513, 0.532] | 0.552 | [0.530, 0.573] |  |
| train/both | fda|db | 0.390 | [0.373, 0.409] | 0.091 | [0.077, 0.105] | 0.601 | [0.587, 0.615] | 0.586 | [0.574, 0.598] |  |
| train/DDI-DrugBank | sem_any|sem_majority | 0.928 | [0.917, 0.937] | 0.621 | [0.571, 0.667] | 0.961 | [0.956, 0.966] | 0.744 | [0.718, 0.770] |  |
| train/DDI-DrugBank | sem_any|fda | 0.845 | [0.830, 0.858] | 0.493 | [0.447, 0.536] | 0.713 | [0.691, 0.735] | 0.812 | [0.786, 0.833] |  |
| train/DDI-DrugBank | sem_any|db | 0.307 | [0.290, 0.324] | 0.047 | [0.036, 0.058] | 0.557 | [0.545, 0.570] | 0.571 | [0.556, 0.584] |  |
| train/DDI-DrugBank | sem_majority|fda | 0.795 | [0.779, 0.810] | 0.234 | [0.190, 0.277] | 0.588 | [0.571, 0.605] | 0.745 | [0.706, 0.778] |  |
| train/DDI-DrugBank | sem_majority|db | 0.241 | [0.225, 0.258] | 0.018 | [0.010, 0.025] | 0.523 | [0.513, 0.532] | 0.554 | [0.532, 0.573] |  |
| train/DDI-DrugBank | fda|db | 0.390 | [0.371, 0.407] | 0.090 | [0.076, 0.104] | 0.601 | [0.587, 0.615] | 0.585 | [0.573, 0.597] |  |
| train/DDI-MedLine | sem_any|sem_majority | 0.808 | NA | 0.301 | NA | 0.899 | NA | 0.611 | NA | small |
| train/DDI-MedLine | sem_any|fda | 0.726 | NA | 0.289 | NA | 0.640 | NA | 0.650 | NA | small |
| train/DDI-MedLine | sem_any|db | 0.329 | NA | -0.002 | NA | 0.498 | NA | 0.498 | NA | small |
| train/DDI-MedLine | sem_majority|fda | 0.726 | NA | 0.083 | NA | 0.531 | NA | 0.620 | NA | small |
| train/DDI-MedLine | sem_majority|db | 0.192 | NA | -0.012 | NA | 0.483 | NA | 0.455 | NA | small |
| train/DDI-MedLine | fda|db | 0.438 | NA | 0.138 | NA | 0.664 | NA | 0.613 | NA | small |
| test/both | sem_any|sem_majority | 0.975 | [0.960, 0.987] | 0.810 | [0.688, 0.905] | 0.986 | [0.978, 0.993] | 0.850 | [0.773, 0.919] |  |
| test/both | sem_any|fda | 0.762 | [0.722, 0.796] | 0.234 | [0.141, 0.317] | 0.592 | [0.554, 0.627] | 0.734 | [0.654, 0.806] |  |
| test/both | sem_any|db | 0.200 | [0.163, 0.234] | 0.002 | [-0.020, 0.022] | 0.504 | [0.465, 0.536] | 0.506 | [0.450, 0.561] |  |
| test/both | sem_majority|fda | 0.758 | [0.718, 0.794] | 0.190 | [0.106, 0.273] | 0.572 | [0.540, 0.605] | 0.754 | [0.665, 0.839] |  |
| test/both | sem_majority|db | 0.178 | [0.142, 0.214] | -0.001 | [-0.020, 0.015] | 0.498 | [0.464, 0.526] | 0.496 | [0.426, 0.561] |  |
| test/both | fda|db | 0.382 | [0.340, 0.427] | 0.073 | [0.040, 0.107] | 0.603 | [0.560, 0.641] | 0.561 | [0.533, 0.587] |  |
| test/DDI-DrugBank | sem_any|sem_majority | 0.984 | [0.971, 0.993] | 0.855 | [0.731, 0.945] | 0.992 | [0.985, 0.997] | 0.879 | [0.795, 0.950] |  |
| test/DDI-DrugBank | sem_any|fda | 0.767 | [0.729, 0.800] | 0.225 | [0.147, 0.317] | 0.586 | [0.554, 0.624] | 0.779 | [0.702, 0.854] |  |
| test/DDI-DrugBank | sem_any|db | 0.182 | [0.148, 0.220] | -0.001 | [-0.021, 0.017] | 0.499 | [0.462, 0.529] | 0.498 | [0.426, 0.560] |  |
| test/DDI-DrugBank | sem_majority|fda | 0.756 | [0.717, 0.789] | 0.168 | [0.091, 0.248] | 0.563 | [0.533, 0.595] | 0.764 | [0.673, 0.851] |  |
| test/DDI-DrugBank | sem_majority|db | 0.166 | [0.132, 0.202] | -0.006 | [-0.025, 0.011] | 0.490 | [0.454, 0.522] | 0.475 | [0.385, 0.558] |  |
| test/DDI-DrugBank | fda|db | 0.379 | [0.336, 0.422] | 0.069 | [0.034, 0.104] | 0.599 | [0.553, 0.639] | 0.558 | [0.529, 0.585] |  |
| test/DDI-MedLine | sem_any|sem_majority | 0.852 | NA | 0.675 | NA | 0.900 | NA | 0.818 | NA | small |
| test/DDI-MedLine | sem_any|fda | 0.630 | NA | 0.211 | NA | 0.611 | NA | 0.602 | NA | small |
| test/DDI-MedLine | sem_any|db | 0.481 | NA | 0.083 | NA | 0.592 | NA | 0.548 | NA | small |
| test/DDI-MedLine | sem_majority|fda | 0.778 | NA | 0.471 | NA | 0.722 | NA | 0.757 | NA | small |
| test/DDI-MedLine | sem_majority|db | 0.407 | NA | 0.115 | NA | 0.652 | NA | 0.600 | NA | small |
| test/DDI-MedLine | fda|db | 0.481 | NA | 0.160 | NA | 0.696 | NA | 0.611 | NA | small |
| pooled/both | sem_any|sem_majority | 0.927 | [0.918, 0.936] | 0.611 | [0.562, 0.657] | 0.961 | [0.956, 0.965] | 0.739 | [0.714, 0.763] |  |
| pooled/both | sem_any|fda | 0.845 | [0.831, 0.857] | 0.486 | [0.440, 0.527] | 0.711 | [0.689, 0.732] | 0.804 | [0.781, 0.825] |  |
| pooled/both | sem_any|db | 0.305 | [0.290, 0.321] | 0.043 | [0.033, 0.053] | 0.552 | [0.540, 0.564] | 0.565 | [0.550, 0.579] |  |
| pooled/both | sem_majority|fda | 0.801 | [0.786, 0.814] | 0.239 | [0.198, 0.279] | 0.590 | [0.574, 0.606] | 0.750 | [0.716, 0.781] |  |
| pooled/both | sem_majority|db | 0.239 | [0.225, 0.254] | 0.016 | [0.008, 0.022] | 0.520 | [0.511, 0.529] | 0.548 | [0.526, 0.568] |  |
| pooled/both | fda|db | 0.386 | [0.369, 0.402] | 0.088 | [0.075, 0.101] | 0.598 | [0.585, 0.612] | 0.585 | [0.574, 0.596] |  |
| pooled/DDI-DrugBank | sem_any|sem_majority | 0.932 | [0.922, 0.941] | 0.626 | [0.576, 0.670] | 0.963 | [0.958, 0.968] | 0.746 | [0.720, 0.770] |  |
| pooled/DDI-DrugBank | sem_any|fda | 0.847 | [0.833, 0.859] | 0.487 | [0.445, 0.527] | 0.709 | [0.689, 0.730] | 0.814 | [0.789, 0.833] |  |
| pooled/DDI-DrugBank | sem_any|db | 0.299 | [0.283, 0.316] | 0.042 | [0.032, 0.052] | 0.551 | [0.539, 0.563] | 0.566 | [0.552, 0.580] |  |
| pooled/DDI-DrugBank | sem_majority|fda | 0.801 | [0.786, 0.814] | 0.239 | [0.199, 0.277] | 0.589 | [0.574, 0.605] | 0.754 | [0.717, 0.786] |  |
| pooled/DDI-DrugBank | sem_majority|db | 0.237 | [0.223, 0.252] | 0.015 | [0.008, 0.022] | 0.520 | [0.510, 0.528] | 0.548 | [0.526, 0.568] |  |
| pooled/DDI-DrugBank | fda|db | 0.384 | [0.367, 0.401] | 0.086 | [0.073, 0.100] | 0.597 | [0.583, 0.610] | 0.583 | [0.571, 0.595] |  |
| pooled/DDI-MedLine | sem_any|sem_majority | 0.818 | NA | 0.464 | NA | 0.898 | NA | 0.690 | NA | small |
| pooled/DDI-MedLine | sem_any|fda | 0.707 | [0.626, 0.798] | 0.286 | [0.091, 0.485] | 0.644 | [0.544, 0.752] | 0.641 | [0.544, 0.742] |  |
| pooled/DDI-MedLine | sem_any|db | 0.374 | NA | 0.022 | NA | 0.526 | NA | 0.517 | NA | small |
| pooled/DDI-MedLine | sem_majority|fda | 0.747 | NA | 0.237 | NA | 0.597 | NA | 0.699 | NA | small |
| pooled/DDI-MedLine | sem_majority|db | 0.253 | NA | 0.021 | NA | 0.529 | NA | 0.540 | NA | small |
| pooled/DDI-MedLine | fda|db | 0.444 | NA | 0.141 | NA | 0.669 | NA | 0.613 | NA | small |

## Pair view, variant S1

| stratum | pairs | FDA decided | FDA undecided | SemEval any + | SemEval majority + | FDA + | DrugBank listed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 5480 | 2884 | 2596 | 402 | 189 | 621 | 2340 |
| train/DDI-DrugBank | 5331 | 2826 | 2505 | 381 | 185 | 611 | 2298 |
| train/DDI-MedLine | 198 | 83 | 115 | 22 | 5 | 20 | 65 |
| test/both | 979 | 523 | 456 | 40 | 28 | 128 | 451 |
| test/DDI-DrugBank | 940 | 498 | 442 | 29 | 22 | 121 | 430 |
| test/DDI-MedLine | 44 | 27 | 17 | 11 | 7 | 9 | 23 |
| pooled/both | 6059 | 3209 | 2850 | 433 | 205 | 674 | 2604 |
| pooled/DDI-DrugBank | 5886 | 3137 | 2749 | 401 | 196 | 660 | 2552 |
| pooled/DDI-MedLine | 241 | 109 | 132 | 33 | 12 | 28 | 87 |

| stratum | labels (first|second) | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | sem_any|sem_majority | 0.926 | [0.916, 0.936] | 0.604 | [0.554, 0.651] | 0.960 | [0.955, 0.965] | 0.735 | [0.710, 0.760] |  |
| train/both | sem_any|fda | 0.849 | [0.835, 0.862] | 0.488 | [0.446, 0.526] | 0.713 | [0.693, 0.732] | 0.800 | [0.778, 0.822] |  |
| train/both | sem_any|db | 0.307 | [0.290, 0.324] | 0.043 | [0.032, 0.054] | 0.551 | [0.538, 0.563] | 0.565 | [0.550, 0.580] |  |
| train/both | sem_majority|fda | 0.807 | [0.792, 0.820] | 0.234 | [0.194, 0.276] | 0.588 | [0.571, 0.604] | 0.741 | [0.705, 0.778] |  |
| train/both | sem_majority|db | 0.242 | [0.227, 0.258] | 0.016 | [0.008, 0.023] | 0.520 | [0.510, 0.529] | 0.550 | [0.526, 0.572] |  |
| train/both | fda|db | 0.382 | [0.364, 0.399] | 0.087 | [0.074, 0.100] | 0.596 | [0.583, 0.610] | 0.587 | [0.575, 0.599] |  |
| train/DDI-DrugBank | sem_any|sem_majority | 0.931 | [0.921, 0.939] | 0.620 | [0.568, 0.666] | 0.963 | [0.958, 0.968] | 0.743 | [0.716, 0.768] |  |
| train/DDI-DrugBank | sem_any|fda | 0.851 | [0.838, 0.863] | 0.492 | [0.449, 0.529] | 0.713 | [0.692, 0.731] | 0.809 | [0.785, 0.830] |  |
| train/DDI-DrugBank | sem_any|db | 0.304 | [0.288, 0.321] | 0.045 | [0.034, 0.055] | 0.554 | [0.542, 0.566] | 0.570 | [0.556, 0.585] |  |
| train/DDI-DrugBank | sem_majority|fda | 0.807 | [0.793, 0.821] | 0.237 | [0.196, 0.278] | 0.589 | [0.573, 0.605] | 0.746 | [0.709, 0.780] |  |
| train/DDI-DrugBank | sem_majority|db | 0.241 | [0.226, 0.257] | 0.017 | [0.010, 0.025] | 0.522 | [0.513, 0.531] | 0.554 | [0.532, 0.575] |  |
| train/DDI-DrugBank | fda|db | 0.380 | [0.363, 0.398] | 0.086 | [0.072, 0.100] | 0.596 | [0.581, 0.610] | 0.586 | [0.573, 0.598] |  |
| train/DDI-MedLine | sem_any|sem_majority | 0.795 | NA | 0.302 | NA | 0.891 | NA | 0.614 | NA | small |
| train/DDI-MedLine | sem_any|fda | 0.711 | [0.614, 0.795] | 0.236 | [0.008, 0.452] | 0.622 | [0.505, 0.739] | 0.614 | [0.504, 0.724] |  |
| train/DDI-MedLine | sem_any|db | 0.337 | NA | -0.047 | NA | 0.456 | NA | 0.462 | NA | small |
| train/DDI-MedLine | sem_majority|fda | 0.747 | NA | 0.070 | NA | 0.526 | NA | 0.585 | NA | small |
| train/DDI-MedLine | sem_majority|db | 0.229 | NA | -0.029 | NA | 0.468 | NA | 0.403 | NA | small |
| train/DDI-MedLine | fda|db | 0.458 | NA | 0.162 | NA | 0.654 | NA | 0.643 | NA | small |
| test/both | sem_any|sem_majority | 0.977 | [0.964, 0.989] | 0.812 | [0.696, 0.907] | 0.988 | [0.981, 0.994] | 0.850 | [0.775, 0.920] |  |
| test/both | sem_any|fda | 0.786 | [0.750, 0.820] | 0.245 | [0.151, 0.335] | 0.594 | [0.557, 0.632] | 0.746 | [0.667, 0.818] |  |
| test/both | sem_any|db | 0.195 | [0.162, 0.229] | 0.002 | [-0.017, 0.019] | 0.504 | [0.471, 0.533] | 0.507 | [0.452, 0.556] |  |
| test/both | sem_majority|fda | 0.782 | [0.746, 0.816] | 0.199 | [0.114, 0.286] | 0.573 | [0.541, 0.609] | 0.767 | [0.672, 0.842] |  |
| test/both | sem_majority|db | 0.176 | [0.143, 0.210] | -0.001 | [-0.018, 0.014] | 0.499 | [0.469, 0.526] | 0.497 | [0.428, 0.559] |  |
| test/both | fda|db | 0.359 | [0.317, 0.402] | 0.065 | [0.036, 0.095] | 0.594 | [0.556, 0.631] | 0.560 | [0.535, 0.587] |  |
| test/DDI-DrugBank | sem_any|sem_majority | 0.986 | [0.974, 0.994] | 0.855 | [0.727, 0.946] | 0.993 | [0.986, 0.997] | 0.879 | [0.793, 0.952] |  |
| test/DDI-DrugBank | sem_any|fda | 0.791 | [0.757, 0.827] | 0.235 | [0.144, 0.331] | 0.587 | [0.552, 0.626] | 0.792 | [0.704, 0.865] |  |
| test/DDI-DrugBank | sem_any|db | 0.179 | [0.145, 0.211] | -0.000 | [-0.019, 0.015] | 0.500 | [0.468, 0.527] | 0.499 | [0.428, 0.554] |  |
| test/DDI-DrugBank | sem_majority|fda | 0.781 | [0.747, 0.819] | 0.176 | [0.095, 0.264] | 0.564 | [0.533, 0.597] | 0.777 | [0.671, 0.860] |  |
| test/DDI-DrugBank | sem_majority|db | 0.165 | [0.133, 0.199] | -0.005 | [-0.024, 0.010] | 0.492 | [0.460, 0.518] | 0.476 | [0.383, 0.547] |  |
| test/DDI-DrugBank | fda|db | 0.355 | [0.315, 0.398] | 0.062 | [0.030, 0.090] | 0.590 | [0.548, 0.625] | 0.557 | [0.530, 0.583] |  |
| test/DDI-MedLine | sem_any|sem_majority | 0.852 | NA | 0.675 | NA | 0.900 | NA | 0.818 | NA | small |
| test/DDI-MedLine | sem_any|fda | 0.630 | NA | 0.211 | NA | 0.611 | NA | 0.602 | NA | small |
| test/DDI-MedLine | sem_any|db | 0.481 | NA | 0.083 | NA | 0.592 | NA | 0.548 | NA | small |
| test/DDI-MedLine | sem_majority|fda | 0.778 | NA | 0.471 | NA | 0.722 | NA | 0.757 | NA | small |
| test/DDI-MedLine | sem_majority|db | 0.407 | NA | 0.115 | NA | 0.652 | NA | 0.600 | NA | small |
| test/DDI-MedLine | fda|db | 0.481 | NA | 0.160 | NA | 0.696 | NA | 0.611 | NA | small |
| pooled/both | sem_any|sem_majority | 0.929 | [0.920, 0.937] | 0.609 | [0.558, 0.655] | 0.962 | [0.957, 0.967] | 0.737 | [0.710, 0.762] |  |
| pooled/both | sem_any|fda | 0.851 | [0.839, 0.863] | 0.484 | [0.444, 0.519] | 0.710 | [0.692, 0.728] | 0.799 | [0.777, 0.820] |  |
| pooled/both | sem_any|db | 0.301 | [0.285, 0.317] | 0.039 | [0.029, 0.049] | 0.546 | [0.535, 0.558] | 0.561 | [0.546, 0.575] |  |
| pooled/both | sem_majority|fda | 0.813 | [0.800, 0.825] | 0.242 | [0.202, 0.281] | 0.590 | [0.574, 0.605] | 0.750 | [0.715, 0.783] |  |
| pooled/both | sem_majority|db | 0.239 | [0.225, 0.255] | 0.014 | [0.007, 0.022] | 0.518 | [0.509, 0.527] | 0.546 | [0.524, 0.567] |  |
| pooled/both | fda|db | 0.376 | [0.359, 0.393] | 0.083 | [0.071, 0.096] | 0.593 | [0.581, 0.605] | 0.586 | [0.574, 0.597] |  |
| pooled/DDI-DrugBank | sem_any|sem_majority | 0.935 | [0.925, 0.943] | 0.625 | [0.574, 0.670] | 0.965 | [0.960, 0.969] | 0.744 | [0.717, 0.769] |  |
| pooled/DDI-DrugBank | sem_any|fda | 0.854 | [0.841, 0.866] | 0.488 | [0.445, 0.524] | 0.709 | [0.688, 0.727] | 0.811 | [0.787, 0.833] |  |
| pooled/DDI-DrugBank | sem_any|db | 0.296 | [0.280, 0.311] | 0.040 | [0.030, 0.049] | 0.548 | [0.537, 0.559] | 0.565 | [0.551, 0.580] |  |
| pooled/DDI-DrugBank | sem_majority|fda | 0.813 | [0.800, 0.826] | 0.242 | [0.201, 0.282] | 0.590 | [0.573, 0.606] | 0.755 | [0.720, 0.790] |  |
| pooled/DDI-DrugBank | sem_majority|db | 0.237 | [0.222, 0.251] | 0.014 | [0.007, 0.022] | 0.518 | [0.509, 0.527] | 0.548 | [0.525, 0.570] |  |
| pooled/DDI-DrugBank | fda|db | 0.374 | [0.356, 0.391] | 0.081 | [0.068, 0.094] | 0.591 | [0.579, 0.604] | 0.584 | [0.572, 0.595] |  |
| pooled/DDI-MedLine | sem_any|sem_majority | 0.807 | NA | 0.443 | NA | 0.892 | NA | 0.682 | NA | small |
| pooled/DDI-MedLine | sem_any|fda | 0.697 | [0.606, 0.780] | 0.251 | [0.050, 0.436] | 0.633 | [0.526, 0.735] | 0.620 | [0.523, 0.715] |  |
| pooled/DDI-MedLine | sem_any|db | 0.376 | [0.284, 0.477] | -0.010 | [-0.121, 0.105] | 0.490 | [0.382, 0.610] | 0.493 | [0.412, 0.580] |  |
| pooled/DDI-MedLine | sem_majority|fda | 0.761 | NA | 0.232 | NA | 0.594 | NA | 0.683 | NA | small |
| pooled/DDI-MedLine | sem_majority|db | 0.275 | NA | 0.011 | NA | 0.512 | NA | 0.520 | NA | small |
| pooled/DDI-MedLine | fda|db | 0.459 | [0.358, 0.550] | 0.161 | [0.089, 0.249] | 0.661 | [0.614, 0.710] | 0.636 | [0.589, 0.687] |  |

## Pair view, variant S2

| stratum | pairs | FDA decided | FDA undecided | SemEval any + | SemEval majority + | FDA + | DrugBank listed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 5480 | 2557 | 2923 | 357 | 171 | 580 | 2095 |
| train/DDI-DrugBank | 5331 | 2509 | 2822 | 341 | 168 | 571 | 2057 |
| train/DDI-MedLine | 198 | 70 | 128 | 17 | 4 | 18 | 59 |
| test/both | 979 | 442 | 537 | 38 | 26 | 118 | 386 |
| test/DDI-DrugBank | 940 | 422 | 518 | 28 | 21 | 112 | 370 |
| test/DDI-MedLine | 44 | 22 | 22 | 10 | 6 | 8 | 18 |
| pooled/both | 6059 | 2832 | 3227 | 386 | 186 | 630 | 2321 |
| pooled/DDI-DrugBank | 5886 | 2770 | 3116 | 360 | 178 | 617 | 2273 |
| pooled/DDI-MedLine | 241 | 91 | 150 | 27 | 10 | 25 | 76 |

| stratum | labels (first|second) | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | sem_any|sem_majority | 0.927 | [0.918, 0.937] | 0.613 | [0.565, 0.661] | 0.961 | [0.956, 0.967] | 0.739 | [0.715, 0.765] |  |
| train/both | sem_any|fda | 0.846 | [0.831, 0.860] | 0.490 | [0.448, 0.532] | 0.712 | [0.691, 0.734] | 0.809 | [0.786, 0.833] |  |
| train/both | sem_any|db | 0.306 | [0.288, 0.323] | 0.050 | [0.039, 0.060] | 0.561 | [0.549, 0.572] | 0.576 | [0.561, 0.589] |  |
| train/both | sem_majority|fda | 0.798 | [0.782, 0.814] | 0.232 | [0.185, 0.273] | 0.587 | [0.569, 0.604] | 0.745 | [0.705, 0.780] |  |
| train/both | sem_majority|db | 0.237 | [0.221, 0.253] | 0.018 | [0.010, 0.025] | 0.524 | [0.513, 0.533] | 0.556 | [0.533, 0.578] |  |
| train/both | fda|db | 0.385 | [0.365, 0.402] | 0.088 | [0.073, 0.102] | 0.600 | [0.585, 0.614] | 0.585 | [0.572, 0.597] |  |
| train/DDI-DrugBank | sem_any|sem_majority | 0.931 | [0.921, 0.941] | 0.627 | [0.577, 0.673] | 0.963 | [0.958, 0.969] | 0.746 | [0.721, 0.772] |  |
| train/DDI-DrugBank | sem_any|fda | 0.847 | [0.833, 0.861] | 0.493 | [0.449, 0.534] | 0.711 | [0.690, 0.732] | 0.816 | [0.792, 0.839] |  |
| train/DDI-DrugBank | sem_any|db | 0.304 | [0.287, 0.322] | 0.051 | [0.040, 0.061] | 0.563 | [0.551, 0.574] | 0.579 | [0.565, 0.592] |  |
| train/DDI-DrugBank | sem_majority|fda | 0.798 | [0.782, 0.814] | 0.235 | [0.190, 0.278] | 0.588 | [0.571, 0.605] | 0.748 | [0.708, 0.783] |  |
| train/DDI-DrugBank | sem_majority|db | 0.238 | [0.222, 0.254] | 0.019 | [0.012, 0.026] | 0.525 | [0.516, 0.534] | 0.558 | [0.536, 0.580] |  |
| train/DDI-DrugBank | fda|db | 0.385 | [0.365, 0.403] | 0.087 | [0.072, 0.102] | 0.600 | [0.585, 0.614] | 0.584 | [0.571, 0.596] |  |
| train/DDI-MedLine | sem_any|sem_majority | 0.814 | NA | 0.318 | NA | 0.902 | NA | 0.618 | NA | small |
| train/DDI-MedLine | sem_any|fda | 0.729 | NA | 0.276 | NA | 0.636 | NA | 0.641 | NA | small |
| train/DDI-MedLine | sem_any|db | 0.314 | NA | -0.014 | NA | 0.482 | NA | 0.487 | NA | small |
| train/DDI-MedLine | sem_majority|fda | 0.743 | NA | 0.097 | NA | 0.536 | NA | 0.629 | NA | small |
| train/DDI-MedLine | sem_majority|db | 0.186 | NA | -0.013 | NA | 0.480 | NA | 0.451 | NA | small |
| train/DDI-MedLine | fda|db | 0.414 | NA | 0.121 | NA | 0.653 | NA | 0.606 | NA | small |
| test/both | sem_any|sem_majority | 0.973 | [0.957, 0.986] | 0.798 | [0.678, 0.899] | 0.986 | [0.977, 0.993] | 0.842 | [0.767, 0.915] |  |
| test/both | sem_any|fda | 0.769 | [0.731, 0.810] | 0.248 | [0.163, 0.347] | 0.597 | [0.563, 0.639] | 0.743 | [0.668, 0.816] |  |
| test/both | sem_any|db | 0.195 | [0.158, 0.233] | 0.005 | [-0.019, 0.024] | 0.508 | [0.462, 0.542] | 0.512 | [0.451, 0.559] |  |
| test/both | sem_majority|fda | 0.765 | [0.724, 0.805] | 0.201 | [0.119, 0.288] | 0.575 | [0.544, 0.610] | 0.767 | [0.681, 0.847] |  |
| test/both | sem_majority|db | 0.172 | [0.138, 0.208] | 0.002 | [-0.019, 0.018] | 0.503 | [0.463, 0.532] | 0.506 | [0.431, 0.563] |  |
| test/both | fda|db | 0.371 | [0.326, 0.414] | 0.067 | [0.031, 0.101] | 0.602 | [0.553, 0.642] | 0.558 | [0.528, 0.583] |  |
| test/DDI-DrugBank | sem_any|sem_majority | 0.983 | [0.969, 0.995] | 0.849 | [0.731, 0.944] | 0.991 | [0.984, 0.997] | 0.875 | [0.796, 0.950] |  |
| test/DDI-DrugBank | sem_any|fda | 0.777 | [0.739, 0.820] | 0.249 | [0.162, 0.348] | 0.595 | [0.560, 0.635] | 0.798 | [0.717, 0.871] |  |
| test/DDI-DrugBank | sem_any|db | 0.175 | [0.140, 0.211] | 0.003 | [-0.019, 0.019] | 0.505 | [0.464, 0.535] | 0.509 | [0.437, 0.563] |  |
| test/DDI-DrugBank | sem_majority|fda | 0.765 | [0.723, 0.808] | 0.188 | [0.110, 0.279] | 0.569 | [0.540, 0.606] | 0.786 | [0.693, 0.870] |  |
| test/DDI-DrugBank | sem_majority|db | 0.159 | [0.126, 0.194] | -0.002 | [-0.023, 0.013] | 0.495 | [0.456, 0.526] | 0.490 | [0.405, 0.562] |  |
| test/DDI-DrugBank | fda|db | 0.365 | [0.318, 0.408] | 0.062 | [0.024, 0.095] | 0.597 | [0.541, 0.639] | 0.553 | [0.522, 0.580] |  |
| test/DDI-MedLine | sem_any|sem_majority | 0.818 | NA | 0.621 | NA | 0.875 | NA | 0.800 | NA | small |
| test/DDI-MedLine | sem_any|fda | 0.545 | NA | 0.068 | NA | 0.536 | NA | 0.533 | NA | small |
| test/DDI-MedLine | sem_any|db | 0.545 | NA | 0.141 | NA | 0.625 | NA | 0.575 | NA | small |
| test/DDI-MedLine | sem_majority|fda | 0.727 | NA | 0.377 | NA | 0.679 | NA | 0.708 | NA | small |
| test/DDI-MedLine | sem_majority|db | 0.455 | NA | 0.154 | NA | 0.667 | NA | 0.625 | NA | small |
| test/DDI-MedLine | fda|db | 0.545 | NA | 0.225 | NA | 0.722 | NA | 0.643 | NA | small |
| pooled/both | sem_any|sem_majority | 0.929 | [0.920, 0.939] | 0.616 | [0.566, 0.665] | 0.962 | [0.957, 0.967] | 0.741 | [0.715, 0.767] |  |
| pooled/both | sem_any|fda | 0.847 | [0.834, 0.861] | 0.486 | [0.443, 0.525] | 0.709 | [0.689, 0.729] | 0.808 | [0.786, 0.829] |  |
| pooled/both | sem_any|db | 0.301 | [0.284, 0.320] | 0.046 | [0.036, 0.056] | 0.557 | [0.545, 0.567] | 0.571 | [0.557, 0.585] |  |
| pooled/both | sem_majority|fda | 0.804 | [0.789, 0.819] | 0.242 | [0.199, 0.284] | 0.590 | [0.573, 0.607] | 0.755 | [0.719, 0.788] |  |
| pooled/both | sem_majority|db | 0.236 | [0.221, 0.251] | 0.017 | [0.010, 0.024] | 0.522 | [0.513, 0.530] | 0.553 | [0.532, 0.574] |  |
| pooled/both | fda|db | 0.380 | [0.362, 0.398] | 0.084 | [0.070, 0.097] | 0.596 | [0.583, 0.609] | 0.582 | [0.570, 0.594] |  |
| pooled/DDI-DrugBank | sem_any|sem_majority | 0.934 | [0.925, 0.943] | 0.630 | [0.581, 0.675] | 0.965 | [0.960, 0.970] | 0.747 | [0.722, 0.771] |  |
| pooled/DDI-DrugBank | sem_any|fda | 0.849 | [0.836, 0.862] | 0.489 | [0.446, 0.530] | 0.708 | [0.688, 0.728] | 0.819 | [0.796, 0.841] |  |
| pooled/DDI-DrugBank | sem_any|db | 0.296 | [0.280, 0.313] | 0.046 | [0.036, 0.055] | 0.557 | [0.545, 0.567] | 0.574 | [0.560, 0.587] |  |
| pooled/DDI-DrugBank | sem_majority|fda | 0.804 | [0.790, 0.819] | 0.241 | [0.198, 0.282] | 0.590 | [0.573, 0.606] | 0.759 | [0.721, 0.792] |  |
| pooled/DDI-DrugBank | sem_majority|db | 0.234 | [0.219, 0.249] | 0.017 | [0.009, 0.023] | 0.522 | [0.512, 0.530] | 0.554 | [0.532, 0.574] |  |
| pooled/DDI-DrugBank | fda|db | 0.378 | [0.360, 0.396] | 0.083 | [0.069, 0.097] | 0.595 | [0.581, 0.608] | 0.581 | [0.568, 0.593] |  |
| pooled/DDI-MedLine | sem_any|sem_majority | 0.813 | NA | 0.453 | NA | 0.895 | NA | 0.685 | NA | small |
| pooled/DDI-MedLine | sem_any|fda | 0.692 | [0.604, 0.791] | 0.247 | [0.032, 0.454] | 0.626 | [0.515, 0.738] | 0.621 | [0.515, 0.732] |  |
| pooled/DDI-MedLine | sem_any|db | 0.374 | NA | 0.016 | NA | 0.518 | NA | 0.512 | NA | small |
| pooled/DDI-MedLine | sem_majority|fda | 0.747 | NA | 0.220 | NA | 0.590 | NA | 0.683 | NA | small |
| pooled/DDI-MedLine | sem_majority|db | 0.253 | NA | 0.019 | NA | 0.526 | NA | 0.536 | NA | small |
| pooled/DDI-MedLine | fda|db | 0.440 | NA | 0.139 | NA | 0.664 | NA | 0.614 | NA | small |

## Pair view, variant db_both_resolved

| stratum | pairs | FDA decided | FDA undecided | SemEval any + | SemEval majority + | FDA + | DrugBank listed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 5337 | 2653 | 2684 | 383 | 179 | 609 | 2206 |
| train/DDI-DrugBank | 5199 | 2606 | 2593 | 367 | 177 | 599 | 2167 |
| train/DDI-MedLine | 187 | 70 | 117 | 17 | 3 | 20 | 61 |
| test/both | 973 | 468 | 505 | 38 | 26 | 126 | 407 |
| test/DDI-DrugBank | 934 | 443 | 491 | 27 | 20 | 119 | 386 |
| test/DDI-MedLine | 44 | 27 | 17 | 11 | 7 | 9 | 23 |
| pooled/both | 5912 | 2941 | 2971 | 412 | 194 | 660 | 2441 |
| pooled/DDI-DrugBank | 5750 | 2880 | 2870 | 385 | 187 | 646 | 2392 |
| pooled/DDI-MedLine | 230 | 96 | 134 | 28 | 10 | 28 | 83 |

| stratum | labels (first|second) | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | sem_any|sem_majority | 0.923 | [0.914, 0.933] | 0.600 | [0.553, 0.646] | 0.959 | [0.954, 0.964] | 0.734 | [0.710, 0.758] |  |
| train/both | sem_any|fda | 0.845 | [0.832, 0.859] | 0.498 | [0.459, 0.536] | 0.716 | [0.698, 0.735] | 0.810 | [0.787, 0.831] |  |
| train/both | sem_any|db | 0.299 | [0.282, 0.317] | 0.047 | [0.036, 0.057] | 0.561 | [0.548, 0.573] | 0.569 | [0.556, 0.583] |  |
| train/both | sem_majority|fda | 0.796 | [0.781, 0.811] | 0.232 | [0.193, 0.275] | 0.587 | [0.572, 0.605] | 0.745 | [0.712, 0.780] |  |
| train/both | sem_majority|db | 0.228 | [0.212, 0.245] | 0.019 | [0.013, 0.026] | 0.527 | [0.518, 0.536] | 0.560 | [0.542, 0.578] |  |
| train/both | fda|db | 0.383 | [0.365, 0.402] | 0.092 | [0.078, 0.106] | 0.611 | [0.598, 0.625] | 0.588 | [0.577, 0.599] |  |
| train/DDI-DrugBank | sem_any|sem_majority | 0.927 | [0.917, 0.937] | 0.615 | [0.570, 0.662] | 0.961 | [0.956, 0.966] | 0.741 | [0.718, 0.766] |  |
| train/DDI-DrugBank | sem_any|fda | 0.847 | [0.834, 0.860] | 0.498 | [0.459, 0.535] | 0.715 | [0.696, 0.734] | 0.815 | [0.793, 0.836] |  |
| train/DDI-DrugBank | sem_any|db | 0.296 | [0.279, 0.314] | 0.047 | [0.036, 0.057] | 0.561 | [0.548, 0.573] | 0.571 | [0.557, 0.585] |  |
| train/DDI-DrugBank | sem_majority|fda | 0.796 | [0.781, 0.812] | 0.234 | [0.196, 0.278] | 0.588 | [0.573, 0.605] | 0.746 | [0.712, 0.782] |  |
| train/DDI-DrugBank | sem_majority|db | 0.229 | [0.212, 0.244] | 0.019 | [0.013, 0.026] | 0.527 | [0.518, 0.536] | 0.560 | [0.541, 0.578] |  |
| train/DDI-DrugBank | fda|db | 0.383 | [0.364, 0.402] | 0.091 | [0.079, 0.106] | 0.611 | [0.597, 0.625] | 0.588 | [0.577, 0.600] |  |
| train/DDI-MedLine | sem_any|sem_majority | 0.800 | NA | 0.245 | NA | 0.896 | NA | 0.588 | NA | small |
| train/DDI-MedLine | sem_any|fda | 0.729 | NA | 0.304 | NA | 0.645 | NA | 0.661 | NA | small |
| train/DDI-MedLine | sem_any|db | 0.314 | NA | 0.008 | NA | 0.512 | NA | 0.507 | NA | small |
| train/DDI-MedLine | sem_majority|fda | 0.729 | NA | 0.107 | NA | 0.540 | NA | 0.699 | NA | small |
| train/DDI-MedLine | sem_majority|db | 0.171 | NA | 0.013 | NA | 0.525 | NA | 0.567 | NA | small |
| train/DDI-MedLine | fda|db | 0.414 | NA | 0.111 | NA | 0.664 | NA | 0.590 | NA | small |
| test/both | sem_any|sem_majority | 0.974 | [0.959, 0.987] | 0.799 | [0.681, 0.903] | 0.986 | [0.978, 0.993] | 0.842 | [0.768, 0.917] |  |
| test/both | sem_any|fda | 0.765 | [0.726, 0.801] | 0.234 | [0.141, 0.327] | 0.591 | [0.554, 0.631] | 0.740 | [0.661, 0.814] |  |
| test/both | sem_any|db | 0.199 | [0.160, 0.235] | 0.010 | [-0.010, 0.026] | 0.518 | [0.483, 0.546] | 0.528 | [0.471, 0.568] |  |
| test/both | sem_majority|fda | 0.761 | [0.720, 0.797] | 0.188 | [0.103, 0.280] | 0.571 | [0.538, 0.607] | 0.765 | [0.671, 0.841] |  |
| test/both | sem_majority|db | 0.177 | [0.143, 0.212] | 0.007 | [-0.008, 0.019] | 0.513 | [0.485, 0.535] | 0.528 | [0.468, 0.574] |  |
| test/both | fda|db | 0.382 | [0.342, 0.427] | 0.079 | [0.051, 0.112] | 0.617 | [0.580, 0.653] | 0.567 | [0.544, 0.592] |  |
| test/DDI-DrugBank | sem_any|sem_majority | 0.984 | [0.971, 0.995] | 0.843 | [0.702, 0.949] | 0.992 | [0.985, 0.998] | 0.870 | [0.780, 0.955] |  |
| test/DDI-DrugBank | sem_any|fda | 0.770 | [0.731, 0.808] | 0.224 | [0.134, 0.315] | 0.585 | [0.550, 0.622] | 0.791 | [0.708, 0.860] |  |
| test/DDI-DrugBank | sem_any|db | 0.181 | [0.144, 0.217] | 0.008 | [-0.007, 0.022] | 0.515 | [0.487, 0.539] | 0.529 | [0.474, 0.574] |  |
| test/DDI-DrugBank | sem_majority|fda | 0.758 | [0.718, 0.795] | 0.166 | [0.082, 0.253] | 0.561 | [0.530, 0.594] | 0.778 | [0.676, 0.860] |  |
| test/DDI-DrugBank | sem_majority|db | 0.165 | [0.131, 0.199] | 0.003 | [-0.012, 0.015] | 0.506 | [0.477, 0.528] | 0.515 | [0.443, 0.573] |  |
| test/DDI-DrugBank | fda|db | 0.379 | [0.336, 0.422] | 0.076 | [0.044, 0.109] | 0.614 | [0.572, 0.652] | 0.565 | [0.539, 0.590] |  |
| test/DDI-MedLine | sem_any|sem_majority | 0.852 | NA | 0.675 | NA | 0.900 | NA | 0.818 | NA | small |
| test/DDI-MedLine | sem_any|fda | 0.630 | NA | 0.211 | NA | 0.611 | NA | 0.602 | NA | small |
| test/DDI-MedLine | sem_any|db | 0.481 | NA | 0.083 | NA | 0.592 | NA | 0.548 | NA | small |
| test/DDI-MedLine | sem_majority|fda | 0.778 | NA | 0.471 | NA | 0.722 | NA | 0.757 | NA | small |
| test/DDI-MedLine | sem_majority|db | 0.407 | NA | 0.115 | NA | 0.652 | NA | 0.600 | NA | small |
| test/DDI-MedLine | fda|db | 0.481 | NA | 0.160 | NA | 0.696 | NA | 0.611 | NA | small |
| pooled/both | sem_any|sem_majority | 0.926 | [0.917, 0.936] | 0.605 | [0.559, 0.651] | 0.960 | [0.955, 0.966] | 0.735 | [0.712, 0.760] |  |
| pooled/both | sem_any|fda | 0.847 | [0.834, 0.860] | 0.493 | [0.454, 0.530] | 0.713 | [0.695, 0.732] | 0.808 | [0.786, 0.829] |  |
| pooled/both | sem_any|db | 0.295 | [0.279, 0.311] | 0.044 | [0.035, 0.054] | 0.558 | [0.546, 0.569] | 0.568 | [0.554, 0.581] |  |
| pooled/both | sem_majority|fda | 0.801 | [0.789, 0.816] | 0.239 | [0.203, 0.280] | 0.589 | [0.575, 0.607] | 0.752 | [0.720, 0.784] |  |
| pooled/both | sem_majority|db | 0.228 | [0.213, 0.243] | 0.018 | [0.012, 0.025] | 0.525 | [0.517, 0.534] | 0.558 | [0.542, 0.576] |  |
| pooled/both | fda|db | 0.379 | [0.361, 0.397] | 0.090 | [0.078, 0.103] | 0.609 | [0.596, 0.621] | 0.588 | [0.577, 0.598] |  |
| pooled/DDI-DrugBank | sem_any|sem_majority | 0.931 | [0.923, 0.941] | 0.621 | [0.575, 0.668] | 0.963 | [0.958, 0.968] | 0.743 | [0.719, 0.769] |  |
| pooled/DDI-DrugBank | sem_any|fda | 0.849 | [0.836, 0.862] | 0.493 | [0.454, 0.530] | 0.711 | [0.692, 0.730] | 0.817 | [0.796, 0.837] |  |
| pooled/DDI-DrugBank | sem_any|db | 0.290 | [0.274, 0.307] | 0.043 | [0.033, 0.053] | 0.557 | [0.545, 0.568] | 0.569 | [0.555, 0.583] |  |
| pooled/DDI-DrugBank | sem_majority|fda | 0.802 | [0.788, 0.816] | 0.238 | [0.202, 0.277] | 0.589 | [0.575, 0.605] | 0.755 | [0.723, 0.787] |  |
| pooled/DDI-DrugBank | sem_majority|db | 0.226 | [0.211, 0.241] | 0.017 | [0.011, 0.024] | 0.524 | [0.516, 0.533] | 0.556 | [0.538, 0.575] |  |
| pooled/DDI-DrugBank | fda|db | 0.378 | [0.361, 0.397] | 0.089 | [0.077, 0.103] | 0.608 | [0.595, 0.621] | 0.587 | [0.577, 0.598] |  |
| pooled/DDI-MedLine | sem_any|sem_majority | 0.812 | NA | 0.440 | NA | 0.895 | NA | 0.679 | NA | small |
| pooled/DDI-MedLine | sem_any|fda | 0.708 | [0.615, 0.792] | 0.294 | [0.101, 0.485] | 0.647 | [0.551, 0.744] | 0.647 | [0.549, 0.751] |  |
| pooled/DDI-MedLine | sem_any|db | 0.365 | NA | 0.025 | NA | 0.535 | NA | 0.520 | NA | small |
| pooled/DDI-MedLine | sem_majority|fda | 0.750 | NA | 0.254 | NA | 0.603 | NA | 0.728 | NA | small |
| pooled/DDI-MedLine | sem_majority|db | 0.240 | NA | 0.036 | NA | 0.560 | NA | 0.576 | NA | small |
| pooled/DDI-MedLine | fda|db | 0.427 | NA | 0.121 | NA | 0.669 | NA | 0.596 | NA | small |

## Instance view, primary

| stratum | instances | labels | agreement | 95% | kappa | 95% | AUROC first for second | 95% | AUROC second for first | 95% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train/both | 4371 | sem_instance|fda | 0.693 | [0.623, 0.747] | 0.239 | [0.196, 0.266] | 0.603 | [0.588, 0.615] | 0.732 | [0.683, 0.770] |
| train/both | 4371 | sem_instance|db | 0.242 | [0.202, 0.281] | 0.023 | [0.012, 0.037] | 0.538 | [0.522, 0.555] | 0.543 | [0.524, 0.562] |
| train/both | 4371 | fda|db | 0.488 | [0.416, 0.562] | 0.134 | [0.091, 0.186] | 0.666 | [0.632, 0.707] | 0.585 | [0.564, 0.608] |
| train/DDI-DrugBank | 4096 | sem_instance|fda | 0.691 | [0.615, 0.747] | 0.238 | [0.193, 0.269] | 0.603 | [0.588, 0.615] | 0.735 | [0.682, 0.775] |
| train/DDI-DrugBank | 4096 | sem_instance|db | 0.240 | [0.200, 0.280] | 0.024 | [0.012, 0.037] | 0.540 | [0.523, 0.556] | 0.545 | [0.526, 0.565] |
| train/DDI-DrugBank | 4096 | fda|db | 0.488 | [0.411, 0.571] | 0.131 | [0.086, 0.186] | 0.664 | [0.627, 0.706] | 0.582 | [0.560, 0.607] |
| train/DDI-MedLine | 275 | sem_instance|fda | 0.724 | [0.625, 0.790] | 0.253 | [0.139, 0.367] | 0.607 | [0.560, 0.661] | 0.696 | [0.609, 0.774] |
| train/DDI-MedLine | 275 | sem_instance|db | 0.269 | [0.190, 0.373] | 0.013 | [-0.024, 0.064] | 0.518 | [0.466, 0.574] | 0.521 | [0.461, 0.582] |
| train/DDI-MedLine | 275 | fda|db | 0.487 | [0.405, 0.619] | 0.173 | [0.108, 0.301] | 0.692 | [0.647, 0.762] | 0.623 | [0.585, 0.676] |
| test/both | 647 | sem_instance|fda | 0.686 | [0.600, 0.751] | 0.148 | [0.063, 0.244] | 0.561 | [0.526, 0.605] | 0.669 | [0.584, 0.745] |
| test/both | 647 | sem_instance|db | 0.179 | [0.140, 0.234] | 0.001 | [-0.020, 0.019] | 0.502 | [0.457, 0.539] | 0.502 | [0.449, 0.545] |
| test/both | 647 | fda|db | 0.425 | [0.371, 0.498] | 0.080 | [0.043, 0.121] | 0.628 | [0.576, 0.672] | 0.556 | [0.528, 0.579] |
| test/DDI-DrugBank | 575 | sem_instance|fda | 0.689 | [0.593, 0.758] | 0.153 | [0.071, 0.253] | 0.562 | [0.530, 0.607] | 0.752 | [0.654, 0.832] |
| test/DDI-DrugBank | 575 | sem_instance|db | 0.151 | [0.116, 0.204] | -0.005 | [-0.027, 0.012] | 0.489 | [0.438, 0.525] | 0.480 | [0.395, 0.539] |
| test/DDI-DrugBank | 575 | fda|db | 0.431 | [0.374, 0.514] | 0.079 | [0.038, 0.123] | 0.625 | [0.567, 0.673] | 0.554 | [0.523, 0.580] |
| test/DDI-MedLine | 72 | sem_instance|fda | 0.667 | NA | 0.196 | NA | 0.605 | NA | 0.594 | NA |
| test/DDI-MedLine | 72 | sem_instance|db | 0.403 | NA | 0.067 | NA | 0.609 | NA | 0.550 | NA |
| test/DDI-MedLine | 72 | fda|db | 0.375 | NA | 0.086 | NA | 0.648 | NA | 0.575 | NA |
| pooled/both | 5018 | sem_instance|fda | 0.692 | [0.628, 0.738] | 0.228 | [0.192, 0.257] | 0.598 | [0.585, 0.610] | 0.726 | [0.680, 0.758] |
| pooled/both | 5018 | sem_instance|db | 0.234 | [0.202, 0.268] | 0.020 | [0.011, 0.032] | 0.533 | [0.520, 0.549] | 0.539 | [0.521, 0.558] |
| pooled/both | 5018 | fda|db | 0.480 | [0.422, 0.547] | 0.127 | [0.092, 0.171] | 0.661 | [0.632, 0.697] | 0.581 | [0.563, 0.601] |
| pooled/DDI-DrugBank | 4671 | sem_instance|fda | 0.691 | [0.620, 0.740] | 0.229 | [0.191, 0.259] | 0.598 | [0.585, 0.610] | 0.736 | [0.687, 0.770] |
| pooled/DDI-DrugBank | 4671 | sem_instance|db | 0.229 | [0.197, 0.264] | 0.020 | [0.010, 0.032] | 0.534 | [0.520, 0.551] | 0.540 | [0.521, 0.559] |
| pooled/DDI-DrugBank | 4671 | fda|db | 0.481 | [0.417, 0.553] | 0.124 | [0.088, 0.172] | 0.659 | [0.628, 0.697] | 0.579 | [0.560, 0.601] |
| pooled/DDI-MedLine | 347 | sem_instance|fda | 0.712 | [0.627, 0.773] | 0.233 | [0.113, 0.348] | 0.603 | [0.550, 0.657] | 0.651 | [0.579, 0.717] |
| pooled/DDI-MedLine | 347 | sem_instance|db | 0.297 | [0.229, 0.388] | 0.028 | [-0.004, 0.078] | 0.538 | [0.494, 0.594] | 0.535 | [0.495, 0.576] |
| pooled/DDI-MedLine | 347 | fda|db | 0.464 | [0.391, 0.555] | 0.152 | [0.102, 0.235] | 0.683 | [0.642, 0.733] | 0.613 | [0.581, 0.651] |

## Cross-tabulations, primary, pooled, both sources

SemEval any, FDA, DrugBank (digits in that order):

| cell | pairs |
| --- | --- |
| 000 | 497 |
| 001 | 1717 |
| 010 | 25 |
| 011 | 334 |
| 100 | 20 |
| 101 | 86 |
| 110 | 11 |
| 111 | 304 |

SemEval majority, FDA, DrugBank:

| cell | pairs |
| --- | --- |
| 000 | 507 |
| 001 | 1751 |
| 010 | 27 |
| 011 | 508 |
| 100 | 10 |
| 101 | 52 |
| 110 | 9 |
| 111 | 130 |

