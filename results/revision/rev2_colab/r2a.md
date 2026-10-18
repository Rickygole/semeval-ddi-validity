# R2a: SemEval-trained encoders on seen-drug and unseen-drug pair labels

post hoc, descriptive; no decision rule

Seen pairs also in SemEval train: 581 of 4643 (213 with a SemEval positive instance); 175 drugs act as both anchor and partner.

## Within-drug AUROC, names only, seed-mean score, two-way bootstrap 95% interval

| family | cohort | input | pairs | positives | anchor drugs | seeds | within-drug AUROC | 95% interval | per seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2mixed | seen | names_only | 4643 | 1542 | 299 | 5 | 0.455 | [0.411, 0.494] | 0.460, 0.458, 0.464, 0.457, 0.451 |
| b2mixed | seen | names_text_b1 | 4643 | 1542 | 299 | 5 | 0.464 | [0.422, 0.504] | 0.478, 0.462, 0.468, 0.461, 0.440 |
| b2mixed | seen_not_in_semeval_train | names_only | 4062 | 1134 | 299 | 5 | 0.439 | [0.390, 0.486] | 0.442, 0.441, 0.443, 0.439, 0.450 |
| b2mixed | seen_not_in_semeval_train | names_text_b1 | 4062 | 1134 | 299 | 5 | 0.450 | [0.404, 0.495] | 0.457, 0.443, 0.456, 0.445, 0.443 |
| b2mixed | novel | names_only | 438 | 148 | 48 | 5 | 0.483 | [0.353, 0.615] | 0.507, 0.547, 0.498, 0.485, 0.494 |
| b2mixed | novel | names_text_b1 | 438 | 148 | 48 | 5 | 0.482 | [0.335, 0.624] | 0.485, 0.539, 0.452, 0.469, 0.483 |
| b2mixed | older_primary | names_only | 1721 | 562 | 121 | 5 | 0.451 | [0.383, 0.518] | 0.462, 0.459, 0.456, 0.459, 0.465 |
| b2sentence | seen | names_only | 4643 | 1542 | 299 | 5 | 0.435 | [0.395, 0.473] | 0.425, 0.466, 0.472, 0.457, 0.446 |
| b2sentence | seen | names_text_b1 | 4643 | 1542 | 299 | 5 | 0.429 | [0.391, 0.466] | 0.430, 0.484, 0.486, 0.457, 0.441 |
| b2sentence | seen_not_in_semeval_train | names_only | 4062 | 1134 | 299 | 5 | 0.439 | [0.396, 0.484] | 0.437, 0.469, 0.487, 0.459, 0.457 |
| b2sentence | seen_not_in_semeval_train | names_text_b1 | 4062 | 1134 | 299 | 5 | 0.441 | [0.395, 0.485] | 0.441, 0.493, 0.492, 0.465, 0.455 |
| b2sentence | novel | names_only | 438 | 148 | 48 | 5 | 0.511 | [0.380, 0.641] | 0.462, 0.464, 0.469, 0.524, 0.507 |
| b2sentence | novel | names_text_b1 | 438 | 148 | 48 | 5 | 0.444 | [0.321, 0.589] | 0.453, 0.465, 0.479, 0.495, 0.463 |
| b2sentence | older_primary | names_only | 1721 | 562 | 121 | 5 | 0.469 | [0.404, 0.534] | 0.461, 0.494, 0.487, 0.472, 0.484 |
| marker | seen | names_only | 4643 | 1542 | 299 | 5 | 0.398 | [0.356, 0.437] | 0.418, 0.438, 0.425, 0.396, 0.417 |
| marker | seen_not_in_semeval_train | names_only | 4062 | 1134 | 299 | 5 | 0.416 | [0.367, 0.465] | 0.428, 0.456, 0.441, 0.409, 0.420 |
| marker | novel | names_only | 438 | 148 | 48 | 5 | 0.494 | [0.357, 0.629] | 0.482, 0.472, 0.476, 0.497, 0.537 |
| marker | older_primary | names_only | 1721 | 562 | 121 | 5 | 0.401 | [0.335, 0.472] | 0.420, 0.448, 0.422, 0.396, 0.443 |

