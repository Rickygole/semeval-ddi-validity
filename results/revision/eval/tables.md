# Revision results

## Per job

| job | key | n | prevalence | auroc | auprc | f1 | mcc | balanced_accuracy | tp | fp | fn | tn | auroc_within | auroc_pooled_lo95 | auroc_pooled_hi95 | auroc_pooled2_lo95 | auroc_pooled2_hi95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b1names-bertbase-s42 | test_names | 2810 | 0.132 | 0.618 | 0.197 | 0.257 | 0.125 | 0.571 | 114 | 402 | 257 | 2037 | NA | NA | NA | NA | NA |
| b1names-bertbase-s42 | ood_names | 438 | 0.338 | 0.543 | 0.371 | 0.268 | 0.036 | 0.515 | 31 | 52 | 117 | 238 | 0.520 | 0.466 | 0.616 | 0.440 | 0.653 |
| b1names-bertbase-s42 | oodold_names | 1944 | 0.333 | 0.469 | 0.318 | 0.216 | -0.033 | 0.486 | 109 | 253 | 539 | 1043 | 0.511 | 0.438 | 0.504 | 0.424 | 0.519 |
| b1names-bertbase-s42 | swap_vocab_names | 2810 | 0.132 | 0.467 | 0.121 | 0.172 | -0.016 | 0.489 | 105 | 742 | 266 | 1697 | NA | NA | NA | NA | NA |
| b1names-bertbase-s42 | swap_novel_names | 2810 | 0.132 | 0.516 | 0.141 | 0.143 | 0.029 | 0.513 | 48 | 252 | 323 | 2187 | NA | NA | NA | NA | NA |
| b1names-bertbase-s42 | swap_pseudo_names | 2810 | 0.132 | 0.498 | 0.129 | 0.099 | -0.016 | 0.493 | 32 | 245 | 339 | 2194 | NA | NA | NA | NA | NA |
| b1names-biobert-s42 | test_names | 2810 | 0.132 | 0.626 | 0.186 | 0.219 | 0.100 | 0.550 | 81 | 288 | 290 | 2151 | NA | NA | NA | NA | NA |
| b1names-biobert-s42 | ood_names | 438 | 0.338 | 0.476 | 0.363 | 0.317 | 0.015 | 0.507 | 43 | 80 | 105 | 210 | 0.514 | 0.401 | 0.550 | 0.372 | 0.580 |
| b1names-biobert-s42 | oodold_names | 1944 | 0.333 | 0.502 | 0.335 | 0.275 | 0.034 | 0.515 | 143 | 248 | 505 | 1048 | 0.511 | 0.465 | 0.540 | 0.453 | 0.554 |
| b1names-biobert-s42 | swap_vocab_names | 2810 | 0.132 | 0.494 | 0.131 | 0.161 | -0.009 | 0.494 | 82 | 566 | 289 | 1873 | NA | NA | NA | NA | NA |
| b1names-biobert-s42 | swap_novel_names | 2810 | 0.132 | 0.508 | 0.135 | 0.174 | 0.019 | 0.511 | 81 | 477 | 290 | 1962 | NA | NA | NA | NA | NA |
| b1names-biobert-s42 | swap_pseudo_names | 2810 | 0.132 | 0.479 | 0.127 | 0.108 | -0.006 | 0.498 | 35 | 242 | 336 | 2197 | NA | NA | NA | NA | NA |
| b1names-biomedbert-disjoint-s42 | test_names | 2810 | 0.132 | 0.613 | 0.188 | 0.237 | 0.092 | 0.556 | 114 | 478 | 257 | 1961 | NA | NA | NA | NA | NA |
| b1names-biomedbert-disjoint-s42 | ood_names | 438 | 0.338 | 0.520 | 0.366 | 0.396 | 0.055 | 0.528 | 63 | 107 | 85 | 183 | 0.481 | 0.445 | 0.610 | 0.406 | 0.633 |
| b1names-biomedbert-disjoint-s42 | oodold_names | 1944 | 0.333 | 0.497 | 0.339 | 0.341 | -0.004 | 0.498 | 228 | 461 | 420 | 835 | 0.474 | 0.459 | 0.535 | 0.442 | 0.546 |
| b1names-biomedbert-disjoint-s42 | swap_vocab_names | 2810 | 0.132 | 0.490 | 0.129 | 0.184 | 0.015 | 0.510 | 99 | 604 | 272 | 1835 | NA | NA | NA | NA | NA |
| b1names-biomedbert-disjoint-s42 | swap_novel_names | 2810 | 0.132 | 0.495 | 0.134 | 0.181 | -0.003 | 0.498 | 110 | 733 | 261 | 1706 | NA | NA | NA | NA | NA |
| b1names-biomedbert-disjoint-s42 | swap_pseudo_names | 2810 | 0.132 | 0.529 | 0.143 | 0.171 | 0.025 | 0.514 | 74 | 419 | 297 | 2020 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s1 | test_names | 2810 | 0.132 | 0.633 | 0.200 | 0.251 | 0.092 | 0.563 | 157 | 724 | 214 | 1715 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s1 | ood_names | 438 | 0.338 | 0.510 | 0.352 | 0.432 | 0.042 | 0.522 | 81 | 146 | 67 | 144 | 0.538 | 0.437 | 0.584 | 0.413 | 0.612 |
| b1names-biomedbert-s1 | oodold_names | 1944 | 0.333 | 0.491 | 0.330 | 0.400 | -0.007 | 0.497 | 328 | 665 | 320 | 631 | 0.478 | 0.458 | 0.526 | 0.441 | 0.538 |
| b1names-biomedbert-s1 | swap_vocab_names | 2810 | 0.132 | 0.486 | 0.127 | 0.184 | -0.006 | 0.496 | 119 | 804 | 252 | 1635 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s1 | swap_novel_names | 2810 | 0.132 | 0.495 | 0.137 | 0.182 | -0.001 | 0.499 | 109 | 720 | 262 | 1719 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s1 | swap_pseudo_names | 2810 | 0.132 | 0.521 | 0.141 | 0.133 | 0.020 | 0.509 | 44 | 245 | 327 | 2194 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s2 | test_names | 2810 | 0.132 | 0.654 | 0.206 | 0.227 | 0.115 | 0.555 | 81 | 262 | 290 | 2177 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s2 | ood_names | 438 | 0.338 | 0.534 | 0.361 | 0.400 | 0.088 | 0.544 | 60 | 92 | 88 | 198 | 0.501 | 0.468 | 0.601 | 0.439 | 0.632 |
| b1names-biomedbert-s2 | oodold_names | 1944 | 0.333 | 0.480 | 0.327 | 0.272 | -0.002 | 0.499 | 149 | 300 | 499 | 996 | 0.475 | 0.442 | 0.518 | 0.425 | 0.533 |
| b1names-biomedbert-s2 | swap_vocab_names | 2810 | 0.132 | 0.477 | 0.125 | 0.139 | -0.012 | 0.493 | 59 | 420 | 312 | 2019 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s2 | swap_novel_names | 2810 | 0.132 | 0.474 | 0.121 | 0.120 | -0.029 | 0.484 | 49 | 400 | 322 | 2039 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s2 | swap_pseudo_names | 2810 | 0.132 | 0.514 | 0.134 | 0.024 | -0.013 | 0.498 | 5 | 45 | 366 | 2394 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s3 | test_names | 2810 | 0.132 | 0.663 | 0.214 | 0.253 | 0.120 | 0.569 | 113 | 408 | 258 | 2031 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s3 | ood_names | 438 | 0.338 | 0.471 | 0.329 | 0.387 | -0.059 | 0.469 | 75 | 165 | 73 | 125 | 0.501 | 0.416 | 0.531 | 0.378 | 0.566 |
| b1names-biomedbert-s3 | oodold_names | 1944 | 0.333 | 0.472 | 0.323 | 0.339 | -0.021 | 0.489 | 233 | 494 | 415 | 802 | 0.469 | 0.435 | 0.508 | 0.418 | 0.521 |
| b1names-biomedbert-s3 | swap_vocab_names | 2810 | 0.132 | 0.512 | 0.140 | 0.195 | 0.015 | 0.510 | 120 | 738 | 251 | 1701 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s3 | swap_novel_names | 2810 | 0.132 | 0.491 | 0.127 | 0.182 | -0.016 | 0.489 | 124 | 869 | 247 | 1570 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s3 | swap_pseudo_names | 2810 | 0.132 | 0.500 | 0.136 | 0.146 | -0.018 | 0.489 | 69 | 505 | 302 | 1934 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s4 | test_names | 2810 | 0.132 | 0.680 | 0.218 | 0.256 | 0.131 | 0.571 | 104 | 339 | 267 | 2100 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s4 | ood_names | 438 | 0.338 | 0.498 | 0.346 | 0.364 | 0.012 | 0.506 | 57 | 108 | 91 | 182 | 0.489 | 0.453 | 0.549 | 0.409 | 0.579 |
| b1names-biomedbert-s4 | oodold_names | 1944 | 0.333 | 0.462 | 0.316 | 0.299 | -0.040 | 0.480 | 190 | 431 | 458 | 865 | 0.464 | 0.421 | 0.502 | 0.409 | 0.517 |
| b1names-biomedbert-s4 | swap_vocab_names | 2810 | 0.132 | 0.486 | 0.126 | 0.162 | -0.014 | 0.491 | 87 | 616 | 284 | 1823 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s4 | swap_novel_names | 2810 | 0.132 | 0.508 | 0.136 | 0.132 | -0.016 | 0.492 | 54 | 396 | 317 | 2043 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s4 | swap_pseudo_names | 2810 | 0.132 | 0.514 | 0.138 | 0.069 | 0.020 | 0.505 | 16 | 79 | 355 | 2360 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s42 | test_names | 2810 | 0.132 | 0.686 | 0.224 | 0.250 | 0.124 | 0.567 | 102 | 344 | 269 | 2095 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s42 | ood_names | 438 | 0.338 | 0.511 | 0.365 | 0.424 | 0.029 | 0.515 | 79 | 146 | 69 | 144 | 0.513 | 0.441 | 0.584 | 0.413 | 0.617 |
| b1names-biomedbert-s42 | oodold_names | 1944 | 0.333 | 0.483 | 0.341 | 0.352 | 0.005 | 0.502 | 239 | 472 | 409 | 824 | 0.462 | 0.444 | 0.525 | 0.430 | 0.536 |
| b1names-biomedbert-s42 | swap_vocab_names | 2810 | 0.132 | 0.490 | 0.129 | 0.169 | -0.008 | 0.495 | 93 | 637 | 278 | 1802 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s42 | swap_novel_names | 2810 | 0.132 | 0.483 | 0.125 | 0.196 | -0.011 | 0.492 | 154 | 1050 | 217 | 1389 | NA | NA | NA | NA | NA |
| b1names-biomedbert-s42 | swap_pseudo_names | 2810 | 0.132 | 0.511 | 0.135 | 0.155 | -0.002 | 0.499 | 70 | 465 | 301 | 1974 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | test_sentence | 2810 | 0.132 | 0.736 | 0.224 | 0.030 | -0.036 | 0.490 | 7 | 95 | 364 | 2344 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | test_masked | 2810 | 0.132 | 0.956 | 0.777 | 0.709 | 0.663 | 0.851 | 282 | 143 | 89 | 2296 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | test_empty | 2810 | 0.132 | 0.512 | 0.137 | 0.011 | 0.015 | 0.501 | 2 | 7 | 369 | 2432 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | test_names | 2810 | 0.132 | 0.493 | 0.131 | 0.000 | -0.010 | 0.500 | 0 | 2 | 371 | 2437 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | ood_empty | 438 | 0.338 | 0.520 | 0.345 | 0.000 | -0.034 | 0.498 | 0 | 1 | 148 | 289 | 0.469 | 0.470 | 0.575 | 0.425 | 0.611 |
| b2masked-biomedbert-s1 | ood_names | 438 | 0.338 | 0.491 | 0.322 | 0.000 | -0.034 | 0.498 | 0 | 1 | 148 | 289 | 0.444 | 0.436 | 0.548 | 0.393 | 0.584 |
| b2masked-biomedbert-s1 | ood_sentence | 50 | 1.000 | NA | NA | 0.000 | 0.000 | 0.000 | 0 | 0 | 50 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | ood_swap_sentence | 100 | 0.500 | 0.502 | 0.518 | 0.000 | 0.000 | 0.500 | 0 | 0 | 50 | 50 | NA | 0.476 | 0.533 | NA | NA |
| b2masked-biomedbert-s1 | oodold_empty | 1944 | 0.333 | 0.507 | 0.338 | 0.000 | -0.016 | 0.500 | 0 | 1 | 648 | 1295 | 0.549 | 0.467 | 0.546 | 0.455 | 0.562 |
| b2masked-biomedbert-s1 | oodold_sentence | 256 | 1.000 | NA | NA | 0.000 | 0.000 | 0.000 | 0 | 0 | 256 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | swap_vocab_sentence | 2810 | 0.132 | 0.760 | 0.249 | 0.071 | 0.013 | 0.504 | 17 | 93 | 354 | 2346 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | swap_novel_sentence | 2810 | 0.132 | 0.789 | 0.283 | 0.066 | 0.026 | 0.506 | 15 | 67 | 356 | 2372 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s1 | swap_pseudo_sentence | 2810 | 0.132 | 0.826 | 0.325 | 0.133 | 0.106 | 0.528 | 31 | 65 | 340 | 2374 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | test_sentence | 2810 | 0.132 | 0.866 | 0.488 | 0.399 | 0.362 | 0.635 | 112 | 79 | 259 | 2360 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | test_masked | 2810 | 0.132 | 0.955 | 0.773 | 0.665 | 0.612 | 0.825 | 266 | 163 | 105 | 2276 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | test_empty | 2810 | 0.132 | 0.483 | 0.129 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | test_names | 2810 | 0.132 | 0.482 | 0.132 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | ood_empty | 438 | 0.338 | 0.467 | 0.312 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.527 | 0.396 | 0.540 | 0.374 | 0.565 |
| b2masked-biomedbert-s2 | ood_names | 438 | 0.338 | 0.470 | 0.311 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.469 | 0.399 | 0.543 | 0.373 | 0.574 |
| b2masked-biomedbert-s2 | ood_sentence | 50 | 1.000 | NA | NA | 0.039 | 0.000 | 0.010 | 1 | 0 | 49 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | ood_swap_sentence | 100 | 0.500 | 0.512 | 0.555 | 0.039 | 0.101 | 0.510 | 1 | 0 | 49 | 50 | NA | 0.471 | 0.566 | NA | NA |
| b2masked-biomedbert-s2 | oodold_empty | 1944 | 0.333 | 0.489 | 0.333 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.541 | 0.453 | 0.525 | 0.442 | 0.540 |
| b2masked-biomedbert-s2 | oodold_sentence | 256 | 1.000 | NA | NA | 0.097 | 0.000 | 0.025 | 13 | 0 | 243 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | swap_vocab_sentence | 2810 | 0.132 | 0.896 | 0.584 | 0.486 | 0.449 | 0.677 | 143 | 75 | 228 | 2364 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | swap_novel_sentence | 2810 | 0.132 | 0.887 | 0.584 | 0.458 | 0.441 | 0.659 | 126 | 53 | 245 | 2386 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s2 | swap_pseudo_sentence | 2810 | 0.132 | 0.905 | 0.591 | 0.491 | 0.454 | 0.680 | 145 | 75 | 226 | 2364 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | test_sentence | 2810 | 0.132 | 0.875 | 0.506 | 0.524 | 0.446 | 0.750 | 226 | 265 | 145 | 2174 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | test_masked | 2810 | 0.132 | 0.955 | 0.787 | 0.715 | 0.673 | 0.873 | 303 | 173 | 68 | 2266 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | test_empty | 2810 | 0.132 | 0.575 | 0.163 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | test_names | 2810 | 0.132 | 0.516 | 0.136 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | ood_empty | 438 | 0.338 | 0.530 | 0.357 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.539 | 0.477 | 0.590 | 0.430 | 0.621 |
| b2masked-biomedbert-s3 | ood_names | 438 | 0.338 | 0.550 | 0.356 | 0.000 | -0.048 | 0.497 | 0 | 2 | 148 | 288 | 0.527 | 0.488 | 0.613 | 0.451 | 0.649 |
| b2masked-biomedbert-s3 | ood_sentence | 50 | 1.000 | NA | NA | 0.305 | 0.000 | 0.090 | 9 | 0 | 41 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | ood_swap_sentence | 100 | 0.500 | 0.506 | 0.531 | 0.265 | 0.000 | 0.500 | 9 | 9 | 41 | 41 | NA | 0.475 | 0.538 | NA | NA |
| b2masked-biomedbert-s3 | oodold_empty | 1944 | 0.333 | 0.499 | 0.341 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.482 | 0.463 | 0.535 | 0.450 | 0.550 |
| b2masked-biomedbert-s3 | oodold_sentence | 256 | 1.000 | NA | NA | 0.316 | 0.000 | 0.094 | 48 | 0 | 208 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | swap_vocab_sentence | 2810 | 0.132 | 0.893 | 0.580 | 0.551 | 0.479 | 0.773 | 244 | 270 | 127 | 2169 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | swap_novel_sentence | 2810 | 0.132 | 0.885 | 0.590 | 0.554 | 0.481 | 0.762 | 229 | 227 | 142 | 2212 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s3 | swap_pseudo_sentence | 2810 | 0.132 | 0.894 | 0.585 | 0.548 | 0.475 | 0.770 | 241 | 267 | 130 | 2172 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | test_sentence | 2810 | 0.132 | 0.852 | 0.459 | 0.475 | 0.397 | 0.759 | 266 | 484 | 105 | 1955 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | test_masked | 2810 | 0.132 | 0.953 | 0.784 | 0.707 | 0.664 | 0.875 | 307 | 191 | 64 | 2248 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | test_empty | 2810 | 0.132 | 0.464 | 0.121 | 0.080 | -0.016 | 0.494 | 23 | 181 | 348 | 2258 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | test_names | 2810 | 0.132 | 0.498 | 0.135 | 0.050 | 0.014 | 0.503 | 11 | 57 | 360 | 2382 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | ood_empty | 438 | 0.338 | 0.498 | 0.344 | 0.122 | 0.003 | 0.501 | 11 | 21 | 137 | 269 | 0.501 | 0.445 | 0.555 | 0.404 | 0.594 |
| b2masked-biomedbert-s4 | ood_names | 438 | 0.338 | 0.495 | 0.335 | 0.050 | 0.009 | 0.501 | 4 | 7 | 144 | 283 | 0.498 | 0.442 | 0.554 | 0.405 | 0.592 |
| b2masked-biomedbert-s4 | ood_sentence | 50 | 1.000 | NA | NA | 0.305 | 0.000 | 0.090 | 9 | 0 | 41 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | ood_swap_sentence | 100 | 0.500 | 0.504 | 0.553 | 0.269 | 0.027 | 0.510 | 9 | 8 | 41 | 42 | NA | 0.451 | 0.552 | NA | NA |
| b2masked-biomedbert-s4 | oodold_empty | 1944 | 0.333 | 0.514 | 0.341 | 0.057 | 0.006 | 0.501 | 20 | 37 | 628 | 1259 | 0.506 | 0.477 | 0.552 | 0.465 | 0.566 |
| b2masked-biomedbert-s4 | oodold_sentence | 256 | 1.000 | NA | NA | 0.444 | 0.000 | 0.143 | 73 | 0 | 183 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | swap_vocab_sentence | 2810 | 0.132 | 0.879 | 0.542 | 0.525 | 0.456 | 0.786 | 272 | 393 | 99 | 2046 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | swap_novel_sentence | 2810 | 0.132 | 0.875 | 0.554 | 0.511 | 0.431 | 0.753 | 236 | 317 | 135 | 2122 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s4 | swap_pseudo_sentence | 2810 | 0.132 | 0.903 | 0.612 | 0.552 | 0.482 | 0.786 | 259 | 309 | 112 | 2130 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | test_sentence | 2810 | 0.132 | 0.840 | 0.434 | 0.455 | 0.374 | 0.749 | 265 | 529 | 106 | 1910 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | test_masked | 2810 | 0.132 | 0.957 | 0.786 | 0.719 | 0.675 | 0.849 | 278 | 124 | 93 | 2315 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | test_empty | 2810 | 0.132 | 0.606 | 0.171 | 0.252 | 0.099 | 0.566 | 146 | 640 | 225 | 1799 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | test_names | 2810 | 0.132 | 0.585 | 0.162 | 0.257 | 0.099 | 0.569 | 165 | 749 | 206 | 1690 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | ood_empty | 438 | 0.338 | 0.448 | 0.319 | 0.370 | -0.068 | 0.464 | 69 | 156 | 79 | 134 | 0.477 | 0.382 | 0.519 | 0.350 | 0.547 |
| b2masked-biomedbert-s42 | ood_names | 438 | 0.338 | 0.437 | 0.301 | 0.363 | -0.108 | 0.443 | 71 | 172 | 77 | 118 | 0.464 | 0.380 | 0.499 | 0.348 | 0.530 |
| b2masked-biomedbert-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.413 | 0.000 | 0.130 | 13 | 0 | 37 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | ood_swap_sentence | 100 | 0.500 | 0.496 | 0.542 | 0.329 | -0.066 | 0.470 | 13 | 16 | 37 | 34 | NA | 0.453 | 0.539 | NA | NA |
| b2masked-biomedbert-s42 | oodold_empty | 1944 | 0.333 | 0.450 | 0.311 | 0.287 | -0.076 | 0.462 | 188 | 475 | 460 | 821 | 0.487 | 0.413 | 0.486 | 0.401 | 0.498 |
| b2masked-biomedbert-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.467 | 0.000 | 0.152 | 78 | 0 | 178 | 0 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.861 | 0.460 | 0.489 | 0.414 | 0.768 | 268 | 456 | 103 | 1983 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | swap_novel_sentence | 2810 | 0.132 | 0.864 | 0.485 | 0.501 | 0.420 | 0.755 | 244 | 360 | 127 | 2079 | NA | NA | NA | NA | NA |
| b2masked-biomedbert-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.866 | 0.496 | 0.507 | 0.428 | 0.760 | 247 | 357 | 124 | 2082 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | test_sentence | 2810 | 0.132 | 0.934 | 0.682 | 0.615 | 0.556 | 0.778 | 228 | 143 | 143 | 2296 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | test_masked | 2810 | 0.132 | 0.827 | 0.411 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | test_empty | 2810 | 0.132 | 0.626 | 0.188 | 0.144 | 0.061 | 0.523 | 41 | 157 | 330 | 2282 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | test_names | 2810 | 0.132 | 0.633 | 0.185 | 0.052 | 0.036 | 0.507 | 11 | 38 | 360 | 2401 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | ood_empty | 438 | 0.338 | 0.493 | 0.335 | 0.091 | -0.029 | 0.493 | 8 | 20 | 140 | 270 | 0.472 | 0.433 | 0.554 | 0.401 | 0.581 |
| b2mixed-bertbase-s1 | ood_names | 438 | 0.338 | 0.476 | 0.322 | 0.026 | -0.025 | 0.496 | 2 | 6 | 146 | 284 | 0.460 | 0.414 | 0.544 | 0.379 | 0.573 |
| b2mixed-bertbase-s1 | ood_sentence | 50 | 1.000 | NA | NA | 0.413 | 0.000 | 0.130 | 13 | 0 | 37 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | ood_swap_sentence | 100 | 0.500 | 0.498 | 0.499 | 0.321 | -0.108 | 0.450 | 13 | 18 | 37 | 32 | NA | 0.459 | 0.532 | NA | NA |
| b2mixed-bertbase-s1 | oodold_empty | 1944 | 0.333 | 0.472 | 0.315 | 0.135 | -0.019 | 0.494 | 56 | 127 | 592 | 1169 | 0.501 | 0.437 | 0.510 | 0.421 | 0.525 |
| b2mixed-bertbase-s1 | oodold_sentence | 256 | 1.000 | NA | NA | 0.499 | 0.000 | 0.166 | 85 | 0 | 171 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | swap_vocab_sentence | 2810 | 0.132 | 0.897 | 0.619 | 0.580 | 0.513 | 0.765 | 224 | 178 | 147 | 2261 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | swap_novel_sentence | 2810 | 0.132 | 0.917 | 0.675 | 0.614 | 0.554 | 0.781 | 232 | 153 | 139 | 2286 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s1 | swap_pseudo_sentence | 2810 | 0.132 | 0.913 | 0.669 | 0.596 | 0.542 | 0.754 | 206 | 114 | 165 | 2325 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | test_sentence | 2810 | 0.132 | 0.934 | 0.686 | 0.637 | 0.580 | 0.805 | 252 | 168 | 119 | 2271 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | test_masked | 2810 | 0.132 | 0.792 | 0.345 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | test_empty | 2810 | 0.132 | 0.622 | 0.206 | 0.171 | 0.127 | 0.540 | 43 | 89 | 328 | 2350 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | test_names | 2810 | 0.132 | 0.603 | 0.200 | 0.132 | 0.117 | 0.529 | 30 | 54 | 341 | 2385 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | ood_empty | 438 | 0.338 | 0.491 | 0.340 | 0.119 | -0.026 | 0.492 | 11 | 26 | 137 | 264 | 0.505 | 0.422 | 0.566 | 0.396 | 0.592 |
| b2mixed-bertbase-s2 | ood_names | 438 | 0.338 | 0.502 | 0.343 | 0.105 | 0.019 | 0.505 | 9 | 15 | 139 | 275 | 0.515 | 0.436 | 0.577 | 0.407 | 0.599 |
| b2mixed-bertbase-s2 | ood_sentence | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | ood_swap_sentence | 100 | 0.500 | 0.494 | 0.523 | 0.385 | 0.045 | 0.520 | 15 | 13 | 35 | 37 | NA | 0.464 | 0.529 | NA | NA |
| b2mixed-bertbase-s2 | oodold_empty | 1944 | 0.333 | 0.462 | 0.308 | 0.096 | -0.044 | 0.488 | 38 | 108 | 610 | 1188 | 0.512 | 0.424 | 0.504 | 0.414 | 0.514 |
| b2mixed-bertbase-s2 | oodold_sentence | 256 | 1.000 | NA | NA | 0.524 | 0.000 | 0.178 | 91 | 0 | 165 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | swap_vocab_sentence | 2810 | 0.132 | 0.902 | 0.626 | 0.578 | 0.510 | 0.769 | 229 | 193 | 142 | 2246 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | swap_novel_sentence | 2810 | 0.132 | 0.924 | 0.665 | 0.617 | 0.556 | 0.801 | 253 | 196 | 118 | 2243 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s2 | swap_pseudo_sentence | 2810 | 0.132 | 0.915 | 0.661 | 0.591 | 0.533 | 0.756 | 209 | 127 | 162 | 2312 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | test_sentence | 2810 | 0.132 | 0.894 | 0.694 | 0.621 | 0.589 | 0.748 | 193 | 58 | 178 | 2381 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | test_masked | 2810 | 0.132 | 0.691 | 0.265 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | test_empty | 2810 | 0.132 | 0.626 | 0.191 | 0.156 | 0.110 | 0.534 | 39 | 90 | 332 | 2349 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | test_names | 2810 | 0.132 | 0.616 | 0.186 | 0.064 | 0.073 | 0.512 | 13 | 25 | 358 | 2414 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | ood_empty | 438 | 0.338 | 0.537 | 0.363 | 0.103 | -0.002 | 0.499 | 9 | 18 | 139 | 272 | 0.491 | 0.482 | 0.589 | 0.435 | 0.631 |
| b2mixed-bertbase-s3 | ood_names | 438 | 0.338 | 0.509 | 0.345 | 0.025 | -0.045 | 0.493 | 2 | 8 | 146 | 282 | 0.460 | 0.449 | 0.573 | 0.405 | 0.607 |
| b2mixed-bertbase-s3 | ood_sentence | 50 | 1.000 | NA | NA | 0.276 | 0.000 | 0.080 | 8 | 0 | 42 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | ood_swap_sentence | 100 | 0.500 | 0.502 | 0.490 | 0.242 | 0.000 | 0.500 | 8 | 8 | 42 | 42 | NA | 0.445 | 0.570 | NA | NA |
| b2mixed-bertbase-s3 | oodold_empty | 1944 | 0.333 | 0.487 | 0.321 | 0.124 | 0.003 | 0.501 | 49 | 96 | 599 | 1200 | 0.495 | 0.447 | 0.530 | 0.434 | 0.541 |
| b2mixed-bertbase-s3 | oodold_sentence | 256 | 1.000 | NA | NA | 0.364 | 0.000 | 0.111 | 57 | 0 | 199 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | swap_vocab_sentence | 2810 | 0.132 | 0.871 | 0.640 | 0.596 | 0.560 | 0.738 | 187 | 69 | 184 | 2370 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | swap_novel_sentence | 2810 | 0.132 | 0.886 | 0.675 | 0.616 | 0.577 | 0.751 | 197 | 72 | 174 | 2367 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s3 | swap_pseudo_sentence | 2810 | 0.132 | 0.872 | 0.648 | 0.577 | 0.551 | 0.721 | 172 | 53 | 199 | 2386 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | test_sentence | 2810 | 0.132 | 0.924 | 0.643 | 0.639 | 0.583 | 0.823 | 271 | 206 | 100 | 2233 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | test_masked | 2810 | 0.132 | 0.785 | 0.330 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | test_empty | 2810 | 0.132 | 0.618 | 0.187 | 0.188 | 0.068 | 0.533 | 68 | 284 | 303 | 2155 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | test_names | 2810 | 0.132 | 0.624 | 0.185 | 0.170 | 0.070 | 0.530 | 54 | 209 | 317 | 2230 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | ood_empty | 438 | 0.338 | 0.515 | 0.371 | 0.244 | 0.082 | 0.529 | 25 | 32 | 123 | 258 | 0.515 | 0.440 | 0.590 | 0.417 | 0.615 |
| b2mixed-bertbase-s4 | ood_names | 438 | 0.338 | 0.500 | 0.345 | 0.191 | 0.027 | 0.509 | 19 | 32 | 129 | 258 | 0.507 | 0.430 | 0.566 | 0.409 | 0.596 |
| b2mixed-bertbase-s4 | ood_sentence | 50 | 1.000 | NA | NA | 0.507 | 0.000 | 0.170 | 17 | 0 | 33 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | ood_swap_sentence | 100 | 0.500 | 0.500 | 0.518 | 0.386 | -0.082 | 0.460 | 17 | 21 | 33 | 29 | NA | 0.473 | 0.533 | NA | NA |
| b2mixed-bertbase-s4 | oodold_empty | 1944 | 0.333 | 0.474 | 0.326 | 0.215 | 0.000 | 0.500 | 103 | 206 | 545 | 1090 | 0.497 | 0.438 | 0.517 | 0.424 | 0.528 |
| b2mixed-bertbase-s4 | oodold_sentence | 256 | 1.000 | NA | NA | 0.490 | 0.000 | 0.162 | 83 | 0 | 173 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | swap_vocab_sentence | 2810 | 0.132 | 0.877 | 0.592 | 0.549 | 0.475 | 0.760 | 229 | 235 | 142 | 2204 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | swap_novel_sentence | 2810 | 0.132 | 0.911 | 0.653 | 0.586 | 0.523 | 0.806 | 270 | 280 | 101 | 2159 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s4 | swap_pseudo_sentence | 2810 | 0.132 | 0.899 | 0.630 | 0.574 | 0.506 | 0.766 | 227 | 193 | 144 | 2246 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | test_sentence | 2810 | 0.132 | 0.914 | 0.693 | 0.608 | 0.551 | 0.768 | 218 | 128 | 153 | 2311 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | test_masked | 2810 | 0.132 | 0.809 | 0.313 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | test_empty | 2810 | 0.132 | 0.650 | 0.200 | 0.187 | 0.086 | 0.538 | 60 | 211 | 311 | 2228 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | test_names | 2810 | 0.132 | 0.635 | 0.187 | 0.080 | 0.049 | 0.512 | 18 | 60 | 353 | 2379 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | ood_empty | 438 | 0.338 | 0.546 | 0.369 | 0.197 | 0.021 | 0.507 | 20 | 35 | 128 | 255 | 0.520 | 0.484 | 0.608 | 0.450 | 0.644 |
| b2mixed-bertbase-s42 | ood_names | 438 | 0.338 | 0.518 | 0.346 | 0.061 | -0.019 | 0.496 | 5 | 12 | 143 | 278 | 0.499 | 0.462 | 0.576 | 0.431 | 0.614 |
| b2mixed-bertbase-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | ood_swap_sentence | 100 | 0.500 | 0.526 | 0.532 | 0.437 | 0.021 | 0.510 | 19 | 18 | 31 | 32 | NA | 0.491 | 0.565 | NA | NA |
| b2mixed-bertbase-s42 | oodold_empty | 1944 | 0.333 | 0.481 | 0.323 | 0.207 | -0.010 | 0.496 | 99 | 208 | 549 | 1088 | 0.510 | 0.444 | 0.519 | 0.433 | 0.532 |
| b2mixed-bertbase-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.533 | 0.000 | 0.182 | 93 | 0 | 163 | 0 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.898 | 0.617 | 0.583 | 0.519 | 0.760 | 217 | 157 | 154 | 2282 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | swap_novel_sentence | 2810 | 0.132 | 0.908 | 0.660 | 0.600 | 0.536 | 0.782 | 237 | 182 | 134 | 2257 | NA | NA | NA | NA | NA |
| b2mixed-bertbase-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.913 | 0.665 | 0.592 | 0.527 | 0.777 | 234 | 185 | 137 | 2254 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | test_sentence | 2810 | 0.132 | 0.954 | 0.749 | 0.662 | 0.613 | 0.797 | 237 | 108 | 134 | 2331 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | test_masked | 2810 | 0.132 | 0.836 | 0.380 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | test_empty | 2810 | 0.132 | 0.635 | 0.207 | 0.154 | 0.062 | 0.525 | 46 | 181 | 325 | 2258 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | test_names | 2810 | 0.132 | 0.637 | 0.210 | 0.158 | 0.063 | 0.526 | 48 | 189 | 323 | 2250 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | ood_empty | 438 | 0.338 | 0.483 | 0.339 | 0.180 | 0.006 | 0.502 | 18 | 34 | 130 | 256 | 0.497 | 0.411 | 0.555 | 0.373 | 0.588 |
| b2mixed-biobert-s42 | ood_names | 438 | 0.338 | 0.480 | 0.336 | 0.180 | 0.006 | 0.502 | 18 | 34 | 130 | 256 | 0.499 | 0.411 | 0.550 | 0.380 | 0.588 |
| b2mixed-biobert-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.333 | 0.000 | 0.100 | 10 | 0 | 40 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | ood_swap_sentence | 100 | 0.500 | 0.505 | 0.524 | 0.294 | 0.052 | 0.520 | 10 | 8 | 40 | 42 | NA | 0.478 | 0.537 | NA | NA |
| b2mixed-biobert-s42 | oodold_empty | 1944 | 0.333 | 0.501 | 0.342 | 0.209 | 0.012 | 0.505 | 97 | 182 | 551 | 1114 | 0.493 | 0.466 | 0.541 | 0.450 | 0.553 |
| b2mixed-biobert-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.499 | 0.000 | 0.166 | 85 | 0 | 171 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.917 | 0.676 | 0.609 | 0.549 | 0.778 | 230 | 154 | 141 | 2285 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | swap_novel_sentence | 2810 | 0.132 | 0.929 | 0.707 | 0.634 | 0.576 | 0.799 | 246 | 159 | 125 | 2280 | NA | NA | NA | NA | NA |
| b2mixed-biobert-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.927 | 0.686 | 0.614 | 0.558 | 0.772 | 221 | 128 | 150 | 2311 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | test_sentence | 2810 | 0.132 | 0.955 | 0.746 | 0.692 | 0.651 | 0.877 | 313 | 220 | 58 | 2219 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | test_masked | 2810 | 0.132 | 0.851 | 0.462 | 0.073 | 0.181 | 0.519 | 14 | 0 | 357 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | test_empty | 2810 | 0.132 | 0.645 | 0.202 | 0.186 | 0.095 | 0.539 | 57 | 184 | 314 | 2255 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | test_names | 2810 | 0.132 | 0.627 | 0.200 | 0.158 | 0.087 | 0.531 | 43 | 131 | 328 | 2308 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | ood_empty | 438 | 0.338 | 0.518 | 0.353 | 0.333 | 0.018 | 0.509 | 47 | 87 | 101 | 203 | 0.536 | 0.460 | 0.577 | 0.423 | 0.607 |
| b2mixed-biomedbert-disjoint-s42 | ood_names | 438 | 0.338 | 0.507 | 0.347 | 0.237 | -0.000 | 0.500 | 27 | 53 | 121 | 237 | 0.522 | 0.454 | 0.569 | 0.419 | 0.596 |
| b2mixed-biomedbert-disjoint-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | ood_swap_sentence | 100 | 0.500 | 0.511 | 0.532 | 0.432 | 0.000 | 0.500 | 19 | 19 | 31 | 31 | NA | 0.480 | 0.545 | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | oodold_empty | 1944 | 0.333 | 0.470 | 0.329 | 0.239 | -0.011 | 0.495 | 123 | 258 | 525 | 1038 | 0.479 | 0.432 | 0.511 | 0.419 | 0.523 |
| b2mixed-biomedbert-disjoint-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.649 | 0.000 | 0.240 | 123 | 0 | 133 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.945 | 0.738 | 0.662 | 0.615 | 0.861 | 305 | 246 | 66 | 2193 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | swap_novel_sentence | 2810 | 0.132 | 0.947 | 0.736 | 0.644 | 0.604 | 0.874 | 325 | 313 | 46 | 2126 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-disjoint-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.940 | 0.727 | 0.653 | 0.598 | 0.828 | 272 | 190 | 99 | 2249 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | test_sentence | 2810 | 0.132 | 0.959 | 0.786 | 0.713 | 0.669 | 0.863 | 294 | 160 | 77 | 2279 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | test_masked | 2810 | 0.132 | 0.871 | 0.536 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | test_empty | 2810 | 0.132 | 0.682 | 0.219 | 0.235 | 0.149 | 0.562 | 72 | 171 | 299 | 2268 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | test_names | 2810 | 0.132 | 0.655 | 0.216 | 0.150 | 0.092 | 0.530 | 39 | 109 | 332 | 2330 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | ood_empty | 438 | 0.338 | 0.526 | 0.365 | 0.343 | 0.036 | 0.517 | 48 | 84 | 100 | 206 | 0.515 | 0.467 | 0.590 | 0.429 | 0.620 |
| b2mixed-biomedbert-s1 | ood_names | 438 | 0.338 | 0.496 | 0.334 | 0.227 | 0.009 | 0.503 | 25 | 47 | 123 | 243 | 0.510 | 0.440 | 0.563 | 0.393 | 0.593 |
| b2mixed-biomedbert-s1 | ood_sentence | 50 | 1.000 | NA | NA | 0.630 | 0.000 | 0.230 | 23 | 0 | 27 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | ood_swap_sentence | 100 | 0.500 | 0.503 | 0.547 | 0.505 | 0.102 | 0.550 | 23 | 18 | 27 | 32 | NA | 0.457 | 0.557 | NA | NA |
| b2mixed-biomedbert-s1 | oodold_empty | 1944 | 0.333 | 0.448 | 0.308 | 0.259 | -0.030 | 0.486 | 145 | 325 | 503 | 971 | 0.452 | 0.409 | 0.489 | 0.395 | 0.500 |
| b2mixed-biomedbert-s1 | oodold_sentence | 256 | 1.000 | NA | NA | 0.609 | 0.000 | 0.219 | 112 | 0 | 144 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | swap_vocab_sentence | 2810 | 0.132 | 0.937 | 0.758 | 0.696 | 0.649 | 0.853 | 288 | 169 | 83 | 2270 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | swap_novel_sentence | 2810 | 0.132 | 0.949 | 0.785 | 0.701 | 0.658 | 0.874 | 308 | 200 | 63 | 2239 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s1 | swap_pseudo_sentence | 2810 | 0.132 | 0.940 | 0.771 | 0.719 | 0.676 | 0.841 | 270 | 110 | 101 | 2329 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | test_sentence | 2810 | 0.132 | 0.961 | 0.790 | 0.711 | 0.672 | 0.887 | 318 | 205 | 53 | 2234 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | test_masked | 2810 | 0.132 | 0.884 | 0.576 | 0.073 | 0.181 | 0.519 | 14 | 0 | 357 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | test_empty | 2810 | 0.132 | 0.672 | 0.219 | 0.191 | 0.101 | 0.541 | 58 | 179 | 313 | 2260 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | test_names | 2810 | 0.132 | 0.665 | 0.216 | 0.205 | 0.121 | 0.549 | 61 | 164 | 310 | 2275 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | ood_empty | 438 | 0.338 | 0.501 | 0.358 | 0.342 | 0.067 | 0.531 | 45 | 70 | 103 | 220 | 0.510 | 0.418 | 0.591 | 0.377 | 0.611 |
| b2mixed-biomedbert-s2 | ood_names | 438 | 0.338 | 0.485 | 0.344 | 0.237 | -0.000 | 0.500 | 27 | 53 | 121 | 237 | 0.509 | 0.414 | 0.560 | 0.365 | 0.589 |
| b2mixed-biomedbert-s2 | ood_sentence | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | ood_swap_sentence | 100 | 0.500 | 0.504 | 0.517 | 0.427 | -0.021 | 0.490 | 19 | 20 | 31 | 30 | NA | 0.474 | 0.542 | NA | NA |
| b2mixed-biomedbert-s2 | oodold_empty | 1944 | 0.333 | 0.468 | 0.319 | 0.216 | -0.002 | 0.499 | 104 | 210 | 544 | 1086 | 0.462 | 0.431 | 0.511 | 0.417 | 0.519 |
| b2mixed-biomedbert-s2 | oodold_sentence | 256 | 1.000 | NA | NA | 0.667 | 0.000 | 0.250 | 128 | 0 | 128 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | swap_vocab_sentence | 2810 | 0.132 | 0.951 | 0.767 | 0.696 | 0.655 | 0.877 | 312 | 213 | 59 | 2226 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | swap_novel_sentence | 2810 | 0.132 | 0.962 | 0.795 | 0.695 | 0.661 | 0.899 | 335 | 258 | 36 | 2181 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s2 | swap_pseudo_sentence | 2810 | 0.132 | 0.957 | 0.786 | 0.712 | 0.669 | 0.875 | 306 | 183 | 65 | 2256 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | test_sentence | 2810 | 0.132 | 0.946 | 0.738 | 0.674 | 0.623 | 0.833 | 272 | 164 | 99 | 2275 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | test_masked | 2810 | 0.132 | 0.827 | 0.432 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | test_empty | 2810 | 0.132 | 0.669 | 0.216 | 0.121 | 0.094 | 0.525 | 28 | 64 | 343 | 2375 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | test_names | 2810 | 0.132 | 0.650 | 0.231 | 0.095 | 0.104 | 0.521 | 20 | 31 | 351 | 2408 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | ood_empty | 438 | 0.338 | 0.488 | 0.356 | 0.159 | 0.019 | 0.506 | 15 | 26 | 133 | 264 | 0.532 | 0.410 | 0.581 | 0.370 | 0.602 |
| b2mixed-biomedbert-s3 | ood_names | 438 | 0.338 | 0.517 | 0.343 | 0.072 | -0.010 | 0.498 | 6 | 13 | 142 | 277 | 0.520 | 0.451 | 0.584 | 0.408 | 0.623 |
| b2mixed-biomedbert-s3 | ood_sentence | 50 | 1.000 | NA | NA | 0.611 | 0.000 | 0.220 | 22 | 0 | 28 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | ood_swap_sentence | 100 | 0.500 | 0.506 | 0.542 | 0.484 | 0.061 | 0.530 | 22 | 19 | 28 | 31 | NA | 0.475 | 0.544 | NA | NA |
| b2mixed-biomedbert-s3 | oodold_empty | 1944 | 0.333 | 0.459 | 0.318 | 0.068 | -0.016 | 0.497 | 25 | 59 | 623 | 1237 | 0.449 | 0.426 | 0.498 | 0.404 | 0.515 |
| b2mixed-biomedbert-s3 | oodold_sentence | 256 | 1.000 | NA | NA | 0.674 | 0.000 | 0.254 | 130 | 0 | 126 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | swap_vocab_sentence | 2810 | 0.132 | 0.943 | 0.739 | 0.695 | 0.647 | 0.837 | 271 | 138 | 100 | 2301 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | swap_novel_sentence | 2810 | 0.132 | 0.957 | 0.777 | 0.727 | 0.685 | 0.875 | 302 | 158 | 69 | 2281 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s3 | swap_pseudo_sentence | 2810 | 0.132 | 0.945 | 0.742 | 0.666 | 0.618 | 0.798 | 237 | 104 | 134 | 2335 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | test_sentence | 2810 | 0.132 | 0.949 | 0.750 | 0.694 | 0.653 | 0.879 | 315 | 222 | 56 | 2217 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | test_masked | 2810 | 0.132 | 0.836 | 0.497 | 0.032 | 0.119 | 0.508 | 6 | 0 | 365 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | test_empty | 2810 | 0.132 | 0.664 | 0.215 | 0.208 | 0.108 | 0.548 | 68 | 214 | 303 | 2225 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | test_names | 2810 | 0.132 | 0.643 | 0.215 | 0.159 | 0.105 | 0.534 | 41 | 103 | 330 | 2336 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | ood_empty | 438 | 0.338 | 0.534 | 0.359 | 0.341 | 0.051 | 0.524 | 46 | 76 | 102 | 214 | 0.507 | 0.453 | 0.618 | 0.416 | 0.643 |
| b2mixed-biomedbert-s4 | ood_names | 438 | 0.338 | 0.517 | 0.341 | 0.156 | 0.002 | 0.501 | 15 | 29 | 133 | 261 | 0.527 | 0.446 | 0.597 | 0.410 | 0.625 |
| b2mixed-biomedbert-s4 | ood_sentence | 50 | 1.000 | NA | NA | 0.507 | 0.000 | 0.170 | 17 | 0 | 33 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | ood_swap_sentence | 100 | 0.500 | 0.511 | 0.540 | 0.425 | 0.087 | 0.540 | 17 | 13 | 33 | 37 | NA | 0.458 | 0.577 | NA | NA |
| b2mixed-biomedbert-s4 | oodold_empty | 1944 | 0.333 | 0.462 | 0.317 | 0.275 | -0.022 | 0.490 | 158 | 342 | 490 | 954 | 0.485 | 0.424 | 0.503 | 0.408 | 0.515 |
| b2mixed-biomedbert-s4 | oodold_sentence | 256 | 1.000 | NA | NA | 0.684 | 0.000 | 0.260 | 133 | 0 | 123 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | swap_vocab_sentence | 2810 | 0.132 | 0.939 | 0.742 | 0.682 | 0.637 | 0.864 | 302 | 212 | 69 | 2227 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | swap_novel_sentence | 2810 | 0.132 | 0.948 | 0.760 | 0.684 | 0.647 | 0.890 | 329 | 262 | 42 | 2177 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s4 | swap_pseudo_sentence | 2810 | 0.132 | 0.944 | 0.754 | 0.675 | 0.626 | 0.849 | 289 | 196 | 82 | 2243 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | test_sentence | 2810 | 0.132 | 0.962 | 0.781 | 0.704 | 0.660 | 0.870 | 303 | 187 | 68 | 2252 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | test_masked | 2810 | 0.132 | 0.866 | 0.520 | 0.093 | 0.206 | 0.524 | 18 | 0 | 353 | 2439 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | test_empty | 2810 | 0.132 | 0.660 | 0.200 | 0.206 | 0.101 | 0.546 | 69 | 230 | 302 | 2209 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | test_names | 2810 | 0.132 | 0.651 | 0.199 | 0.144 | 0.067 | 0.524 | 40 | 144 | 331 | 2295 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | ood_empty | 438 | 0.338 | 0.518 | 0.361 | 0.358 | 0.002 | 0.501 | 56 | 109 | 92 | 181 | 0.518 | 0.457 | 0.584 | 0.418 | 0.613 |
| b2mixed-biomedbert-s42 | ood_names | 438 | 0.338 | 0.508 | 0.354 | 0.270 | -0.013 | 0.494 | 34 | 70 | 114 | 220 | 0.515 | 0.449 | 0.577 | 0.408 | 0.605 |
| b2mixed-biomedbert-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.592 | 0.000 | 0.210 | 21 | 0 | 29 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | ood_swap_sentence | 100 | 0.500 | 0.514 | 0.555 | 0.447 | -0.040 | 0.480 | 21 | 23 | 29 | 27 | NA | 0.479 | 0.561 | NA | NA |
| b2mixed-biomedbert-s42 | oodold_empty | 1944 | 0.333 | 0.450 | 0.311 | 0.284 | -0.005 | 0.498 | 162 | 330 | 486 | 966 | 0.453 | 0.411 | 0.489 | 0.395 | 0.499 |
| b2mixed-biomedbert-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.704 | 0.000 | 0.271 | 139 | 0 | 117 | 0 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.948 | 0.759 | 0.674 | 0.628 | 0.863 | 304 | 227 | 67 | 2212 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | swap_novel_sentence | 2810 | 0.132 | 0.948 | 0.764 | 0.670 | 0.628 | 0.872 | 315 | 254 | 56 | 2185 | NA | NA | NA | NA | NA |
| b2mixed-biomedbert-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.943 | 0.742 | 0.671 | 0.619 | 0.833 | 273 | 170 | 98 | 2269 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | test_sentence | 2810 | 0.132 | 0.936 | 0.707 | 0.672 | 0.620 | 0.827 | 266 | 155 | 105 | 2284 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | test_masked | 2810 | 0.132 | 0.794 | 0.345 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | test_empty | 2810 | 0.132 | 0.631 | 0.178 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | test_names | 2810 | 0.132 | 0.615 | 0.172 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | ood_empty | 438 | 0.338 | 0.464 | 0.312 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.518 | 0.402 | 0.526 | 0.368 | 0.560 |
| b2sentence-bertbase-s1 | ood_names | 438 | 0.338 | 0.428 | 0.299 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.468 | 0.378 | 0.482 | 0.343 | 0.520 |
| b2sentence-bertbase-s1 | ood_sentence | 50 | 1.000 | NA | NA | 0.485 | 0.000 | 0.160 | 16 | 0 | 34 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | ood_swap_sentence | 100 | 0.500 | 0.494 | 0.506 | 0.386 | -0.021 | 0.490 | 16 | 17 | 34 | 33 | NA | 0.466 | 0.519 | NA | NA |
| b2sentence-bertbase-s1 | oodold_empty | 1944 | 0.333 | 0.515 | 0.335 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.492 | 0.474 | 0.556 | 0.465 | 0.565 |
| b2sentence-bertbase-s1 | oodold_sentence | 256 | 1.000 | NA | NA | 0.520 | 0.000 | 0.176 | 90 | 0 | 166 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | swap_vocab_sentence | 2810 | 0.132 | 0.917 | 0.676 | 0.621 | 0.560 | 0.803 | 254 | 193 | 117 | 2246 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | swap_novel_sentence | 2810 | 0.132 | 0.920 | 0.686 | 0.621 | 0.561 | 0.811 | 263 | 213 | 108 | 2226 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s1 | swap_pseudo_sentence | 2810 | 0.132 | 0.924 | 0.699 | 0.621 | 0.561 | 0.790 | 240 | 162 | 131 | 2277 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | test_sentence | 2810 | 0.132 | 0.949 | 0.718 | 0.675 | 0.626 | 0.850 | 290 | 198 | 81 | 2241 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | test_masked | 2810 | 0.132 | 0.817 | 0.401 | 0.047 | 0.145 | 0.512 | 9 | 0 | 362 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | test_empty | 2810 | 0.132 | 0.539 | 0.146 | 0.000 | -0.010 | 0.500 | 0 | 2 | 371 | 2437 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | test_names | 2810 | 0.132 | 0.514 | 0.133 | 0.011 | 0.015 | 0.501 | 2 | 7 | 369 | 2432 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | ood_empty | 438 | 0.338 | 0.432 | 0.319 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.494 | 0.362 | 0.515 | 0.327 | 0.546 |
| b2sentence-bertbase-s2 | ood_names | 438 | 0.338 | 0.454 | 0.311 | 0.000 | -0.048 | 0.497 | 0 | 2 | 148 | 288 | 0.469 | 0.396 | 0.516 | 0.352 | 0.551 |
| b2sentence-bertbase-s2 | ood_sentence | 50 | 1.000 | NA | NA | 0.592 | 0.000 | 0.210 | 21 | 0 | 29 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | ood_swap_sentence | 100 | 0.500 | 0.488 | 0.504 | 0.442 | -0.060 | 0.470 | 21 | 24 | 29 | 26 | NA | 0.456 | 0.522 | NA | NA |
| b2sentence-bertbase-s2 | oodold_empty | 1944 | 0.333 | 0.497 | 0.331 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.485 | 0.458 | 0.535 | 0.444 | 0.550 |
| b2sentence-bertbase-s2 | oodold_sentence | 256 | 1.000 | NA | NA | 0.601 | 0.000 | 0.215 | 110 | 0 | 146 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | swap_vocab_sentence | 2810 | 0.132 | 0.924 | 0.687 | 0.632 | 0.574 | 0.816 | 265 | 202 | 106 | 2237 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | swap_novel_sentence | 2810 | 0.132 | 0.932 | 0.705 | 0.632 | 0.575 | 0.824 | 274 | 222 | 97 | 2217 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s2 | swap_pseudo_sentence | 2810 | 0.132 | 0.933 | 0.723 | 0.657 | 0.602 | 0.824 | 267 | 175 | 104 | 2264 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | test_sentence | 2810 | 0.132 | 0.935 | 0.740 | 0.672 | 0.620 | 0.830 | 270 | 163 | 101 | 2276 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | test_masked | 2810 | 0.132 | 0.805 | 0.445 | 0.027 | 0.108 | 0.507 | 5 | 0 | 366 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | test_empty | 2810 | 0.132 | 0.611 | 0.168 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | test_names | 2810 | 0.132 | 0.476 | 0.117 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | ood_empty | 438 | 0.338 | 0.429 | 0.299 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.470 | 0.357 | 0.502 | 0.318 | 0.532 |
| b2sentence-bertbase-s3 | ood_names | 438 | 0.338 | 0.415 | 0.293 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.470 | 0.361 | 0.472 | 0.322 | 0.510 |
| b2sentence-bertbase-s3 | ood_sentence | 50 | 1.000 | NA | NA | 0.507 | 0.000 | 0.170 | 17 | 0 | 33 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | ood_swap_sentence | 100 | 0.500 | 0.490 | 0.501 | 0.400 | -0.021 | 0.490 | 17 | 18 | 33 | 32 | NA | 0.449 | 0.512 | NA | NA |
| b2sentence-bertbase-s3 | oodold_empty | 1944 | 0.333 | 0.513 | 0.340 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.485 | 0.479 | 0.545 | 0.466 | 0.563 |
| b2sentence-bertbase-s3 | oodold_sentence | 256 | 1.000 | NA | NA | 0.554 | 0.000 | 0.191 | 98 | 0 | 158 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | swap_vocab_sentence | 2810 | 0.132 | 0.927 | 0.725 | 0.672 | 0.620 | 0.831 | 271 | 165 | 100 | 2274 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | swap_novel_sentence | 2810 | 0.132 | 0.934 | 0.743 | 0.665 | 0.613 | 0.834 | 276 | 183 | 95 | 2256 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s3 | swap_pseudo_sentence | 2810 | 0.132 | 0.926 | 0.729 | 0.657 | 0.604 | 0.804 | 246 | 132 | 125 | 2307 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | test_sentence | 2810 | 0.132 | 0.942 | 0.689 | 0.683 | 0.635 | 0.851 | 289 | 186 | 82 | 2253 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | test_masked | 2810 | 0.132 | 0.794 | 0.337 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | test_empty | 2810 | 0.132 | 0.611 | 0.166 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | test_names | 2810 | 0.132 | 0.588 | 0.171 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | ood_empty | 438 | 0.338 | 0.455 | 0.301 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.507 | 0.382 | 0.530 | 0.353 | 0.553 |
| b2sentence-bertbase-s4 | ood_names | 438 | 0.338 | 0.477 | 0.333 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.482 | 0.394 | 0.558 | 0.371 | 0.591 |
| b2sentence-bertbase-s4 | ood_sentence | 50 | 1.000 | NA | NA | 0.529 | 0.000 | 0.180 | 18 | 0 | 32 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | ood_swap_sentence | 100 | 0.500 | 0.506 | 0.522 | 0.429 | 0.042 | 0.520 | 18 | 16 | 32 | 34 | NA | 0.490 | 0.531 | NA | NA |
| b2sentence-bertbase-s4 | oodold_empty | 1944 | 0.333 | 0.465 | 0.314 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.465 | 0.431 | 0.501 | 0.417 | 0.518 |
| b2sentence-bertbase-s4 | oodold_sentence | 256 | 1.000 | NA | NA | 0.554 | 0.000 | 0.191 | 98 | 0 | 158 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | swap_vocab_sentence | 2810 | 0.132 | 0.916 | 0.654 | 0.608 | 0.546 | 0.802 | 257 | 217 | 114 | 2222 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | swap_novel_sentence | 2810 | 0.132 | 0.924 | 0.674 | 0.608 | 0.549 | 0.820 | 278 | 265 | 93 | 2174 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s4 | swap_pseudo_sentence | 2810 | 0.132 | 0.932 | 0.688 | 0.629 | 0.571 | 0.818 | 269 | 215 | 102 | 2224 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | test_sentence | 2810 | 0.132 | 0.936 | 0.694 | 0.627 | 0.575 | 0.775 | 221 | 113 | 150 | 2326 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | test_masked | 2810 | 0.132 | 0.804 | 0.338 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | test_empty | 2810 | 0.132 | 0.629 | 0.180 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | test_names | 2810 | 0.132 | 0.575 | 0.159 | 0.005 | 0.029 | 0.501 | 1 | 1 | 370 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | ood_empty | 438 | 0.338 | 0.445 | 0.310 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.517 | 0.382 | 0.522 | 0.341 | 0.544 |
| b2sentence-bertbase-s42 | ood_names | 438 | 0.338 | 0.420 | 0.302 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.485 | 0.353 | 0.493 | 0.324 | 0.511 |
| b2sentence-bertbase-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.438 | 0.000 | 0.140 | 14 | 0 | 36 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | ood_swap_sentence | 100 | 0.500 | 0.518 | 0.529 | 0.354 | -0.022 | 0.490 | 14 | 15 | 36 | 35 | NA | 0.493 | 0.556 | NA | NA |
| b2sentence-bertbase-s42 | oodold_empty | 1944 | 0.333 | 0.475 | 0.315 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.485 | 0.437 | 0.517 | 0.423 | 0.527 |
| b2sentence-bertbase-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.499 | 0.000 | 0.166 | 85 | 0 | 171 | 0 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.914 | 0.659 | 0.606 | 0.549 | 0.767 | 218 | 130 | 153 | 2309 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | swap_novel_sentence | 2810 | 0.132 | 0.926 | 0.688 | 0.621 | 0.563 | 0.783 | 232 | 144 | 139 | 2295 | NA | NA | NA | NA | NA |
| b2sentence-bertbase-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.927 | 0.696 | 0.638 | 0.585 | 0.786 | 231 | 122 | 140 | 2317 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | test_sentence | 2810 | 0.132 | 0.946 | 0.720 | 0.675 | 0.625 | 0.818 | 256 | 131 | 115 | 2308 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | test_masked | 2810 | 0.132 | 0.860 | 0.427 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | test_empty | 2810 | 0.132 | 0.581 | 0.162 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | test_names | 2810 | 0.132 | 0.589 | 0.154 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | ood_empty | 438 | 0.338 | 0.485 | 0.376 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.489 | 0.407 | 0.562 | 0.382 | 0.590 |
| b2sentence-biobert-s42 | ood_names | 438 | 0.338 | 0.496 | 0.368 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.532 | 0.414 | 0.576 | 0.389 | 0.609 |
| b2sentence-biobert-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | ood_swap_sentence | 100 | 0.500 | 0.509 | 0.496 | 0.370 | -0.022 | 0.490 | 15 | 16 | 35 | 34 | NA | 0.458 | 0.565 | NA | NA |
| b2sentence-biobert-s42 | oodold_empty | 1944 | 0.333 | 0.494 | 0.333 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.484 | 0.457 | 0.534 | 0.442 | 0.546 |
| b2sentence-biobert-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.550 | 0.000 | 0.189 | 97 | 0 | 159 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.934 | 0.709 | 0.648 | 0.592 | 0.806 | 250 | 151 | 121 | 2288 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | swap_novel_sentence | 2810 | 0.132 | 0.940 | 0.728 | 0.672 | 0.620 | 0.833 | 273 | 169 | 98 | 2270 | NA | NA | NA | NA | NA |
| b2sentence-biobert-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.943 | 0.739 | 0.660 | 0.606 | 0.818 | 260 | 157 | 111 | 2282 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | test_sentence | 2810 | 0.132 | 0.959 | 0.755 | 0.704 | 0.659 | 0.865 | 298 | 178 | 73 | 2261 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | test_masked | 2810 | 0.132 | 0.822 | 0.452 | 0.052 | 0.153 | 0.513 | 10 | 0 | 361 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | test_empty | 2810 | 0.132 | 0.569 | 0.171 | 0.026 | 0.047 | 0.505 | 5 | 9 | 366 | 2430 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | test_names | 2810 | 0.132 | 0.537 | 0.166 | 0.005 | 0.048 | 0.501 | 1 | 0 | 370 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | ood_empty | 438 | 0.338 | 0.527 | 0.359 | 0.051 | 0.020 | 0.503 | 4 | 6 | 144 | 284 | 0.543 | 0.443 | 0.610 | 0.420 | 0.644 |
| b2sentence-biomedbert-disjoint-s42 | ood_names | 438 | 0.338 | 0.466 | 0.312 | 0.000 | -0.034 | 0.498 | 0 | 1 | 148 | 289 | 0.506 | 0.400 | 0.539 | 0.356 | 0.569 |
| b2sentence-biomedbert-disjoint-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.630 | 0.000 | 0.230 | 23 | 0 | 27 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | ood_swap_sentence | 100 | 0.500 | 0.511 | 0.548 | 0.479 | 0.000 | 0.500 | 23 | 23 | 27 | 27 | NA | 0.478 | 0.556 | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | oodold_empty | 1944 | 0.333 | 0.471 | 0.313 | 0.035 | -0.003 | 0.500 | 12 | 25 | 636 | 1271 | 0.465 | 0.436 | 0.509 | 0.417 | 0.523 |
| b2sentence-biomedbert-disjoint-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.694 | 0.000 | 0.266 | 136 | 0 | 120 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.947 | 0.742 | 0.652 | 0.605 | 0.858 | 305 | 259 | 66 | 2180 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | swap_novel_sentence | 2810 | 0.132 | 0.950 | 0.746 | 0.654 | 0.610 | 0.866 | 313 | 273 | 58 | 2166 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-disjoint-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.949 | 0.744 | 0.688 | 0.641 | 0.859 | 296 | 194 | 75 | 2245 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | test_sentence | 2810 | 0.132 | 0.959 | 0.780 | 0.717 | 0.677 | 0.883 | 313 | 189 | 58 | 2250 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | test_masked | 2810 | 0.132 | 0.848 | 0.449 | 0.016 | 0.084 | 0.504 | 3 | 0 | 368 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | test_empty | 2810 | 0.132 | 0.551 | 0.180 | 0.005 | 0.013 | 0.501 | 1 | 3 | 370 | 2436 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | test_names | 2810 | 0.132 | 0.490 | 0.159 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | ood_empty | 438 | 0.338 | 0.546 | 0.360 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.494 | 0.476 | 0.622 | 0.435 | 0.650 |
| b2sentence-biomedbert-s1 | ood_names | 438 | 0.338 | 0.470 | 0.322 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.425 | 0.393 | 0.546 | 0.362 | 0.577 |
| b2sentence-biomedbert-s1 | ood_sentence | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | ood_swap_sentence | 100 | 0.500 | 0.495 | 0.510 | 0.380 | 0.022 | 0.510 | 15 | 14 | 35 | 36 | NA | 0.453 | 0.533 | NA | NA |
| b2sentence-biomedbert-s1 | oodold_empty | 1944 | 0.333 | 0.486 | 0.321 | 0.000 | -0.016 | 0.500 | 0 | 1 | 648 | 1295 | 0.491 | 0.450 | 0.523 | 0.438 | 0.537 |
| b2sentence-biomedbert-s1 | oodold_sentence | 256 | 1.000 | NA | NA | 0.601 | 0.000 | 0.215 | 110 | 0 | 146 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | swap_vocab_sentence | 2810 | 0.132 | 0.948 | 0.771 | 0.709 | 0.667 | 0.876 | 308 | 190 | 63 | 2249 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | swap_novel_sentence | 2810 | 0.132 | 0.958 | 0.794 | 0.707 | 0.671 | 0.893 | 326 | 225 | 45 | 2214 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s1 | swap_pseudo_sentence | 2810 | 0.132 | 0.957 | 0.786 | 0.727 | 0.686 | 0.879 | 306 | 165 | 65 | 2274 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | test_sentence | 2810 | 0.132 | 0.970 | 0.836 | 0.742 | 0.704 | 0.887 | 311 | 156 | 60 | 2283 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | test_masked | 2810 | 0.132 | 0.857 | 0.427 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | test_empty | 2810 | 0.132 | 0.617 | 0.191 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | test_names | 2810 | 0.132 | 0.628 | 0.190 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | ood_empty | 438 | 0.338 | 0.470 | 0.322 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.495 | 0.398 | 0.546 | 0.367 | 0.572 |
| b2sentence-biomedbert-s2 | ood_names | 438 | 0.338 | 0.432 | 0.306 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.445 | 0.359 | 0.511 | 0.323 | 0.538 |
| b2sentence-biomedbert-s2 | ood_sentence | 50 | 1.000 | NA | NA | 0.507 | 0.000 | 0.170 | 17 | 0 | 33 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | ood_swap_sentence | 100 | 0.500 | 0.521 | 0.542 | 0.410 | 0.021 | 0.510 | 17 | 16 | 33 | 34 | NA | 0.466 | 0.573 | NA | NA |
| b2sentence-biomedbert-s2 | oodold_empty | 1944 | 0.333 | 0.482 | 0.317 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.496 | 0.447 | 0.519 | 0.429 | 0.533 |
| b2sentence-biomedbert-s2 | oodold_sentence | 256 | 1.000 | NA | NA | 0.631 | 0.000 | 0.230 | 118 | 0 | 138 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | swap_vocab_sentence | 2810 | 0.132 | 0.955 | 0.807 | 0.740 | 0.700 | 0.874 | 298 | 136 | 73 | 2303 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | swap_novel_sentence | 2810 | 0.132 | 0.963 | 0.812 | 0.741 | 0.703 | 0.889 | 313 | 161 | 58 | 2278 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s2 | swap_pseudo_sentence | 2810 | 0.132 | 0.962 | 0.812 | 0.741 | 0.701 | 0.865 | 289 | 120 | 82 | 2319 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | test_sentence | 2810 | 0.132 | 0.964 | 0.799 | 0.722 | 0.684 | 0.891 | 320 | 196 | 51 | 2243 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | test_masked | 2810 | 0.132 | 0.883 | 0.550 | 0.063 | 0.168 | 0.516 | 12 | 0 | 359 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | test_empty | 2810 | 0.132 | 0.548 | 0.174 | 0.011 | 0.068 | 0.503 | 2 | 0 | 369 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | test_names | 2810 | 0.132 | 0.449 | 0.138 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | ood_empty | 438 | 0.338 | 0.500 | 0.351 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.501 | 0.419 | 0.586 | 0.391 | 0.618 |
| b2sentence-biomedbert-s3 | ood_names | 438 | 0.338 | 0.462 | 0.312 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.498 | 0.385 | 0.536 | 0.359 | 0.568 |
| b2sentence-biomedbert-s3 | ood_sentence | 50 | 1.000 | NA | NA | 0.529 | 0.000 | 0.180 | 18 | 0 | 32 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | ood_swap_sentence | 100 | 0.500 | 0.487 | 0.508 | 0.424 | 0.021 | 0.510 | 18 | 17 | 32 | 33 | NA | 0.439 | 0.532 | NA | NA |
| b2sentence-biomedbert-s3 | oodold_empty | 1944 | 0.333 | 0.498 | 0.324 | 0.003 | 0.032 | 0.501 | 1 | 0 | 647 | 1296 | 0.498 | 0.464 | 0.535 | 0.452 | 0.548 |
| b2sentence-biomedbert-s3 | oodold_sentence | 256 | 1.000 | NA | NA | 0.663 | 0.000 | 0.248 | 127 | 0 | 129 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | swap_vocab_sentence | 2810 | 0.132 | 0.953 | 0.780 | 0.712 | 0.672 | 0.883 | 314 | 197 | 57 | 2242 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | swap_novel_sentence | 2810 | 0.132 | 0.957 | 0.776 | 0.711 | 0.673 | 0.891 | 323 | 215 | 48 | 2224 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s3 | swap_pseudo_sentence | 2810 | 0.132 | 0.956 | 0.784 | 0.733 | 0.695 | 0.891 | 317 | 177 | 54 | 2262 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | test_sentence | 2810 | 0.132 | 0.955 | 0.801 | 0.718 | 0.677 | 0.877 | 306 | 175 | 65 | 2264 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | test_masked | 2810 | 0.132 | 0.873 | 0.487 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | test_empty | 2810 | 0.132 | 0.589 | 0.191 | 0.005 | 0.048 | 0.501 | 1 | 0 | 370 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | test_names | 2810 | 0.132 | 0.513 | 0.158 | 0.005 | 0.029 | 0.501 | 1 | 1 | 370 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | ood_empty | 438 | 0.338 | 0.456 | 0.325 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.485 | 0.375 | 0.538 | 0.349 | 0.565 |
| b2sentence-biomedbert-s4 | ood_names | 438 | 0.338 | 0.435 | 0.306 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.472 | 0.351 | 0.526 | 0.321 | 0.548 |
| b2sentence-biomedbert-s4 | ood_sentence | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | ood_swap_sentence | 100 | 0.500 | 0.494 | 0.530 | 0.458 | 0.106 | 0.550 | 19 | 14 | 31 | 36 | NA | 0.441 | 0.538 | NA | NA |
| b2sentence-biomedbert-s4 | oodold_empty | 1944 | 0.333 | 0.448 | 0.300 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.461 | 0.415 | 0.482 | 0.404 | 0.495 |
| b2sentence-biomedbert-s4 | oodold_sentence | 256 | 1.000 | NA | NA | 0.638 | 0.000 | 0.234 | 120 | 0 | 136 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | swap_vocab_sentence | 2810 | 0.132 | 0.956 | 0.799 | 0.724 | 0.682 | 0.873 | 301 | 160 | 70 | 2279 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | swap_novel_sentence | 2810 | 0.132 | 0.959 | 0.805 | 0.733 | 0.694 | 0.885 | 311 | 167 | 60 | 2272 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s4 | swap_pseudo_sentence | 2810 | 0.132 | 0.955 | 0.778 | 0.714 | 0.670 | 0.836 | 266 | 108 | 105 | 2331 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | test_sentence | 2810 | 0.132 | 0.957 | 0.746 | 0.706 | 0.668 | 0.891 | 324 | 223 | 47 | 2216 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | test_masked | 2810 | 0.132 | 0.785 | 0.378 | 0.021 | 0.097 | 0.505 | 4 | 0 | 367 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | test_empty | 2810 | 0.132 | 0.609 | 0.176 | 0.005 | 0.048 | 0.501 | 1 | 0 | 370 | 2439 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | test_names | 2810 | 0.132 | 0.592 | 0.161 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | ood_empty | 438 | 0.338 | 0.474 | 0.355 | 0.013 | 0.067 | 0.503 | 1 | 0 | 147 | 290 | 0.489 | 0.407 | 0.540 | 0.363 | 0.573 |
| b2sentence-biomedbert-s42 | ood_names | 438 | 0.338 | 0.464 | 0.317 | 0.000 | -0.048 | 0.497 | 0 | 2 | 148 | 288 | 0.493 | 0.388 | 0.538 | 0.363 | 0.559 |
| b2sentence-biomedbert-s42 | ood_sentence | 50 | 1.000 | NA | NA | 0.718 | 0.000 | 0.280 | 28 | 0 | 22 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | ood_swap_sentence | 100 | 0.500 | 0.517 | 0.538 | 0.544 | 0.060 | 0.530 | 28 | 25 | 22 | 25 | NA | 0.485 | 0.557 | NA | NA |
| b2sentence-biomedbert-s42 | oodold_empty | 1944 | 0.333 | 0.447 | 0.306 | 0.000 | -0.028 | 0.499 | 0 | 3 | 648 | 1293 | 0.464 | 0.412 | 0.482 | 0.398 | 0.499 |
| b2sentence-biomedbert-s42 | oodold_sentence | 256 | 1.000 | NA | NA | 0.674 | 0.000 | 0.254 | 130 | 0 | 126 | 0 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | swap_vocab_sentence | 2810 | 0.132 | 0.923 | 0.671 | 0.612 | 0.565 | 0.852 | 313 | 339 | 58 | 2100 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | swap_novel_sentence | 2810 | 0.132 | 0.934 | 0.695 | 0.589 | 0.549 | 0.859 | 330 | 419 | 41 | 2020 | NA | NA | NA | NA | NA |
| b2sentence-biomedbert-s42 | swap_pseudo_sentence | 2810 | 0.132 | 0.925 | 0.675 | 0.619 | 0.566 | 0.839 | 295 | 287 | 76 | 2152 | NA | NA | NA | NA | NA |
| krag-bm25-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.600 | 0.179 | 0.258 | 0.114 | 0.571 | 133 | 526 | 238 | 1913 | NA | NA | NA | NA | NA |
| krag-bm25-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.459 | 0.330 | 0.267 | -0.024 | 0.489 | 34 | 73 | 114 | 217 | 0.440 | 0.385 | 0.532 | 0.345 | 0.566 |
| krag-contaminated-k5-c400-biomedbert-s1 | test | 2810 | 0.132 | 0.639 | 0.208 | 0.266 | 0.141 | 0.578 | 112 | 358 | 259 | 2081 | NA | NA | NA | NA | NA |
| krag-contaminated-k5-c400-biomedbert-s1 | ood | 438 | 0.338 | 0.573 | 0.390 | 0.367 | 0.095 | 0.545 | 49 | 70 | 99 | 220 | 0.544 | 0.509 | 0.640 | 0.473 | 0.673 |
| krag-contaminated-k5-c400-biomedbert-s2 | test | 2810 | 0.132 | 0.600 | 0.191 | 0.206 | 0.116 | 0.548 | 63 | 179 | 308 | 2260 | NA | NA | NA | NA | NA |
| krag-contaminated-k5-c400-biomedbert-s2 | ood | 438 | 0.338 | 0.604 | 0.445 | 0.313 | 0.142 | 0.555 | 34 | 35 | 114 | 255 | 0.564 | 0.547 | 0.666 | 0.503 | 0.703 |
| krag-contaminated-k5-c400-biomedbert-s3 | test | 2810 | 0.132 | 0.622 | 0.204 | 0.184 | 0.090 | 0.538 | 57 | 191 | 314 | 2248 | NA | NA | NA | NA | NA |
| krag-contaminated-k5-c400-biomedbert-s3 | ood | 438 | 0.338 | 0.578 | 0.420 | 0.152 | 0.032 | 0.509 | 14 | 22 | 134 | 268 | 0.583 | 0.501 | 0.648 | 0.459 | 0.687 |
| krag-contaminated-k5-c400-biomedbert-s4 | test | 2810 | 0.132 | 0.631 | 0.208 | 0.214 | 0.119 | 0.551 | 68 | 197 | 303 | 2242 | NA | NA | NA | NA | NA |
| krag-contaminated-k5-c400-biomedbert-s4 | ood | 438 | 0.338 | 0.593 | 0.444 | 0.254 | 0.168 | 0.552 | 24 | 17 | 124 | 273 | 0.563 | 0.509 | 0.676 | 0.480 | 0.700 |
| krag-contaminated-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.604 | 0.195 | 0.173 | 0.074 | 0.532 | 54 | 201 | 317 | 2238 | NA | NA | NA | NA | NA |
| krag-contaminated-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.561 | 0.401 | 0.061 | -0.002 | 0.500 | 5 | 10 | 143 | 280 | 0.489 | 0.480 | 0.632 | 0.434 | 0.678 |
| krag-dense-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.647 | 0.196 | 0.228 | 0.121 | 0.557 | 79 | 242 | 292 | 2197 | NA | NA | NA | NA | NA |
| krag-dense-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.523 | 0.353 | 0.343 | -0.004 | 0.498 | 52 | 103 | 96 | 187 | 0.490 | 0.454 | 0.598 | 0.422 | 0.629 |
| krag-excl_clinical_pharmacology-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.640 | 0.196 | 0.200 | 0.091 | 0.542 | 68 | 241 | 303 | 2198 | NA | NA | NA | NA | NA |
| krag-excl_clinical_pharmacology-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.525 | 0.375 | 0.171 | 0.048 | 0.514 | 16 | 23 | 132 | 267 | 0.489 | 0.455 | 0.593 | 0.416 | 0.626 |
| krag-excl_mechanism_of_action-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.661 | 0.220 | 0.225 | 0.117 | 0.555 | 78 | 244 | 293 | 2195 | NA | NA | NA | NA | NA |
| krag-excl_mechanism_of_action-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.522 | 0.381 | 0.262 | 0.077 | 0.529 | 28 | 38 | 120 | 252 | 0.522 | 0.446 | 0.602 | 0.400 | 0.626 |
| krag-excl_pharmacokinetics-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.595 | 0.174 | 0.202 | 0.077 | 0.539 | 77 | 315 | 294 | 2124 | NA | NA | NA | NA | NA |
| krag-excl_pharmacokinetics-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.503 | 0.343 | 0.267 | 0.011 | 0.505 | 32 | 60 | 116 | 230 | 0.505 | 0.429 | 0.578 | 0.395 | 0.614 |
| krag-excl_warnings_and_cautions-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.639 | 0.204 | 0.239 | 0.122 | 0.561 | 89 | 286 | 282 | 2153 | NA | NA | NA | NA | NA |
| krag-excl_warnings_and_cautions-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.496 | 0.342 | 0.204 | -0.038 | 0.485 | 23 | 54 | 125 | 236 | 0.490 | 0.435 | 0.559 | 0.401 | 0.594 |
| krag-hybrid-k1-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.647 | 0.210 | 0.208 | 0.121 | 0.549 | 63 | 173 | 308 | 2266 | NA | NA | NA | NA | NA |
| krag-hybrid-k1-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.460 | 0.323 | 0.284 | -0.028 | 0.487 | 38 | 82 | 110 | 208 | 0.478 | 0.391 | 0.530 | 0.359 | 0.564 |
| krag-hybrid-k3-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.652 | 0.203 | 0.205 | 0.109 | 0.547 | 65 | 198 | 306 | 2241 | NA | NA | NA | NA | NA |
| krag-hybrid-k3-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.477 | 0.330 | 0.247 | -0.061 | 0.472 | 32 | 79 | 116 | 211 | 0.498 | 0.414 | 0.541 | 0.380 | 0.571 |
| krag-hybrid-k5-c100-biomedbert-s42 | test | 2810 | 0.132 | 0.670 | 0.216 | 0.254 | 0.133 | 0.570 | 101 | 322 | 270 | 2117 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c100-biomedbert-s42 | ood | 438 | 0.338 | 0.505 | 0.335 | 0.383 | 0.011 | 0.506 | 64 | 122 | 84 | 168 | 0.534 | 0.451 | 0.568 | 0.399 | 0.615 |
| krag-hybrid-k5-c400-biomedbert-s1 | test | 2810 | 0.132 | 0.636 | 0.201 | 0.213 | 0.107 | 0.549 | 72 | 234 | 299 | 2205 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c400-biomedbert-s1 | ood | 438 | 0.338 | 0.474 | 0.320 | 0.283 | -0.031 | 0.485 | 38 | 83 | 110 | 207 | 0.506 | 0.400 | 0.545 | 0.371 | 0.582 |
| krag-hybrid-k5-c400-biomedbert-s2 | test | 2810 | 0.132 | 0.619 | 0.196 | 0.245 | 0.113 | 0.564 | 106 | 387 | 265 | 2052 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c400-biomedbert-s2 | ood | 438 | 0.338 | 0.496 | 0.337 | 0.379 | 0.046 | 0.524 | 58 | 100 | 90 | 190 | 0.534 | 0.437 | 0.556 | 0.395 | 0.597 |
| krag-hybrid-k5-c400-biomedbert-s3 | test | 2810 | 0.132 | 0.638 | 0.203 | 0.201 | 0.104 | 0.545 | 64 | 202 | 307 | 2237 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c400-biomedbert-s3 | ood | 438 | 0.338 | 0.466 | 0.313 | 0.216 | -0.085 | 0.462 | 27 | 75 | 121 | 215 | 0.538 | 0.409 | 0.530 | 0.364 | 0.573 |
| krag-hybrid-k5-c400-biomedbert-s4 | test | 2810 | 0.132 | 0.601 | 0.178 | 0.270 | 0.114 | 0.584 | 250 | 1232 | 121 | 1207 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c400-biomedbert-s4 | ood | 438 | 0.338 | 0.499 | 0.316 | 0.484 | 0.073 | 0.535 | 109 | 193 | 39 | 97 | 0.510 | 0.429 | 0.576 | 0.393 | 0.603 |
| krag-hybrid-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.676 | 0.216 | 0.223 | 0.121 | 0.555 | 74 | 220 | 297 | 2219 | NA | NA | NA | NA | NA |
| krag-hybrid-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.498 | 0.368 | 0.259 | 0.067 | 0.526 | 28 | 40 | 120 | 250 | 0.527 | 0.419 | 0.587 | 0.385 | 0.611 |
| krag-masked-k5-c400-biomedbert-s42 | test | 2810 | 0.132 | 0.679 | 0.228 | 0.205 | 0.110 | 0.547 | 65 | 197 | 306 | 2242 | NA | NA | NA | NA | NA |
| krag-masked-k5-c400-biomedbert-s42 | ood | 438 | 0.338 | 0.522 | 0.351 | 0.140 | -0.053 | 0.482 | 14 | 38 | 134 | 252 | 0.507 | 0.462 | 0.586 | 0.426 | 0.614 |
| llm-biomistral-names | test | 2810 | 0.132 | 0.591 | 0.162 | 0.233 | 0.013 | 0.501 | 371 | 2436 | 0 | 3 | NA | NA | NA | NA | NA |
| llm-biomistral-names | ood | 438 | 0.338 | 0.470 | 0.335 | 0.505 | 0.000 | 0.500 | 148 | 290 | 0 | 0 | 0.518 | 0.407 | 0.532 | 0.378 | 0.575 |
| llm-biomistral-names | oodold | 1944 | 0.333 | 0.522 | 0.355 | 0.500 | 0.000 | 0.500 | 648 | 1296 | 0 | 0 | 0.514 | 0.485 | 0.561 | 0.474 | 0.569 |
| llm-biomistral-rag | test | 2810 | 0.132 | 0.560 | 0.154 | 0.235 | 0.025 | 0.513 | 326 | 2080 | 45 | 359 | NA | NA | NA | NA | NA |
| llm-biomistral-rag | ood | 438 | 0.338 | 0.435 | 0.306 | 0.499 | 0.009 | 0.502 | 140 | 273 | 8 | 17 | 0.449 | 0.379 | 0.493 | 0.339 | 0.528 |
| llm-qwen-names | test | 2810 | 0.132 | 0.495 | 0.121 | 0.239 | 0.047 | 0.519 | 353 | 2227 | 18 | 212 | NA | NA | NA | NA | NA |
| llm-qwen-names | ood | 438 | 0.338 | 0.600 | 0.446 | 0.514 | 0.099 | 0.521 | 146 | 274 | 2 | 16 | 0.579 | 0.524 | 0.669 | 0.503 | 0.695 |
| llm-qwen-names | oodold | 1944 | 0.333 | 0.658 | 0.476 | 0.505 | 0.072 | 0.514 | 638 | 1240 | 10 | 56 | 0.608 | 0.622 | 0.693 | 0.610 | 0.711 |
| llm-qwen-rag | test | 2810 | 0.132 | 0.506 | 0.139 | 0.229 | 0.006 | 0.504 | 302 | 1967 | 69 | 472 | NA | NA | NA | NA | NA |
| llm-qwen-rag | ood | 438 | 0.338 | 0.484 | 0.332 | 0.491 | -0.002 | 0.499 | 133 | 261 | 15 | 29 | 0.513 | 0.411 | 0.568 | 0.377 | 0.596 |

