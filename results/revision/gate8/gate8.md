# Gate 8: can a validated-label Amendment 8 on about 60 drugs reach a decision?

Status: synthetic power simulation, post hoc and exploratory; criteria.json was written before any run; changes no preregistered decision.

Scores are synthetic. No model score of any tested system is used; the only real score is the DrugBank lookup, the kappa reference. Null scorer: noise (true kappa 0). Positive control: DrugBank blend on the noise base calibrated to true kappa 0.6. 200 reps per point, 300 two-way bootstrap draws per rep.

Rules: (a) H8 supported if the one-sided 95% upper bound of kappa is at most K, power at true kappa 0 at least 0.80; (b) control detected if the kappa 95% lower bound (2.5th percentile) is at least 0.25, power at true kappa 0.6 at least 0.80. GO needs both.

## Verdict

| K | verdict | governing designs passing (validated_rule) | optimistic bound passing | note |
| --- | --- | --- | --- | --- |
| 0.25 | NO-GO | none | none | no design passes, not even the optimistic upper bound |
| 0.33 | NO-GO | none | none | no design passes, not even the optimistic upper bound |
| 0.5 | NO-GO | none | none | no design passes, not even the optimistic upper bound |

## Power

| design | labels | rows (per realisation) | informative drugs | DrugBank within | P(a) K=0.25 | P(a) K=0.33 | P(a) K=0.50 | mean null upper bound | P(b) | P(b) one-sided | mean control lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel48 | as_is | 438 | 48 | 0.729 | 0.075 | 0.135 | 0.515 | 0.518 | 0.135 | 0.230 | 0.031 |
| novel48 | validated_rule | 437 | 48 | 0.727 | 0.095 | 0.165 | 0.460 | 0.523 | 0.110 | 0.210 | 0.002 |
| novel48 | validated_rule_plus_db (OPTIMISTIC UPPER BOUND, uses DrugBank) | 331 | 43 | 0.914 | 0.195 | 0.475 | 0.940 | 0.339 | 0.480 | 0.705 | 0.234 |
| novel60 | as_is | 553, 537, 544 | 60, 60, 60 | 0.748, 0.723, 0.726 | 0.092 | 0.232 | 0.652 | 0.444 | 0.180 | 0.377 | 0.100 |
| novel60 | validated_rule | 551, 536, 543 | 60, 60, 60 | 0.746, 0.721, 0.725 | 0.115 | 0.232 | 0.632 | 0.447 | 0.147 | 0.333 | 0.090 |
| novel60 | validated_rule_plus_db (OPTIMISTIC UPPER BOUND, uses DrugBank) | 427, 406, 415 | 54, 54, 54 | 0.916, 0.924, 0.917 | 0.333 | 0.670 | 0.982 | 0.290 | 0.622 | 0.833 | 0.281 |
| older_clean60 | as_is | 829, 861, 869 | 60, 60, 60 | 0.645, 0.655, 0.612 | 0.052 | 0.108 | 0.297 | 0.635 | 0.057 | 0.145 | -0.145 |
| older_clean60 | validated_rule | 811, 847, 850 | 56, 57, 57 | 0.657, 0.651, 0.610 | 0.040 | 0.088 | 0.300 | 0.655 | 0.053 | 0.148 | -0.161 |
| older_clean60 | validated_rule_plus_db (OPTIMISTIC UPPER BOUND, uses DrugBank) | 577, 650, 592 | 53, 54, 51 | 0.828, 0.796, 0.811 | 0.195 | 0.445 | 0.875 | 0.355 | 0.372 | 0.613 | 0.205 |

Powers pool the reps of all realisations (seeds 1, 2, 3 for the 60-drug designs); per-realisation values are in gate8.json.

## DrugBank within-drug ceiling on the existing cohorts

| cohort | labels | rows | positives | drugs | DrugBank within | 95% CI | at least 0.80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| novel | as_is | 438 | 148 | 48 | 0.729 | [0.642, 0.808] | no |
| novel | validated_rule | 437 | 147 | 48 | 0.727 | [0.641, 0.808] | no |
| novel | validated_rule_plus_db (OPTIMISTIC UPPER BOUND, uses DrugBank) | 331 | 147 | 48 | 0.914 | [0.820, 0.982] | yes |
| older_clean | as_is | 1832 | 599 | 128 | 0.641 | [0.595, 0.689] | no |
| older_clean | validated_rule | 1794 | 561 | 128 | 0.644 | [0.596, 0.695] | no |
| older_clean | validated_rule_plus_db (OPTIMISTIC UPPER BOUND, uses DrugBank) | 1297 | 561 | 128 | 0.813 | [0.741, 0.883] | yes |

A ceiling of at least 0.80 would mean the kappa denominator widens. On the optimistic variant the ceiling is raised by construction, because the negatives it drops are exactly those DrugBank scores as positive.
