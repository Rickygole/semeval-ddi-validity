# Experiment 5: double dissociation (DrugBank lookup on SemEval 2013 test)

n = 2810 test pairs (371 positive, 2439 negative); 71 unresolvable (neither drug in DrugBank), 157 with one drug resolved, 2582 with both resolved; 289 self pairs.

SemEval negatives that DrugBank lists as interacting: 1609 of 2377 resolvable (0.677); 0.712 when both drugs resolve. Positives listed: 0.727 of resolvable, 0.819 with both resolved.

## By SemEval label

| subset | label | n | unresolvable | one side | both resolved | listed | listed / resolvable | listed / both resolved | co-mentioned in train |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | false | 2439 | 62 | 116 | 2261 | 1609 | 0.677 | 0.712 | 969 |
| all | mechanism | 157 | 0 | 20 | 137 | 119 | 0.758 | 0.869 | 27 |
| all | effect | 113 | 9 | 7 | 97 | 71 | 0.683 | 0.732 | 19 |
| all | advise | 63 | 0 | 5 | 58 | 58 | 0.921 | 1.000 | 8 |
| all | int | 38 | 0 | 9 | 29 | 15 | 0.395 | 0.517 | 0 |
| all | any positive | 371 | 9 | 41 | 321 | 263 | 0.727 | 0.819 | 54 |
| pair co-mentioned in a SemEval train sentence | false | 969 | 0 | 2 | 967 | 702 | 0.724 | 0.726 | 969 |
| pair co-mentioned in a SemEval train sentence | mechanism | 27 | 0 | 0 | 27 | 26 | 0.963 | 0.963 | 27 |
| pair co-mentioned in a SemEval train sentence | effect | 19 | 0 | 0 | 19 | 16 | 0.842 | 0.842 | 19 |
| pair co-mentioned in a SemEval train sentence | advise | 8 | 0 | 1 | 7 | 7 | 0.875 | 1.000 | 8 |
| pair co-mentioned in a SemEval train sentence | int | 0 | 0 | 0 | 0 | 0 | NA | NA | 0 |
| pair co-mentioned in a SemEval train sentence | any positive | 54 | 0 | 1 | 53 | 49 | 0.907 | 0.925 | 54 |
| pair not co-mentioned in SemEval train | false | 1470 | 62 | 114 | 1294 | 907 | 0.644 | 0.701 | 0 |
| pair not co-mentioned in SemEval train | mechanism | 130 | 0 | 20 | 110 | 93 | 0.715 | 0.845 | 0 |
| pair not co-mentioned in SemEval train | effect | 94 | 9 | 7 | 78 | 55 | 0.647 | 0.705 | 0 |
| pair not co-mentioned in SemEval train | advise | 55 | 0 | 4 | 51 | 51 | 0.927 | 1.000 | 0 |
| pair not co-mentioned in SemEval train | int | 38 | 0 | 9 | 29 | 15 | 0.395 | 0.517 | 0 |
| pair not co-mentioned in SemEval train | any positive | 317 | 9 | 40 | 268 | 214 | 0.695 | 0.799 | 0 |
| both drugs resolved in DrugBank | false | 2261 | 0 | 0 | 2261 | 1609 | 0.712 | 0.712 | 967 |
| both drugs resolved in DrugBank | mechanism | 137 | 0 | 0 | 137 | 119 | 0.869 | 0.869 | 27 |
| both drugs resolved in DrugBank | effect | 97 | 0 | 0 | 97 | 71 | 0.732 | 0.732 | 19 |
| both drugs resolved in DrugBank | advise | 58 | 0 | 0 | 58 | 58 | 1.000 | 1.000 | 7 |
| both drugs resolved in DrugBank | int | 29 | 0 | 0 | 29 | 15 | 0.517 | 0.517 | 0 |
| both drugs resolved in DrugBank | any positive | 321 | 0 | 0 | 321 | 263 | 0.819 | 0.819 | 53 |

## Lookup AUROC against SemEval labels