## Seed aggregated

| group | key | n_seeds | seed_auroc_mean | seed_auroc_sd | n | prevalence | auroc | auprc | f1 | mcc | balanced_accuracy | tp | fp | fn | tn | auroc_within | auroc_pooled_lo95 | auroc_pooled_hi95 | auroc_pooled2_lo95 | auroc_pooled2_hi95 | partner_prior_auroc | beats_partner_prior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b1names/bertbase | ood_names | 1 | 0.543 | NA | 438 | 0.338 | 0.543 | 0.371 | 0.268 | 0.036 | 0.515 | 31 | 52 | 117 | 238 | 0.520 | 0.466 | 0.616 | 0.440 | 0.653 | 0.508 | False |
| b1names/bertbase | oodold_names | 1 | 0.469 | NA | 1944 | 0.333 | 0.469 | 0.318 | 0.216 | -0.033 | 0.486 | 109 | 253 | 539 | 1043 | 0.511 | 0.438 | 0.504 | 0.424 | 0.519 | 0.500 | False |
| b1names/bertbase | swap_novel_names | 1 | 0.516 | NA | 2810 | 0.132 | 0.516 | 0.141 | 0.143 | 0.029 | 0.513 | 48 | 252 | 323 | 2187 | NA | NA | NA | NA | NA | NA | NA |
| b1names/bertbase | swap_pseudo_names | 1 | 0.498 | NA | 2810 | 0.132 | 0.498 | 0.129 | 0.099 | -0.016 | 0.493 | 32 | 245 | 339 | 2194 | NA | NA | NA | NA | NA | NA | NA |
| b1names/bertbase | swap_vocab_names | 1 | 0.467 | NA | 2810 | 0.132 | 0.467 | 0.121 | 0.172 | -0.016 | 0.489 | 105 | 742 | 266 | 1697 | NA | NA | NA | NA | NA | NA | NA |
| b1names/bertbase | test_names | 1 | 0.618 | NA | 2810 | 0.132 | 0.618 | 0.197 | 0.257 | 0.125 | 0.571 | 114 | 402 | 257 | 2037 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biobert | ood_names | 1 | 0.476 | NA | 438 | 0.338 | 0.476 | 0.363 | 0.317 | 0.015 | 0.507 | 43 | 80 | 105 | 210 | 0.514 | 0.401 | 0.550 | 0.372 | 0.580 | 0.508 | False |
| b1names/biobert | oodold_names | 1 | 0.502 | NA | 1944 | 0.333 | 0.502 | 0.335 | 0.275 | 0.034 | 0.515 | 143 | 248 | 505 | 1048 | 0.511 | 0.465 | 0.540 | 0.453 | 0.554 | 0.500 | False |
| b1names/biobert | swap_novel_names | 1 | 0.508 | NA | 2810 | 0.132 | 0.508 | 0.135 | 0.174 | 0.019 | 0.511 | 81 | 477 | 290 | 1962 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biobert | swap_pseudo_names | 1 | 0.479 | NA | 2810 | 0.132 | 0.479 | 0.127 | 0.108 | -0.006 | 0.498 | 35 | 242 | 336 | 2197 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biobert | swap_vocab_names | 1 | 0.494 | NA | 2810 | 0.132 | 0.494 | 0.131 | 0.161 | -0.009 | 0.494 | 82 | 566 | 289 | 1873 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biobert | test_names | 1 | 0.626 | NA | 2810 | 0.132 | 0.626 | 0.186 | 0.219 | 0.100 | 0.550 | 81 | 288 | 290 | 2151 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert/disjoint | ood_names | 1 | 0.520 | NA | 438 | 0.338 | 0.520 | 0.366 | 0.396 | 0.055 | 0.528 | 63 | 107 | 85 | 183 | 0.481 | 0.445 | 0.610 | 0.406 | 0.633 | 0.508 | False |
| b1names/biomedbert/disjoint | oodold_names | 1 | 0.497 | NA | 1944 | 0.333 | 0.497 | 0.339 | 0.341 | -0.004 | 0.498 | 228 | 461 | 420 | 835 | 0.474 | 0.459 | 0.535 | 0.442 | 0.546 | 0.500 | False |
| b1names/biomedbert/disjoint | swap_novel_names | 1 | 0.495 | NA | 2810 | 0.132 | 0.495 | 0.134 | 0.181 | -0.003 | 0.498 | 110 | 733 | 261 | 1706 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert/disjoint | swap_pseudo_names | 1 | 0.529 | NA | 2810 | 0.132 | 0.529 | 0.143 | 0.171 | 0.025 | 0.514 | 74 | 419 | 297 | 2020 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert/disjoint | swap_vocab_names | 1 | 0.490 | NA | 2810 | 0.132 | 0.490 | 0.129 | 0.184 | 0.015 | 0.510 | 99 | 604 | 272 | 1835 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert/disjoint | test_names | 1 | 0.613 | NA | 2810 | 0.132 | 0.613 | 0.188 | 0.237 | 0.092 | 0.556 | 114 | 478 | 257 | 1961 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert | ood_names | 5 | 0.505 | 0.023 | 438 | 0.338 | 0.505 | 0.353 | 0.401 | 0.020 | 0.511 | 70 | 131 | 78 | 159 | 0.514 | 0.450 | 0.566 | 0.415 | 0.594 | 0.508 | False |
| b1names/biomedbert | oodold_names | 5 | 0.478 | 0.011 | 1944 | 0.333 | 0.477 | 0.324 | 0.323 | -0.009 | 0.496 | 207 | 425 | 441 | 871 | 0.467 | 0.438 | 0.517 | 0.423 | 0.529 | 0.500 | False |
| b1names/biomedbert | swap_novel_names | 5 | 0.490 | 0.013 | 2810 | 0.132 | 0.486 | 0.127 | 0.153 | -0.011 | 0.493 | 73 | 512 | 298 | 1927 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert | swap_pseudo_names | 5 | 0.512 | 0.008 | 2810 | 0.132 | 0.512 | 0.136 | 0.092 | 0.032 | 0.510 | 23 | 104 | 348 | 2335 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert | swap_vocab_names | 5 | 0.490 | 0.013 | 2810 | 0.132 | 0.488 | 0.128 | 0.165 | -0.004 | 0.497 | 84 | 565 | 287 | 1874 | NA | NA | NA | NA | NA | NA | NA |
| b1names/biomedbert | test_names | 5 | 0.663 | 0.021 | 2810 | 0.132 | 0.671 | 0.218 | 0.262 | 0.140 | 0.575 | 106 | 331 | 265 | 2108 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | ood_empty | 5 | 0.493 | 0.035 | 438 | 0.338 | 0.461 | 0.322 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.472 | 0.400 | 0.525 | 0.371 | 0.549 | 0.508 | False |
| b2masked/biomedbert | ood_names | 5 | 0.489 | 0.041 | 438 | 0.338 | 0.449 | 0.303 | 0.000 | -0.048 | 0.497 | 0 | 2 | 148 | 288 | 0.474 | 0.396 | 0.508 | 0.366 | 0.538 | 0.508 | False |
| b2masked/biomedbert | ood_sentence | 5 | NA | NA | 50 | 1.000 | NA | NA | 0.246 | 0.000 | 0.070 | 7 | 0 | 43 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2masked/biomedbert | ood_swap_sentence | 5 | 0.504 | 0.006 | 100 | 0.500 | 0.504 | 0.554 | 0.222 | 0.030 | 0.510 | 7 | 6 | 43 | 44 | NA | 0.467 | 0.541 | NA | NA | NA | NA |
| b2masked/biomedbert | oodold_empty | 5 | 0.492 | 0.025 | 1944 | 0.333 | 0.463 | 0.316 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.493 | 0.428 | 0.499 | 0.413 | 0.511 | 0.500 | False |
| b2masked/biomedbert | oodold_sentence | 5 | NA | NA | 256 | 1.000 | NA | NA | 0.270 | 0.000 | 0.078 | 40 | 0 | 216 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2masked/biomedbert | swap_novel_sentence | 5 | 0.860 | 0.041 | 2810 | 0.132 | 0.879 | 0.547 | 0.534 | 0.468 | 0.725 | 190 | 150 | 181 | 2289 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | swap_pseudo_sentence | 5 | 0.879 | 0.033 | 2810 | 0.132 | 0.891 | 0.574 | 0.557 | 0.490 | 0.743 | 204 | 158 | 167 | 2281 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | swap_vocab_sentence | 5 | 0.858 | 0.057 | 2810 | 0.132 | 0.880 | 0.518 | 0.553 | 0.482 | 0.755 | 220 | 204 | 151 | 2235 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | test_empty | 5 | 0.528 | 0.061 | 2810 | 0.132 | 0.567 | 0.156 | 0.000 | -0.010 | 0.500 | 0 | 2 | 371 | 2437 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | test_masked | 5 | 0.955 | 0.002 | 2810 | 0.132 | 0.959 | 0.795 | 0.717 | 0.673 | 0.866 | 296 | 159 | 75 | 2280 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | test_names | 5 | 0.515 | 0.041 | 2810 | 0.132 | 0.570 | 0.157 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA | NA | NA |
| b2masked/biomedbert | test_sentence | 5 | 0.834 | 0.056 | 2810 | 0.132 | 0.855 | 0.428 | 0.508 | 0.428 | 0.729 | 205 | 231 | 166 | 2208 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | ood_empty | 5 | 0.517 | 0.025 | 438 | 0.338 | 0.527 | 0.361 | 0.113 | 0.004 | 0.501 | 10 | 19 | 138 | 271 | 0.514 | 0.464 | 0.589 | 0.436 | 0.616 | 0.508 | False |
| b2mixed/bertbase | ood_names | 5 | 0.501 | 0.016 | 438 | 0.338 | 0.502 | 0.339 | 0.038 | -0.012 | 0.498 | 3 | 7 | 145 | 283 | 0.491 | 0.442 | 0.560 | 0.415 | 0.590 | 0.508 | False |
| b2mixed/bertbase | ood_sentence | 5 | NA | NA | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2mixed/bertbase | ood_swap_sentence | 5 | 0.504 | 0.012 | 100 | 0.500 | 0.506 | 0.509 | 0.366 | -0.043 | 0.480 | 15 | 17 | 35 | 33 | NA | 0.484 | 0.534 | NA | NA | NA | NA |
| b2mixed/bertbase | oodold_empty | 5 | 0.475 | 0.009 | 1944 | 0.333 | 0.472 | 0.318 | 0.136 | 0.005 | 0.502 | 55 | 106 | 593 | 1190 | 0.507 | 0.434 | 0.513 | 0.422 | 0.526 | 0.500 | False |
| b2mixed/bertbase | oodold_sentence | 5 | NA | NA | 256 | 1.000 | NA | NA | 0.490 | 0.000 | 0.162 | 83 | 0 | 173 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2mixed/bertbase | swap_novel_sentence | 5 | 0.909 | 0.014 | 2810 | 0.132 | 0.931 | 0.703 | 0.619 | 0.560 | 0.785 | 235 | 153 | 136 | 2286 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | swap_pseudo_sentence | 5 | 0.902 | 0.018 | 2810 | 0.132 | 0.924 | 0.686 | 0.599 | 0.545 | 0.757 | 208 | 115 | 163 | 2324 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | swap_vocab_sentence | 5 | 0.889 | 0.014 | 2810 | 0.132 | 0.912 | 0.669 | 0.593 | 0.531 | 0.765 | 219 | 149 | 152 | 2290 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | test_empty | 5 | 0.629 | 0.013 | 2810 | 0.132 | 0.633 | 0.204 | 0.157 | 0.092 | 0.532 | 42 | 121 | 329 | 2318 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | test_masked | 5 | 0.781 | 0.053 | 2810 | 0.132 | 0.812 | 0.367 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | test_names | 5 | 0.622 | 0.013 | 2810 | 0.132 | 0.632 | 0.199 | 0.072 | 0.080 | 0.514 | 15 | 28 | 356 | 2411 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/bertbase | test_sentence | 5 | 0.920 | 0.017 | 2810 | 0.132 | 0.943 | 0.725 | 0.634 | 0.579 | 0.784 | 230 | 125 | 141 | 2314 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | ood_empty | 1 | 0.483 | NA | 438 | 0.338 | 0.483 | 0.339 | 0.180 | 0.006 | 0.502 | 18 | 34 | 130 | 256 | 0.497 | 0.411 | 0.555 | 0.373 | 0.588 | 0.508 | False |
| b2mixed/biobert | ood_names | 1 | 0.480 | NA | 438 | 0.338 | 0.480 | 0.336 | 0.180 | 0.006 | 0.502 | 18 | 34 | 130 | 256 | 0.499 | 0.411 | 0.550 | 0.380 | 0.588 | 0.508 | False |
| b2mixed/biobert | ood_sentence | 1 | NA | NA | 50 | 1.000 | NA | NA | 0.333 | 0.000 | 0.100 | 10 | 0 | 40 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2mixed/biobert | ood_swap_sentence | 1 | 0.505 | NA | 100 | 0.500 | 0.505 | 0.524 | 0.294 | 0.052 | 0.520 | 10 | 8 | 40 | 42 | NA | 0.478 | 0.537 | NA | NA | NA | NA |
| b2mixed/biobert | oodold_empty | 1 | 0.501 | NA | 1944 | 0.333 | 0.501 | 0.342 | 0.209 | 0.012 | 0.505 | 97 | 182 | 551 | 1114 | 0.493 | 0.466 | 0.541 | 0.450 | 0.553 | 0.500 | False |
| b2mixed/biobert | oodold_sentence | 1 | NA | NA | 256 | 1.000 | NA | NA | 0.499 | 0.000 | 0.166 | 85 | 0 | 171 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2mixed/biobert | swap_novel_sentence | 1 | 0.929 | NA | 2810 | 0.132 | 0.929 | 0.707 | 0.634 | 0.576 | 0.799 | 246 | 159 | 125 | 2280 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | swap_pseudo_sentence | 1 | 0.927 | NA | 2810 | 0.132 | 0.927 | 0.686 | 0.614 | 0.558 | 0.772 | 221 | 128 | 150 | 2311 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | swap_vocab_sentence | 1 | 0.917 | NA | 2810 | 0.132 | 0.917 | 0.676 | 0.609 | 0.549 | 0.778 | 230 | 154 | 141 | 2285 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | test_empty | 1 | 0.635 | NA | 2810 | 0.132 | 0.635 | 0.207 | 0.154 | 0.062 | 0.525 | 46 | 181 | 325 | 2258 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | test_masked | 1 | 0.836 | NA | 2810 | 0.132 | 0.836 | 0.380 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | test_names | 1 | 0.637 | NA | 2810 | 0.132 | 0.637 | 0.210 | 0.158 | 0.063 | 0.526 | 48 | 189 | 323 | 2250 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biobert | test_sentence | 1 | 0.954 | NA | 2810 | 0.132 | 0.954 | 0.749 | 0.662 | 0.613 | 0.797 | 237 | 108 | 134 | 2331 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | ood_empty | 1 | 0.518 | NA | 438 | 0.338 | 0.518 | 0.353 | 0.333 | 0.018 | 0.509 | 47 | 87 | 101 | 203 | 0.536 | 0.460 | 0.577 | 0.423 | 0.607 | 0.508 | False |
| b2mixed/biomedbert/disjoint | ood_names | 1 | 0.507 | NA | 438 | 0.338 | 0.507 | 0.347 | 0.237 | -0.000 | 0.500 | 27 | 53 | 121 | 237 | 0.522 | 0.454 | 0.569 | 0.419 | 0.596 | 0.508 | False |
| b2mixed/biomedbert/disjoint | ood_sentence | 1 | NA | NA | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2mixed/biomedbert/disjoint | ood_swap_sentence | 1 | 0.511 | NA | 100 | 0.500 | 0.511 | 0.532 | 0.432 | 0.000 | 0.500 | 19 | 19 | 31 | 31 | NA | 0.480 | 0.545 | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | oodold_empty | 1 | 0.470 | NA | 1944 | 0.333 | 0.470 | 0.329 | 0.239 | -0.011 | 0.495 | 123 | 258 | 525 | 1038 | 0.479 | 0.432 | 0.511 | 0.419 | 0.523 | 0.500 | False |
| b2mixed/biomedbert/disjoint | oodold_sentence | 1 | NA | NA | 256 | 1.000 | NA | NA | 0.649 | 0.000 | 0.240 | 123 | 0 | 133 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2mixed/biomedbert/disjoint | swap_novel_sentence | 1 | 0.947 | NA | 2810 | 0.132 | 0.947 | 0.736 | 0.644 | 0.604 | 0.874 | 325 | 313 | 46 | 2126 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | swap_pseudo_sentence | 1 | 0.940 | NA | 2810 | 0.132 | 0.940 | 0.727 | 0.653 | 0.598 | 0.828 | 272 | 190 | 99 | 2249 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | swap_vocab_sentence | 1 | 0.945 | NA | 2810 | 0.132 | 0.945 | 0.738 | 0.662 | 0.615 | 0.861 | 305 | 246 | 66 | 2193 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | test_empty | 1 | 0.645 | NA | 2810 | 0.132 | 0.645 | 0.202 | 0.186 | 0.095 | 0.539 | 57 | 184 | 314 | 2255 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | test_masked | 1 | 0.851 | NA | 2810 | 0.132 | 0.851 | 0.462 | 0.073 | 0.181 | 0.519 | 14 | 0 | 357 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | test_names | 1 | 0.627 | NA | 2810 | 0.132 | 0.627 | 0.200 | 0.158 | 0.087 | 0.531 | 43 | 131 | 328 | 2308 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert/disjoint | test_sentence | 1 | 0.955 | NA | 2810 | 0.132 | 0.955 | 0.746 | 0.692 | 0.651 | 0.877 | 313 | 220 | 58 | 2219 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | ood_empty | 5 | 0.513 | 0.019 | 438 | 0.338 | 0.529 | 0.376 | 0.336 | 0.100 | 0.544 | 41 | 55 | 107 | 235 | 0.523 | 0.457 | 0.608 | 0.410 | 0.637 | 0.508 | False |
| b2mixed/biomedbert | ood_names | 5 | 0.505 | 0.014 | 438 | 0.338 | 0.503 | 0.339 | 0.118 | -0.032 | 0.491 | 11 | 27 | 137 | 263 | 0.490 | 0.437 | 0.579 | 0.395 | 0.606 | 0.508 | False |
| b2mixed/biomedbert | ood_sentence | 5 | NA | NA | 50 | 1.000 | NA | NA | 0.551 | 0.000 | 0.190 | 19 | 0 | 31 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2mixed/biomedbert | ood_swap_sentence | 5 | 0.508 | 0.005 | 100 | 0.500 | 0.507 | 0.533 | 0.437 | 0.021 | 0.510 | 19 | 18 | 31 | 32 | NA | 0.475 | 0.553 | NA | NA | NA | NA |
| b2mixed/biomedbert | oodold_empty | 5 | 0.457 | 0.008 | 1944 | 0.333 | 0.452 | 0.318 | 0.209 | -0.011 | 0.496 | 100 | 211 | 548 | 1085 | 0.455 | 0.412 | 0.495 | 0.399 | 0.504 | 0.500 | False |
| b2mixed/biomedbert | oodold_sentence | 5 | NA | NA | 256 | 1.000 | NA | NA | 0.687 | 0.000 | 0.262 | 134 | 0 | 122 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2mixed/biomedbert | swap_novel_sentence | 5 | 0.953 | 0.006 | 2810 | 0.132 | 0.961 | 0.806 | 0.713 | 0.676 | 0.895 | 326 | 218 | 45 | 2221 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | swap_pseudo_sentence | 5 | 0.946 | 0.006 | 2810 | 0.132 | 0.957 | 0.787 | 0.707 | 0.661 | 0.850 | 282 | 145 | 89 | 2294 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | swap_vocab_sentence | 5 | 0.944 | 0.006 | 2810 | 0.132 | 0.954 | 0.773 | 0.713 | 0.671 | 0.878 | 309 | 187 | 62 | 2252 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | test_empty | 5 | 0.670 | 0.009 | 2810 | 0.132 | 0.678 | 0.220 | 0.194 | 0.119 | 0.545 | 55 | 142 | 316 | 2297 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | test_masked | 5 | 0.857 | 0.024 | 2810 | 0.132 | 0.902 | 0.616 | 0.011 | 0.068 | 0.503 | 2 | 0 | 369 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | test_names | 5 | 0.653 | 0.008 | 2810 | 0.132 | 0.662 | 0.220 | 0.147 | 0.107 | 0.532 | 36 | 82 | 335 | 2357 | NA | NA | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | test_sentence | 5 | 0.955 | 0.007 | 2810 | 0.132 | 0.963 | 0.783 | 0.706 | 0.663 | 0.874 | 307 | 192 | 64 | 2247 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | ood_empty | 5 | 0.445 | 0.015 | 438 | 0.338 | 0.449 | 0.308 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.526 | 0.382 | 0.517 | 0.349 | 0.550 | 0.508 | False |
| b2sentence/bertbase | ood_names | 5 | 0.439 | 0.026 | 438 | 0.338 | 0.442 | 0.302 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.486 | 0.389 | 0.501 | 0.353 | 0.532 | 0.508 | False |
| b2sentence/bertbase | ood_sentence | 5 | NA | NA | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2sentence/bertbase | ood_swap_sentence | 5 | 0.499 | 0.013 | 100 | 0.500 | 0.498 | 0.512 | 0.366 | -0.043 | 0.480 | 15 | 17 | 35 | 33 | NA | 0.473 | 0.528 | NA | NA | NA | NA |
| b2sentence/bertbase | oodold_empty | 5 | 0.493 | 0.023 | 1944 | 0.333 | 0.480 | 0.319 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.478 | 0.443 | 0.517 | 0.431 | 0.532 | 0.500 | False |
| b2sentence/bertbase | oodold_sentence | 5 | NA | NA | 256 | 1.000 | NA | NA | 0.545 | 0.000 | 0.188 | 96 | 0 | 160 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2sentence/bertbase | swap_novel_sentence | 5 | 0.927 | 0.006 | 2810 | 0.132 | 0.939 | 0.729 | 0.654 | 0.600 | 0.822 | 266 | 176 | 105 | 2263 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | swap_pseudo_sentence | 5 | 0.928 | 0.004 | 2810 | 0.132 | 0.941 | 0.729 | 0.661 | 0.607 | 0.812 | 253 | 142 | 118 | 2297 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | swap_vocab_sentence | 5 | 0.919 | 0.006 | 2810 | 0.132 | 0.933 | 0.714 | 0.643 | 0.586 | 0.807 | 252 | 161 | 119 | 2278 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | test_empty | 5 | 0.604 | 0.038 | 2810 | 0.132 | 0.636 | 0.175 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | test_masked | 5 | 0.803 | 0.010 | 2810 | 0.132 | 0.825 | 0.424 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | test_names | 5 | 0.553 | 0.057 | 2810 | 0.132 | 0.578 | 0.156 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/bertbase | test_sentence | 5 | 0.940 | 0.006 | 2810 | 0.132 | 0.953 | 0.739 | 0.681 | 0.631 | 0.832 | 269 | 150 | 102 | 2289 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | ood_empty | 1 | 0.485 | NA | 438 | 0.338 | 0.485 | 0.376 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.489 | 0.407 | 0.562 | 0.382 | 0.590 | 0.508 | False |
| b2sentence/biobert | ood_names | 1 | 0.496 | NA | 438 | 0.338 | 0.496 | 0.368 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.532 | 0.414 | 0.576 | 0.389 | 0.609 | 0.508 | False |
| b2sentence/biobert | ood_sentence | 1 | NA | NA | 50 | 1.000 | NA | NA | 0.462 | 0.000 | 0.150 | 15 | 0 | 35 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2sentence/biobert | ood_swap_sentence | 1 | 0.509 | NA | 100 | 0.500 | 0.509 | 0.496 | 0.370 | -0.022 | 0.490 | 15 | 16 | 35 | 34 | NA | 0.458 | 0.565 | NA | NA | NA | NA |
| b2sentence/biobert | oodold_empty | 1 | 0.494 | NA | 1944 | 0.333 | 0.494 | 0.333 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.484 | 0.457 | 0.534 | 0.442 | 0.546 | 0.500 | False |
| b2sentence/biobert | oodold_sentence | 1 | NA | NA | 256 | 1.000 | NA | NA | 0.550 | 0.000 | 0.189 | 97 | 0 | 159 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2sentence/biobert | swap_novel_sentence | 1 | 0.940 | NA | 2810 | 0.132 | 0.940 | 0.728 | 0.672 | 0.620 | 0.833 | 273 | 169 | 98 | 2270 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | swap_pseudo_sentence | 1 | 0.943 | NA | 2810 | 0.132 | 0.943 | 0.739 | 0.660 | 0.606 | 0.818 | 260 | 157 | 111 | 2282 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | swap_vocab_sentence | 1 | 0.934 | NA | 2810 | 0.132 | 0.934 | 0.709 | 0.648 | 0.592 | 0.806 | 250 | 151 | 121 | 2288 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | test_empty | 1 | 0.581 | NA | 2810 | 0.132 | 0.581 | 0.162 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | test_masked | 1 | 0.860 | NA | 2810 | 0.132 | 0.860 | 0.427 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | test_names | 1 | 0.589 | NA | 2810 | 0.132 | 0.589 | 0.154 | 0.000 | 0.000 | 0.500 | 0 | 0 | 371 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biobert | test_sentence | 1 | 0.946 | NA | 2810 | 0.132 | 0.946 | 0.720 | 0.675 | 0.625 | 0.818 | 256 | 131 | 115 | 2308 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | ood_empty | 1 | 0.527 | NA | 438 | 0.338 | 0.527 | 0.359 | 0.051 | 0.020 | 0.503 | 4 | 6 | 144 | 284 | 0.543 | 0.443 | 0.610 | 0.420 | 0.644 | 0.508 | False |
| b2sentence/biomedbert/disjoint | ood_names | 1 | 0.466 | NA | 438 | 0.338 | 0.466 | 0.312 | 0.000 | -0.034 | 0.498 | 0 | 1 | 148 | 289 | 0.506 | 0.400 | 0.539 | 0.356 | 0.569 | 0.508 | False |
| b2sentence/biomedbert/disjoint | ood_sentence | 1 | NA | NA | 50 | 1.000 | NA | NA | 0.630 | 0.000 | 0.230 | 23 | 0 | 27 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2sentence/biomedbert/disjoint | ood_swap_sentence | 1 | 0.511 | NA | 100 | 0.500 | 0.511 | 0.548 | 0.479 | 0.000 | 0.500 | 23 | 23 | 27 | 27 | NA | 0.478 | 0.556 | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | oodold_empty | 1 | 0.471 | NA | 1944 | 0.333 | 0.471 | 0.313 | 0.035 | -0.003 | 0.500 | 12 | 25 | 636 | 1271 | 0.465 | 0.436 | 0.509 | 0.417 | 0.523 | 0.500 | False |
| b2sentence/biomedbert/disjoint | oodold_sentence | 1 | NA | NA | 256 | 1.000 | NA | NA | 0.694 | 0.000 | 0.266 | 136 | 0 | 120 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2sentence/biomedbert/disjoint | swap_novel_sentence | 1 | 0.950 | NA | 2810 | 0.132 | 0.950 | 0.746 | 0.654 | 0.610 | 0.866 | 313 | 273 | 58 | 2166 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | swap_pseudo_sentence | 1 | 0.949 | NA | 2810 | 0.132 | 0.949 | 0.744 | 0.688 | 0.641 | 0.859 | 296 | 194 | 75 | 2245 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | swap_vocab_sentence | 1 | 0.947 | NA | 2810 | 0.132 | 0.947 | 0.742 | 0.652 | 0.605 | 0.858 | 305 | 259 | 66 | 2180 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | test_empty | 1 | 0.569 | NA | 2810 | 0.132 | 0.569 | 0.171 | 0.026 | 0.047 | 0.505 | 5 | 9 | 366 | 2430 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | test_masked | 1 | 0.822 | NA | 2810 | 0.132 | 0.822 | 0.452 | 0.052 | 0.153 | 0.513 | 10 | 0 | 361 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | test_names | 1 | 0.537 | NA | 2810 | 0.132 | 0.537 | 0.166 | 0.005 | 0.048 | 0.501 | 1 | 0 | 370 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert/disjoint | test_sentence | 1 | 0.959 | NA | 2810 | 0.132 | 0.959 | 0.755 | 0.704 | 0.659 | 0.865 | 298 | 178 | 73 | 2261 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | ood_empty | 5 | 0.489 | 0.036 | 438 | 0.338 | 0.472 | 0.344 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.490 | 0.408 | 0.538 | 0.365 | 0.569 | 0.508 | False |
| b2sentence/biomedbert | ood_names | 5 | 0.452 | 0.018 | 438 | 0.338 | 0.459 | 0.316 | 0.000 | 0.000 | 0.500 | 0 | 0 | 148 | 290 | 0.491 | 0.384 | 0.533 | 0.356 | 0.554 | 0.508 | False |
| b2sentence/biomedbert | ood_sentence | 5 | NA | NA | 50 | 1.000 | NA | NA | 0.529 | 0.000 | 0.180 | 18 | 0 | 32 | 0 | NA | NA | NA | NA | NA | 0.508 | NA |
| b2sentence/biomedbert | ood_swap_sentence | 5 | 0.503 | 0.015 | 100 | 0.500 | 0.503 | 0.527 | 0.434 | 0.064 | 0.530 | 18 | 15 | 32 | 35 | NA | 0.464 | 0.545 | NA | NA | NA | NA |
| b2sentence/biomedbert | oodold_empty | 5 | 0.472 | 0.024 | 1944 | 0.333 | 0.446 | 0.303 | 0.000 | 0.000 | 0.500 | 0 | 0 | 648 | 1296 | 0.462 | 0.412 | 0.482 | 0.399 | 0.498 | 0.500 | False |
| b2sentence/biomedbert | oodold_sentence | 5 | NA | NA | 256 | 1.000 | NA | NA | 0.653 | 0.000 | 0.242 | 124 | 0 | 132 | 0 | NA | NA | NA | NA | NA | 0.500 | NA |
| b2sentence/biomedbert | swap_novel_sentence | 5 | 0.954 | 0.012 | 2810 | 0.132 | 0.961 | 0.811 | 0.714 | 0.678 | 0.893 | 324 | 212 | 47 | 2227 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | swap_pseudo_sentence | 5 | 0.951 | 0.015 | 2810 | 0.132 | 0.957 | 0.794 | 0.739 | 0.700 | 0.881 | 306 | 151 | 65 | 2288 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | swap_vocab_sentence | 5 | 0.947 | 0.014 | 2810 | 0.132 | 0.955 | 0.789 | 0.722 | 0.683 | 0.885 | 314 | 185 | 57 | 2254 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | test_empty | 5 | 0.583 | 0.032 | 2810 | 0.132 | 0.614 | 0.185 | 0.005 | 0.048 | 0.501 | 1 | 0 | 370 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | test_masked | 5 | 0.849 | 0.038 | 2810 | 0.132 | 0.874 | 0.518 | 0.011 | 0.068 | 0.503 | 2 | 0 | 369 | 2439 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | test_names | 5 | 0.534 | 0.074 | 2810 | 0.132 | 0.594 | 0.166 | 0.000 | -0.007 | 0.500 | 0 | 1 | 371 | 2438 | NA | NA | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | test_sentence | 5 | 0.961 | 0.006 | 2810 | 0.132 | 0.968 | 0.816 | 0.735 | 0.700 | 0.901 | 327 | 192 | 44 | 2247 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/bm25-k5-c400 | ood | 1 | 0.459 | NA | 438 | 0.338 | 0.459 | 0.330 | 0.267 | -0.024 | 0.489 | 34 | 73 | 114 | 217 | 0.440 | 0.385 | 0.532 | 0.345 | 0.566 | 0.508 | False |
| krag/biomedbert/bm25-k5-c400 | test | 1 | 0.600 | NA | 2810 | 0.132 | 0.600 | 0.179 | 0.258 | 0.114 | 0.571 | 133 | 526 | 238 | 1913 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/contaminated-k5-c400 | ood | 5 | 0.582 | 0.017 | 438 | 0.338 | 0.621 | 0.479 | 0.186 | 0.167 | 0.540 | 16 | 8 | 132 | 282 | 0.580 | 0.557 | 0.687 | 0.519 | 0.721 | 0.508 | True |
| krag/biomedbert/contaminated-k5-c400 | test | 5 | 0.619 | 0.017 | 2810 | 0.132 | 0.639 | 0.214 | 0.201 | 0.121 | 0.548 | 59 | 156 | 312 | 2283 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/dense-k5-c400 | ood | 1 | 0.523 | NA | 438 | 0.338 | 0.523 | 0.353 | 0.343 | -0.004 | 0.498 | 52 | 103 | 96 | 187 | 0.490 | 0.454 | 0.598 | 0.422 | 0.629 | 0.508 | False |
| krag/biomedbert/dense-k5-c400 | test | 1 | 0.647 | NA | 2810 | 0.132 | 0.647 | 0.196 | 0.228 | 0.121 | 0.557 | 79 | 242 | 292 | 2197 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/excl_clinical_pharmacology-k5-c400 | ood | 1 | 0.525 | NA | 438 | 0.338 | 0.525 | 0.375 | 0.171 | 0.048 | 0.514 | 16 | 23 | 132 | 267 | 0.489 | 0.455 | 0.593 | 0.416 | 0.626 | 0.508 | False |
| krag/biomedbert/excl_clinical_pharmacology-k5-c400 | test | 1 | 0.640 | NA | 2810 | 0.132 | 0.640 | 0.196 | 0.200 | 0.091 | 0.542 | 68 | 241 | 303 | 2198 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/excl_mechanism_of_action-k5-c400 | ood | 1 | 0.522 | NA | 438 | 0.338 | 0.522 | 0.381 | 0.262 | 0.077 | 0.529 | 28 | 38 | 120 | 252 | 0.522 | 0.446 | 0.602 | 0.400 | 0.626 | 0.508 | False |
| krag/biomedbert/excl_mechanism_of_action-k5-c400 | test | 1 | 0.661 | NA | 2810 | 0.132 | 0.661 | 0.220 | 0.225 | 0.117 | 0.555 | 78 | 244 | 293 | 2195 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/excl_pharmacokinetics-k5-c400 | ood | 1 | 0.503 | NA | 438 | 0.338 | 0.503 | 0.343 | 0.267 | 0.011 | 0.505 | 32 | 60 | 116 | 230 | 0.505 | 0.429 | 0.578 | 0.395 | 0.614 | 0.508 | False |
| krag/biomedbert/excl_pharmacokinetics-k5-c400 | test | 1 | 0.595 | NA | 2810 | 0.132 | 0.595 | 0.174 | 0.202 | 0.077 | 0.539 | 77 | 315 | 294 | 2124 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/excl_warnings_and_cautions-k5-c400 | ood | 1 | 0.496 | NA | 438 | 0.338 | 0.496 | 0.342 | 0.204 | -0.038 | 0.485 | 23 | 54 | 125 | 236 | 0.490 | 0.435 | 0.559 | 0.401 | 0.594 | 0.508 | False |
| krag/biomedbert/excl_warnings_and_cautions-k5-c400 | test | 1 | 0.639 | NA | 2810 | 0.132 | 0.639 | 0.204 | 0.239 | 0.122 | 0.561 | 89 | 286 | 282 | 2153 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/hybrid-k1-c400 | ood | 1 | 0.460 | NA | 438 | 0.338 | 0.460 | 0.323 | 0.284 | -0.028 | 0.487 | 38 | 82 | 110 | 208 | 0.478 | 0.391 | 0.530 | 0.359 | 0.564 | 0.508 | False |
| krag/biomedbert/hybrid-k1-c400 | test | 1 | 0.647 | NA | 2810 | 0.132 | 0.647 | 0.210 | 0.208 | 0.121 | 0.549 | 63 | 173 | 308 | 2266 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/hybrid-k3-c400 | ood | 1 | 0.477 | NA | 438 | 0.338 | 0.477 | 0.330 | 0.247 | -0.061 | 0.472 | 32 | 79 | 116 | 211 | 0.498 | 0.414 | 0.541 | 0.380 | 0.571 | 0.508 | False |
| krag/biomedbert/hybrid-k3-c400 | test | 1 | 0.652 | NA | 2810 | 0.132 | 0.652 | 0.203 | 0.205 | 0.109 | 0.547 | 65 | 198 | 306 | 2241 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/hybrid-k5-c100 | ood | 1 | 0.505 | NA | 438 | 0.338 | 0.505 | 0.335 | 0.383 | 0.011 | 0.506 | 64 | 122 | 84 | 168 | 0.534 | 0.451 | 0.568 | 0.399 | 0.615 | 0.508 | False |
| krag/biomedbert/hybrid-k5-c100 | test | 1 | 0.670 | NA | 2810 | 0.132 | 0.670 | 0.216 | 0.254 | 0.133 | 0.570 | 101 | 322 | 270 | 2117 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/hybrid-k5-c400 | ood | 5 | 0.487 | 0.015 | 438 | 0.338 | 0.496 | 0.324 | 0.288 | -0.013 | 0.494 | 38 | 78 | 110 | 212 | 0.519 | 0.426 | 0.568 | 0.400 | 0.591 | 0.508 | False |
| krag/biomedbert/hybrid-k5-c400 | test | 5 | 0.634 | 0.028 | 2810 | 0.132 | 0.645 | 0.210 | 0.212 | 0.101 | 0.548 | 74 | 253 | 297 | 2186 | NA | NA | NA | NA | NA | NA | NA |
| krag/biomedbert/masked-k5-c400 | ood | 1 | 0.522 | NA | 438 | 0.338 | 0.522 | 0.351 | 0.140 | -0.053 | 0.482 | 14 | 38 | 134 | 252 | 0.507 | 0.462 | 0.586 | 0.426 | 0.614 | 0.508 | False |
| krag/biomedbert/masked-k5-c400 | test | 1 | 0.679 | NA | 2810 | 0.132 | 0.679 | 0.228 | 0.205 | 0.110 | 0.547 | 65 | 197 | 306 | 2242 | NA | NA | NA | NA | NA | NA | NA |
| names/biomistral | ood | 1 | 0.470 | NA | 438 | 0.338 | 0.470 | 0.335 | 0.505 | 0.000 | 0.500 | 148 | 290 | 0 | 0 | 0.518 | 0.407 | 0.532 | 0.378 | 0.575 | 0.508 | False |
| names/biomistral | oodold | 1 | 0.522 | NA | 1944 | 0.333 | 0.522 | 0.355 | 0.500 | 0.000 | 0.500 | 648 | 1296 | 0 | 0 | 0.514 | 0.485 | 0.561 | 0.474 | 0.569 | 0.500 | False |
| names/biomistral | test | 1 | 0.591 | NA | 2810 | 0.132 | 0.591 | 0.162 | 0.233 | 0.013 | 0.501 | 371 | 2436 | 0 | 3 | NA | NA | NA | NA | NA | NA | NA |
| rag/biomistral | ood | 1 | 0.435 | NA | 438 | 0.338 | 0.435 | 0.306 | 0.499 | 0.009 | 0.502 | 140 | 273 | 8 | 17 | 0.449 | 0.379 | 0.493 | 0.339 | 0.528 | 0.508 | False |
| rag/biomistral | test | 1 | 0.560 | NA | 2810 | 0.132 | 0.560 | 0.154 | 0.235 | 0.025 | 0.513 | 326 | 2080 | 45 | 359 | NA | NA | NA | NA | NA | NA | NA |
| names/qwen | ood | 1 | 0.600 | NA | 438 | 0.338 | 0.600 | 0.446 | 0.514 | 0.099 | 0.521 | 146 | 274 | 2 | 16 | 0.579 | 0.524 | 0.669 | 0.503 | 0.695 | 0.508 | True |
| names/qwen | oodold | 1 | 0.658 | NA | 1944 | 0.333 | 0.658 | 0.476 | 0.505 | 0.072 | 0.514 | 638 | 1240 | 10 | 56 | 0.608 | 0.622 | 0.693 | 0.610 | 0.711 | 0.500 | True |
| names/qwen | test | 1 | 0.495 | NA | 2810 | 0.132 | 0.495 | 0.121 | 0.239 | 0.047 | 0.519 | 353 | 2227 | 18 | 212 | NA | NA | NA | NA | NA | NA | NA |
| rag/qwen | ood | 1 | 0.484 | NA | 438 | 0.338 | 0.484 | 0.332 | 0.491 | -0.002 | 0.499 | 133 | 261 | 15 | 29 | 0.513 | 0.411 | 0.568 | 0.377 | 0.596 | 0.508 | False |
| rag/qwen | test | 1 | 0.506 | NA | 2810 | 0.132 | 0.506 | 0.139 | 0.229 | 0.006 | 0.504 | 302 | 1967 | 69 | 472 | NA | NA | NA | NA | NA | NA | NA |