## SemEval 2013 test, pooled AUROC

| family | key | seeds | seed-mean AUROC | per seed |
| --- | --- | --- | --- | --- |
| b2mixed | test_sentence | 5 | 0.961 | 0.959, 0.960, 0.947, 0.959, 0.941 |
| b2mixed | test_empty | 5 | 0.670 | 0.648, 0.684, 0.662, 0.659, 0.660 |
| b2sentence | test_sentence | 5 | 0.970 | 0.971, 0.954, 0.965, 0.960, 0.962 |
| b2sentence | test_empty | 5 | 0.631 | 0.645, 0.633, 0.499, 0.592, 0.599 |
| marker | test_sentence | 5 | 0.984 | 0.978, 0.977, 0.982, 0.977, 0.972 |
| marker | test_empty | 5 | 0.640 | 0.594, 0.598, 0.611, 0.641, 0.606 |

## Reproducibility of the retrained b2mixed and b2sentence models against the stored predictions

| family | seed | key | n | Spearman | max abs diff | same class |
| --- | --- | --- | --- | --- | --- | --- |
| b2mixed | 42 | ood_empty | 438 | 0.702 | 0.8440 | 0.7123 |
| b2mixed | 42 | ood_names | 438 | 0.699 | 0.7282 | 0.7945 |
| b2mixed | 42 | ood_sentence | 50 | 0.938 | 0.6137 | 0.9200 |
| b2mixed | 42 | ood_swap_sentence | 100 | 0.907 | 0.7924 | 0.8900 |
| b2mixed | 42 | oodold_empty | 1944 | 0.765 | 0.7472 | 0.7737 |
| b2mixed | 42 | oodold_sentence | 256 | 0.934 | 0.9626 | 0.8750 |
| b2mixed | 42 | swap_novel_sentence | 2810 | 0.893 | 0.9931 | 0.9295 |
| b2mixed | 42 | swap_pseudo_sentence | 2810 | 0.885 | 0.9845 | 0.9327 |
| b2mixed | 42 | swap_vocab_sentence | 2810 | 0.884 | 0.9911 | 0.9363 |
| b2mixed | 42 | test_empty | 2810 | 0.861 | 0.8080 | 0.9078 |
| b2mixed | 42 | test_masked | 2810 | 0.802 | 0.9939 | 0.9936 |
| b2mixed | 42 | test_names | 2810 | 0.816 | 0.8974 | 0.9377 |
| b2mixed | 42 | test_sentence | 2810 | 0.861 | 0.9915 | 0.9473 |
| b2mixed | 1 | ood_empty | 438 | 0.756 | 0.8620 | 0.7717 |
| b2mixed | 1 | ood_names | 438 | 0.714 | 0.8054 | 0.8402 |
| b2mixed | 1 | ood_sentence | 50 | 0.912 | 0.9442 | 0.8800 |
| b2mixed | 1 | ood_swap_sentence | 100 | 0.892 | 0.9442 | 0.8500 |
| b2mixed | 1 | oodold_empty | 1944 | 0.831 | 0.7421 | 0.8349 |
| b2mixed | 1 | oodold_sentence | 256 | 0.890 | 0.9951 | 0.8633 |
| b2mixed | 1 | swap_novel_sentence | 2810 | 0.967 | 0.9901 | 0.9374 |
| b2mixed | 1 | swap_pseudo_sentence | 2810 | 0.953 | 0.9788 | 0.9395 |
| b2mixed | 1 | swap_vocab_sentence | 2810 | 0.951 | 0.9935 | 0.9434 |
| b2mixed | 1 | test_empty | 2810 | 0.880 | 0.8357 | 0.9445 |
| b2mixed | 1 | test_masked | 2810 | 0.893 | 0.9819 | 0.9929 |
| b2mixed | 1 | test_names | 2810 | 0.833 | 0.8990 | 0.9559 |
| b2mixed | 1 | test_sentence | 2810 | 0.954 | 0.9913 | 0.9512 |
| b2mixed | 2 | ood_empty | 438 | 0.749 | 0.8690 | 0.7557 |
| b2mixed | 2 | ood_names | 438 | 0.637 | 0.9639 | 0.7900 |
| b2mixed | 2 | ood_sentence | 50 | 0.744 | 0.8291 | 0.8200 |
| b2mixed | 2 | ood_swap_sentence | 100 | 0.743 | 0.8291 | 0.8000 |
| b2mixed | 2 | oodold_empty | 1944 | 0.771 | 0.9480 | 0.8256 |
| b2mixed | 2 | oodold_sentence | 256 | 0.916 | 0.9940 | 0.8711 |
| b2mixed | 2 | swap_novel_sentence | 2810 | 0.934 | 0.9945 | 0.9388 |
| b2mixed | 2 | swap_pseudo_sentence | 2810 | 0.928 | 0.9956 | 0.9416 |
| b2mixed | 2 | swap_vocab_sentence | 2810 | 0.924 | 0.9908 | 0.9288 |
| b2mixed | 2 | test_empty | 2810 | 0.887 | 0.9642 | 0.9249 |
| b2mixed | 2 | test_masked | 2810 | 0.900 | 0.9642 | 0.9943 |
| b2mixed | 2 | test_names | 2810 | 0.868 | 0.8987 | 0.9359 |
| b2mixed | 2 | test_sentence | 2810 | 0.912 | 0.9967 | 0.9459 |
| b2mixed | 3 | ood_empty | 438 | 0.743 | 0.9292 | 0.6689 |
| b2mixed | 3 | ood_names | 438 | 0.538 | 0.9850 | 0.8402 |
| b2mixed | 3 | ood_sentence | 50 | 0.659 | 0.9577 | 0.7800 |
| b2mixed | 3 | ood_swap_sentence | 100 | 0.664 | 0.9577 | 0.8100 |
| b2mixed | 3 | oodold_empty | 1944 | 0.743 | 0.9196 | 0.7742 |
| b2mixed | 3 | oodold_sentence | 256 | 0.902 | 0.9870 | 0.8750 |
| b2mixed | 3 | swap_novel_sentence | 2810 | 0.911 | 0.9955 | 0.9413 |
| b2mixed | 3 | swap_pseudo_sentence | 2810 | 0.889 | 0.9964 | 0.9377 |
| b2mixed | 3 | swap_vocab_sentence | 2810 | 0.913 | 0.9923 | 0.9409 |
| b2mixed | 3 | test_empty | 2810 | 0.875 | 0.9488 | 0.9142 |
| b2mixed | 3 | test_masked | 2810 | 0.808 | 0.5634 | 0.9996 |
| b2mixed | 3 | test_names | 2810 | 0.757 | 0.9662 | 0.9107 |
| b2mixed | 3 | test_sentence | 2810 | 0.914 | 0.9816 | 0.9580 |
| b2mixed | 4 | ood_empty | 438 | 0.463 | 0.8275 | 0.5594 |
| b2mixed | 4 | ood_names | 438 | 0.470 | 0.9597 | 0.8607 |
| b2mixed | 4 | ood_sentence | 50 | 0.692 | 0.7092 | 0.7800 |
| b2mixed | 4 | ood_swap_sentence | 100 | 0.686 | 0.8170 | 0.7700 |
| b2mixed | 4 | oodold_empty | 1944 | 0.673 | 0.8770 | 0.7490 |
| b2mixed | 4 | oodold_sentence | 256 | 0.856 | 0.9883 | 0.8086 |
| b2mixed | 4 | swap_novel_sentence | 2810 | 0.906 | 0.9900 | 0.9075 |
| b2mixed | 4 | swap_pseudo_sentence | 2810 | 0.906 | 0.9962 | 0.9185 |
| b2mixed | 4 | swap_vocab_sentence | 2810 | 0.886 | 0.9933 | 0.9231 |
| b2mixed | 4 | test_empty | 2810 | 0.822 | 0.8379 | 0.8762 |
| b2mixed | 4 | test_masked | 2810 | 0.796 | 0.9897 | 0.9690 |
| b2mixed | 4 | test_names | 2810 | 0.813 | 0.8011 | 0.9466 |
| b2mixed | 4 | test_sentence | 2810 | 0.872 | 0.9863 | 0.9445 |
| b2sentence | 42 | ood_empty | 438 | 0.635 | 0.7197 | 0.9886 |
| b2sentence | 42 | ood_names | 438 | 0.621 | 0.7452 | 0.9954 |
| b2sentence | 42 | ood_sentence | 50 | 0.820 | 0.9350 | 0.7600 |
| b2sentence | 42 | ood_swap_sentence | 100 | 0.826 | 0.9350 | 0.7600 |
| b2sentence | 42 | oodold_empty | 1944 | 0.607 | 0.8799 | 0.9779 |
| b2sentence | 42 | oodold_sentence | 256 | 0.773 | 0.9837 | 0.7812 |
| b2sentence | 42 | swap_novel_sentence | 2810 | 0.923 | 0.9908 | 0.8794 |
| b2sentence | 42 | swap_pseudo_sentence | 2810 | 0.914 | 0.9886 | 0.9050 |
| b2sentence | 42 | swap_vocab_sentence | 2810 | 0.916 | 0.9959 | 0.8957 |
| b2sentence | 42 | test_empty | 2810 | 0.747 | 0.9003 | 0.9957 |
| b2sentence | 42 | test_masked | 2810 | 0.795 | 0.9584 | 0.9982 |
| b2sentence | 42 | test_names | 2810 | 0.670 | 0.3435 | 0.9996 |
| b2sentence | 42 | test_sentence | 2810 | 0.912 | 0.9901 | 0.9448 |
| b2sentence | 1 | ood_empty | 438 | 0.570 | 0.0633 | 1.0000 |
| b2sentence | 1 | ood_names | 438 | 0.541 | 0.0390 | 1.0000 |
| b2sentence | 1 | ood_sentence | 50 | 0.940 | 0.5202 | 0.9800 |
| b2sentence | 1 | ood_swap_sentence | 100 | 0.941 | 0.7685 | 0.9700 |
| b2sentence | 1 | oodold_empty | 1944 | 0.717 | 0.8158 | 0.9990 |
| b2sentence | 1 | oodold_sentence | 256 | 0.963 | 0.8890 | 0.9297 |
| b2sentence | 1 | swap_novel_sentence | 2810 | 0.953 | 0.9923 | 0.9690 |
| b2sentence | 1 | swap_pseudo_sentence | 2810 | 0.946 | 0.9940 | 0.9616 |
| b2sentence | 1 | swap_vocab_sentence | 2810 | 0.925 | 0.9934 | 0.9705 |
| b2sentence | 1 | test_empty | 2810 | 0.631 | 0.9795 | 0.9986 |
| b2sentence | 1 | test_masked | 2810 | 0.934 | 0.6626 | 0.9986 |
| b2sentence | 1 | test_names | 2810 | 0.494 | 0.8331 | 0.9996 |
| b2sentence | 1 | test_sentence | 2810 | 0.913 | 0.9814 | 0.9744 |
| b2sentence | 2 | ood_empty | 438 | 0.599 | 0.1136 | 1.0000 |
| b2sentence | 2 | ood_names | 438 | 0.603 | 0.0842 | 1.0000 |
| b2sentence | 2 | ood_sentence | 50 | 0.963 | 0.5442 | 0.9800 |
| b2sentence | 2 | ood_swap_sentence | 100 | 0.963 | 0.8426 | 0.9500 |
| b2sentence | 2 | oodold_empty | 1944 | 0.393 | 0.1050 | 1.0000 |
| b2sentence | 2 | oodold_sentence | 256 | 0.960 | 0.8176 | 0.9180 |
| b2sentence | 2 | swap_novel_sentence | 2810 | 0.967 | 0.8622 | 0.9658 |
| b2sentence | 2 | swap_pseudo_sentence | 2810 | 0.963 | 0.9827 | 0.9665 |
| b2sentence | 2 | swap_vocab_sentence | 2810 | 0.961 | 0.9364 | 0.9619 |
| b2sentence | 2 | test_empty | 2810 | 0.128 | 0.1302 | 1.0000 |
| b2sentence | 2 | test_masked | 2810 | 0.911 | 0.0710 | 1.0000 |
| b2sentence | 2 | test_names | 2810 | 0.030 | 0.1264 | 1.0000 |
| b2sentence | 2 | test_sentence | 2810 | 0.947 | 0.9488 | 0.9623 |
| b2sentence | 3 | ood_empty | 438 | 0.636 | 0.6518 | 0.9977 |
| b2sentence | 3 | ood_names | 438 | 0.698 | 0.0439 | 1.0000 |
| b2sentence | 3 | ood_sentence | 50 | 0.893 | 0.9606 | 0.8000 |
| b2sentence | 3 | ood_swap_sentence | 100 | 0.855 | 0.9686 | 0.7700 |
| b2sentence | 3 | oodold_empty | 1944 | 0.662 | 0.5813 | 0.9985 |
| b2sentence | 3 | oodold_sentence | 256 | 0.924 | 0.9599 | 0.8555 |
| b2sentence | 3 | swap_novel_sentence | 2810 | 0.950 | 0.9806 | 0.9505 |
| b2sentence | 3 | swap_pseudo_sentence | 2810 | 0.949 | 0.9694 | 0.9548 |
| b2sentence | 3 | swap_vocab_sentence | 2810 | 0.937 | 0.9886 | 0.9548 |
| b2sentence | 3 | test_empty | 2810 | 0.556 | 0.5400 | 0.9986 |
| b2sentence | 3 | test_masked | 2810 | 0.931 | 0.9222 | 0.9964 |
| b2sentence | 3 | test_names | 2810 | 0.473 | 0.2526 | 1.0000 |
| b2sentence | 3 | test_sentence | 2810 | 0.932 | 0.9679 | 0.9687 |
| b2sentence | 4 | ood_empty | 438 | 0.616 | 0.1020 | 1.0000 |
| b2sentence | 4 | ood_names | 438 | 0.722 | 0.1058 | 1.0000 |
| b2sentence | 4 | ood_sentence | 50 | 0.857 | 0.7236 | 0.8800 |
| b2sentence | 4 | ood_swap_sentence | 100 | 0.865 | 0.8282 | 0.8700 |
| b2sentence | 4 | oodold_empty | 1944 | 0.546 | 0.1867 | 1.0000 |
| b2sentence | 4 | oodold_sentence | 256 | 0.916 | 0.9868 | 0.8906 |
| b2sentence | 4 | swap_novel_sentence | 2810 | 0.931 | 0.9929 | 0.9473 |
| b2sentence | 4 | swap_pseudo_sentence | 2810 | 0.925 | 0.9957 | 0.9381 |
| b2sentence | 4 | swap_vocab_sentence | 2810 | 0.915 | 0.9915 | 0.9463 |
| b2sentence | 4 | test_empty | 2810 | 0.401 | 0.5192 | 0.9996 |
| b2sentence | 4 | test_masked | 2810 | 0.883 | 0.7362 | 0.9993 |
| b2sentence | 4 | test_names | 2810 | 0.468 | 0.7589 | 0.9993 |
| b2sentence | 4 | test_sentence | 2810 | 0.903 | 0.9968 | 0.9587 |
| marker | 42 | ood_empty | 438 | 0.618 | 0.3513 | 1.0000 |
| marker | 42 | ood_sentence | 50 | 0.817 | 0.9923 | 0.9600 |
| marker | 42 | oodold_empty | 1944 | 0.523 | 0.0319 | 1.0000 |
| marker | 42 | oodold_sentence | 255 | 0.906 | 0.9980 | 0.8824 |
| marker | 42 | test_empty | 2810 | 0.631 | 0.0206 | 1.0000 |
| marker | 42 | test_sentence | 2810 | 0.923 | 0.9984 | 0.9747 |

