# Post hoc analyses after Amendment 7: summary

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision. Criteria: `criteria.json`.

## Headline framing row

H1 kappa against the DrugBank lookup (Older-clean, tier A, two-way bootstrap with paired DrugBank draws): -0.342, 95% [-0.794, 0.133]; upper bound 0.133. b2mixed carries at most 0.133 of the within-drug signal of the DrugBank lookup (AUROC 0.641) at 95% confidence. Under the one-way drug bootstrap the kappa interval is [-0.626, -0.039].

## 1. Interval calibration

* Two-way (preregistered): H1 0.452, 90% [0.395, 0.509], 95% [0.389, 0.518], p_TOST 0.061.
* One-way drug (sensitivity): 90% [0.417, 0.487], 95% [0.412, 0.495], p_TOST 0.005 (Holm 0.015). The 95% interval lies below 0.5: True. Under this bootstrap the model is significantly below chance on Older-clean, that is, it carries inverted information; this is not support for equivalence and it changes no preregistered decision.
* Partner-only: 90% [0.419, 0.482], 95% [0.415, 0.488].
* Bayesian bootstrap over drugs: P(0.40 <= AUROC <= 0.60) = 0.993 (practically equivalent), and P(AUROC < 0.5) = 0.992. With Dirichlet weights on partners as well: 0.938 (undecided), P(AUROC < 0.5) = 0.927.

Coverage simulation (1000 replicates, 1000 draws each):

| design | bootstrap | 90% coverage range | half-width ratio range | labels | adequate |
| --- | --- | --- | --- | --- | --- |
| older_clean tier A | two_way | [0.989, 1.000] | [1.546, 2.186] | conservative | True |
| older_clean tier A | one_way_drug | [0.871, 0.958] | [0.953, 1.207] | calibrated, conservative | True |
| older_clean tier A | partner_only | [0.828, 0.958] | [0.868, 1.201] | anti-conservative, calibrated, conservative | False |
| older_clean tier B | two_way | [0.995, 1.000] | [1.614, 1.943] | conservative | True |
| older_clean tier B | one_way_drug | [0.865, 0.909] | [0.933, 1.042] | anti-conservative, calibrated | False |
| older_clean tier B | partner_only | [0.873, 0.950] | [0.947, 1.197] | calibrated, conservative | True |
| novel tier A | two_way | [0.994, 1.000] | [1.692, 2.228] | conservative | True |
| novel tier A | one_way_drug | [0.872, 0.951] | [0.948, 1.185] | calibrated, conservative | True |
| novel tier A | partner_only | [0.897, 0.963] | [1.019, 1.284] | calibrated, conservative | True |
| novel tier B | two_way | [0.995, 0.999] | [1.766, 1.964] | conservative | True |
| novel tier B | one_way_drug | [0.870, 0.900] | [0.947, 0.997] | calibrated | True |
| novel tier B | partner_only | [0.918, 0.958] | [1.096, 1.243] | calibrated, conservative | True |

In the simulation the partner effects are independent of the labels; the real design links partners to labels through partner matching (negatives reuse other drugs' positive partners), which the simulation does not reproduce. The one-way drug bootstrap is near nominal there (one Older-clean tier B scenario at 0.865, just under the 0.87 bar) and the two-way bootstrap covers 0.989 to 1.000 with 1.5 to 2.2 times the nominal half-width.

## 2. Partner structure

Validity (DrugBank lookup, Older-clean tier A): partner-stratified 0.699 (lower 95% 0.627, valid True); tetrad 0.691 (lower 95% 0.577, valid True).

* b2mixed Older-clean tier A: within-drug 0.452; partner-stratified 0.461 [0.368, 0.543], explained False; tetrad 0.375 [0.233, 0.541], explained False.
* Popularity-only scorer: feature within-drug AUROC 0.506; at b2mixed's within-drug Spearman (0.257) it gives 0.501; share of the gap reproduced -0.019; popularity explains: False. No popularity sensitivity reaches 0.452: the scorer's AUROC range is [0.493, 0.506].
* Label-derived contrast (leave-one-drug-out partner positive rate, no decision): at b2mixed's Spearman with it (0.055) a scorer of that rate gives 0.476 (share 0.504).

Every verdict above is post hoc and exploratory. H1, H4 and H6 stay inconclusive and H5 stays falsified.
