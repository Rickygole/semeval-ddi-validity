# Experiment 7: the below-chance Older-clean result

Exploratory and post hoc. Criteria were written to `exp7_criteria.json` before any statistic below was computed. Primary system b2mixed-biomedbert (seed-averaged, names only); tiers A and B are co-primary. Verdicts answer the below-chance question for the primary system on Older-clean; rows for other systems and for Novel are for information.

## Verdicts for the primary system on Older-clean

| cause | tier A | tier B |
| --- | --- | --- |
| a (a_semeval_train_frequency) | rejected | rejected |
| b (b_partner_popularity_loo_positives) | rejected | rejected |
| c (c_partner_wordpieces) | rejected | rejected |
| e (e_shared_stem) | rejected | rejected |
| d (label-noise asymmetry, tier B versus tier A) | rejected | rejected |

(iii) test-label partner prior (leave-one-drug-out positive rate in the cohort), Older-clean within drug: tier A 0.088 [0.049, 0.130], tier B 0.053 [0.016, 0.102]; b2mixed within-drug Spearman with it 0.055 [-0.002, 0.119]; b2mixed partialled 0.484 (tier A).
(iii) label-free partner prior (share of vocabulary Drug Interactions sections naming the partner), Older-clean within drug: tier A 0.506 [0.431, 0.575], tier B 0.534 [0.417, 0.655]; b2mixed within-drug Spearman with it 0.257 [0.209, 0.304]; b2mixed partialled 0.447 (tier A).

## older_clean, tier A (n = 1832, 599 positive, 128 drugs)

| feature | cause | within-drug AUROC | 95% CI | mean pos | mean neg |
| --- | --- | --- | --- | --- | --- |
| a_semeval_train_frequency | a | 0.507 | [0.436, 0.570] | 4.193 | 4.185 |
| a2_semeval_train_positive_rate | a (secondary, no decision) | 0.517 | [0.459, 0.572] | 0.137 | 0.135 |
| b_partner_popularity_loo_positives | b | 0.449 | [0.371, 0.520] | 7.703 | 8.632 |
| iii_partner_prior_loo_rate | iii | 0.088 | [0.049, 0.130] | 0.234 | 0.372 |
| iii2_partner_prior_vocab_di | iii (label-free; added after the criteria were written, no decision) | 0.506 | [0.431, 0.575] | 0.086 | 0.085 |
| c_partner_wordpieces | c | 0.481 | [0.429, 0.536] | 2.316 | 2.324 |
| c2_partner_words | c (secondary, no decision) | 0.499 | [0.482, 0.514] | 1.022 | 1.024 |
| e_shared_stem | e (exploratory) | 0.509 | [0.496, 0.529] | 0.025 | 0.006 |

