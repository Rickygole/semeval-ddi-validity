# M3b: DrugBank listing rates, SemEval source split and the string-match baseline

Status: post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision.

DrugBank release: version 5.1, exported on 2026-03-05 (`drugbank_all_full_database.xml.zip`). Resolution is the experiment 5 rule.

## (a) Listing rate of random vocabulary pairs against SemEval pairs

Random: 10,000 unordered pairs of SemEval vocabulary names (keys of `artifacts/vocab/drug_lookup.json`) with different RxCUI, RandomState(1). Wilson 95% intervals.

| set | n | resolvable | listed / all | listed / resolvable | 95% CI | listed / both resolved | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random vocabulary pairs (names) | 10000 | 9944 | 0.353 | 0.355 | [0.346, 0.364] | 0.404 | [0.394, 0.415] |
| random vocabulary pairs (one name per RxCUI) | 10000 | 9943 | 0.343 | 0.345 | [0.335, 0.354] | 0.397 | [0.386, 0.407] |
| SemEval test negatives | 2439 | 2377 | 0.660 | 0.677 | [0.658, 0.695] | 0.712 | [0.693, 0.730] |
| SemEval test positives | 371 | 362 | 0.709 | 0.727 | [0.678, 0.770] | 0.819 | [0.774, 0.858] |
| SemEval test negatives, no self pairs | 2150 | 2108 | 0.748 | 0.763 | [0.745, 0.781] | 0.808 | [0.790, 0.824] |
| SemEval test positives, no self pairs | 371 | 362 | 0.709 | 0.727 | [0.678, 0.770] | 0.819 | [0.774, 0.858] |
| SemEval test negatives, DDI-DrugBank | 2161 | 2148 | 0.698 | 0.702 | [0.682, 0.721] | 0.730 | [0.710, 0.748] |
| SemEval test positives, DDI-DrugBank | 291 | 291 | 0.763 | 0.763 | [0.711, 0.808] | 0.860 | [0.813, 0.897] |
| SemEval test negatives, DDI-MedLine | 278 | 229 | 0.363 | 0.441 | [0.378, 0.506] | 0.521 | [0.451, 0.590] |
| SemEval test positives, DDI-MedLine | 80 | 71 | 0.512 | 0.577 | [0.462, 0.685] | 0.651 | [0.528, 0.757] |

## (b) DrugBank lookup AUROC on SemEval test by source document

Pooled AUROC against the binary SemEval label; unresolvable counted as not listed; sentence-cluster bootstrap, 1,000 draws, seed 42. For a 0/1 score AUROC = 0.5 (1 + TPR - FPR).

| subset | n | positives | listed | TPR | FPR | AUROC | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all sources, all pairs | 2810 | 371 | 1872 | 0.709 | 0.660 | 0.525 | [0.484, 0.570] |
| all sources, no self pairs | 2521 | 371 | 1872 | 0.709 | 0.748 | 0.480 | [0.439, 0.521] |
| DDI-DrugBank documents, all pairs | 2452 | 291 | 1730 | 0.763 | 0.698 | 0.533 | [0.481, 0.585] |
| DDI-DrugBank documents, no self pairs | 2212 | 291 | 1730 | 0.763 | 0.785 | 0.489 | [0.447, 0.536] |
| DDI-MedLine abstracts, all pairs | 358 | 80 | 142 | 0.512 | 0.363 | 0.575 | [0.504, 0.644] |
| DDI-MedLine abstracts, no self pairs | 309 | 80 | 142 | 0.512 | 0.441 | 0.536 | [0.461, 0.607] |

## (c) Label string-match baseline

`non_di_label_string_match`: 1 if the partner is named anywhere outside the Drug Interactions section of the OOD drug's label.

| cohort | statistic | n | AUROC | 95% CI | source |
| --- | --- | --- | --- | --- | --- |
| Novel | pooled | 438 | 0.797 | [0.709, 0.877] | baselines.json, two-way cluster bootstrap |
| Older (full, 1944) | pooled | 1944 | 0.837 | [0.790, 0.880] | baselines.json, two-way cluster bootstrap |
| novel | within-drug | 438 | 0.814 | [0.719, 0.903] | recomputed, two-way paired_draws (pooled on these rows 0.797) |
| older_clean | within-drug | 1832 | 0.844 | [0.792, 0.890] | recomputed, two-way paired_draws (pooled on these rows 0.832) |

## (d) Why both co-mention subgroups exceed the overall value

Set: all 2810 SemEval test pairs, self pairs kept, unresolvable as not listed (the experiment 5 set behind 0.525, 0.591 and 0.529) (n = 2810).

| subgroup | n | positives | negatives | share of all positives | share of all negatives | TPR | FPR | AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| co-mentioned in a SemEval train sentence | 1023 | 54 | 969 | 0.146 | 0.397 | 0.907 | 0.724 | 0.591 |
| not co-mentioned | 1787 | 317 | 1470 | 0.854 | 0.603 | 0.675 | 0.617 | 0.529 |
| pooled | 2810 | | | | | 0.709 | 0.660 | 0.525 |

If the negatives had the positives' co-mention mix, the pooled AUROC would be 0.538.

Set: 2521 pairs without self pairs (n = 2521).

| subgroup | n | positives | negatives | share of all positives | share of all negatives | TPR | FPR | AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| co-mentioned in a SemEval train sentence | 844 | 54 | 790 | 0.146 | 0.367 | 0.907 | 0.889 | 0.509 |
| not co-mentioned | 1677 | 317 | 1360 | 0.854 | 0.633 | 0.675 | 0.667 | 0.504 |
| pooled | 2521 | | | | | 0.709 | 0.748 | 0.480 |

If the negatives had the positives' co-mention mix, the pooled AUROC would be 0.505.

The three values use the same set: all 2,810 SemEval test pairs with the 289 self pairs kept and unresolvable pairs counted as not listed, pooled AUROC of the 0/1 lookup, sentence bootstrap (Amendment 7 experiment 5). Both subgroups beat the pooled value because co-mention is associated with both the label and the score (Simpson's paradox). Co-mentioned pairs are rarely positive (54 of 1023, 0.053) but are listed often (FPR 0.724); not co-mentioned pairs are positive more often (0.177) and listed less (FPR 0.617). Pooling weights the TPR by where the positives are (0.854 of positives are not co-mentioned, so pooled TPR 0.709 sits near the low subgroup TPR 0.675) and the FPR by where the negatives are (0.397 of negatives are co-mentioned, which pulls pooled FPR up to 0.660). The pooled TPR minus FPR, 0.049, is smaller than in either subgroup (0.183 and 0.058), so 0.5 (1 + TPR - FPR) is 0.525 overall against 0.591 and 0.529.