## OOD cohorts and label tiers (within-drug AUROC, two-way cluster bootstrap)

| group | key | cohort | tier | status | seed_gate | n | n_drugs | n_drugs_contributing | auroc_within | auroc_pooled | lo90 | hi90 | lo95 | hi95 | upper95_one_sided | p_tost | neg_disagreement_rate | expected_observed_if_true_070 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b1names/bertbase | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.520 | 0.543 | 0.417 | 0.626 | 0.393 | 0.648 | 0.626 | 0.108 | 0.367 | 0.627 |
| b1names/bertbase | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.508 | 0.581 | 0.366 | 0.660 | 0.335 | 0.690 | 0.660 | 0.153 | 0.000 | 0.700 |
| b1names/bertbase | oodold_names | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.511 | 0.469 | 0.464 | 0.560 | 0.454 | 0.570 | 0.560 | 0.002 | 0.384 | 0.623 |
| b1names/bertbase | oodold_names | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.511 | 0.456 | 0.429 | 0.596 | 0.413 | 0.613 | 0.596 | 0.044 | 0.000 | 0.700 |
| b1names/bertbase | oodold_names | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.514 | 0.470 | 0.460 | 0.562 | 0.451 | 0.571 | 0.562 | 0.001 | 0.404 | 0.619 |
| b1names/bertbase | oodold_names | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.511 | 0.462 | 0.425 | 0.596 | 0.401 | 0.615 | 0.596 | 0.041 | 0.000 | 0.700 |
| b1names/biobert | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.514 | 0.476 | 0.412 | 0.614 | 0.397 | 0.634 | 0.614 | 0.073 | 0.367 | 0.627 |
| b1names/biobert | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.546 | 0.529 | 0.390 | 0.704 | 0.357 | 0.732 | 0.704 | 0.290 | 0.000 | 0.700 |
| b1names/biobert | oodold_names | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.511 | 0.502 | 0.464 | 0.558 | 0.454 | 0.567 | 0.558 | 0.003 | 0.384 | 0.623 |
| b1names/biobert | oodold_names | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.509 | 0.520 | 0.425 | 0.590 | 0.411 | 0.602 | 0.590 | 0.027 | 0.000 | 0.700 |
| b1names/biobert | oodold_names | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.513 | 0.504 | 0.463 | 0.559 | 0.451 | 0.570 | 0.559 | 0.003 | 0.404 | 0.619 |
| b1names/biobert | oodold_names | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.509 | 0.521 | 0.429 | 0.590 | 0.406 | 0.605 | 0.590 | 0.036 | 0.000 | 0.700 |
| b1names/biomedbert/disjoint | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.481 | 0.520 | 0.355 | 0.603 | 0.329 | 0.624 | 0.603 | 0.135 | 0.367 | 0.627 |
| b1names/biomedbert/disjoint | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.481 | 0.539 | 0.310 | 0.649 | 0.278 | 0.668 | 0.649 | 0.217 | 0.000 | 0.700 |
| b1names/biomedbert/disjoint | oodold_names | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.474 | 0.497 | 0.418 | 0.532 | 0.407 | 0.540 | 0.532 | 0.019 | 0.384 | 0.623 |
| b1names/biomedbert/disjoint | oodold_names | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.447 | 0.471 | 0.356 | 0.548 | 0.336 | 0.561 | 0.548 | 0.213 | 0.000 | 0.700 |
| b1names/biomedbert/disjoint | oodold_names | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.478 | 0.492 | 0.417 | 0.532 | 0.408 | 0.546 | 0.532 | 0.015 | 0.404 | 0.619 |
| b1names/biomedbert/disjoint | oodold_names | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.447 | 0.478 | 0.355 | 0.543 | 0.336 | 0.563 | 0.543 | 0.192 | 0.000 | 0.700 |
| b1names/biomedbert | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.514 | 0.505 | 0.402 | 0.617 | 0.384 | 0.635 | 0.617 | 0.085 | 0.367 | 0.627 |
| b1names/biomedbert | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.530 | 0.530 | 0.364 | 0.693 | 0.341 | 0.724 | 0.693 | 0.225 | 0.000 | 0.700 |
| b1names/biomedbert | oodold_names | older_full | A | ok | complete | 1944 | 135 | 135 | 0.467 | 0.477 | 0.414 | 0.520 | 0.404 | 0.530 | 0.520 | 0.016 | 0.384 | 0.623 |
| b1names/biomedbert | oodold_names | older_full | B | ok | complete | 1254 | 135 | 95 | 0.419 | 0.426 | 0.332 | 0.510 | 0.314 | 0.530 | 0.510 | 0.371 | 0.000 | 0.700 |
| b1names/biomedbert | oodold_names | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.463 | 0.466 | 0.408 | 0.512 | 0.398 | 0.521 | 0.512 | 0.030 | 0.404 | 0.619 |
| b1names/biomedbert | oodold_names | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.419 | 0.421 | 0.336 | 0.510 | 0.320 | 0.531 | 0.510 | 0.354 | 0.000 | 0.700 |
| b2masked/biomedbert | ood_empty | novel | A | ok | complete | 438 | 48 | 48 | 0.472 | 0.461 | 0.376 | 0.571 | 0.357 | 0.593 | 0.571 | 0.116 | 0.367 | 0.627 |
| b2masked/biomedbert | ood_empty | novel | B | ok | complete | 316 | 48 | 40 | 0.486 | 0.450 | 0.345 | 0.615 | 0.322 | 0.646 | 0.615 | 0.162 | 0.000 | 0.700 |
| b2masked/biomedbert | oodold_empty | older_full | A | ok | complete | 1944 | 135 | 135 | 0.493 | 0.463 | 0.445 | 0.545 | 0.423 | 0.556 | 0.545 | 0.008 | 0.384 | 0.623 |
| b2masked/biomedbert | oodold_empty | older_full | B | ok | complete | 1254 | 135 | 95 | 0.497 | 0.510 | 0.418 | 0.589 | 0.396 | 0.609 | 0.589 | 0.039 | 0.000 | 0.700 |
| b2masked/biomedbert | oodold_empty | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.489 | 0.468 | 0.432 | 0.542 | 0.422 | 0.554 | 0.542 | 0.004 | 0.404 | 0.619 |
| b2masked/biomedbert | oodold_empty | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.497 | 0.498 | 0.410 | 0.588 | 0.390 | 0.605 | 0.588 | 0.041 | 0.000 | 0.700 |
| b2masked/biomedbert | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.474 | 0.449 | 0.377 | 0.576 | 0.361 | 0.599 | 0.576 | 0.110 | 0.367 | 0.627 |
| b2masked/biomedbert | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.500 | 0.465 | 0.360 | 0.636 | 0.337 | 0.667 | 0.636 | 0.118 | 0.000 | 0.700 |
| b2mixed/bertbase | ood_empty | novel | A | ok | complete | 438 | 48 | 48 | 0.514 | 0.527 | 0.402 | 0.610 | 0.386 | 0.644 | 0.610 | 0.069 | 0.367 | 0.627 |
| b2mixed/bertbase | ood_empty | novel | B | ok | complete | 316 | 48 | 40 | 0.533 | 0.592 | 0.391 | 0.671 | 0.360 | 0.701 | 0.671 | 0.188 | 0.000 | 0.700 |
| b2mixed/bertbase | oodold_empty | older_full | A | ok | complete | 1944 | 135 | 135 | 0.507 | 0.472 | 0.461 | 0.559 | 0.449 | 0.568 | 0.559 | 0.004 | 0.384 | 0.623 |
| b2mixed/bertbase | oodold_empty | older_full | B | ok | complete | 1254 | 135 | 95 | 0.512 | 0.450 | 0.423 | 0.594 | 0.408 | 0.614 | 0.594 | 0.041 | 0.000 | 0.700 |
| b2mixed/bertbase | oodold_empty | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.508 | 0.463 | 0.456 | 0.558 | 0.447 | 0.567 | 0.558 | 0.004 | 0.404 | 0.619 |
| b2mixed/bertbase | oodold_empty | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.512 | 0.457 | 0.427 | 0.597 | 0.404 | 0.615 | 0.597 | 0.050 | 0.000 | 0.700 |
| b2mixed/bertbase | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.491 | 0.502 | 0.392 | 0.596 | 0.373 | 0.618 | 0.596 | 0.065 | 0.367 | 0.627 |
| b2mixed/bertbase | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.505 | 0.563 | 0.362 | 0.643 | 0.333 | 0.678 | 0.643 | 0.120 | 0.000 | 0.700 |
| b2mixed/biobert | ood_empty | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.497 | 0.483 | 0.384 | 0.609 | 0.364 | 0.629 | 0.609 | 0.080 | 0.367 | 0.627 |
| b2mixed/biobert | ood_empty | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.489 | 0.531 | 0.313 | 0.649 | 0.292 | 0.682 | 0.649 | 0.213 | 0.000 | 0.700 |
| b2mixed/biobert | oodold_empty | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.493 | 0.501 | 0.448 | 0.539 | 0.440 | 0.553 | 0.539 | 0.003 | 0.384 | 0.623 |
| b2mixed/biobert | oodold_empty | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.479 | 0.517 | 0.397 | 0.563 | 0.381 | 0.579 | 0.563 | 0.061 | 0.000 | 0.700 |
| b2mixed/biobert | oodold_empty | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.500 | 0.506 | 0.448 | 0.545 | 0.438 | 0.555 | 0.545 | 0.002 | 0.404 | 0.619 |
| b2mixed/biobert | oodold_empty | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.479 | 0.513 | 0.397 | 0.560 | 0.382 | 0.573 | 0.560 | 0.063 | 0.000 | 0.700 |
| b2mixed/biobert | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.499 | 0.480 | 0.389 | 0.608 | 0.367 | 0.625 | 0.608 | 0.072 | 0.367 | 0.627 |
| b2mixed/biobert | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.492 | 0.529 | 0.329 | 0.649 | 0.294 | 0.680 | 0.649 | 0.184 | 0.000 | 0.700 |
| b2mixed/biomedbert/disjoint | ood_empty | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.536 | 0.518 | 0.420 | 0.647 | 0.403 | 0.668 | 0.647 | 0.180 | 0.367 | 0.627 |
| b2mixed/biomedbert/disjoint | ood_empty | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.546 | 0.544 | 0.395 | 0.683 | 0.376 | 0.711 | 0.683 | 0.267 | 0.000 | 0.700 |
| b2mixed/biomedbert/disjoint | oodold_empty | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.479 | 0.470 | 0.428 | 0.529 | 0.418 | 0.541 | 0.529 | 0.007 | 0.384 | 0.623 |
| b2mixed/biomedbert/disjoint | oodold_empty | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.428 | 0.412 | 0.339 | 0.514 | 0.320 | 0.535 | 0.514 | 0.314 | 0.000 | 0.700 |
| b2mixed/biomedbert/disjoint | oodold_empty | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.471 | 0.458 | 0.418 | 0.523 | 0.408 | 0.535 | 0.523 | 0.013 | 0.404 | 0.619 |
| b2mixed/biomedbert/disjoint | oodold_empty | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.428 | 0.407 | 0.345 | 0.511 | 0.326 | 0.534 | 0.511 | 0.270 | 0.000 | 0.700 |
| b2mixed/biomedbert/disjoint | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.522 | 0.507 | 0.400 | 0.635 | 0.377 | 0.667 | 0.635 | 0.149 | 0.367 | 0.627 |
| b2mixed/biomedbert/disjoint | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.530 | 0.537 | 0.364 | 0.692 | 0.331 | 0.729 | 0.692 | 0.255 | 0.000 | 0.700 |
| b2mixed/biomedbert | ood_empty | novel | A | ok | complete | 438 | 48 | 48 | 0.523 | 0.529 | 0.411 | 0.626 | 0.397 | 0.650 | 0.626 | 0.117 | 0.367 | 0.627 |
| b2mixed/biomedbert | ood_empty | novel | B | ok | complete | 316 | 48 | 40 | 0.533 | 0.551 | 0.383 | 0.682 | 0.357 | 0.714 | 0.682 | 0.239 | 0.000 | 0.700 |
| b2mixed/biomedbert | oodold_empty | older_full | A | ok | complete | 1944 | 135 | 135 | 0.455 | 0.452 | 0.404 | 0.508 | 0.396 | 0.517 | 0.508 | 0.039 | 0.384 | 0.623 |
| b2mixed/biomedbert | oodold_empty | older_full | B | ok | complete | 1254 | 135 | 95 | 0.397 | 0.399 | 0.310 | 0.491 | 0.293 | 0.512 | 0.491 | 0.529 | 0.000 | 0.700 |
| b2mixed/biomedbert | oodold_empty | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.452 | 0.444 | 0.395 | 0.509 | 0.389 | 0.518 | 0.509 | 0.061 | 0.404 | 0.619 |
| b2mixed/biomedbert | oodold_empty | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.397 | 0.391 | 0.308 | 0.493 | 0.289 | 0.514 | 0.493 | 0.519 | 0.000 | 0.700 |
| b2mixed/biomedbert | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.490 | 0.503 | 0.376 | 0.595 | 0.356 | 0.620 | 0.595 | 0.106 | 0.367 | 0.627 |
| b2mixed/biomedbert | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.481 | 0.519 | 0.320 | 0.642 | 0.298 | 0.669 | 0.642 | 0.206 | 0.000 | 0.700 |
| b2sentence/bertbase | ood_empty | novel | A | ok | complete | 438 | 48 | 48 | 0.526 | 0.449 | 0.414 | 0.632 | 0.390 | 0.656 | 0.632 | 0.151 | 0.367 | 0.627 |
| b2sentence/bertbase | ood_empty | novel | B | ok | complete | 316 | 48 | 40 | 0.489 | 0.454 | 0.336 | 0.643 | 0.304 | 0.665 | 0.643 | 0.173 | 0.000 | 0.700 |
| b2sentence/bertbase | oodold_empty | older_full | A | ok | complete | 1944 | 135 | 135 | 0.478 | 0.480 | 0.430 | 0.528 | 0.420 | 0.535 | 0.528 | 0.005 | 0.384 | 0.623 |
| b2sentence/bertbase | oodold_empty | older_full | B | ok | complete | 1254 | 135 | 95 | 0.453 | 0.510 | 0.380 | 0.534 | 0.368 | 0.547 | 0.534 | 0.115 | 0.000 | 0.700 |
| b2sentence/bertbase | oodold_empty | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.477 | 0.481 | 0.432 | 0.530 | 0.423 | 0.538 | 0.530 | 0.005 | 0.404 | 0.619 |
| b2sentence/bertbase | oodold_empty | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.453 | 0.495 | 0.377 | 0.535 | 0.363 | 0.553 | 0.535 | 0.127 | 0.000 | 0.700 |
| b2sentence/bertbase | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.486 | 0.442 | 0.389 | 0.582 | 0.375 | 0.599 | 0.582 | 0.076 | 0.367 | 0.627 |
| b2sentence/bertbase | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.462 | 0.457 | 0.322 | 0.595 | 0.299 | 0.618 | 0.595 | 0.211 | 0.000 | 0.700 |
| b2sentence/biobert | ood_empty | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.489 | 0.485 | 0.374 | 0.601 | 0.355 | 0.624 | 0.601 | 0.097 | 0.367 | 0.627 |
| b2sentence/biobert | ood_empty | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.497 | 0.523 | 0.327 | 0.653 | 0.302 | 0.679 | 0.653 | 0.189 | 0.000 | 0.700 |
| b2sentence/biobert | oodold_empty | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.484 | 0.494 | 0.433 | 0.536 | 0.421 | 0.545 | 0.536 | 0.009 | 0.384 | 0.623 |
| b2sentence/biobert | oodold_empty | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.468 | 0.492 | 0.378 | 0.563 | 0.364 | 0.579 | 0.563 | 0.115 | 0.000 | 0.700 |
| b2sentence/biobert | oodold_empty | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.482 | 0.497 | 0.431 | 0.534 | 0.420 | 0.542 | 0.534 | 0.010 | 0.404 | 0.619 |
| b2sentence/biobert | oodold_empty | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.468 | 0.487 | 0.375 | 0.562 | 0.352 | 0.581 | 0.562 | 0.117 | 0.000 | 0.700 |
| b2sentence/biobert | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.532 | 0.496 | 0.417 | 0.645 | 0.392 | 0.661 | 0.645 | 0.178 | 0.367 | 0.627 |
| b2sentence/biobert | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.530 | 0.537 | 0.361 | 0.689 | 0.338 | 0.724 | 0.689 | 0.238 | 0.000 | 0.700 |
| b2sentence/biomedbert/disjoint | ood_empty | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.543 | 0.527 | 0.444 | 0.653 | 0.425 | 0.665 | 0.653 | 0.212 | 0.367 | 0.627 |
| b2sentence/biomedbert/disjoint | ood_empty | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.549 | 0.502 | 0.418 | 0.700 | 0.387 | 0.732 | 0.700 | 0.280 | 0.000 | 0.700 |
| b2sentence/biomedbert/disjoint | oodold_empty | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.465 | 0.471 | 0.415 | 0.516 | 0.400 | 0.526 | 0.516 | 0.028 | 0.384 | 0.623 |
| b2sentence/biomedbert/disjoint | oodold_empty | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.420 | 0.483 | 0.333 | 0.504 | 0.314 | 0.524 | 0.504 | 0.353 | 0.000 | 0.700 |
| b2sentence/biomedbert/disjoint | oodold_empty | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.464 | 0.470 | 0.411 | 0.517 | 0.398 | 0.528 | 0.517 | 0.028 | 0.404 | 0.619 |
| b2sentence/biomedbert/disjoint | oodold_empty | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.420 | 0.467 | 0.336 | 0.513 | 0.320 | 0.529 | 0.513 | 0.367 | 0.000 | 0.700 |
| b2sentence/biomedbert/disjoint | ood_names | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.506 | 0.466 | 0.398 | 0.608 | 0.373 | 0.626 | 0.608 | 0.076 | 0.367 | 0.627 |
| b2sentence/biomedbert/disjoint | ood_names | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.492 | 0.426 | 0.330 | 0.637 | 0.302 | 0.657 | 0.637 | 0.159 | 0.000 | 0.700 |
| b2sentence/biomedbert | ood_empty | novel | A | ok | complete | 438 | 48 | 48 | 0.490 | 0.472 | 0.389 | 0.595 | 0.370 | 0.612 | 0.595 | 0.067 | 0.367 | 0.627 |
| b2sentence/biomedbert | ood_empty | novel | B | ok | complete | 316 | 48 | 40 | 0.475 | 0.439 | 0.337 | 0.615 | 0.308 | 0.644 | 0.615 | 0.178 | 0.000 | 0.700 |
| b2sentence/biomedbert | oodold_empty | older_full | A | ok | complete | 1944 | 135 | 135 | 0.462 | 0.446 | 0.412 | 0.514 | 0.399 | 0.528 | 0.514 | 0.027 | 0.384 | 0.623 |
| b2sentence/biomedbert | oodold_empty | older_full | B | ok | complete | 1254 | 135 | 95 | 0.393 | 0.422 | 0.306 | 0.482 | 0.291 | 0.497 | 0.482 | 0.556 | 0.000 | 0.700 |
| b2sentence/biomedbert | oodold_empty | older_clean | A | ok | complete | 1832 | 128 | 128 | 0.453 | 0.437 | 0.398 | 0.508 | 0.391 | 0.518 | 0.508 | 0.063 | 0.404 | 0.619 |
| b2sentence/biomedbert | oodold_empty | older_clean | B | ok | complete | 1191 | 128 | 95 | 0.393 | 0.406 | 0.310 | 0.485 | 0.296 | 0.501 | 0.485 | 0.545 | 0.000 | 0.700 |
| b2sentence/biomedbert | ood_names | novel | A | ok | complete | 438 | 48 | 48 | 0.491 | 0.459 | 0.373 | 0.604 | 0.350 | 0.630 | 0.604 | 0.098 | 0.367 | 0.627 |
| b2sentence/biomedbert | ood_names | novel | B | ok | complete | 316 | 48 | 40 | 0.440 | 0.437 | 0.297 | 0.588 | 0.271 | 0.620 | 0.588 | 0.327 | 0.000 | 0.700 |
| krag/biomedbert/bm25-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.440 | 0.459 | 0.316 | 0.565 | 0.296 | 0.597 | 0.565 | 0.310 | 0.367 | 0.627 |
| krag/biomedbert/bm25-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.448 | 0.475 | 0.311 | 0.602 | 0.276 | 0.635 | 0.602 | 0.301 | 0.000 | 0.700 |
| krag/biomedbert/contaminated-k5-c400 | ood | novel | A | ok | complete | 438 | 48 | 48 | 0.580 | 0.621 | 0.466 | 0.692 | 0.425 | 0.716 | 0.692 | 0.382 | 0.367 | 0.627 |
| krag/biomedbert/contaminated-k5-c400 | ood | novel | B | ok | complete | 316 | 48 | 40 | 0.626 | 0.711 | 0.469 | 0.762 | 0.441 | 0.792 | 0.762 | 0.639 | 0.000 | 0.700 |
| krag/biomedbert/dense-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.490 | 0.523 | 0.382 | 0.597 | 0.353 | 0.615 | 0.597 | 0.084 | 0.367 | 0.627 |
| krag/biomedbert/dense-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.544 | 0.561 | 0.395 | 0.685 | 0.366 | 0.711 | 0.685 | 0.248 | 0.000 | 0.700 |
| krag/biomedbert/excl_clinical_pharmacology-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.489 | 0.525 | 0.383 | 0.593 | 0.360 | 0.617 | 0.593 | 0.087 | 0.367 | 0.627 |
| krag/biomedbert/excl_clinical_pharmacology-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.464 | 0.562 | 0.313 | 0.606 | 0.289 | 0.636 | 0.606 | 0.237 | 0.000 | 0.700 |
| krag/biomedbert/excl_mechanism_of_action-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.522 | 0.522 | 0.404 | 0.632 | 0.388 | 0.653 | 0.632 | 0.117 | 0.367 | 0.627 |
| krag/biomedbert/excl_mechanism_of_action-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.530 | 0.532 | 0.363 | 0.696 | 0.323 | 0.725 | 0.696 | 0.236 | 0.000 | 0.700 |
| krag/biomedbert/excl_pharmacokinetics-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.505 | 0.503 | 0.395 | 0.620 | 0.369 | 0.638 | 0.620 | 0.087 | 0.367 | 0.627 |
| krag/biomedbert/excl_pharmacokinetics-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.527 | 0.539 | 0.368 | 0.684 | 0.334 | 0.718 | 0.684 | 0.234 | 0.000 | 0.700 |
| krag/biomedbert/excl_warnings_and_cautions-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.490 | 0.496 | 0.379 | 0.599 | 0.360 | 0.621 | 0.599 | 0.084 | 0.367 | 0.627 |
| krag/biomedbert/excl_warnings_and_cautions-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.538 | 0.544 | 0.382 | 0.701 | 0.347 | 0.736 | 0.701 | 0.254 | 0.000 | 0.700 |
| krag/biomedbert/hybrid-k1-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.478 | 0.460 | 0.368 | 0.586 | 0.355 | 0.603 | 0.586 | 0.120 | 0.367 | 0.627 |
| krag/biomedbert/hybrid-k1-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.497 | 0.491 | 0.341 | 0.643 | 0.313 | 0.680 | 0.643 | 0.159 | 0.000 | 0.700 |
| krag/biomedbert/hybrid-k3-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.498 | 0.477 | 0.387 | 0.610 | 0.365 | 0.633 | 0.610 | 0.071 | 0.367 | 0.627 |
| krag/biomedbert/hybrid-k3-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.538 | 0.514 | 0.388 | 0.686 | 0.360 | 0.712 | 0.686 | 0.242 | 0.000 | 0.700 |
| krag/biomedbert/hybrid-k5-c100 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.534 | 0.505 | 0.429 | 0.641 | 0.411 | 0.662 | 0.641 | 0.153 | 0.367 | 0.627 |
| krag/biomedbert/hybrid-k5-c100 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.585 | 0.535 | 0.444 | 0.724 | 0.408 | 0.764 | 0.724 | 0.415 | 0.000 | 0.700 |
| krag/biomedbert/hybrid-k5-c400 | ood | novel | A | ok | complete | 438 | 48 | 48 | 0.519 | 0.496 | 0.421 | 0.627 | 0.393 | 0.647 | 0.627 | 0.102 | 0.367 | 0.627 |
| krag/biomedbert/hybrid-k5-c400 | ood | novel | B | ok | complete | 316 | 48 | 40 | 0.552 | 0.555 | 0.397 | 0.692 | 0.367 | 0.725 | 0.692 | 0.304 | 0.000 | 0.700 |
| krag/biomedbert/masked-k5-c400 | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.507 | 0.522 | 0.392 | 0.618 | 0.371 | 0.636 | 0.618 | 0.083 | 0.367 | 0.627 |
| krag/biomedbert/masked-k5-c400 | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.533 | 0.557 | 0.380 | 0.672 | 0.356 | 0.699 | 0.672 | 0.215 | 0.000 | 0.700 |
| names/biomistral | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.518 | 0.470 | 0.409 | 0.633 | 0.387 | 0.654 | 0.633 | 0.114 | 0.367 | 0.627 |
| names/biomistral | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.508 | 0.481 | 0.346 | 0.679 | 0.320 | 0.705 | 0.679 | 0.182 | 0.000 | 0.700 |
| names/biomistral | oodold | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.514 | 0.522 | 0.464 | 0.562 | 0.455 | 0.571 | 0.562 | 0.004 | 0.384 | 0.623 |
| names/biomistral | oodold | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.505 | 0.532 | 0.413 | 0.593 | 0.399 | 0.609 | 0.593 | 0.041 | 0.000 | 0.700 |
| names/biomistral | oodold | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.517 | 0.531 | 0.465 | 0.570 | 0.455 | 0.578 | 0.570 | 0.007 | 0.404 | 0.619 |
| names/biomistral | oodold | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.505 | 0.523 | 0.415 | 0.603 | 0.400 | 0.617 | 0.603 | 0.056 | 0.000 | 0.700 |
| rag/biomistral | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.449 | 0.435 | 0.338 | 0.558 | 0.314 | 0.582 | 0.558 | 0.274 | 0.367 | 0.627 |
| rag/biomistral | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.492 | 0.463 | 0.338 | 0.641 | 0.314 | 0.666 | 0.641 | 0.159 | 0.000 | 0.700 |
| names/qwen | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.579 | 0.600 | 0.470 | 0.691 | 0.440 | 0.713 | 0.691 | 0.383 | 0.367 | 0.627 |
| names/qwen | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.577 | 0.628 | 0.427 | 0.717 | 0.397 | 0.736 | 0.717 | 0.395 | 0.000 | 0.700 |
| names/qwen | oodold | older_full | A | ok | pending (1 of 5 seeds) | 1944 | 135 | 135 | 0.608 | 0.658 | 0.554 | 0.665 | 0.545 | 0.675 | 0.665 | 0.612 | 0.384 | 0.623 |
| names/qwen | oodold | older_full | B | ok | pending (1 of 5 seeds) | 1254 | 135 | 95 | 0.660 | 0.728 | 0.584 | 0.750 | 0.563 | 0.766 | 0.750 | 0.889 | 0.000 | 0.700 |
| names/qwen | oodold | older_clean | A | ok | pending (1 of 5 seeds) | 1832 | 128 | 128 | 0.602 | 0.653 | 0.543 | 0.658 | 0.533 | 0.667 | 0.658 | 0.536 | 0.404 | 0.619 |
| names/qwen | oodold | older_clean | B | ok | pending (1 of 5 seeds) | 1191 | 128 | 95 | 0.660 | 0.734 | 0.560 | 0.751 | 0.543 | 0.767 | 0.751 | 0.860 | 0.000 | 0.700 |
| rag/qwen | ood | novel | A | ok | pending (1 of 5 seeds) | 438 | 48 | 48 | 0.513 | 0.484 | 0.387 | 0.631 | 0.366 | 0.651 | 0.631 | 0.110 | 0.367 | 0.627 |
| rag/qwen | ood | novel | B | ok | pending (1 of 5 seeds) | 316 | 48 | 40 | 0.478 | 0.495 | 0.278 | 0.666 | 0.250 | 0.711 | 0.666 | 0.252 | 0.000 | 0.700 |