| system | raw within AUROC | 95% CI | feature | Spearman within | 95% CI | partialled AUROC | 95% CI | C1 | C2 | C3 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | a_semeval_train_frequency | 0.199 | [0.152, 0.245] | 0.445 | [0.383, 0.511] | False | False | False | rejected |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | a2_semeval_train_positive_rate | 0.403 | [0.356, 0.444] | 0.449 | [0.389, 0.519] |  |  |  |  |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | b_partner_popularity_loo_positives | 0.245 | [0.190, 0.299] | 0.460 | [0.399, 0.526] | False | True | False | rejected |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | iii_partner_prior_loo_rate | 0.055 | [-0.002, 0.119] | 0.484 | [0.418, 0.550] |  |  |  |  |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | iii2_partner_prior_vocab_di | 0.257 | [0.209, 0.304] | 0.447 | [0.385, 0.511] |  |  |  |  |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | c_partner_wordpieces | -0.253 | [-0.308, -0.193] | 0.438 | [0.376, 0.507] | False | False | False | rejected |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | c2_partner_words | -0.005 | [-0.058, 0.043] | 0.452 | [0.389, 0.519] |  |  |  |  |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | e_shared_stem | -0.150 | [-0.216, -0.080] | 0.458 | [0.396, 0.527] | False | True | False | rejected |
| b2mixed-biomedbert | 0.452 | [0.389, 0.518] | joint a+b+c+e | NA | NA | 0.455 | [0.396, 0.521] |  |  |  |  |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | a_semeval_train_frequency | 0.222 | [0.169, 0.274] | 0.460 | [0.398, 0.520] | False | False | False | rejected |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | a2_semeval_train_positive_rate | 0.471 | [0.432, 0.506] | 0.460 | [0.398, 0.521] |  |  |  |  |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | b_partner_popularity_loo_positives | 0.255 | [0.205, 0.303] | 0.470 | [0.408, 0.531] | False | True | False | rejected |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | iii_partner_prior_loo_rate | 0.037 | [-0.024, 0.107] | 0.477 | [0.415, 0.535] |  |  |  |  |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | iii2_partner_prior_vocab_di | 0.268 | [0.216, 0.316] | 0.458 | [0.398, 0.520] |  |  |  |  |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | c_partner_wordpieces | -0.249 | [-0.307, -0.181] | 0.451 | [0.386, 0.509] | False | False | False | rejected |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | c2_partner_words | 0.026 | [-0.024, 0.075] | 0.463 | [0.398, 0.521] |  |  |  |  |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | e_shared_stem | -0.119 | [-0.176, -0.059] | 0.467 | [0.404, 0.525] | False | True | False | rejected |
| b1names-biomedbert | 0.463 | [0.398, 0.521] | joint a+b+c+e | NA | NA | 0.464 | [0.400, 0.524] |  |  |  |  |
| llm-qwen-names | 0.602 | [0.533, 0.667] | a_semeval_train_frequency | 0.483 | [0.449, 0.517] | 0.630 | [0.566, 0.696] | False | False | False | rejected |
| llm-qwen-names | 0.602 | [0.533, 0.667] | a2_semeval_train_positive_rate | 0.154 | [0.106, 0.199] | 0.601 | [0.533, 0.667] |  |  |  |  |
| llm-qwen-names | 0.602 | [0.533, 0.667] | b_partner_popularity_loo_positives | 0.554 | [0.506, 0.596] | 0.652 | [0.589, 0.717] | False | True | False | rejected |
| llm-qwen-names | 0.602 | [0.533, 0.667] | iii_partner_prior_loo_rate | -0.234 | [-0.294, -0.172] | 0.558 | [0.488, 0.623] |  |  |  |  |
| llm-qwen-names | 0.602 | [0.533, 0.667] | iii2_partner_prior_vocab_di | 0.570 | [0.536, 0.605] | 0.621 | [0.554, 0.691] |  |  |  |  |
| llm-qwen-names | 0.602 | [0.533, 0.667] | c_partner_wordpieces | 0.066 | [0.023, 0.110] | 0.604 | [0.535, 0.669] | False | True | False | rejected |
| llm-qwen-names | 0.602 | [0.533, 0.667] | c2_partner_words | -0.079 | [-0.117, -0.036] | 0.601 | [0.532, 0.667] |  |  |  |  |
| llm-qwen-names | 0.602 | [0.533, 0.667] | e_shared_stem | 0.038 | [-0.040, 0.105] | 0.602 | [0.533, 0.666] | False | False | False | rejected |
| llm-qwen-names | 0.602 | [0.533, 0.667] | joint a+b+c+e | NA | NA | 0.662 | [0.603, 0.727] |  |  |  |  |
| DrugBank lookup | 0.641 | [0.595, 0.689] | a_semeval_train_frequency | 0.093 | [0.015, 0.167] | 0.640 | [0.570, 0.712] | False | False | False | rejected |
| DrugBank lookup | 0.641 | [0.595, 0.689] | a2_semeval_train_positive_rate | 0.029 | [-0.029, 0.083] | 0.628 | [0.565, 0.695] |  |  |  |  |
| DrugBank lookup | 0.641 | [0.595, 0.689] | b_partner_popularity_loo_positives | 0.007 | [-0.065, 0.076] | 0.662 | [0.589, 0.740] | False | False | False | rejected |
| DrugBank lookup | 0.641 | [0.595, 0.689] | iii_partner_prior_loo_rate | -0.249 | [-0.314, -0.187] | 0.398 | [0.315, 0.479] |  |  |  |  |
| DrugBank lookup | 0.641 | [0.595, 0.689] | iii2_partner_prior_vocab_di | 0.078 | [0.006, 0.149] | 0.640 | [0.567, 0.715] |  |  |  |  |
| DrugBank lookup | 0.641 | [0.595, 0.689] | c_partner_wordpieces | -0.002 | [-0.056, 0.057] | 0.624 | [0.561, 0.691] | False | False | False | rejected |
| DrugBank lookup | 0.641 | [0.595, 0.689] | c2_partner_words | -0.035 | [-0.097, 0.025] | 0.642 | [0.593, 0.693] |  |  |  |  |
| DrugBank lookup | 0.641 | [0.595, 0.689] | e_shared_stem | 0.004 | [-0.064, 0.078] | 0.645 | [0.598, 0.695] | False | False | False | rejected |
| DrugBank lookup | 0.641 | [0.595, 0.689] | joint a+b+c+e | NA | NA | 0.638 | [0.569, 0.707] |  |  |  |  |

## older_clean, tier B (n = 1191, 457 positive, 128 drugs)

