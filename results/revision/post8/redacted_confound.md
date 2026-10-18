# Redacted-oracle context-length confound (post hoc, exploratory)

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

The redacted evidence of every row was rebuilt with ddiood.amend7_evidence.EvidenceBuilder from artifacts/amend7/di_sections.json and the Qwen tokenizer; the mean prompt token counts reproduce the recorded answer.tokens_mean of a7-qwen-redactedoracle.json and a7-qwen-oracle.json:

- a7-qwen-redactedoracle/ood: reconstructed 731.2192, recorded 731.2192, max 1906 vs 1906
- a7-qwen-redactedoracle/oodold: reconstructed 813.6944, recorded 813.6944, max 6087 vs 6087
- a7-qwen-oracle/ood: reconstructed 760.5776, recorded 760.5776, max 1907 vs 1907
- a7-qwen-oracle/oodold: reconstructed 852.7341, recorded 852.7341, max 6087 vs 6087

## Tier A

| cohort | class | n | evidence tokens mean | median | tokens removed mean | median | share with tokens removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| novel | positives | 148 | 792.3 | 764.0 | 86.9 | 73.5 | 1.000 |
| novel | negatives | 290 | 574.0 | 422.0 | 0.0 | 0.0 | 0.000 |
| older_primary | positives | 562 | 822.4 | 625.0 | 121.1 | 90.5 | 1.000 |
| older_primary | negatives | 1159 | 579.1 | 463.0 | 0.0 | 0.0 | 0.000 |

| cohort | per-drug mean neg minus pos tokens: mean | median | share of drugs > 0 | length-only within-drug AUROC | 95% CI | Qwen redacted within-drug AUROC | 95% CI | Qwen minus length | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel | 79.3 | 76.5 | 1.000 | 1.000 | [1.000, 1.000] | 0.731 | [0.609, 0.844] | -0.269 | [-0.391, -0.156] |
| older_primary | 111.8 | 97.0 | 1.000 | 1.000 | [1.000, 1.000] | 0.682 | [0.617, 0.744] | -0.318 | [-0.383, -0.256] |

## Tier C-auto

| cohort | class | n | evidence tokens mean | median | tokens removed mean | median | share with tokens removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| novel | positives | 147 | 790.3 | 764.0 | 86.7 | 73.0 | 1.000 |
| novel | negatives | 290 | 574.0 | 422.0 | 0.0 | 0.0 | 0.000 |
| older_primary | positives | 525 | 842.5 | 632.0 | 123.1 | 91.0 | 1.000 |
| older_primary | negatives | 1159 | 579.1 | 463.0 | 0.0 | 0.0 | 0.000 |

| cohort | per-drug mean neg minus pos tokens: mean | median | share of drugs > 0 | length-only within-drug AUROC | 95% CI | Qwen redacted within-drug AUROC | 95% CI | Qwen minus length | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel | 79.0 | 76.5 | 1.000 | 1.000 | [1.000, 1.000] | 0.728 | [0.609, 0.844] | -0.272 | [-0.391, -0.156] |
| older_primary | 115.6 | 103.1 | 1.000 | 1.000 | [1.000, 1.000] | 0.684 | [0.615, 0.747] | -0.316 | [-0.385, -0.253] |

Length-only score: minus the Qwen token count of the redacted evidence, so a shorter context ranks higher. Two-way bootstrap, Novel seed 1042, Older-primary seed 42.