## CPU baselines (partner_frequency_prior is the reference a model must beat)

| set | baseline | n | prevalence | auroc | auprc | f1 | mcc | balanced_accuracy | tp | fp | fn | tn | auroc_lo | auroc_hi | auroc2_lo | auroc2_hi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Novel OOD | all_positive | 438 | 0.338 | 0.500 | 0.338 | 0.505 | 0.000 | 0.500 | 148 | 290 | 0 | 0 | 0.500 | 0.500 | NA | NA |
| Novel OOD | partner_frequency_prior | 438 | 0.338 | 0.508 | 0.345 | 0.367 | 0.012 | 0.506 | 58 | 110 | 90 | 180 | 0.403 | 0.613 | NA | NA |
| Novel OOD | novel_drug_prior | 438 | 0.338 | 0.643 | 0.473 | 0.488 | 0.188 | 0.598 | 80 | 100 | 68 | 190 | 0.533 | 0.747 | NA | NA |
| Novel OOD | non_di_label_string_match | 438 | 0.338 | 0.797 | 0.732 | 0.746 | 0.702 | 0.797 | 88 | 0 | 60 | 290 | 0.709 | 0.877 | NA | NA |
| Novel OOD | cyp3a_keyword_rule | 438 | 0.338 | 0.539 | 0.361 | 0.286 | 0.102 | 0.539 | 31 | 38 | 117 | 252 | 0.478 | 0.617 | NA | NA |
| Novel OOD | drugbank_lookup_reference | 438 | 0.338 | 0.767 | 0.534 | 0.687 | 0.506 | 0.767 | 133 | 106 | 15 | 184 | 0.691 | 0.839 | NA | NA |
| Older OOD | all_positive | 1944 | 0.333 | 0.500 | 0.333 | 0.500 | 0.000 | 0.500 | 648 | 1296 | 0 | 0 | 0.500 | 0.500 | NA | NA |
| Older OOD | partner_frequency_prior | 1944 | 0.333 | 0.500 | 0.333 | 0.349 | 0.000 | 0.500 | 237 | 474 | 411 | 822 | 0.453 | 0.546 | NA | NA |
| Older OOD | novel_drug_prior | 1944 | 0.333 | 0.621 | 0.446 | 0.476 | 0.171 | 0.590 | 346 | 460 | 302 | 836 | 0.560 | 0.678 | NA | NA |
| Older OOD | non_di_label_string_match | 1944 | 0.333 | 0.837 | 0.783 | 0.806 | 0.762 | 0.837 | 437 | 0 | 211 | 1296 | 0.790 | 0.880 | NA | NA |
| Older OOD | cyp3a_keyword_rule | 1944 | 0.333 | 0.568 | 0.386 | 0.315 | 0.194 | 0.568 | 141 | 105 | 507 | 1191 | 0.518 | 0.624 | NA | NA |

