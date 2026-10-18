# D9: DrugBank listing rates of SemEval 2013 test pairs under one convention

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

DrugBank release: version 5.1, exported on 2026-03-05. Resolution is the experiment 5 rule (`resolve`), unresolvable pairs are those where neither name maps to a DrugBank entry. Self pairs: the two names are equal after lowercase and strip (`drugbank._norm`), as in m3b. Primary number: share listed among resolvable pairs, Wilson 95%. The Wilson intervals treat instances as independent; sentence clustering is not applied.

## Instance rows (the SemEval test rows, as m3b)

| convention | class | scope | n | resolvable | listed | listed / resolvable | Wilson 95% | listed / all | Wilson 95% | self pairs removed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| self_pairs_excluded | negatives | pooled | 2150 | 2108 | 1609 | 0.763 | [0.745, 0.781] | 0.748 | [0.730, 0.766] | 289 |
| self_pairs_excluded | negatives | DDI-DrugBank | 1921 | 1912 | 1508 | 0.789 | [0.770, 0.806] | 0.785 | [0.766, 0.803] | 240 |
| self_pairs_excluded | negatives | DDI-MedLine | 229 | 196 | 101 | 0.515 | [0.446, 0.584] | 0.441 | [0.378, 0.506] | 49 |
| self_pairs_excluded | positives | pooled | 371 | 362 | 263 | 0.727 | [0.678, 0.770] | 0.709 | [0.661, 0.753] | 0 |
| self_pairs_excluded | positives | DDI-DrugBank | 291 | 291 | 222 | 0.763 | [0.711, 0.808] | 0.763 | [0.711, 0.808] | 0 |
| self_pairs_excluded | positives | DDI-MedLine | 80 | 71 | 41 | 0.577 | [0.462, 0.685] | 0.512 | [0.405, 0.619] | 0 |
| self_pairs_included | negatives | pooled | 2439 | 2377 | 1609 | 0.677 | [0.658, 0.695] | 0.660 | [0.641, 0.678] | 0 |
| self_pairs_included | negatives | DDI-DrugBank | 2161 | 2148 | 1508 | 0.702 | [0.682, 0.721] | 0.698 | [0.678, 0.717] | 0 |
| self_pairs_included | negatives | DDI-MedLine | 278 | 229 | 101 | 0.441 | [0.378, 0.506] | 0.363 | [0.309, 0.421] | 0 |
| self_pairs_included | positives | pooled | 371 | 362 | 263 | 0.727 | [0.678, 0.770] | 0.709 | [0.661, 0.753] | 0 |
| self_pairs_included | positives | DDI-DrugBank | 291 | 291 | 222 | 0.763 | [0.711, 0.808] | 0.763 | [0.711, 0.808] | 0 |
| self_pairs_included | positives | DDI-MedLine | 80 | 71 | 41 | 0.577 | [0.462, 0.685] | 0.512 | [0.405, 0.619] | 0 |

## Distinct unordered pairs (reference)

A distinct pair is counted in each class in which it has an instance; 126 pairs have both classes.

| convention | class | scope | n | resolvable | listed | listed / resolvable | Wilson 95% | listed / all | Wilson 95% | self pairs removed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| self_pairs_excluded | negatives | pooled | 1559 | 1532 | 1147 | 0.749 | [0.726, 0.770] | 0.736 | [0.713, 0.757] |  |
| self_pairs_excluded | negatives | DDI-DrugBank | 1446 | 1439 | 1104 | 0.767 | [0.745, 0.788] | 0.763 | [0.741, 0.785] |  |
| self_pairs_excluded | negatives | DDI-MedLine | 118 | 98 | 47 | 0.480 | [0.383, 0.577] | 0.398 | [0.315, 0.488] |  |
| self_pairs_excluded | positives | pooled | 298 | 293 | 206 | 0.703 | [0.648, 0.752] | 0.691 | [0.637, 0.741] |  |
| self_pairs_excluded | positives | DDI-DrugBank | 249 | 249 | 183 | 0.735 | [0.677, 0.786] | 0.735 | [0.677, 0.786] |  |
| self_pairs_excluded | positives | DDI-MedLine | 49 | 44 | 23 | 0.523 | [0.379, 0.662] | 0.469 | [0.337, 0.606] |  |
| self_pairs_included | negatives | pooled | 1672 | 1635 | 1147 | 0.702 | [0.679, 0.723] | 0.686 | [0.663, 0.708] |  |
| self_pairs_included | negatives | DDI-DrugBank | 1538 | 1527 | 1104 | 0.723 | [0.700, 0.745] | 0.718 | [0.695, 0.740] |  |
| self_pairs_included | negatives | DDI-MedLine | 143 | 117 | 47 | 0.402 | [0.317, 0.492] | 0.329 | [0.257, 0.409] |  |
| self_pairs_included | positives | pooled | 298 | 293 | 206 | 0.703 | [0.648, 0.752] | 0.691 | [0.637, 0.741] |  |
| self_pairs_included | positives | DDI-DrugBank | 249 | 249 | 183 | 0.735 | [0.677, 0.786] | 0.735 | [0.677, 0.786] |  |
| self_pairs_included | positives | DDI-MedLine | 49 | 44 | 23 | 0.523 | [0.379, 0.662] | 0.469 | [0.337, 0.606] |  |

## Reproduction of stored values

| value | recomputed (listed, resolvable, n) | recomputed value | stored | match |
| --- | --- | --- | --- | --- |
| MedLine negatives, self pairs excluded, listed over resolvable | 101, 196, 229 | 0.515 | {"listed": 101, "resolvable": 196, "value": 0.515, "ci95": [0.446, 0.584]} | True |
| pooled negatives, self pairs excluded, listed over resolvable (0.763 in the abstract) | 1609, 2108, 2150 | 0.763 | {"resolvable": 2108, "value": 0.763} | True |
| pooled positives, listed over resolvable (0.727) | 263, 362, 371 | 0.727 | {"resolvable": 362, "value": 0.727} | True |
| DDI-DrugBank negatives, self pairs excluded, listed over all pairs (0.785, the AUROC table false positive rate) | 1508, 1912, 1921 | 0.785 | {"value": 0.785} | True |
| DDI-DrugBank positives, listed over all pairs (0.763, the AUROC table true positive rate) | 222, 291, 291 | 0.763 | {"value": 0.763} | True |

## Which row each existing value uses

| existing value | row | denominator |
| --- | --- | --- |
| 0.763 (negatives) | self_pairs_excluded / negatives / pooled | resolvable pairs |
| 0.727 | self_pairs_excluded / positives / pooled | resolvable pairs (positives have no self pairs) |
| 0.785 | self_pairs_excluded / negatives / DDI-DrugBank | all pairs, unresolvable counted as not listed |
| 0.763 (true positive rate) | self_pairs_excluded / positives / DDI-DrugBank | all pairs; equal to the resolvable denominator here |

