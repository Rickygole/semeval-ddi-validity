# Preregistered decisions

| id | cohort | statistic | value | ci90 | ci95 | upper95 | p_tost | p_holm | decision | detail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Older-clean | within-drug AUROC | 0.452 | [0.395, 0.509] | [0.389, 0.518] | 0.509 | 0.061 | 0.183 | inconclusive | b2mixed names only, seeds [1, 2, 3, 4, 42], n=1832, 128 drugs |
| H1-novel | Novel | within-drug AUROC | 0.523 | [0.411, 0.626] | [0.397, 0.650] | 0.626 | NA | NA | estimate only (no equivalence test) | b2mixed names only, seeds [1, 2, 3, 4, 42], n=438, 48 drugs; upper95 one-sided 0.626 |
| H1-pooled | Novel + Older-clean | within-drug AUROC | 0.461 | [0.410, 0.511] | [0.399, 0.520] | 0.511 | 0.028 | NA | descriptive, secondary (no pre-registered decision rule) | secondary, outside the Holm family, n=2270, 176 drugs |
| H1-sensitivity | Older-clean sensitivity | within-drug AUROC | 0.453 | [0.394, 0.511] | [0.379, 0.522] | 0.511 | 0.078 | NA | sensitivity, not preregistered (no decision rule) | b2mixed names only, Older-clean without clopidogrel bisulfate, perindopril erbumine, peginterferon alfa-2a, calcitonin, esmolol (SemEval vocabulary drugs the filter missed), n=1754, 123 drugs, outside the Holm family |
| H2a | test-time masking of the sentence-trained model | masked F1 ratio and flip rates | ratio=0.028, vocab=0.057, novel=0.054, pseudo=0.059 | NA | NA | NA | NA | NA | falsified | b2sentence, seeds [1, 2, 3, 4, 42] |
| H2b | masked-trained model | masked F1 ratio and flip rates | ratio=6.008, vocab=0.064, novel=0.072, pseudo=0.072 | NA | NA | NA | NA | NA | supported | b2masked, seeds [1, 2, 3, 4, 42]; seed-mean ratio is the preregistered value; median ratio 1.581, ratio of mean F1s 1.868, per-seed ratio range 1.364 to 23.939; per seed (flips vocab/novel/pseudo): s1 ratio 23.939 flips 0.028/0.024/0.031; s2 ratio 1.668 flips 0.047/0.043/0.049; s3 ratio 1.364 flips 0.063/0.076/0.073; s4 ratio 1.489 flips 0.090/0.108/0.103 (over 0.10: novel, pseudo); s42 ratio 1.581 flips 0.092/0.110/0.106 (over 0.10: novel, pseudo); the seed-mean aggregation was not preregistered |
| H3 | OOD swap | pooled AUROC | 0.503 | [0.472, 0.537] | [0.464, 0.545] | 0.537 | NA | NA | descriptive only | b2sentence, seeds [1, 2, 3, 4, 42], no p-value, outside the Holm family |
| H4 | cohort comparison | Older-clean minus Novel within-drug AUROC | -0.071 | [-0.192, 0.045] | [-0.220, 0.068] | 0.045 | 0.339 | 0.339 | inconclusive | Older-clean 0.452 vs Novel 0.523; equivalence of the difference within +/-0.10 |
| H5 | Novel | AUROC and MCC | 0.621, 0.167 | [0.568, 0.678] | [0.557, 0.687] | 0.678 | NA | NA | falsified | below either threshold: null results uninterpretable |
| H6 | Novel | within-drug AUROC | 0.519 | [0.421, 0.627] | [0.393, 0.647] | 0.627 | 0.102 | 0.204 | inconclusive | krag hybrid k5 c400, seeds [1, 2, 3, 4, 42], upper95 one-sided 0.627 |

OOD hypotheses use the within-drug AUROC with two-way cluster bootstrap intervals over OOD drugs and partners. A decision needs all five seeds (42, 1, 2, 3, 4); otherwise it is pending and the estimate is provisional. Older-clean is primary for H1; Novel is an estimate with a one-sided 95% upper bound. The Holm family is H1, H4 and H6; pending tests count as p = 1. H2a is test-time masking of the sentence-trained model, H2b the masked-trained model; neither is preferred. H3 is descriptive. H1-novel and H1-pooled are secondary rows. H1-sensitivity is a sensitivity analysis, not preregistered: Older-clean without five SemEval-vocabulary drugs the filter missed.

## Label tiers for the primary systems

| group | key | cohort | tier | status | n_seeds | n | n_drugs | n_drugs_contributing | auroc_within | auroc_pooled | lo90 | hi90 | lo95 | hi95 | upper95_one_sided | neg_disagreement_rate | expected_observed_if_true_070 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed/biomedbert | ood_empty | novel | A | ok | 5 | 438 | 48 | 48 | 0.523 | 0.529 | 0.411 | 0.626 | 0.397 | 0.650 | 0.626 | 0.367 | 0.627 |
| b2mixed/biomedbert | ood_empty | novel | B | ok | 5 | 316 | 48 | 40 | 0.533 | 0.551 | 0.383 | 0.682 | 0.357 | 0.714 | 0.682 | 0.000 | 0.700 |
| b2mixed/biomedbert | oodold_empty | older_full | A | ok | 5 | 1944 | 135 | 135 | 0.455 | 0.452 | 0.404 | 0.508 | 0.396 | 0.517 | 0.508 | 0.384 | 0.623 |
| b2mixed/biomedbert | oodold_empty | older_full | B | ok | 5 | 1254 | 135 | 95 | 0.397 | 0.399 | 0.310 | 0.491 | 0.293 | 0.512 | 0.491 | 0.000 | 0.700 |
| b2mixed/biomedbert | oodold_empty | older_clean | A | ok | 5 | 1832 | 128 | 128 | 0.452 | 0.444 | 0.395 | 0.509 | 0.389 | 0.518 | 0.509 | 0.404 | 0.619 |
| b2mixed/biomedbert | oodold_empty | older_clean | B | ok | 5 | 1191 | 128 | 95 | 0.397 | 0.391 | 0.308 | 0.493 | 0.289 | 0.514 | 0.493 | 0.000 | 0.700 |
| krag/biomedbert/hybrid-k5-c400 | ood | novel | A | ok | 5 | 438 | 48 | 48 | 0.519 | 0.496 | 0.421 | 0.627 | 0.393 | 0.647 | 0.627 | 0.367 | 0.627 |
| krag/biomedbert/hybrid-k5-c400 | ood | novel | B | ok | 5 | 316 | 48 | 40 | 0.552 | 0.555 | 0.397 | 0.692 | 0.367 | 0.725 | 0.692 | 0.000 | 0.700 |