## Name swap

| job | swap | n | flip_rate | mean_abs_dp |
| --- | --- | --- | --- | --- |
| b1names-bertbase-s42 | vocab | 2810 | 0.373 | 0.334 |
| b1names-bertbase-s42 | novel | 2810 | 0.243 | 0.255 |
| b1names-bertbase-s42 | pseudo | 2810 | 0.249 | 0.256 |
| b1names-biobert-s42 | vocab | 2810 | 0.303 | 0.303 |
| b1names-biobert-s42 | novel | 2810 | 0.274 | 0.296 |
| b1names-biobert-s42 | pseudo | 2810 | 0.200 | 0.240 |
| b1names-biomedbert-disjoint-s42 | vocab | 2810 | 0.358 | 0.172 |
| b1names-biomedbert-disjoint-s42 | novel | 2810 | 0.390 | 0.186 |
| b1names-biomedbert-disjoint-s42 | pseudo | 2810 | 0.304 | 0.152 |
| b1names-biomedbert-s1 | vocab | 2810 | 0.438 | 0.306 |
| b1names-biomedbert-s1 | novel | 2810 | 0.421 | 0.291 |
| b1names-biomedbert-s1 | pseudo | 2810 | 0.354 | 0.276 |
| b1names-biomedbert-s2 | vocab | 2810 | 0.251 | 0.272 |
| b1names-biomedbert-s2 | novel | 2810 | 0.238 | 0.282 |
| b1names-biomedbert-s2 | pseudo | 2810 | 0.138 | 0.203 |
| b1names-biomedbert-s3 | vocab | 2810 | 0.383 | 0.311 |
| b1names-biomedbert-s3 | novel | 2810 | 0.407 | 0.330 |
| b1names-biomedbert-s3 | pseudo | 2810 | 0.305 | 0.278 |
| b1names-biomedbert-s4 | vocab | 2810 | 0.335 | 0.323 |
| b1names-biomedbert-s4 | novel | 2810 | 0.264 | 0.277 |
| b1names-biomedbert-s4 | pseudo | 2810 | 0.180 | 0.221 |
| b1names-biomedbert-s42 | vocab | 2810 | 0.332 | 0.314 |
| b1names-biomedbert-s42 | novel | 2810 | 0.450 | 0.402 |
| b1names-biomedbert-s42 | pseudo | 2810 | 0.294 | 0.324 |
| b2masked-biomedbert-s1 | vocab | 2810 | 0.028 | 0.026 |
| b2masked-biomedbert-s1 | novel | 2810 | 0.024 | 0.027 |
| b2masked-biomedbert-s1 | pseudo | 2810 | 0.031 | 0.031 |
| b2masked-biomedbert-s2 | vocab | 2810 | 0.047 | 0.050 |
| b2masked-biomedbert-s2 | novel | 2810 | 0.043 | 0.045 |
| b2masked-biomedbert-s2 | pseudo | 2810 | 0.049 | 0.044 |
| b2masked-biomedbert-s3 | vocab | 2810 | 0.063 | 0.063 |
| b2masked-biomedbert-s3 | novel | 2810 | 0.076 | 0.071 |
| b2masked-biomedbert-s3 | pseudo | 2810 | 0.073 | 0.067 |
| b2masked-biomedbert-s4 | vocab | 2810 | 0.090 | 0.089 |
| b2masked-biomedbert-s4 | novel | 2810 | 0.108 | 0.101 |
| b2masked-biomedbert-s4 | pseudo | 2810 | 0.103 | 0.100 |
| b2masked-biomedbert-s42 | vocab | 2810 | 0.092 | 0.091 |
| b2masked-biomedbert-s42 | novel | 2810 | 0.110 | 0.109 |
| b2masked-biomedbert-s42 | pseudo | 2810 | 0.106 | 0.104 |
| b2mixed-bertbase-s1 | vocab | 2810 | 0.091 | 0.089 |
| b2mixed-bertbase-s1 | novel | 2810 | 0.076 | 0.076 |
| b2mixed-bertbase-s1 | pseudo | 2810 | 0.082 | 0.081 |
| b2mixed-bertbase-s2 | vocab | 2810 | 0.095 | 0.096 |
| b2mixed-bertbase-s2 | novel | 2810 | 0.096 | 0.088 |
| b2mixed-bertbase-s2 | pseudo | 2810 | 0.091 | 0.089 |
| b2mixed-bertbase-s3 | vocab | 2810 | 0.052 | 0.057 |
| b2mixed-bertbase-s3 | novel | 2810 | 0.047 | 0.050 |
| b2mixed-bertbase-s3 | pseudo | 2810 | 0.047 | 0.052 |
| b2mixed-bertbase-s4 | vocab | 2810 | 0.113 | 0.109 |
| b2mixed-bertbase-s4 | novel | 2810 | 0.089 | 0.094 |
| b2mixed-bertbase-s4 | pseudo | 2810 | 0.094 | 0.095 |
| b2mixed-bertbase-s42 | vocab | 2810 | 0.084 | 0.088 |
| b2mixed-bertbase-s42 | novel | 2810 | 0.078 | 0.078 |
| b2mixed-bertbase-s42 | pseudo | 2810 | 0.085 | 0.085 |
| b2mixed-biobert-s42 | vocab | 2810 | 0.081 | 0.084 |
| b2mixed-biobert-s42 | novel | 2810 | 0.065 | 0.069 |
| b2mixed-biobert-s42 | pseudo | 2810 | 0.068 | 0.070 |
| b2mixed-biomedbert-disjoint-s42 | vocab | 2810 | 0.082 | 0.078 |
| b2mixed-biomedbert-disjoint-s42 | novel | 2810 | 0.080 | 0.082 |
| b2mixed-biomedbert-disjoint-s42 | pseudo | 2810 | 0.090 | 0.088 |
| b2mixed-biomedbert-s1 | vocab | 2810 | 0.075 | 0.077 |
| b2mixed-biomedbert-s1 | novel | 2810 | 0.069 | 0.075 |
| b2mixed-biomedbert-s1 | pseudo | 2810 | 0.078 | 0.082 |
| b2mixed-biomedbert-s2 | vocab | 2810 | 0.068 | 0.067 |
| b2mixed-biomedbert-s2 | novel | 2810 | 0.059 | 0.063 |
| b2mixed-biomedbert-s2 | pseudo | 2810 | 0.056 | 0.059 |
| b2mixed-biomedbert-s3 | vocab | 2810 | 0.062 | 0.063 |
| b2mixed-biomedbert-s3 | novel | 2810 | 0.049 | 0.054 |
| b2mixed-biomedbert-s3 | pseudo | 2810 | 0.074 | 0.072 |
| b2mixed-biomedbert-s4 | vocab | 2810 | 0.068 | 0.066 |
| b2mixed-biomedbert-s4 | novel | 2810 | 0.062 | 0.064 |
| b2mixed-biomedbert-s4 | pseudo | 2810 | 0.075 | 0.075 |
| b2mixed-biomedbert-s42 | vocab | 2810 | 0.064 | 0.065 |
| b2mixed-biomedbert-s42 | novel | 2810 | 0.067 | 0.067 |
| b2mixed-biomedbert-s42 | pseudo | 2810 | 0.073 | 0.073 |
| b2sentence-bertbase-s1 | vocab | 2810 | 0.062 | 0.067 |
| b2sentence-bertbase-s1 | novel | 2810 | 0.057 | 0.062 |
| b2sentence-bertbase-s1 | pseudo | 2810 | 0.058 | 0.061 |
| b2sentence-bertbase-s2 | vocab | 2810 | 0.086 | 0.085 |
| b2sentence-bertbase-s2 | novel | 2810 | 0.079 | 0.077 |
| b2sentence-bertbase-s2 | pseudo | 2810 | 0.076 | 0.076 |
| b2sentence-bertbase-s3 | vocab | 2810 | 0.057 | 0.057 |
| b2sentence-bertbase-s3 | novel | 2810 | 0.054 | 0.053 |
| b2sentence-bertbase-s3 | pseudo | 2810 | 0.059 | 0.059 |
| b2sentence-bertbase-s4 | vocab | 2810 | 0.078 | 0.082 |
| b2sentence-bertbase-s4 | novel | 2810 | 0.075 | 0.079 |
| b2sentence-bertbase-s4 | pseudo | 2810 | 0.075 | 0.073 |
| b2sentence-bertbase-s42 | vocab | 2810 | 0.062 | 0.065 |
| b2sentence-bertbase-s42 | novel | 2810 | 0.060 | 0.060 |
| b2sentence-bertbase-s42 | pseudo | 2810 | 0.057 | 0.059 |
| b2sentence-biobert-s42 | vocab | 2810 | 0.066 | 0.071 |
| b2sentence-biobert-s42 | novel | 2810 | 0.055 | 0.062 |
| b2sentence-biobert-s42 | pseudo | 2810 | 0.049 | 0.055 |
| b2sentence-biomedbert-disjoint-s42 | vocab | 2810 | 0.067 | 0.065 |
| b2sentence-biomedbert-disjoint-s42 | novel | 2810 | 0.061 | 0.061 |
| b2sentence-biomedbert-disjoint-s42 | pseudo | 2810 | 0.063 | 0.061 |
| b2sentence-biomedbert-s1 | vocab | 2810 | 0.050 | 0.052 |
| b2sentence-biomedbert-s1 | novel | 2810 | 0.048 | 0.049 |
| b2sentence-biomedbert-s1 | pseudo | 2810 | 0.051 | 0.049 |
| b2sentence-biomedbert-s2 | vocab | 2810 | 0.049 | 0.048 |
| b2sentence-biomedbert-s2 | novel | 2810 | 0.042 | 0.044 |
| b2sentence-biomedbert-s2 | pseudo | 2810 | 0.047 | 0.048 |
| b2sentence-biomedbert-s3 | vocab | 2810 | 0.050 | 0.051 |
| b2sentence-biomedbert-s3 | novel | 2810 | 0.040 | 0.043 |
| b2sentence-biomedbert-s3 | pseudo | 2810 | 0.043 | 0.048 |
| b2sentence-biomedbert-s4 | vocab | 2810 | 0.054 | 0.048 |
| b2sentence-biomedbert-s4 | novel | 2810 | 0.042 | 0.042 |
| b2sentence-biomedbert-s4 | pseudo | 2810 | 0.062 | 0.059 |
| b2sentence-biomedbert-s42 | vocab | 2810 | 0.080 | 0.083 |
| b2sentence-biomedbert-s42 | novel | 2810 | 0.095 | 0.094 |
| b2sentence-biomedbert-s42 | pseudo | 2810 | 0.094 | 0.093 |

