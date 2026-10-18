# Partner matching builds an anti-signal into the OOD sets

Post hoc note. Every number is read from `results/revision/amend7/cpu/exp7_below_chance.json` by `scripts/sens_partner_design_note.py`; shares are computed from those values. No decision changes.

## The design

Negatives are partner matched: each negative reuses a positive's partner with a different OOD drug whose label never names it (`docs/PREREGISTRATION.md`, frozen evaluation sets). The partner of a negative is therefore, by construction, a positive partner of some other drug in the cohort, while the partner of a positive need not be. Within a drug, the partner's positive rate among the other drugs of the cohort is then higher for negatives than for positives.

## The size of the anti-signal

On Older-clean (tier A, n = 1832, 128 drugs) the leave-one-drug-out partner positive rate has within-drug AUROC 0.088 [0.049, 0.130]: its mean is 0.234 for positives and 0.372 for negatives. On tier B it is 0.053 [0.016, 0.102], and on Novel tier A 0.028 [0.000, 0.096]. The partner positive count gives 0.449 [0.371, 0.520]. A label-free partner prior (how often vocabulary Drug Interactions sections name the partner) sits at 0.506 [0.431, 0.575], so the anti-signal is a property of the test labels, not of the partners.

Any scorer whose output rises with how often a partner is a positive in this cohort is pushed below 0.5 within drug by construction. A model that learned that some partners interact often, and applied that to these pairs, would score below chance without any error about the OOD drug.

## How much of the 0.452 it can account for

Primary system b2mixed-biomedbert, five-seed mean, names only, Older-clean tier A: raw within-drug AUROC 0.452 [0.389, 0.518], a gap of 0.048 below chance. exp7 removes the within-drug linear association with each feature and recomputes the AUROC (partialled).

| feature | Spearman with the model, within drug | 95% CI | partialled AUROC | 95% CI | change | share of the gap below 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| leave-one-drug-out partner positive rate (test labels) | 0.055 | [-0.002, 0.119] | 0.484 | [0.418, 0.550] | +0.032 | 0.663 |
| leave-one-drug-out partner positive count (test labels) | 0.245 | [0.190, 0.299] | 0.460 | [0.399, 0.526] | +0.008 | 0.169 |
| label-free partner prior (share of vocabulary Drug Interactions sections naming the partner) | 0.257 | [0.209, 0.304] | 0.447 | [0.385, 0.511] | -0.005 | -0.096 |

Joint partialling on the preregistered causes a, b, c and e gives 0.455.

Partialling on the test-label partner rate moves the primary system from 0.452 to 0.484, 0.663 of the gap below 0.5, and its interval [0.418, 0.550] then covers 0.5. This is an upper estimate of what the design explains: the model's within-drug Spearman with the feature is only 0.055 [-0.002, 0.119], and the feature is built from the test labels, so partialling on it also removes label information. The same partialling takes the DrugBank lookup from 0.641 to 0.398, which shows how strongly a label-derived regressor can move any scorer. The label-free prior explains none of it (0.447), and the partner count 0.169 of the gap.

On Novel the primary system is 0.523 raw and 0.523 partialled on the same feature, so there is no below-chance result to explain.

Reading: partner matching makes below-chance scores the expected outcome for a partner-popularity-sensitive scorer, and can account for up to 0.663 of the Older-clean deficit under the most generous partialling. It is reported as a design property of the evaluation sets, not as a confirmed cause; exp7's preregistered verdict for cause b stays rejected.
