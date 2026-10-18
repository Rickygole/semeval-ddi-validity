# SemEval self pairs and the DrugBank lookup

289 of 2810 SemEval test pairs name the same drug twice; 0 of them are positive and DrugBank lists 0. Sentence bootstrap, 1000 draws, seed 42.

Self pairs are negatives the lookup never lists, so they enter as correctly ranked negatives and raise the all-pairs AUROC; the lookup AUROC on genuine two-drug pairs is the row that excludes them.

| subset | n | n_pos | listed | lookup AUROC | 95% CI |
| --- | --- | --- | --- | --- | --- |
| all pairs, unresolvable counted as not listed | 2810 | 371 | 1872 | 0.525 | [0.484, 0.570] |
| excluding self pairs | 2521 | 371 | 1872 | 0.480 | [0.439, 0.521] |
| self pairs only | 289 | 0 | 0 | NA | [NA, NA] |

Agreement with `results/revision/amend7/cpu/exp5_dissociation.json` (AUROC to 4 decimals): all pairs, unresolvable counted as not listed: True, excluding self pairs: True.