## Masking ratio

| job | f1_masked | f1_sentence | ratio |
| --- | --- | --- | --- |
| b2masked-biomedbert-s1 | 0.709 | 0.030 | 23.939 |
| b2masked-biomedbert-s2 | 0.665 | 0.399 | 1.668 |
| b2masked-biomedbert-s3 | 0.715 | 0.524 | 1.364 |
| b2masked-biomedbert-s4 | 0.707 | 0.475 | 1.489 |
| b2masked-biomedbert-s42 | 0.719 | 0.455 | 1.581 |
| b2mixed-bertbase-s1 | 0.000 | 0.615 | 0.000 |
| b2mixed-bertbase-s2 | 0.000 | 0.637 | 0.000 |
| b2mixed-bertbase-s3 | 0.000 | 0.621 | 0.000 |
| b2mixed-bertbase-s4 | 0.000 | 0.639 | 0.000 |
| b2mixed-bertbase-s42 | 0.000 | 0.608 | 0.000 |
| b2mixed-biobert-s42 | 0.000 | 0.662 | 0.000 |
| b2mixed-biomedbert-disjoint-s42 | 0.073 | 0.692 | 0.105 |
| b2mixed-biomedbert-s1 | 0.000 | 0.713 | 0.000 |
| b2mixed-biomedbert-s2 | 0.073 | 0.711 | 0.102 |
| b2mixed-biomedbert-s3 | 0.000 | 0.674 | 0.000 |
| b2mixed-biomedbert-s4 | 0.032 | 0.694 | 0.046 |
| b2mixed-biomedbert-s42 | 0.093 | 0.704 | 0.131 |
| b2sentence-bertbase-s1 | 0.000 | 0.672 | 0.000 |
| b2sentence-bertbase-s2 | 0.047 | 0.675 | 0.070 |
| b2sentence-bertbase-s3 | 0.027 | 0.672 | 0.040 |
| b2sentence-bertbase-s4 | 0.000 | 0.683 | 0.000 |
| b2sentence-bertbase-s42 | 0.000 | 0.627 | 0.000 |
| b2sentence-biobert-s42 | 0.000 | 0.675 | 0.000 |
| b2sentence-biomedbert-disjoint-s42 | 0.052 | 0.704 | 0.075 |
| b2sentence-biomedbert-s1 | 0.016 | 0.717 | 0.022 |
| b2sentence-biomedbert-s2 | 0.000 | 0.742 | 0.000 |
| b2sentence-biomedbert-s3 | 0.063 | 0.722 | 0.087 |
| b2sentence-biomedbert-s4 | 0.000 | 0.718 | 0.000 |
| b2sentence-biomedbert-s42 | 0.021 | 0.706 | 0.030 |

