# Kappa against the DrugBank ceiling and drug-weighted sensitivity

kappa = (AUROC - 0.5) / (AUROC_DrugBank - 0.5), within drug, tier A. Drug-weighted rows are sensitivity analyses, not preregistered.

| id | cohort | n | drugs | decision | pair-weighted AUROC | 90% CI | p_tost | DrugBank | kappa | kappa 95% CI | kappa at 0.60 | drug-weighted AUROC | 90% CI | 95% CI | p_tost | kappa (drug-weighted) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Older-clean | 1832 | 128 | inconclusive | 0.452 | [0.395, 0.509] | 0.061 | 0.641 | -0.342 | [-0.794, 0.133] | 0.708 | 0.440 | [0.389, 0.495] | [0.379, 0.508] | 0.104 | -0.438 |
| H1-sensitivity | Older-clean sensitivity | 1754 | 123 | sensitivity, not preregistered (no decision rule) | 0.453 | [0.394, 0.511] | 0.078 | 0.648 | -0.319 | [-0.827, 0.153] | 0.674 | 0.441 | [0.387, 0.498] | [0.374, 0.508] | 0.099 | -0.421 |
| H1-novel | Novel | 438 | 48 | estimate only (no equivalence test) | 0.523 | [0.411, 0.626] | 0.117 | 0.729 | 0.101 | [-0.486, 0.722] | 0.438 | 0.506 | [0.395, 0.616] | [0.372, 0.635] | 0.088 | 0.026 |
| H6 | Novel | 438 | 48 | inconclusive | 0.519 | [0.421, 0.627] | 0.102 | 0.729 | 0.084 | [-0.499, 0.682] | 0.438 | 0.536 | [0.429, 0.629] | [0.403, 0.652] | 0.110 | 0.158 |
| H1-pooled | Novel + Older-clean | 2270 | 176 | descriptive, secondary (no pre-registered decision rule) | 0.461 | [0.410, 0.511] | 0.028 | 0.652 | -0.257 | [-0.675, 0.137] | 0.656 | 0.458 | [0.413, 0.510] | [0.403, 0.517] | 0.018 | -0.258 |

H4 compares cohorts and has no single kappa; use the H1 and H1-novel rows.
