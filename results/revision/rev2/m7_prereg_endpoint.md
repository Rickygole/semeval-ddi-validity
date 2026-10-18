# M7: the originally preregistered primary endpoint

Status: post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision.

Preregistration, Primary endpoint: AUROC of P(interaction) for `b2mixed` BiomedBERT on Novel OOD, names only, averaged over seeds 1, 2, 3, 4 and 42, with a 95% bootstrap interval that resamples novel drugs. Amendment 4 replaced it by the within-drug AUROC; Amendment 7 asks for it to be shown with equal prominence.

| statistic | n | positives | drugs | AUROC | 95% CI (drug cluster, preregistered) | 90% CI | p_TOST [0.40, 0.60] | 95% CI (two-way) | 90% CI (two-way) | within-drug (H1-novel) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pooled Novel AUROC, names only, 5-seed mean | 438 | 148 | 48 | 0.529 | [0.457, 0.608] | [0.465, 0.597] | 0.046 | [0.410, 0.637] | [0.436, 0.620] | 0.523 |

1,000 draws, seed 42 (`ddiood.evaluate2.boot_auroc`). Reproduces `results/revision/eval/tables.md` (0.529 [0.457, 0.608]): True. The p_TOST is shown for completeness; under the original plan the H1 decision used this interval, and the amended H1 is the within-drug Older-clean test.
