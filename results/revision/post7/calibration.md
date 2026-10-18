# Interval calibration, kappa framing and Bayesian equivalence

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

## Primary framing row: H1 kappa against the DrugBank lookup

kappa = (AUROC - 0.5) / (AUROC_DrugBank - 0.5), within drug, with paired draws for the model and DrugBank.

| id | tier | bootstrap | AUROC | DrugBank | kappa | 95% CI | 95% upper bound | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | A | two_way | 0.452 | 0.641 | -0.342 | [-0.794, 0.133] | 0.133 |  |
| H1 | A | one_way_drug | 0.452 | 0.641 | -0.342 | [-0.626, -0.039] | -0.039 |  |
| H1 | B | two_way | 0.397 | 1.000 | -0.206 | [-0.422, 0.029] | 0.029 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |
| H1 | B | one_way_drug | 0.397 | 1.000 | -0.206 | [-0.335, -0.072] | -0.072 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |
| H1-novel | A | two_way | 0.523 | 0.729 | 0.101 | [-0.486, 0.722] | 0.722 |  |
| H1-novel | A | one_way_drug | 0.523 | 0.729 | 0.101 | [-0.177, 0.412] | 0.412 |  |
| H1-novel | B | two_way | 0.533 | 1.000 | 0.066 | [-0.286, 0.429] | 0.429 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |
| H1-novel | B | one_way_drug | 0.533 | 1.000 | 0.066 | [-0.119, 0.253] | 0.253 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |
| H6 | A | two_way | 0.519 | 0.729 | 0.084 | [-0.499, 0.682] | 0.682 |  |
| H6 | A | one_way_drug | 0.519 | 0.729 | 0.084 | [-0.211, 0.373] | 0.373 |  |
| H6 | B | two_way | 0.552 | 1.000 | 0.104 | [-0.267, 0.451] | 0.451 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |
| H6 | B | one_way_drug | 0.552 | 1.000 | 0.104 | [-0.083, 0.293] | 0.293 | DrugBank is 1.0 on tier B by construction; kappa = 2 x (AUROC - 0.5) |

## 1a. Two-way, one-way drug and partner-only bootstrap

The two-way rows are the preregistered intervals recomputed by the same code (they reproduce decisions.md). The one-way and partner-only rows are sensitivity analyses. A one-way interval that lies below 0.5 means the model is significantly below chance under that bootstrap (inverted information); it is not support for equivalence.

| id | tier | bootstrap | estimate | 90% CI | 95% CI | p_TOST | Holm (H1, H4, H6) | 90% CI below 0.5 | 95% CI below 0.5 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | A | two_way | 0.452 | [0.395, 0.509] | [0.389, 0.518] | 0.061 | 0.183 | False | False |  |
| H1-novel | A | two_way | 0.523 | [0.411, 0.626] | [0.397, 0.650] | 0.117 | NA | False | False | no preregistered test (estimate only) |
| H6 | A | two_way | 0.519 | [0.421, 0.627] | [0.393, 0.647] | 0.102 | 0.204 | False | False |  |
| H4 | A | two_way | -0.071 | [-0.192, 0.045] | [-0.220, 0.068] | 0.339 | 0.339 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |
| H1 | A | one_way_drug | 0.452 | [0.417, 0.487] | [0.412, 0.495] | 0.005 | 0.015 | True | True |  |
| H1-novel | A | one_way_drug | 0.523 | [0.469, 0.579] | [0.458, 0.585] | 0.005 | NA | False | False | no preregistered test (estimate only) |
| H6 | A | one_way_drug | 0.519 | [0.465, 0.573] | [0.456, 0.583] | 0.007 | 0.015 | False | False |  |
| H4 | A | one_way_drug | -0.071 | [-0.139, -0.002] | [-0.146, 0.009] | 0.265 | 0.265 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |
| H1 | A | partner_only | 0.452 | [0.419, 0.482] | [0.415, 0.488] | 0.004 | 0.012 | True | True |  |
| H1-novel | A | partner_only | 0.523 | [0.460, 0.575] | [0.446, 0.587] | 0.010 | NA | False | False | no preregistered test (estimate only) |
| H6 | A | partner_only | 0.519 | [0.460, 0.577] | [0.451, 0.585] | 0.011 | 0.022 | False | False |  |
| H4 | A | partner_only | -0.071 | [-0.131, 0.003] | [-0.145, 0.021] | 0.203 | 0.203 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |
| H1 | B | two_way | 0.397 | [0.308, 0.493] | [0.289, 0.514] | 0.519 | 1.000 | True | False |  |
| H1-novel | B | two_way | 0.533 | [0.383, 0.682] | [0.357, 0.714] | 0.239 | NA | False | False | no preregistered test (estimate only) |
| H6 | B | two_way | 0.552 | [0.397, 0.692] | [0.367, 0.725] | 0.304 | 0.911 | False | False |  |
| H4 | B | two_way | -0.136 | [-0.299, 0.046] | [-0.334, 0.071] | 0.624 | 1.000 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |
| H1 | B | one_way_drug | 0.397 | [0.342, 0.453] | [0.333, 0.464] | 0.560 | 1.000 | True | True |  |
| H1-novel | B | one_way_drug | 0.533 | [0.452, 0.613] | [0.440, 0.627] | 0.084 | NA | False | False | no preregistered test (estimate only) |
| H6 | B | one_way_drug | 0.552 | [0.471, 0.630] | [0.458, 0.646] | 0.159 | 0.477 | False | False |  |
| H4 | B | one_way_drug | -0.136 | [-0.237, -0.040] | [-0.258, -0.021] | 0.728 | 1.000 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |
| H1 | B | partner_only | 0.397 | [0.346, 0.453] | [0.339, 0.464] | 0.531 | 1.000 | True | True |  |
| H1-novel | B | partner_only | 0.533 | [0.428, 0.615] | [0.411, 0.632] | 0.087 | NA | False | False | no preregistered test (estimate only) |
| H6 | B | partner_only | 0.552 | [0.464, 0.633] | [0.448, 0.644] | 0.165 | 0.495 | False | False |  |
| H4 | B | partner_only | -0.136 | [-0.230, -0.022] | [-0.255, 0.007] | 0.674 | 1.000 |  |  | Older-clean minus Novel; margin +/- 0.10; independent per-cohort draws |

