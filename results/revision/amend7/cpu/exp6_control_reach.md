# Experiment 6: what the failed positive control could see (Novel, n = 438)

Older cohort: not available (0 of 135 Older drugs have chunks in the retrieval index).

`partner_in_own_label_*` is a construction leak: a retrieved passage from the OOD drug's own label names the partner. Negatives are built from partners the drug's label never names, so this rule cannot fire on a negative and any positive it reaches is answered by construction.

## contaminated index

n = 438 (148 positive, 290 negative); 35 inputs truncated at 512 tokens.

| feature | positives | negatives | share pos | share neg | rule AUROC within | 95% CI | rule AUROC pooled | 95% CI | MCC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| di_chunk_of_ood_drug | 33 | 3 | 0.223 | 0.010 | 0.604 | [0.527, 0.703] | 0.606 | [0.539, 0.690] | 0.366 |
| partner_in_full_chunks | 97 | 67 | 0.655 | 0.231 | 0.717 | [0.597, 0.821] | 0.712 | [0.616, 0.799] | 0.415 |
| partner_in_first400 | 68 | 59 | 0.459 | 0.203 | 0.635 | [0.510, 0.737] | 0.628 | [0.529, 0.717] | 0.267 |
| partner_in_512_tokens | 68 | 59 | 0.459 | 0.203 | 0.635 | [0.510, 0.737] | 0.628 | [0.529, 0.717] | 0.267 |
| partner_in_di_chunk_first400 | 20 | 0 | 0.135 | 0.000 | 0.587 | [0.517, 0.669] | 0.568 | [0.517, 0.630] | 0.306 |
| own_label_chunk_retrieved | 142 | 279 | 0.959 | 0.962 | 0.518 | [0.479, 0.567] | 0.499 | [0.467, 0.531] | -0.006 |
| partner_in_own_label_chunk | 72 | 0 | 0.486 | 0.000 | 0.762 | [0.653, 0.865] | 0.743 | [0.645, 0.839] | 0.621 |
| partner_in_own_label_first400 | 44 | 0 | 0.297 | 0.000 | 0.674 | [0.572, 0.777] | 0.649 | [0.569, 0.736] | 0.468 |

## hybrid index

n = 438 (148 positive, 290 negative); 56 inputs truncated at 512 tokens.

| feature | positives | negatives | share pos | share neg | rule AUROC within | 95% CI | rule AUROC pooled | 95% CI | MCC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| di_chunk_of_ood_drug | 0 | 0 | 0.000 | 0.000 | 0.500 | [0.500, 0.500] | 0.500 | [0.500, 0.500] | 0.000 |
| partner_in_full_chunks | 62 | 71 | 0.419 | 0.245 | 0.542 | [0.427, 0.639] | 0.587 | [0.504, 0.668] | 0.179 |
| partner_in_first400 | 48 | 68 | 0.324 | 0.234 | 0.501 | [0.396, 0.603] | 0.545 | [0.469, 0.619] | 0.096 |
| partner_in_512_tokens | 48 | 68 | 0.324 | 0.234 | 0.501 | [0.396, 0.603] | 0.545 | [0.469, 0.619] | 0.096 |
| partner_in_di_chunk_first400 | 0 | 0 | 0.000 | 0.000 | 0.500 | [0.500, 0.500] | 0.500 | [0.500, 0.500] | 0.000 |
| own_label_chunk_retrieved | 135 | 270 | 0.912 | 0.931 | 0.496 | [0.442, 0.548] | 0.491 | [0.435, 0.539] | -0.034 |
| partner_in_own_label_chunk | 23 | 0 | 0.155 | 0.000 | 0.571 | [0.522, 0.647] | 0.578 | [0.526, 0.647] | 0.330 |
| partner_in_own_label_first400 | 14 | 0 | 0.095 | 0.000 | 0.540 | [0.506, 0.596] | 0.547 | [0.510, 0.604] | 0.254 |

## SemEval test AUROC and best epoch per seed

| job | seed | SemEval test AUROC | best epoch | max epochs | best val macro F1 |
| --- | --- | --- | --- | --- | --- |
| krag-contaminated-k5-c400-biomedbert-s42 | 42 | 0.604 | 8 | 10 | 0.395 |
| krag-hybrid-k5-c400-biomedbert-s42 | 42 | 0.676 | 8 | 10 | 0.447 |
| b1names-biomedbert-s42 | 42 | 0.686 | 5 | 5 | 0.412 |
| krag-contaminated-k5-c400-biomedbert-s1 | 1 | 0.639 | 7 | 10 | 0.420 |
| krag-hybrid-k5-c400-biomedbert-s1 | 1 | 0.636 | 9 | 10 | 0.452 |
| b1names-biomedbert-s1 | 1 | 0.633 | 5 | 5 | 0.375 |
| krag-contaminated-k5-c400-biomedbert-s2 | 2 | 0.600 | 4 | 10 | 0.409 |
| krag-hybrid-k5-c400-biomedbert-s2 | 2 | 0.619 | 7 | 10 | 0.400 |
| b1names-biomedbert-s2 | 2 | 0.654 | 4 | 5 | 0.456 |
| krag-contaminated-k5-c400-biomedbert-s3 | 3 | 0.622 | 6 | 10 | 0.470 |
| krag-hybrid-k5-c400-biomedbert-s3 | 3 | 0.638 | 8 | 10 | 0.430 |
| b1names-biomedbert-s3 | 3 | 0.663 | 5 | 5 | 0.418 |
| krag-contaminated-k5-c400-biomedbert-s4 | 4 | 0.631 | 9 | 10 | 0.507 |
| krag-hybrid-k5-c400-biomedbert-s4 | 4 | 0.601 | 3 | 10 | 0.361 |
| b1names-biomedbert-s4 | 4 | 0.680 | 5 | 5 | 0.496 |
