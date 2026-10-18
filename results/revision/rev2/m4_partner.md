# M4: partner anti-correlation

Status: post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision.

## (a) SemEval binary F1 against within-drug AUROC, by input format

F1 from `results/revision/post8/e9.json`; tier A AUROC from `results/revision/amend7/e9.json`, C-auto from post8. Percentile bootstrap over checkpoints (10,000 draws, seed 42); permutation p from 10,000 permutations. With 10 checkpoints per format the interval is wide, and it ignores the within-checkpoint bootstrap uncertainty of each AUROC.

| tier | cohort | format | checkpoints | rho | 95% CI | 90% CI | share of draws < 0 | permutation p | AUROC range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | older_primary | marker | 10 | -0.479 | [-0.889, 0.274] | [-0.824, 0.163] | 0.903 | 0.171 | [0.424, 0.507] |
| A | older_primary | pair | 10 | -0.309 | [-0.888, 0.447] | [-0.826, 0.329] | 0.791 | 0.387 | [0.424, 0.508] |
| A | older_primary | all | 20 | -0.161 | [-0.635, 0.358] | [-0.568, 0.281] | 0.733 | 0.492 | [0.424, 0.508] |
| A | novel | marker | 10 | -0.261 | [-0.811, 0.503] | [-0.765, 0.362] | 0.759 | 0.466 | [0.469, 0.533] |
| A | novel | pair | 10 | -0.030 | [-0.673, 0.696] | [-0.593, 0.580] | 0.520 | 0.946 | [0.460, 0.520] |
| A | novel | all | 20 | -0.016 | [-0.511, 0.476] | [-0.442, 0.402] | 0.521 | 0.947 | [0.460, 0.533] |
| C-auto | older_primary | marker | 10 | -0.539 | [-0.907, 0.195] | [-0.852, 0.057] | 0.939 | 0.117 | [0.414, 0.501] |
| C-auto | older_primary | pair | 10 | -0.406 | [-0.961, 0.396] | [-0.922, 0.242] | 0.847 | 0.244 | [0.415, 0.514] |
| C-auto | older_primary | all | 20 | -0.167 | [-0.636, 0.365] | [-0.564, 0.279] | 0.748 | 0.466 | [0.414, 0.514] |
| C-auto | novel | marker | 10 | -0.297 | [-0.912, 0.538] | [-0.840, 0.374] | 0.770 | 0.406 | [0.470, 0.532] |
| C-auto | novel | pair | 10 | -0.030 | [-0.704, 0.673] | [-0.635, 0.572] | 0.512 | 0.937 | [0.457, 0.518] |
| C-auto | novel | all | 20 | 0.007 | [-0.517, 0.512] | [-0.434, 0.437] | 0.488 | 0.980 | [0.457, 0.532] |

## (b) Within-drug AUROC, partner-prior-adjusted within-drug AUROC and tetrad AUROC

Tier A labels. Partner prior: share of vocabulary Drug Interactions sections naming the partner (label-free, experiment 7 feature iii2). Adjusted: score residualized on the prior within OOD drug (experiment 7 `partial`). Tetrad: doubly matched tetrad AUROC (post7). Two-way cluster bootstrap over OOD drugs and partners, 1,000 draws, seeds 1042 Novel and 42 Older-clean; raw and adjusted share draws. Models on the logit scale, DrugBank on 0/1. Panel checkpoints are single seeds; b2mixed averages 5 seeds.

### novel (n = 438, 148 positive, 48 drugs, 74 partners, 152 tetrads; prior alone within-drug AUROC 0.522)