## Drug disjoint

| job | key | subset | n | prevalence | auroc | auprc | f1 | mcc | balanced_accuracy | tp | fp | fn | tn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b1names-biomedbert-disjoint-s42 | test_names | unseen | 1271 | 0.152 | 0.609 | 0.212 | 0.258 | 0.091 | 0.554 | 65 | 246 | 128 | 832 |
| b1names-biomedbert-disjoint-s42 | test_names | seen | 1539 | 0.116 | 0.610 | 0.168 | 0.214 | 0.087 | 0.552 | 49 | 232 | 129 | 1129 |
| b1names-biomedbert-disjoint-s42 | swap_vocab_names | unseen | 1271 | 0.152 | 0.516 | 0.161 | 0.216 | 0.028 | 0.518 | 58 | 286 | 135 | 792 |
| b1names-biomedbert-disjoint-s42 | swap_vocab_names | seen | 1539 | 0.116 | 0.459 | 0.105 | 0.153 | -0.003 | 0.498 | 41 | 318 | 137 | 1043 |
| b1names-biomedbert-disjoint-s42 | swap_novel_names | unseen | 1271 | 0.152 | 0.492 | 0.153 | 0.193 | -0.012 | 0.492 | 56 | 330 | 137 | 748 |
| b1names-biomedbert-disjoint-s42 | swap_novel_names | seen | 1539 | 0.116 | 0.497 | 0.125 | 0.170 | 0.005 | 0.504 | 54 | 403 | 124 | 958 |
| b1names-biomedbert-disjoint-s42 | swap_pseudo_names | unseen | 1271 | 0.152 | 0.513 | 0.165 | 0.192 | 0.034 | 0.518 | 40 | 184 | 153 | 894 |
| b1names-biomedbert-disjoint-s42 | swap_pseudo_names | seen | 1539 | 0.116 | 0.546 | 0.128 | 0.152 | 0.015 | 0.509 | 34 | 235 | 144 | 1126 |
| b2mixed-biomedbert-disjoint-s42 | test_sentence | unseen | 1271 | 0.152 | 0.940 | 0.697 | 0.652 | 0.599 | 0.860 | 166 | 150 | 27 | 928 |
| b2mixed-biomedbert-disjoint-s42 | test_sentence | seen | 1539 | 0.116 | 0.967 | 0.811 | 0.744 | 0.712 | 0.887 | 147 | 70 | 31 | 1291 |
| b2mixed-biomedbert-disjoint-s42 | test_masked | unseen | 1271 | 0.152 | 0.830 | 0.454 | 0.060 | 0.163 | 0.516 | 6 | 0 | 187 | 1078 |
| b2mixed-biomedbert-disjoint-s42 | test_masked | seen | 1539 | 0.116 | 0.875 | 0.482 | 0.086 | 0.200 | 0.522 | 8 | 0 | 170 | 1361 |
| b2mixed-biomedbert-disjoint-s42 | test_empty | unseen | 1271 | 0.152 | 0.612 | 0.198 | 0.158 | 0.046 | 0.519 | 25 | 99 | 168 | 979 |
| b2mixed-biomedbert-disjoint-s42 | test_empty | seen | 1539 | 0.116 | 0.667 | 0.212 | 0.217 | 0.142 | 0.559 | 32 | 85 | 146 | 1276 |
| b2mixed-biomedbert-disjoint-s42 | test_names | unseen | 1271 | 0.152 | 0.606 | 0.196 | 0.106 | 0.013 | 0.505 | 15 | 74 | 178 | 1004 |
| b2mixed-biomedbert-disjoint-s42 | test_names | seen | 1539 | 0.116 | 0.637 | 0.212 | 0.213 | 0.162 | 0.558 | 28 | 57 | 150 | 1304 |
| b2mixed-biomedbert-disjoint-s42 | swap_vocab_sentence | unseen | 1271 | 0.152 | 0.937 | 0.711 | 0.657 | 0.601 | 0.856 | 162 | 138 | 31 | 940 |
| b2mixed-biomedbert-disjoint-s42 | swap_vocab_sentence | seen | 1539 | 0.116 | 0.951 | 0.765 | 0.667 | 0.627 | 0.862 | 143 | 108 | 35 | 1253 |
| b2mixed-biomedbert-disjoint-s42 | swap_novel_sentence | unseen | 1271 | 0.152 | 0.946 | 0.736 | 0.642 | 0.595 | 0.871 | 175 | 177 | 18 | 901 |
| b2mixed-biomedbert-disjoint-s42 | swap_novel_sentence | seen | 1539 | 0.116 | 0.947 | 0.735 | 0.647 | 0.611 | 0.871 | 150 | 136 | 28 | 1225 |
| b2mixed-biomedbert-disjoint-s42 | swap_pseudo_sentence | unseen | 1271 | 0.152 | 0.940 | 0.729 | 0.646 | 0.581 | 0.826 | 146 | 113 | 47 | 965 |
| b2mixed-biomedbert-disjoint-s42 | swap_pseudo_sentence | seen | 1539 | 0.116 | 0.938 | 0.723 | 0.661 | 0.616 | 0.826 | 126 | 77 | 52 | 1284 |
| b2sentence-biomedbert-disjoint-s42 | test_sentence | unseen | 1271 | 0.152 | 0.942 | 0.699 | 0.676 | 0.622 | 0.861 | 161 | 122 | 32 | 956 |
| b2sentence-biomedbert-disjoint-s42 | test_sentence | seen | 1539 | 0.116 | 0.974 | 0.826 | 0.739 | 0.704 | 0.864 | 137 | 56 | 41 | 1305 |
| b2sentence-biomedbert-disjoint-s42 | test_masked | unseen | 1271 | 0.152 | 0.785 | 0.422 | 0.041 | 0.133 | 0.510 | 4 | 0 | 189 | 1078 |
| b2sentence-biomedbert-disjoint-s42 | test_masked | seen | 1539 | 0.116 | 0.858 | 0.496 | 0.065 | 0.173 | 0.517 | 6 | 0 | 172 | 1361 |
| b2sentence-biomedbert-disjoint-s42 | test_empty | unseen | 1271 | 0.152 | 0.542 | 0.169 | 0.010 | 0.008 | 0.501 | 1 | 4 | 192 | 1074 |
| b2sentence-biomedbert-disjoint-s42 | test_empty | seen | 1539 | 0.116 | 0.591 | 0.177 | 0.043 | 0.079 | 0.509 | 4 | 5 | 174 | 1356 |
| b2sentence-biomedbert-disjoint-s42 | test_names | unseen | 1271 | 0.152 | 0.527 | 0.168 | 0.000 | 0.000 | 0.500 | 0 | 0 | 193 | 1078 |
| b2sentence-biomedbert-disjoint-s42 | test_names | seen | 1539 | 0.116 | 0.551 | 0.177 | 0.011 | 0.071 | 0.503 | 1 | 0 | 177 | 1361 |
| b2sentence-biomedbert-disjoint-s42 | swap_vocab_sentence | unseen | 1271 | 0.152 | 0.939 | 0.709 | 0.644 | 0.591 | 0.861 | 168 | 161 | 25 | 917 |
| b2sentence-biomedbert-disjoint-s42 | swap_vocab_sentence | seen | 1539 | 0.116 | 0.952 | 0.777 | 0.663 | 0.620 | 0.849 | 137 | 98 | 41 | 1263 |
| b2sentence-biomedbert-disjoint-s42 | swap_novel_sentence | unseen | 1271 | 0.152 | 0.947 | 0.729 | 0.653 | 0.604 | 0.870 | 172 | 162 | 21 | 916 |
| b2sentence-biomedbert-disjoint-s42 | swap_novel_sentence | seen | 1539 | 0.116 | 0.951 | 0.766 | 0.656 | 0.614 | 0.855 | 141 | 111 | 37 | 1250 |
| b2sentence-biomedbert-disjoint-s42 | swap_pseudo_sentence | unseen | 1271 | 0.152 | 0.943 | 0.714 | 0.685 | 0.632 | 0.865 | 162 | 118 | 31 | 960 |
| b2sentence-biomedbert-disjoint-s42 | swap_pseudo_sentence | seen | 1539 | 0.116 | 0.952 | 0.775 | 0.691 | 0.649 | 0.848 | 134 | 76 | 44 | 1285 |

