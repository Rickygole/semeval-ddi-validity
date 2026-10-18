# M8: coverage simulations reconciled, and the criteria-backed post hoc results

Status: post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision.

## Reconciled statement

Both simulations find the two-way cluster bootstrap conservative on these designs. On a common scale (mean 90% half-width divided by the calibrated 1.645 x SD) the two-way interval is 1.533 to 2.281 times nominal in the 300-replicate sensitivity run and 1.546 to 2.228 times nominal over every design of the 1000-replicate post7 run (1.546 to 2.186 on Older-clean tier A); 90% coverage is 0.989 to 1.000. The 2.52 to 3.75 figure is the same quantity before division by 1.645. The one-way drug bootstrap is near nominal in both (0.978 to 1.129 and 0.933 to 1.207). In both simulations partner effects are independent of the labels, which the real partner-matched design is not.

## Two-way bootstrap by cell

| cohort | tier | sensitivity half-width / SD | sensitivity ratio | post7 half-width / SD | post7 ratio | sensitivity 90% coverage | post7 90% coverage | scenarios (sens / post7) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel | A | [2.893, 3.655] | [1.759, 2.222] | [2.783, 3.664] | [1.692, 2.228] | [0.997, 1.000] | [0.994, 1.000] | 6 / 12 |
| novel | B | NA | NA | [2.905, 3.230] | [1.766, 1.964] | NA | [0.995, 0.999] | 0 / 12 |
| older_clean | A | [2.521, 3.751] | [1.533, 2.281] | [2.543, 3.595] | [1.546, 2.186] | [0.990, 1.000] | [0.989, 1.000] | 6 / 12 |
| older_clean | B | NA | NA | [2.655, 3.196] | [1.614, 1.943] | NA | [0.995, 1.000] | 0 / 12 |

Ratio = half-width / (1.645 SD); 1 is calibrated. Half-width / SD: 1.645 is calibrated.

## What differs

| aspect | sensitivity/bootstrap_coverage | post7/coverage | consequence |
| --- | --- | --- | --- |
| normalisation | 90% half-width / replicate SD; a calibrated interval gives 1.645 | 90% half-width / (1.645 x replicate SD); a calibrated interval gives 1 | the main difference: 2.52 / 1.645 = 1.53 and 3.75 / 1.645 = 2.28 |
| replicates and seed | 300 replicates, 1000 bootstrap draws, seed 1 | 1000 replicates, 1000 bootstrap draws, seed 7 | Monte Carlo noise only |
| designs | Novel and Older-clean, tier A only | Novel and Older-clean, tiers A and B | the post7 headline 1.546 to 2.186 is Older-clean tier A only; over all post7 designs the two-way ratio is wider |
| scenarios | model A: fixed signal 0 or 0.37 on the score scale, partner SD 0 or 1, drug SD 1; model B: per-drug random slope (mean 0 or 0.37, SD 0.6), partner SD 0 or 1 | target true AUROC 0.45, 0.50, 0.60 crossed with partner SD 0 or 1 and slope SD 0 or 0.5, drug SD 1 | different grids; both have label-independent partner effects; only post7 has a below-chance truth |
| true value | mean estimate over replicates | analytic Phi(beta / sqrt(2 (sigma_p^2 + 1) + tau^2)) | affects coverage, not the half-width ratio |
| SD estimator | numpy std, ddof 0 | ddof 1 | factor sqrt(n/(n-1)), at most 0.2% at 300 replicates |
| criteria file | none (sensitivity analysis) | results/revision/post7/criteria.json analysis_1b_coverage | only the post7 run is criteria-backed |

## Post hoc results with a criteria file (copied, not recomputed)

Bayesian region of practical equivalence [0.40, 0.60], H1 Older-clean tier A (results/revision/post7/criteria.json analysis_1c_bayes):

| model | posterior mean | 95% CrI | P(in region) | P(AUROC < 0.5) | verdict |
| --- | --- | --- | --- | --- | --- |
| Bayesian bootstrap over drugs (primary) | 0.452 | [0.411, 0.491] | 0.993 | 0.992 | practically equivalent |
| two-way Bayesian bootstrap over drugs and partners (secondary) | 0.452 | [0.386, 0.515] | 0.938 | 0.927 | undecided |

Bootstrap schemes, H1 Older-clean tier A (results/revision/post7/criteria.json analysis_1a_one_way):

| bootstrap | estimate | 90% CI | 95% CI | p_TOST | Holm (H1, H4, H6) | 95% CI below 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| two_way | 0.452 | [0.395, 0.509] | [0.389, 0.518] | 0.061 | 0.183 | False |
| one_way_drug | 0.452 | [0.417, 0.487] | [0.412, 0.495] | 0.005 | 0.015 | True |
| partner_only | 0.452 | [0.419, 0.482] | [0.415, 0.488] | 0.004 | 0.012 | True |

The one-way drug and partner-only intervals lie inside 0.40 to 0.60 (p_TOST 0.005 and 0.004) and also below 0.5: under those bootstraps the model is below chance, which is inverted information, not equivalence support.

Partner-only coverage (results/revision/post7/criteria.json analysis_1b_coverage):

| design | 90% coverage range | ratio range | labels | adequate |
| --- | --- | --- | --- | --- |
| older_clean tier A | [0.828, 0.958] | [0.868, 1.201] | anti-conservative, calibrated, conservative | False |
| older_clean tier B | [0.873, 0.950] | [0.947, 1.197] | calibrated, conservative | True |
| novel tier A | [0.897, 0.963] | [1.019, 1.284] | calibrated, conservative | True |
| novel tier B | [0.918, 0.958] | [1.096, 1.243] | calibrated, conservative | True |

Spike-in kappa rule (results/revision/spikein/criteria.json): equivalent if the paired kappa 95% upper bound is at most 0.25, falsified if its 95% lower bound is above 0.25. Smallest kappa falsified with 80% power on Older-clean tier A: 0.754 (b2mixed base, grid 0.8), 0.779 (noise base). Observed b2mixed: kappa -0.342, 95% [-0.794, 0.133], upper bound 0.133, decision under the kappa rule: equivalent.