| system | within | 95% CI | adjusted | 95% CI | adjusted - within | 95% CI | slope | tetrad | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed BiomedBERT | 0.523 | [0.397, 0.650] | 0.511 | [0.380, 0.638] | -0.012 | [-0.073, 0.043] | 2.56 | 0.480 | [0.120, 0.825] |
| Qwen names only | 0.579 | [0.440, 0.713] | 0.590 | [0.458, 0.723] | 0.012 | [-0.085, 0.111] | 15.9 | 0.664 | [0.297, 0.940] |
| DrugBank lookup | 0.729 | [0.642, 0.808] | 0.722 | [0.584, 0.843] | -0.007 | [-0.108, 0.090] | 0.501 | 0.885 | [0.702, 1.000] |
| panel bertbase-marker | 0.481 | [0.353, 0.600] | 0.480 | [0.341, 0.610] | -0.001 | [-0.035, 0.038] | 0.775 | 0.395 | [0.092, 0.776] |
| panel bertbase-pair | 0.476 | [0.347, 0.600] | 0.482 | [0.341, 0.613] | 0.007 | [-0.062, 0.079] | -2.12 | 0.474 | [0.112, 0.828] |
| panel biobert-marker | 0.473 | [0.340, 0.607] | 0.476 | [0.348, 0.610] | 0.003 | [-0.051, 0.056] | -0.247 | 0.467 | [0.134, 0.855] |
| panel biobert-pair | 0.481 | [0.351, 0.614] | 0.480 | [0.350, 0.614] | -0.001 | [-0.009, 0.000] | 0.062 | 0.474 | [0.076, 0.873] |
| panel biolinkbert-marker | 0.469 | [0.351, 0.597] | 0.469 | [0.344, 0.597] | 0.000 | [-0.068, 0.070] | 5.87 | 0.507 | [0.138, 0.844] |
| panel biolinkbert-pair | 0.517 | [0.386, 0.650] | 0.520 | [0.389, 0.646] | 0.004 | [-0.088, 0.095] | 3.69 | 0.553 | [0.197, 0.875] |
| panel biomedbert_abs-marker | 0.529 | [0.410, 0.657] | 0.551 | [0.422, 0.679] | 0.022 | [-0.055, 0.098] | 2.93 | 0.526 | [0.184, 0.852] |
| panel biomedbert_abs-pair | 0.520 | [0.379, 0.669] | 0.506 | [0.364, 0.655] | -0.015 | [-0.069, 0.030] | 0.579 | 0.539 | [0.173, 0.875] |
| panel biomedbert_full-marker | 0.475 | [0.320, 0.616] | 0.474 | [0.320, 0.615] | -0.001 | [-0.034, 0.033] | -0.0924 | 0.592 | [0.137, 0.882] |
| panel biomedbert_full-pair | 0.491 | [0.364, 0.629] | 0.494 | [0.371, 0.638] | 0.003 | [-0.052, 0.061] | 0.976 | 0.566 | [0.200, 0.899] |
| panel clinicalbert-marker | 0.507 | [0.379, 0.647] | 0.507 | [0.371, 0.649] | 0.000 | [-0.058, 0.060] | -1.61 | 0.546 | [0.165, 0.825] |
| panel clinicalbert-pair | 0.494 | [0.356, 0.631] | 0.497 | [0.358, 0.630] | 0.003 | [-0.044, 0.055] | -1.36 | 0.507 | [0.130, 0.820] |
| panel deberta-marker | 0.530 | [0.394, 0.654] | 0.535 | [0.405, 0.659] | 0.005 | [-0.030, 0.038] | 0.192 | 0.480 | [0.115, 0.846] |
| panel deberta-pair | 0.510 | [0.385, 0.629] | 0.520 | [0.399, 0.640] | 0.011 | [0.000, 0.037] | 0.356 | 0.539 | [0.200, 0.894] |
| panel electra-marker | 0.483 | [0.350, 0.613] | 0.474 | [0.341, 0.610] | -0.009 | [-0.067, 0.046] | 0.384 | 0.414 | [0.116, 0.820] |
| panel electra-pair | 0.460 | [0.338, 0.584] | 0.468 | [0.344, 0.595] | 0.008 | [-0.020, 0.039] | -0.254 | 0.447 | [0.100, 0.815] |
| panel roberta-marker | 0.474 | [0.347, 0.606] | 0.473 | [0.349, 0.605] | -0.001 | [-0.017, 0.019] | 0.109 | 0.441 | [0.093, 0.801] |
| panel roberta-pair | 0.469 | [0.325, 0.613] | 0.465 | [0.328, 0.611] | -0.004 | [-0.045, 0.039] | 1.19 | 0.395 | [0.074, 0.737] |
| panel scibert-marker | 0.533 | [0.406, 0.665] | 0.552 | [0.422, 0.681] | 0.019 | [-0.038, 0.080] | -0.826 | 0.645 | [0.273, 0.959] |
| panel scibert-pair | 0.485 | [0.346, 0.636] | 0.483 | [0.344, 0.634] | -0.001 | [-0.014, 0.010] | -0.0924 | 0.447 | [0.108, 0.823] |