| subset | n | n_pos | AUROC | 95% CI |
| --- | --- | --- | --- | --- |
| all pairs, unresolvable counted as not listed | 2810 | 371 | 0.525 | [0.484, 0.570] |
| both drugs resolved | 2582 | 321 | 0.554 | [0.521, 0.591] |
| co-mentioned in SemEval train | 1023 | 54 | 0.591 | [0.540, 0.649] |
| not co-mentioned in SemEval train | 1787 | 317 | 0.529 | [0.482, 0.583] |
| both resolved and co-mentioned in train | 1020 | 53 | 0.599 | [0.550, 0.652] |
| both resolved and not co-mentioned in train | 1562 | 268 | 0.549 | [0.514, 0.588] |
| excluding self pairs | 2521 | 371 | 0.480 | [0.439, 0.521] |

Distinct unordered pairs: 1844; 426 occur more than once, 126 of them with both a positive and a negative instance. Among distinct pairs labelled only negative and resolvable (1513), DrugBank lists 0.692; among only-positive (171), 0.620.

## 2x2 figure data

| system | labels | tier | statistic | n | drugs | value | 95% CI | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DrugBank lookup | SemEval 2013 test (sentence-level) | A | pooled AUROC | 2810 |  | 0.525 | [0.484, 0.570] |  |
| b1names-biomedbert (names only) | SemEval 2013 test (sentence-level) | A | pooled AUROC | 2810 |  | 0.671 | [0.637, 0.710] |  |
| llm-qwen-names (names only) | SemEval 2013 test (sentence-level) | A | pooled AUROC | 2810 |  | 0.495 | [0.437, 0.552] |  |
| b2sentence-biomedbert (sentence model; OOD has no sentence) | SemEval 2013 test (sentence-level) | A | pooled AUROC | 2810 |  | 0.968 | [0.955, 0.978] |  |
| DrugBank lookup | novel pair labels | A | within-drug AUROC | 438 | 48 | 0.729 | [0.642, 0.808] |  |
| b1names-biomedbert (names only) | novel pair labels | A | within-drug AUROC | 438 | 48 | 0.514 | [0.384, 0.635] |  |
| llm-qwen-names (names only) | novel pair labels | A | within-drug AUROC | 438 | 48 | 0.579 | [0.440, 0.713] |  |
| b2sentence-biomedbert (sentence model; OOD has no sentence) | novel pair labels | A | within-drug AUROC | 438 | 48 | 0.490 | [0.370, 0.612] |  |
| DrugBank lookup | novel pair labels | B | within-drug AUROC | 316 | 48 | 1.000 | [1.000, 1.000] | circular: tier B is defined by DrugBank agreement |
| b1names-biomedbert (names only) | novel pair labels | B | within-drug AUROC | 316 | 48 | 0.530 | [0.341, 0.724] |  |
| llm-qwen-names (names only) | novel pair labels | B | within-drug AUROC | 316 | 48 | 0.577 | [0.397, 0.736] |  |
| b2sentence-biomedbert (sentence model; OOD has no sentence) | novel pair labels | B | within-drug AUROC | 316 | 48 | 0.475 | [0.308, 0.644] |  |
| DrugBank lookup | older_clean pair labels | A | within-drug AUROC | 1832 | 128 | 0.641 | [0.595, 0.689] |  |
| b1names-biomedbert (names only) | older_clean pair labels | A | within-drug AUROC | 1832 | 128 | 0.463 | [0.398, 0.521] |  |
| llm-qwen-names (names only) | older_clean pair labels | A | within-drug AUROC | 1832 | 128 | 0.602 | [0.533, 0.667] |  |
| b2sentence-biomedbert (sentence model; OOD has no sentence) | older_clean pair labels | A | within-drug AUROC | 1832 | 128 | 0.453 | [0.391, 0.518] |  |
| DrugBank lookup | older_clean pair labels | B | within-drug AUROC | 1191 | 128 | 1.000 | [1.000, 1.000] | circular: tier B is defined by DrugBank agreement |
| b1names-biomedbert (names only) | older_clean pair labels | B | within-drug AUROC | 1191 | 128 | 0.419 | [0.320, 0.531] |  |
| llm-qwen-names (names only) | older_clean pair labels | B | within-drug AUROC | 1191 | 128 | 0.660 | [0.543, 0.767] |  |
| b2sentence-biomedbert (sentence model; OOD has no sentence) | older_clean pair labels | B | within-drug AUROC | 1191 | 128 | 0.393 | [0.296, 0.501] |  |
