# D6: sentence dependence of the entity-marker models

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

Seeds present: [42, 1, 2, 3, 4] (complete: True). SemEval 2013 test, 2810 pairs, 371 positive. Pooled AUROC is the positive-class probability against the binary label; binary F1 is `preds != 0` against the binary label. Seed mean = mean of the per-seed value; the AUROC of the seed-mean probability is listed separately. Intervals: sentence-cluster bootstrap, 1000 draws, seed 42, one resample for all seeds and inputs, 95% percentile on the seed mean.

| input | AUROC seed mean | 95% CI | binary F1 seed mean | 95% CI | AUROC of seed-mean p | 95% CI | marker fallback rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sentence | 0.977 | [0.965, 0.986] | 0.845 | [0.805, 0.883] | 0.984 | [0.975, 0.990] | 14 |
| masked | 0.958 | [0.941, 0.971] | 0.523 | [0.461, 0.594] | 0.968 | [0.954, 0.980] | 14 |
| swap_vocab | 0.918 | [0.889, 0.942] | 0.670 | [0.617, 0.726] | 0.921 | [0.891, 0.945] | 375 |
| swap_novel | 0.916 | [0.887, 0.940] | 0.663 | [0.611, 0.720] | 0.917 | [0.886, 0.943] | 376 |
| swap_pseudo | 0.920 | [0.892, 0.944] | 0.681 | [0.627, 0.734] | 0.922 | [0.892, 0.946] | 376 |
| names | 0.610 | [0.573, 0.647] | 0.000 | [0.000, 0.000] | 0.640 | [0.600, 0.678] | 0 |

## Difference from the original marked sentence (seed mean, paired draws)

| input | AUROC difference | 95% CI | binary F1 difference | 95% CI |
| --- | --- | --- | --- | --- |
| masked | -0.019 | [-0.027, -0.012] | -0.321 | [-0.374, -0.266] |
| swap_vocab | -0.060 | [-0.086, -0.039] | -0.174 | [-0.219, -0.130] |
| swap_novel | -0.061 | [-0.089, -0.039] | -0.181 | [-0.225, -0.137] |
| swap_pseudo | -0.058 | [-0.083, -0.037] | -0.164 | [-0.206, -0.122] |
| names | -0.367 | [-0.402, -0.329] | -0.845 | [-0.883, -0.805] |

## Swap inputs against the original sentence (seed mean)

| input | flip rate of the binary prediction | mean absolute change in probability |
| --- | --- | --- |
| swap_vocab | 0.068 | 0.068 |
| swap_novel | 0.071 | 0.071 |
| swap_pseudo | 0.063 | 0.063 |

## Per seed

| seed | input | AUROC | binary F1 | flip rate | mean abs dp |
| --- | --- | --- | --- | --- | --- |
| 42 | sentence | 0.978 | 0.825 | NA | NA |
| 42 | masked | 0.959 | 0.548 | NA | NA |
| 42 | swap_vocab | 0.926 | 0.688 | 0.063 | 0.062 |
| 42 | swap_novel | 0.923 | 0.674 | 0.064 | 0.064 |
| 42 | swap_pseudo | 0.926 | 0.690 | 0.063 | 0.062 |
| 42 | names | 0.594 | 0.000 | NA | NA |
| 1 | sentence | 0.977 | 0.842 | NA | NA |
| 1 | masked | 0.964 | 0.353 | NA | NA |
| 1 | swap_vocab | 0.928 | 0.671 | 0.057 | 0.057 |
| 1 | swap_novel | 0.928 | 0.679 | 0.058 | 0.057 |
| 1 | swap_pseudo | 0.931 | 0.667 | 0.059 | 0.058 |
| 1 | names | 0.598 | 0.000 | NA | NA |
| 2 | sentence | 0.982 | 0.870 | NA | NA |
| 2 | masked | 0.961 | 0.465 | NA | NA |
| 2 | swap_vocab | 0.924 | 0.685 | 0.074 | 0.074 |
| 2 | swap_novel | 0.921 | 0.686 | 0.072 | 0.073 |
| 2 | swap_pseudo | 0.925 | 0.703 | 0.065 | 0.066 |
| 2 | names | 0.611 | 0.000 | NA | NA |
| 3 | sentence | 0.977 | 0.847 | NA | NA |
| 3 | masked | 0.963 | 0.717 | NA | NA |
| 3 | swap_vocab | 0.901 | 0.637 | 0.085 | 0.086 |
| 3 | swap_novel | 0.897 | 0.614 | 0.095 | 0.095 |
| 3 | swap_pseudo | 0.903 | 0.657 | 0.073 | 0.075 |
| 3 | names | 0.641 | 0.000 | NA | NA |
| 4 | sentence | 0.972 | 0.839 | NA | NA |
| 4 | masked | 0.946 | 0.533 | NA | NA |
| 4 | swap_vocab | 0.910 | 0.669 | 0.063 | 0.063 |
| 4 | swap_novel | 0.911 | 0.663 | 0.064 | 0.064 |
| 4 | swap_pseudo | 0.915 | 0.686 | 0.055 | 0.055 |
| 4 | names | 0.606 | 0.000 | NA | NA |

## Five-class micro F1 on the original sentence (as `m10_semeval_standard`)

| seed | micro F1 (2810 pairs) | 95% CI | official-set bound | precision | recall | binary F1 |
| --- | --- | --- | --- | --- | --- | --- |
| 42 | 0.778 | [0.718, 0.832] | 0.425 | 0.791 | 0.765 | 0.825 |
| 1 | 0.787 | [0.730, 0.836] | 0.422 | 0.836 | 0.744 | 0.842 |
| 2 | 0.835 | [0.784, 0.876] | 0.456 | 0.845 | 0.825 | 0.870 |
| 3 | 0.807 | [0.753, 0.856] | 0.435 | 0.844 | 0.774 | 0.847 |
| 4 | 0.783 | [0.723, 0.833] | 0.422 | 0.820 | 0.749 | 0.839 |

## Reproduction against the stored R2a files

| seed | stored file found | max abs gap, sentence | argmax identical |
| --- | --- | --- | --- |
| 42 | True | 4.000000000004e-06 | True |
| 1 | True | 1.0000000000287557e-06 | True |
| 2 | True | 2.000000000002e-06 | True |
| 3 | True | 1.000000000001e-06 | True |
| 4 | True | 1.999999999946489e-06 | True |

Rows for which the entity markers could not be placed fall back to the template followed by the sentence; their counts are in the first table. Swapped rows keep the gold label of the original pair.