Panel (20 checkpoints): within min 0.460, median 0.484, max 0.533, 95% upper < 0.5 in 0, 95% lower > 0.5 in 0; partner_adjusted_within min 0.465, median 0.483, max 0.552, 95% upper < 0.5 in 0, 95% lower > 0.5 in 0; tetrad min 0.395, median 0.493, max 0.645, 95% upper < 0.5 in 0, 95% lower > 0.5 in 0; adjusted_minus_raw min -0.015, median 0.001, max 0.022.

### older_clean (n = 1832, 599 positive, 128 drugs, 212 partners, 1975 tetrads; prior alone within-drug AUROC 0.506)

| system | within | 95% CI | adjusted | 95% CI | adjusted - within | 95% CI | slope | tetrad | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed BiomedBERT | 0.452 | [0.389, 0.518] | 0.447 | [0.385, 0.511] | -0.005 | [-0.031, 0.024] | 3.84 | 0.375 | [0.233, 0.541] |
| Qwen names only | 0.602 | [0.533, 0.667] | 0.621 | [0.554, 0.691] | 0.019 | [-0.028, 0.063] | 18.7 | 0.758 | [0.619, 0.882] |
| DrugBank lookup | 0.641 | [0.595, 0.689] | 0.640 | [0.567, 0.715] | -0.002 | [-0.050, 0.051] | 0.486 | 0.691 | [0.577, 0.802] |
| panel bertbase-marker | 0.488 | [0.429, 0.544] | 0.490 | [0.431, 0.547] | 0.003 | [-0.020, 0.025] | 1.47 | 0.510 | [0.365, 0.629] |
| panel bertbase-pair | 0.480 | [0.422, 0.537] | 0.482 | [0.422, 0.545] | 0.003 | [-0.012, 0.019] | -0.685 | 0.467 | [0.320, 0.610] |
| panel biobert-marker | 0.499 | [0.439, 0.559] | 0.499 | [0.436, 0.559] | 0.000 | [-0.012, 0.012] | 0.102 | 0.508 | [0.372, 0.649] |
| panel biobert-pair | 0.476 | [0.408, 0.536] | 0.479 | [0.416, 0.542] | 0.003 | [-0.019, 0.026] | 1.68 | 0.457 | [0.323, 0.602] |
| panel biolinkbert-marker | 0.435 | [0.367, 0.498] | 0.439 | [0.374, 0.504] | 0.004 | [-0.022, 0.034] | 5.16 | 0.396 | [0.266, 0.538] |
| panel biolinkbert-pair | 0.465 | [0.402, 0.522] | 0.446 | [0.384, 0.509] | -0.018 | [-0.063, 0.027] | 5.83 | 0.417 | [0.288, 0.557] |
| panel biomedbert_abs-marker | 0.449 | [0.384, 0.515] | 0.449 | [0.389, 0.511] | 0.001 | [-0.032, 0.035] | 2.51 | 0.348 | [0.226, 0.501] |
| panel biomedbert_abs-pair | 0.481 | [0.416, 0.545] | 0.480 | [0.414, 0.544] | -0.001 | [-0.011, 0.009] | 0.253 | 0.456 | [0.303, 0.597] |
| panel biomedbert_full-marker | 0.432 | [0.370, 0.498] | 0.431 | [0.371, 0.498] | -0.001 | [-0.007, 0.006] | -0.0294 | 0.339 | [0.199, 0.476] |
| panel biomedbert_full-pair | 0.472 | [0.401, 0.537] | 0.477 | [0.412, 0.547] | 0.006 | [-0.036, 0.054] | 3.13 | 0.441 | [0.277, 0.622] |
| panel clinicalbert-marker | 0.492 | [0.434, 0.547] | 0.495 | [0.439, 0.549] | 0.003 | [-0.016, 0.021] | -1.18 | 0.510 | [0.371, 0.635] |
| panel clinicalbert-pair | 0.481 | [0.426, 0.541] | 0.482 | [0.426, 0.544] | 0.002 | [-0.018, 0.019] | -1.54 | 0.498 | [0.354, 0.622] |
| panel deberta-marker | 0.512 | [0.448, 0.573] | 0.511 | [0.451, 0.571] | -0.001 | [-0.020, 0.018] | 0.285 | 0.498 | [0.359, 0.628] |
| panel deberta-pair | 0.428 | [0.367, 0.488] | 0.429 | [0.370, 0.490] | 0.001 | [-0.010, 0.013] | 0.606 | 0.326 | [0.201, 0.463] |
| panel electra-marker | 0.487 | [0.424, 0.546] | 0.484 | [0.420, 0.543] | -0.004 | [-0.032, 0.027] | 0.513 | 0.544 | [0.375, 0.697] |
| panel electra-pair | 0.506 | [0.450, 0.566] | 0.508 | [0.451, 0.564] | 0.002 | [-0.016, 0.020] | -0.51 | 0.514 | [0.369, 0.672] |
| panel roberta-marker | 0.478 | [0.425, 0.533] | 0.474 | [0.421, 0.528] | -0.004 | [-0.017, 0.010] | 0.354 | 0.446 | [0.311, 0.591] |
| panel roberta-pair | 0.462 | [0.403, 0.519] | 0.462 | [0.403, 0.520] | -0.000 | [-0.011, 0.009] | 1.02 | 0.447 | [0.310, 0.577] |
| panel scibert-marker | 0.474 | [0.410, 0.536] | 0.475 | [0.409, 0.536] | 0.001 | [-0.011, 0.013] | -0.172 | 0.429 | [0.295, 0.586] |
| panel scibert-pair | 0.457 | [0.394, 0.516] | 0.453 | [0.393, 0.513] | -0.004 | [-0.020, 0.011] | 0.688 | 0.443 | [0.303, 0.580] |