| feature | cause | within-drug AUROC | 95% CI | mean pos | mean neg |
| --- | --- | --- | --- | --- | --- |
| a_semeval_train_frequency | a | 0.543 | [0.411, 0.662] | 4.288 | 4.119 |
| a2_semeval_train_positive_rate | a (secondary, no decision) | 0.517 | [0.409, 0.614] | 0.135 | 0.132 |
| b_partner_popularity_loo_positives | b | 0.438 | [0.308, 0.564] | 8.044 | 8.805 |
| iii_partner_prior_loo_rate | iii | 0.053 | [0.016, 0.102] | 0.239 | 0.375 |
| iii2_partner_prior_vocab_di | iii (label-free; added after the criteria were written, no decision) | 0.534 | [0.417, 0.655] | 0.090 | 0.083 |
| c_partner_wordpieces | c | 0.501 | [0.399, 0.594] | 2.346 | 2.343 |
| c2_partner_words | c (secondary, no decision) | 0.493 | [0.462, 0.519] | 1.013 | 1.026 |
| e_shared_stem | e (exploratory) | 0.512 | [0.488, 0.541] | 0.022 | 0.005 |

| system | raw within AUROC | 95% CI | feature | Spearman within | 95% CI | partialled AUROC | 95% CI | C1 | C2 | C3 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | a_semeval_train_frequency | 0.199 | [0.119, 0.275] | 0.372 | [0.273, 0.479] | False | False | False | rejected |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | a2_semeval_train_positive_rate | 0.379 | [0.313, 0.442] | 0.393 | [0.294, 0.503] |  |  |  |  |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | b_partner_popularity_loo_positives | 0.223 | [0.160, 0.287] | 0.389 | [0.283, 0.506] | False | True | False | rejected |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | iii_partner_prior_loo_rate | 0.068 | [-0.010, 0.147] | 0.439 | [0.332, 0.556] |  |  |  |  |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | iii2_partner_prior_vocab_di | 0.228 | [0.160, 0.292] | 0.370 | [0.271, 0.484] |  |  |  |  |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | c_partner_wordpieces | -0.208 | [-0.284, -0.131] | 0.382 | [0.285, 0.494] | False | True | False | rejected |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | c2_partner_words | -0.036 | [-0.096, 0.024] | 0.396 | [0.288, 0.516] |  |  |  |  |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | e_shared_stem | -0.169 | [-0.244, -0.077] | 0.402 | [0.296, 0.516] | False | True | False | rejected |
| b2mixed-biomedbert | 0.397 | [0.289, 0.514] | joint a+b+c+e | NA | NA | 0.392 | [0.296, 0.504] |  |  |  |  |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | a_semeval_train_frequency | 0.236 | [0.158, 0.312] | 0.396 | [0.301, 0.498] | False | False | False | rejected |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | a2_semeval_train_positive_rate | 0.458 | [0.394, 0.516] | 0.416 | [0.321, 0.521] |  |  |  |  |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | b_partner_popularity_loo_positives | 0.276 | [0.214, 0.339] | 0.410 | [0.317, 0.514] | False | True | False | rejected |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | iii_partner_prior_loo_rate | 0.022 | [-0.053, 0.104] | 0.441 | [0.342, 0.553] |  |  |  |  |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | iii2_partner_prior_vocab_di | 0.281 | [0.207, 0.345] | 0.389 | [0.297, 0.488] |  |  |  |  |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | c_partner_wordpieces | -0.210 | [-0.277, -0.132] | 0.402 | [0.304, 0.508] | False | True | False | rejected |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | c2_partner_words | -0.021 | [-0.088, 0.050] | 0.419 | [0.320, 0.531] |  |  |  |  |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | e_shared_stem | -0.128 | [-0.208, -0.017] | 0.423 | [0.322, 0.532] | False | True | False | rejected |
| b1names-biomedbert | 0.419 | [0.320, 0.531] | joint a+b+c+e | NA | NA | 0.406 | [0.313, 0.507] |  |  |  |  |
| llm-qwen-names | 0.660 | [0.543, 0.767] | a_semeval_train_frequency | 0.473 | [0.417, 0.527] | 0.668 | [0.564, 0.768] | False | False | False | rejected |
| llm-qwen-names | 0.660 | [0.543, 0.767] | a2_semeval_train_positive_rate | 0.195 | [0.132, 0.259] | 0.660 | [0.542, 0.767] |  |  |  |  |
| llm-qwen-names | 0.660 | [0.543, 0.767] | b_partner_popularity_loo_positives | 0.562 | [0.492, 0.625] | 0.734 | [0.630, 0.819] | False | True | False | rejected |
| llm-qwen-names | 0.660 | [0.543, 0.767] | iii_partner_prior_loo_rate | -0.245 | [-0.327, -0.162] | 0.612 | [0.487, 0.716] |  |  |  |  |
| llm-qwen-names | 0.660 | [0.543, 0.767] | iii2_partner_prior_vocab_di | 0.577 | [0.532, 0.621] | 0.688 | [0.586, 0.781] |  |  |  |  |
| llm-qwen-names | 0.660 | [0.543, 0.767] | c_partner_wordpieces | 0.042 | [-0.014, 0.095] | 0.663 | [0.547, 0.769] | False | False | False | rejected |
| llm-qwen-names | 0.660 | [0.543, 0.767] | c2_partner_words | -0.073 | [-0.131, -0.017] | 0.658 | [0.542, 0.764] |  |  |  |  |
| llm-qwen-names | 0.660 | [0.543, 0.767] | e_shared_stem | 0.066 | [-0.043, 0.141] | 0.659 | [0.542, 0.765] | False | False | False | rejected |
| llm-qwen-names | 0.660 | [0.543, 0.767] | joint a+b+c+e | NA | NA | 0.729 | [0.626, 0.809] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | a_semeval_train_frequency | 0.026 | [-0.107, 0.142] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | a2_semeval_train_positive_rate | 0.018 | [-0.071, 0.098] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | b_partner_popularity_loo_positives | -0.109 | [-0.230, 0.014] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | iii_partner_prior_loo_rate | -0.581 | [-0.643, -0.512] | 0.989 | [0.957, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | iii2_partner_prior_vocab_di | 0.015 | [-0.100, 0.131] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | c_partner_wordpieces | 0.006 | [-0.054, 0.075] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | c2_partner_words | -0.039 | [-0.111, 0.037] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | e_shared_stem | 0.076 | [-0.026, 0.180] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | joint a+b+c+e | NA | NA | 1.000 | [1.000, 1.000] |  |  |  |  |

### Cause d (label-noise asymmetry), older_clean

| system | tier A gap | tier B gap | tier B CI contains 0.5 | contradicted vs confirmed negatives AUROC | verdict |
| --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.048 | 0.103 | True | 0.468 (n 497/734) | rejected |
| b1names-biomedbert | 0.037 | 0.081 | True | 0.451 (n 497/734) | rejected |
| llm-qwen-names | 0.102 | 0.160 | False | 0.594 (n 497/734) | rejected |
| DrugBank lookup | 0.141 | 0.500 | False | NA (n /) | rejected |

## novel, tier A (n = 438, 148 positive, 48 drugs)

| feature | cause | within-drug AUROC | 95% CI | mean pos | mean neg |
| --- | --- | --- | --- | --- | --- |
| a_semeval_train_frequency | a | 0.508 | [0.365, 0.647] | 4.006 | 3.978 |
| a2_semeval_train_positive_rate | a (secondary, no decision) | 0.474 | [0.354, 0.590] | 0.134 | 0.134 |
| b_partner_popularity_loo_positives | b | 0.409 | [0.263, 0.534] | 2.757 | 3.607 |
| iii_partner_prior_loo_rate | iii | 0.028 | [0.000, 0.096] | 0.187 | 0.415 |
| iii2_partner_prior_vocab_di | iii (label-free; added after the criteria were written, no decision) | 0.522 | [0.367, 0.671] | 0.083 | 0.081 |
| c_partner_wordpieces | c | 0.512 | [0.386, 0.627] | 2.236 | 2.241 |
| c2_partner_words | c (secondary, no decision) | 0.501 | [0.460, 0.546] | 1.041 | 1.041 |
| e_shared_stem | e (exploratory) | 0.510 | [0.497, 0.539] | 0.034 | 0.003 |

| system | raw within AUROC | 95% CI | feature | Spearman within | 95% CI | partialled AUROC | 95% CI | C1 | C2 | C3 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | a_semeval_train_frequency | 0.211 | [0.113, 0.305] | 0.515 | [0.381, 0.643] | False | False | False | rejected |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | a2_semeval_train_positive_rate | 0.400 | [0.301, 0.492] | 0.542 | [0.409, 0.671] |  |  |  |  |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | b_partner_popularity_loo_positives | 0.112 | [0.019, 0.210] | 0.535 | [0.396, 0.668] | False | True | False | rejected |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | iii_partner_prior_loo_rate | -0.046 | [-0.137, 0.038] | 0.523 | [0.397, 0.650] |  |  |  |  |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | iii2_partner_prior_vocab_di | 0.225 | [0.129, 0.325] | 0.511 | [0.380, 0.638] |  |  |  |  |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | c_partner_wordpieces | -0.335 | [-0.435, -0.209] | 0.520 | [0.386, 0.651] | False | True | False | rejected |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | c2_partner_words | 0.077 | [-0.016, 0.161] | 0.526 | [0.400, 0.654] |  |  |  |  |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | e_shared_stem | -0.157 | [-0.241, -0.056] | 0.536 | [0.405, 0.666] | False | True | False | rejected |
| b2mixed-biomedbert | 0.523 | [0.397, 0.650] | joint a+b+c+e | NA | NA | 0.523 | [0.391, 0.649] |  |  |  |  |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | a_semeval_train_frequency | 0.280 | [0.180, 0.372] | 0.502 | [0.376, 0.628] | False | False | True | rejected |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | a2_semeval_train_positive_rate | 0.406 | [0.343, 0.461] | 0.511 | [0.383, 0.634] |  |  |  |  |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | b_partner_popularity_loo_positives | 0.258 | [0.173, 0.355] | 0.547 | [0.410, 0.668] | False | True | False | rejected |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | iii_partner_prior_loo_rate | -0.033 | [-0.126, 0.061] | 0.506 | [0.374, 0.627] |  |  |  |  |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | iii2_partner_prior_vocab_di | 0.307 | [0.214, 0.396] | 0.509 | [0.376, 0.626] |  |  |  |  |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | c_partner_wordpieces | -0.401 | [-0.508, -0.265] | 0.517 | [0.373, 0.644] | False | True | False | rejected |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | c2_partner_words | 0.072 | [-0.032, 0.170] | 0.511 | [0.379, 0.639] |  |  |  |  |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | e_shared_stem | -0.132 | [-0.202, -0.056] | 0.523 | [0.388, 0.642] | False | True | False | rejected |
| b1names-biomedbert | 0.514 | [0.384, 0.635] | joint a+b+c+e | NA | NA | 0.547 | [0.394, 0.678] |  |  |  |  |
| llm-qwen-names | 0.579 | [0.440, 0.713] | a_semeval_train_frequency | 0.336 | [0.227, 0.441] | 0.604 | [0.479, 0.723] | False | False | False | rejected |
| llm-qwen-names | 0.579 | [0.440, 0.713] | a2_semeval_train_positive_rate | 0.102 | [0.005, 0.199] | 0.579 | [0.443, 0.711] |  |  |  |  |
| llm-qwen-names | 0.579 | [0.440, 0.713] | b_partner_popularity_loo_positives | 0.257 | [0.178, 0.330] | 0.614 | [0.488, 0.740] | False | True | False | rejected |
| llm-qwen-names | 0.579 | [0.440, 0.713] | iii_partner_prior_loo_rate | -0.064 | [-0.168, 0.056] | 0.561 | [0.419, 0.701] |  |  |  |  |
| llm-qwen-names | 0.579 | [0.440, 0.713] | iii2_partner_prior_vocab_di | 0.465 | [0.385, 0.551] | 0.590 | [0.458, 0.723] |  |  |  |  |
| llm-qwen-names | 0.579 | [0.440, 0.713] | c_partner_wordpieces | -0.019 | [-0.121, 0.087] | 0.580 | [0.443, 0.715] | False | False | False | rejected |
| llm-qwen-names | 0.579 | [0.440, 0.713] | c2_partner_words | -0.073 | [-0.144, -0.004] | 0.581 | [0.453, 0.714] |  |  |  |  |
| llm-qwen-names | 0.579 | [0.440, 0.713] | e_shared_stem | -0.012 | [-0.051, 0.035] | 0.580 | [0.440, 0.714] | False | False | False | rejected |
| llm-qwen-names | 0.579 | [0.440, 0.713] | joint a+b+c+e | NA | NA | 0.617 | [0.484, 0.751] |  |  |  |  |
| DrugBank lookup | 0.729 | [0.642, 0.808] | a_semeval_train_frequency | 0.098 | [-0.023, 0.217] | 0.734 | [0.596, 0.849] | False | False | False | rejected |
| DrugBank lookup | 0.729 | [0.642, 0.808] | a2_semeval_train_positive_rate | 0.059 | [-0.061, 0.176] | 0.733 | [0.608, 0.845] |  |  |  |  |
| DrugBank lookup | 0.729 | [0.642, 0.808] | b_partner_popularity_loo_positives | 0.049 | [-0.074, 0.167] | 0.800 | [0.695, 0.894] | False | False | False | rejected |
| DrugBank lookup | 0.729 | [0.642, 0.808] | iii_partner_prior_loo_rate | -0.387 | [-0.494, -0.265] | 0.499 | [0.340, 0.650] |  |  |  |  |
| DrugBank lookup | 0.729 | [0.642, 0.808] | iii2_partner_prior_vocab_di | 0.078 | [-0.036, 0.199] | 0.722 | [0.584, 0.843] |  |  |  |  |
| DrugBank lookup | 0.729 | [0.642, 0.808] | c_partner_wordpieces | -0.044 | [-0.131, 0.045] | 0.750 | [0.624, 0.845] | False | False | False | rejected |
| DrugBank lookup | 0.729 | [0.642, 0.808] | c2_partner_words | -0.055 | [-0.155, 0.064] | 0.732 | [0.644, 0.812] |  |  |  |  |
| DrugBank lookup | 0.729 | [0.642, 0.808] | e_shared_stem | 0.003 | [-0.017, 0.017] | 0.738 | [0.651, 0.815] | False | False | False | rejected |
| DrugBank lookup | 0.729 | [0.642, 0.808] | joint a+b+c+e | NA | NA | 0.764 | [0.636, 0.868] |  |  |  |  |

## novel, tier B (n = 316, 133 positive, 48 drugs)

| feature | cause | within-drug AUROC | 95% CI | mean pos | mean neg |
| --- | --- | --- | --- | --- | --- |
| a_semeval_train_frequency | a | 0.525 | [0.310, 0.732] | 4.064 | 3.932 |
| a2_semeval_train_positive_rate | a (secondary, no decision) | 0.474 | [0.311, 0.656] | 0.142 | 0.126 |
| b_partner_popularity_loo_positives | b | 0.480 | [0.273, 0.665] | 2.947 | 3.596 |
| iii_partner_prior_loo_rate | iii | 0.025 | [0.000, 0.099] | 0.192 | 0.420 |
| iii2_partner_prior_vocab_di | iii (label-free; added after the criteria were written, no decision) | 0.536 | [0.315, 0.745] | 0.084 | 0.077 |
| c_partner_wordpieces | c | 0.478 | [0.314, 0.646] | 2.203 | 2.279 |
| c2_partner_words | c (secondary, no decision) | 0.493 | [0.431, 0.555] | 1.038 | 1.044 |
| e_shared_stem | e (exploratory) | 0.500 | [0.490, 0.511] | 0.038 | 0.005 |

| system | raw within AUROC | 95% CI | feature | Spearman within | 95% CI | partialled AUROC | 95% CI | C1 | C2 | C3 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | a_semeval_train_frequency | 0.269 | [0.158, 0.371] | 0.505 | [0.322, 0.690] | False | False | True | rejected |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | a2_semeval_train_positive_rate | 0.402 | [0.293, 0.502] | 0.557 | [0.363, 0.729] |  |  |  |  |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | b_partner_popularity_loo_positives | 0.131 | [0.036, 0.245] | 0.519 | [0.332, 0.691] | False | True | False | rejected |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | iii_partner_prior_loo_rate | -0.030 | [-0.124, 0.076] | 0.538 | [0.362, 0.724] |  |  |  |  |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | iii2_partner_prior_vocab_di | 0.281 | [0.147, 0.402] | 0.514 | [0.336, 0.696] |  |  |  |  |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | c_partner_wordpieces | -0.365 | [-0.493, -0.194] | 0.519 | [0.338, 0.696] | False | False | False | rejected |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | c2_partner_words | 0.120 | [-0.003, 0.208] | 0.536 | [0.362, 0.719] |  |  |  |  |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | e_shared_stem | -0.184 | [-0.282, -0.082] | 0.533 | [0.357, 0.714] | False | False | False | rejected |
| b2mixed-biomedbert | 0.533 | [0.357, 0.714] | joint a+b+c+e | NA | NA | 0.516 | [0.335, 0.696] |  |  |  |  |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | a_semeval_train_frequency | 0.296 | [0.188, 0.398] | 0.519 | [0.335, 0.700] | False | False | False | rejected |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | a2_semeval_train_positive_rate | 0.392 | [0.300, 0.470] | 0.536 | [0.338, 0.730] |  |  |  |  |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | b_partner_popularity_loo_positives | 0.213 | [0.110, 0.341] | 0.555 | [0.350, 0.752] | False | True | False | rejected |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | iii_partner_prior_loo_rate | 0.024 | [-0.115, 0.172] | 0.555 | [0.361, 0.751] |  |  |  |  |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | iii2_partner_prior_vocab_di | 0.321 | [0.213, 0.423] | 0.533 | [0.341, 0.721] |  |  |  |  |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | c_partner_wordpieces | -0.407 | [-0.553, -0.233] | 0.514 | [0.320, 0.711] | False | False | True | rejected |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | c2_partner_words | 0.125 | [-0.019, 0.233] | 0.527 | [0.339, 0.723] |  |  |  |  |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | e_shared_stem | -0.149 | [-0.244, -0.075] | 0.530 | [0.341, 0.724] | False | False | False | rejected |
| b1names-biomedbert | 0.530 | [0.341, 0.724] | joint a+b+c+e | NA | NA | 0.552 | [0.354, 0.731] |  |  |  |  |
| llm-qwen-names | 0.577 | [0.397, 0.736] | a_semeval_train_frequency | 0.390 | [0.236, 0.524] | 0.604 | [0.422, 0.780] | False | False | False | rejected |
| llm-qwen-names | 0.577 | [0.397, 0.736] | a2_semeval_train_positive_rate | 0.213 | [0.109, 0.322] | 0.582 | [0.401, 0.750] |  |  |  |  |
| llm-qwen-names | 0.577 | [0.397, 0.736] | b_partner_popularity_loo_positives | 0.325 | [0.221, 0.417] | 0.577 | [0.388, 0.751] | False | True | False | rejected |
| llm-qwen-names | 0.577 | [0.397, 0.736] | iii_partner_prior_loo_rate | -0.026 | [-0.191, 0.156] | 0.571 | [0.391, 0.735] |  |  |  |  |
| llm-qwen-names | 0.577 | [0.397, 0.736] | iii2_partner_prior_vocab_di | 0.495 | [0.377, 0.618] | 0.587 | [0.385, 0.779] |  |  |  |  |
| llm-qwen-names | 0.577 | [0.397, 0.736] | c_partner_wordpieces | -0.027 | [-0.142, 0.103] | 0.585 | [0.411, 0.747] | False | False | False | rejected |
| llm-qwen-names | 0.577 | [0.397, 0.736] | c2_partner_words | -0.058 | [-0.128, 0.009] | 0.574 | [0.406, 0.731] |  |  |  |  |
| llm-qwen-names | 0.577 | [0.397, 0.736] | e_shared_stem | -0.064 | [-0.122, 0.000] | 0.574 | [0.395, 0.735] | False | False | False | rejected |
| llm-qwen-names | 0.577 | [0.397, 0.736] | joint a+b+c+e | NA | NA | 0.582 | [0.398, 0.755] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | a_semeval_train_frequency | 0.046 | [-0.133, 0.226] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | a2_semeval_train_positive_rate | -0.044 | [-0.145, 0.069] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | b_partner_popularity_loo_positives | -0.012 | [-0.172, 0.132] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | iii_partner_prior_loo_rate | -0.650 | [-0.733, -0.547] | 0.891 | [0.698, 0.977] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | iii2_partner_prior_vocab_di | 0.040 | [-0.147, 0.243] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | c_partner_wordpieces | -0.041 | [-0.160, 0.087] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | c2_partner_words | -0.044 | [-0.202, 0.128] | 1.000 | [1.000, 1.000] |  |  |  |  |
| DrugBank lookup | 1.000 | [1.000, 1.000] | e_shared_stem | 0.004 | [-0.027, 0.026] | 1.000 | [1.000, 1.000] | False | False | False | rejected |
| DrugBank lookup | 1.000 | [1.000, 1.000] | joint a+b+c+e | NA | NA | 1.000 | [1.000, 1.000] |  |  |  |  |

### Cause d (label-noise asymmetry), novel

| system | tier A gap | tier B gap | tier B CI contains 0.5 | contradicted vs confirmed negatives AUROC | verdict |
| --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 0.023 | 0.033 | True | 0.573 (n 106/183) | rejected |
| b1names-biomedbert | 0.014 | 0.030 | True | 0.566 (n 106/183) | rejected |
| llm-qwen-names | 0.079 | 0.077 | True | 0.513 (n 106/183) | partial |
| DrugBank lookup | 0.229 | 0.500 | False | NA (n /) | rejected |

## (i) Paired within-drug differences (shared two-way draws)

| cohort | tier | comparison | n | drugs | b2mixed | other | difference | 95% CI | share of draws above 0 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| older_clean | A | b2mixed-biomedbert minus llm-qwen-names | 1832 | 128 | 0.452 | 0.602 | -0.150 | [-0.242, -0.054] | 0.002 |  |
| older_clean | A | b2mixed-biomedbert minus DrugBank lookup | 1832 | 128 | 0.452 | 0.641 | -0.189 | [-0.285, -0.103] | 0.000 |  |
| older_clean | B | b2mixed-biomedbert minus llm-qwen-names | 1191 | 128 | 0.397 | 0.660 | -0.263 | [-0.418, -0.087] | 0.003 |  |
| older_clean | B | b2mixed-biomedbert minus DrugBank lookup | 1191 | 128 | 0.397 | 1.000 | -0.603 | [-0.711, -0.486] | 0.000 | DrugBank is circular on tier B (1.0 by construction) |
| novel | A | b2mixed-biomedbert minus llm-qwen-names | 438 | 48 | 0.523 | 0.579 | -0.055 | [-0.249, 0.152] | 0.251 |  |
| novel | A | b2mixed-biomedbert minus DrugBank lookup | 438 | 48 | 0.523 | 0.729 | -0.205 | [-0.372, -0.051] | 0.005 |  |
| novel | B | b2mixed-biomedbert minus llm-qwen-names | 316 | 48 | 0.533 | 0.577 | -0.044 | [-0.285, 0.221] | 0.358 |  |
| novel | B | b2mixed-biomedbert minus DrugBank lookup | 316 | 48 | 0.533 | 1.000 | -0.467 | [-0.643, -0.286] | 0.000 | DrugBank is circular on tier B (1.0 by construction) |

## (ii) Knowledge ceiling on tier A (a scorer that knows DrugBank exactly)

| cohort | n | drugs | c (positives listed) | r (negatives listed) | analytic pooled 0.5(1+c-r) | within-drug AUROC | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| older_clean | 1832 | 128 | 0.763 | 0.403 | 0.680 | 0.641 | [0.595, 0.689] |
| novel | 438 | 48 | 0.899 | 0.366 | 0.767 | 0.729 | [0.642, 0.808] |

## (iv) Confidently wrong

| system | set | n | negatives | share neg > 0.5 | share neg > 0.9 | ECE (10 bins) |
| --- | --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | SemEval test, sentence | 2810 | 2439 | 0.078 (191) | 0.035 (86) | 0.055 |
| b2mixed-biomedbert | SemEval test, names only | 2810 | 2439 | 0.068 (167) | 0.007 (18) | 0.098 |
| b2mixed-biomedbert | novel | 438 | 290 | 0.279 (81) | 0.007 (2) | 0.170 |
| b2mixed-biomedbert | older_clean | 1832 | 1233 | 0.214 (264) | 0.000 (0) | 0.221 |
| b2sentence-biomedbert | SemEval test, sentence | 2810 | 2439 | 0.079 (193) | 0.028 (68) | 0.060 |
| b2sentence-biomedbert | SemEval test, names only | 2810 | 2439 | 0.000 (0) | 0.000 (0) | 0.124 |
| b2sentence-biomedbert | novel | 438 | 290 | 0.000 (0) | 0.000 (0) | 0.314 |
| b2sentence-biomedbert | older_clean | 1832 | 1233 | 0.000 (0) | 0.000 (0) | 0.313 |
| b1names-biomedbert | SemEval test, names only | 2810 | 2439 | 0.169 (413) | 0.012 (30) | 0.167 |
| b1names-biomedbert | novel | 438 | 290 | 0.579 (168) | 0.014 (4) | 0.263 |
| b1names-biomedbert | older_clean | 1832 | 1233 | 0.477 (588) | 0.008 (10) | 0.234 |
| llm-qwen-names | SemEval test, names only | 2810 | 2439 | 0.918 (2240) | 0.777 (1895) | 0.772 |
| llm-qwen-names | novel | 438 | 290 | 0.948 (275) | 0.738 (214) | 0.582 |
| llm-qwen-names | older_clean | 1832 | 1233 | 0.964 (1188) | 0.829 (1022) | 0.614 |

## Approval-year gradient (descriptive only, exploratory)

Per-drug within-drug AUROC on continuous first approval year, weighted by pairs, Novel and Older-clean drugs together, drug bootstrap. The 2013 to 2019 gap and the label-format difference between cohorts make this weak.

| system | drugs | slope per decade | 95% CI | Older-clean weighted mean (drugs, years) | Novel weighted mean (drugs, years) |
| --- | --- | --- | --- | --- | --- |
| b2mixed-biomedbert | 176 | 0.046 | [0.011, 0.082] | 0.443 (128, 1985 to 2012) | 0.517 (48, 2020 to 2024) |
| llm-qwen-names | 176 | 0.025 | [-0.012, 0.063] | 0.590 (128, 1985 to 2012) | 0.530 (48, 2020 to 2024) |
| b1names-biomedbert | 176 | 0.025 | [-0.010, 0.063] | 0.462 (128, 1985 to 2012) | 0.515 (48, 2020 to 2024) |
| DrugBank lookup | 176 | 0.057 | [0.032, 0.079] | 0.642 (128, 1985 to 2012) | 0.727 (48, 2020 to 2024) |