## Input format by novelty (lo, hi: pair bootstrap on SemEval, drug bootstrap on Novel; lo_clustered, hi_clustered: clustered by sentence on SemEval, two-way by drug and partner on Novel)

| group | format | novelty | n | auroc | lo | hi | lo_clustered | hi_clustered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed/bertbase | sentence | SemEval test | 2810 | 0.943 | 0.934 | 0.952 | 0.920 | 0.961 |
| b2mixed/bertbase | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2mixed/bertbase | names only | SemEval test | 2810 | 0.633 | 0.605 | 0.661 | 0.592 | 0.673 |
| b2mixed/bertbase | names only | Novel OOD | 438 | 0.527 | 0.464 | 0.589 | 0.436 | 0.616 |
| b2mixed/biobert | sentence | SemEval test | 2810 | 0.954 | 0.946 | 0.962 | 0.935 | 0.969 |
| b2mixed/biobert | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2mixed/biobert | names only | SemEval test | 2810 | 0.635 | 0.609 | 0.662 | 0.597 | 0.674 |
| b2mixed/biobert | names only | Novel OOD | 438 | 0.483 | 0.411 | 0.555 | 0.373 | 0.588 |
| b2mixed/biomedbert | sentence | SemEval test | 2810 | 0.963 | 0.957 | 0.970 | 0.951 | 0.974 |
| b2mixed/biomedbert | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2mixed/biomedbert | names only | SemEval test | 2810 | 0.678 | 0.653 | 0.705 | 0.633 | 0.723 |
| b2mixed/biomedbert | names only | Novel OOD | 438 | 0.529 | 0.457 | 0.608 | 0.410 | 0.637 |
| b2sentence/bertbase | sentence | SemEval test | 2810 | 0.953 | 0.945 | 0.961 | 0.933 | 0.968 |
| b2sentence/bertbase | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2sentence/bertbase | names only | SemEval test | 2810 | 0.636 | 0.609 | 0.663 | 0.598 | 0.676 |
| b2sentence/bertbase | names only | Novel OOD | 438 | 0.449 | 0.382 | 0.517 | 0.349 | 0.550 |
| b2sentence/biobert | sentence | SemEval test | 2810 | 0.946 | 0.937 | 0.955 | 0.924 | 0.962 |
| b2sentence/biobert | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2sentence/biobert | names only | SemEval test | 2810 | 0.581 | 0.550 | 0.612 | 0.533 | 0.633 |
| b2sentence/biobert | names only | Novel OOD | 438 | 0.485 | 0.407 | 0.562 | 0.382 | 0.590 |
| b2sentence/biomedbert | sentence | SemEval test | 2810 | 0.968 | 0.961 | 0.974 | 0.955 | 0.978 |
| b2sentence/biomedbert | sentence | Novel OOD | 50 | NA | NA | NA | NA | NA |
| b2sentence/biomedbert | names only | SemEval test | 2810 | 0.614 | 0.587 | 0.639 | 0.575 | 0.655 |
| b2sentence/biomedbert | names only | Novel OOD | 438 | 0.472 | 0.408 | 0.538 | 0.365 | 0.569 |