| family | seed | key / cohort | retrained within-drug AUROC | stored | difference |
| --- | --- | --- | --- | --- | --- |
| b2mixed | 42 | ood_empty/novel | 0.507 | 0.518 | -0.0106 |
| b2mixed | 42 | oodold_empty/older_primary | 0.462 | 0.448 | +0.0140 |
| b2mixed | 42 | ood_names/novel | 0.485 | 0.515 | -0.0304 |
| b2mixed | 1 | ood_empty/novel | 0.547 | 0.515 | +0.0317 |
| b2mixed | 1 | oodold_empty/older_primary | 0.459 | 0.448 | +0.0106 |
| b2mixed | 1 | ood_names/novel | 0.539 | 0.510 | +0.0291 |
| b2mixed | 2 | ood_empty/novel | 0.498 | 0.510 | -0.0119 |
| b2mixed | 2 | oodold_empty/older_primary | 0.456 | 0.454 | +0.0015 |
| b2mixed | 2 | ood_names/novel | 0.452 | 0.509 | -0.0568 |
| b2mixed | 3 | ood_empty/novel | 0.485 | 0.532 | -0.0476 |
| b2mixed | 3 | oodold_empty/older_primary | 0.459 | 0.441 | +0.0179 |
| b2mixed | 3 | ood_names/novel | 0.469 | 0.520 | -0.0515 |
| b2mixed | 4 | ood_empty/novel | 0.494 | 0.507 | -0.0132 |
| b2mixed | 4 | oodold_empty/older_primary | 0.465 | 0.481 | -0.0163 |
| b2mixed | 4 | ood_names/novel | 0.483 | 0.527 | -0.0436 |
| b2sentence | 42 | ood_empty/novel | 0.462 | 0.489 | -0.0271 |
| b2sentence | 42 | oodold_empty/older_primary | 0.461 | 0.458 | +0.0027 |
| b2sentence | 42 | ood_names/novel | 0.453 | 0.493 | -0.0396 |
| b2sentence | 1 | ood_empty/novel | 0.464 | 0.494 | -0.0304 |
| b2sentence | 1 | oodold_empty/older_primary | 0.494 | 0.478 | +0.0153 |
| b2sentence | 1 | ood_names/novel | 0.465 | 0.425 | +0.0396 |
| b2sentence | 2 | ood_empty/novel | 0.469 | 0.495 | -0.0264 |
| b2sentence | 2 | oodold_empty/older_primary | 0.487 | 0.484 | +0.0027 |
| b2sentence | 2 | ood_names/novel | 0.479 | 0.445 | +0.0337 |
| b2sentence | 3 | ood_empty/novel | 0.524 | 0.501 | +0.0225 |
| b2sentence | 3 | oodold_empty/older_primary | 0.472 | 0.488 | -0.0164 |
| b2sentence | 3 | ood_names/novel | 0.495 | 0.498 | -0.0026 |
| b2sentence | 4 | ood_empty/novel | 0.507 | 0.485 | +0.0225 |
| b2sentence | 4 | oodold_empty/older_primary | 0.484 | 0.449 | +0.0353 |
| b2sentence | 4 | ood_names/novel | 0.463 | 0.472 | -0.0092 |
| marker | 42 | ood_empty/novel | 0.482 | 0.475 | +0.0066 |
| marker | 42 | oodold_empty/older_primary | 0.420 | 0.424 | -0.0040 |