## 1c. Bayesian region of practical equivalence

Region [0.40, 0.60] for AUROC rows and [-0.10, 0.10] for H4. Primary: Bayesian bootstrap over drugs, Dirichlet(1, ..., 1) weights (the posterior under a Dirichlet process prior with concentration tending to 0; noninformative, all mass on the observed drugs, partners fixed). Secondary: independent Dirichlet(1) weights on drugs and on partners. Rule: posterior probability at least 0.95 is practically equivalent, at most 0.05 practically not equivalent, otherwise undecided. p_below is P(AUROC < 0.5), or P(difference < 0) for H4.

| id | tier | model | posterior mean | 90% CrI | 95% CrI | P(in region) | p_below | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | A | Bayesian bootstrap over drugs (primary) | 0.452 | [0.418, 0.485] | [0.411, 0.491] | 0.993 | 0.992 | practically equivalent |
| H1-novel | A | Bayesian bootstrap over drugs (primary) | 0.523 | [0.467, 0.576] | [0.456, 0.585] | 0.993 | 0.237 | practically equivalent |
| H6 | A | Bayesian bootstrap over drugs (primary) | 0.519 | [0.464, 0.571] | [0.452, 0.582] | 0.994 | 0.268 | practically equivalent |
| H4 | A | Bayesian bootstrap over drugs (primary) | -0.071 | [-0.133, -0.008] | [-0.145, 0.006] | 0.769 | 0.966 | undecided |
| H1 | B | Bayesian bootstrap over drugs (primary) | 0.398 | [0.345, 0.450] | [0.333, 0.460] | 0.477 | 0.999 | undecided |
| H1-novel | B | Bayesian bootstrap over drugs (primary) | 0.534 | [0.457, 0.610] | [0.441, 0.623] | 0.922 | 0.231 | undecided |
| H6 | B | Bayesian bootstrap over drugs (primary) | 0.552 | [0.472, 0.626] | [0.455, 0.640] | 0.847 | 0.134 | undecided |
| H4 | B | Bayesian bootstrap over drugs (primary) | -0.136 | [-0.229, -0.043] | [-0.247, -0.025] | 0.259 | 0.991 | undecided |
| H1 | A | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.452 | [0.397, 0.506] | [0.386, 0.515] | 0.938 | 0.927 | undecided |
| H1-novel | A | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.521 | [0.420, 0.619] | [0.400, 0.641] | 0.880 | 0.369 | undecided |
| H6 | A | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.518 | [0.419, 0.614] | [0.397, 0.632] | 0.894 | 0.374 | undecided |
| H4 | A | two-way Bayesian bootstrap over drugs and partners (secondary) | -0.069 | [-0.180, 0.048] | [-0.208, 0.070] | 0.663 | 0.835 | undecided |
| H1 | B | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.400 | [0.312, 0.487] | [0.299, 0.506] | 0.494 | 0.969 | undecided |
| H1-novel | B | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.531 | [0.391, 0.666] | [0.366, 0.688] | 0.722 | 0.350 | undecided |
| H6 | B | two-way Bayesian bootstrap over drugs and partners (secondary) | 0.549 | [0.411, 0.682] | [0.378, 0.705] | 0.686 | 0.268 | undecided |
| H4 | B | two-way Bayesian bootstrap over drugs and partners (secondary) | -0.131 | [-0.296, 0.032] | [-0.318, 0.063] | 0.366 | 0.905 | undecided |
