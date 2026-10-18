# Positive control (H5): what an ideal reader of the H5 input reaches

Sensitivity analysis, post hoc. Novel cohort, n = 438. Within-drug AUROC with the two-way cluster bootstrap (1000 draws, seed 1042); pooled AUROC with the two-way bootstrap of `ddiood.evaluate2`.

The ideal reader uses the labels: it scores a visible partner mention up for positives and down for negatives, which is what a perfect judge of interaction statements would do if every visible positive mention stated the interaction. It is an upper bound for this input. The source proxy is the label-free version that treats a mention in the OOD drug's own label as the interaction statement.

## contaminated index

Partner visible after truncation: 68 of 148 positives, 59 of 290 negatives; in a visible own-label passage: 44 positives, 0 negatives. Visibility rule equals exp6 `partner_in_512_tokens`: True.

| reader | AUROC within | 95% CI | AUROC pooled | 95% CI | MCC (score > 0) |
| --- | --- | --- | --- | --- | --- |
| partner_visibility_rule | 0.635 | [0.510, 0.737] | 0.628 | [0.529, 0.717] | 0.267 |
| ideal_reader | 0.775 | [0.674, 0.869] | 0.785 | [0.704, 0.863] | 0.600 |
| source_proxy_reader | 0.677 | [0.557, 0.783] | 0.639 | [0.523, 0.744] | 0.468 |

## hybrid index

Partner visible after truncation: 48 of 148 positives, 68 of 290 negatives; in a visible own-label passage: 14 positives, 0 negatives. Visibility rule equals exp6 `partner_in_512_tokens`: True.

| reader | AUROC within | 95% CI | AUROC pooled | 95% CI | MCC (score > 0) |
| --- | --- | --- | --- | --- | --- |
| partner_visibility_rule | 0.501 | [0.396, 0.603] | 0.545 | [0.469, 0.619] | 0.096 |
| ideal_reader | 0.725 | [0.640, 0.822] | 0.741 | [0.653, 0.819] | 0.491 |
| source_proxy_reader | 0.574 | [0.485, 0.671] | 0.539 | [0.454, 0.624] | 0.254 |

The H5 thresholds are Novel pooled AUROC 0.75 and MCC 0.30. The trained control reached 0.621 and 0.167 (`results/revision/eval/decisions.md`).