Panel (20 checkpoints): within min 0.428, median 0.477, max 0.512, 95% upper < 0.5 in 3, 95% lower > 0.5 in 0; partner_adjusted_within min 0.429, median 0.478, max 0.511, 95% upper < 0.5 in 2, 95% lower > 0.5 in 0; tetrad min 0.326, median 0.452, max 0.544, 95% upper < 0.5 in 2, 95% lower > 0.5 in 0; adjusted_minus_raw min -0.018, median 0.001, max 0.006.

## Reproduction checks

| check | reference | got | reference 95% | got 95% | match |
| --- | --- | --- | --- | --- | --- |
| exp7 iii2 partialled, novel, b2mixed BiomedBERT | 0.511 | 0.511 | [0.380, 0.638] | [0.380, 0.638] | True |
| exp7 iii2 partialled, novel, Qwen names only | 0.590 | 0.590 | [0.458, 0.723] | [0.458, 0.723] | True |
| exp7 iii2 partialled, novel, DrugBank lookup | 0.722 | 0.722 | [0.584, 0.843] | [0.584, 0.843] | True |
| post7 tetrad, novel, b2mixed BiomedBERT | 0.480 | 0.480 | [0.120, 0.825] | [0.120, 0.825] | True |
| post7 tetrad, novel, Qwen names only | 0.664 | 0.664 | [0.297, 0.940] | [0.297, 0.940] | True |
| post7 tetrad, novel, DrugBank lookup | 0.885 | 0.885 | [0.702, 1.000] | [0.702, 1.000] | True |
| exp7 iii2 partialled, older_clean, b2mixed BiomedBERT | 0.447 | 0.447 | [0.385, 0.511] | [0.385, 0.511] | True |
| exp7 iii2 partialled, older_clean, Qwen names only | 0.621 | 0.621 | [0.554, 0.691] | [0.554, 0.691] | True |
| exp7 iii2 partialled, older_clean, DrugBank lookup | 0.640 | 0.640 | [0.567, 0.715] | [0.567, 0.715] | True |
| post7 tetrad, older_clean, b2mixed BiomedBERT | 0.375 | 0.375 | [0.233, 0.541] | [0.233, 0.541] | True |
| post7 tetrad, older_clean, Qwen names only | 0.758 | 0.758 | [0.619, 0.882] | [0.619, 0.882] | True |
| post7 tetrad, older_clean, DrugBank lookup | 0.691 | 0.691 | [0.577, 0.802] | [0.577, 0.802] | True |
