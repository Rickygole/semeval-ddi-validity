# M10: standard SemEval 2013 DDI evaluation

Status: post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision.

Metric: micro-averaged F1 over mechanism, effect, advise and int, from the stored 5-class argmax predictions on `test_sentence` (the predictions store class ids, so this is computed directly). Repository test set: 2810 pairs, 371 positive (entity types drug and drug_n, `config.ENTITY_TYPES`). Official DDI 2013 extraction test set: 5716 pairs, 979 positive; 2906 pairs (entity types brand and group, 608 of them positive) were never scored. The 'official-set bound' counts those unscored positives as false negatives: it is what these predictions would score on the 5,716-pair set, a lower bound for a model that scored those pairs, not an estimate of it. 95% intervals: sentence-cluster bootstrap, 1,000 draws, seed 42.

## Per seed

| system | model | seed | micro F1 (2810 pairs) | 95% CI | official-set bound | 95% CI | precision | recall | mechanism | effect | advise | int | binary F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2sentence | biomedbert | 42 | 0.634 | [0.566, 0.698] | 0.381 | [0.321, 0.439] | 0.532 | 0.784 | 0.648 | 0.680 | 0.577 | 0.533 | 0.706 |
| b2sentence | biomedbert | 1 | 0.669 | [0.605, 0.731] | 0.394 | [0.331, 0.451] | 0.582 | 0.787 | 0.665 | 0.723 | 0.630 | 0.609 | 0.717 |
| b2sentence | biomedbert | 2 | 0.673 | [0.584, 0.753] | 0.390 | [0.329, 0.453] | 0.604 | 0.760 | 0.606 | 0.739 | 0.764 | 0.657 | 0.742 |
| b2sentence | biomedbert | 3 | 0.649 | [0.559, 0.736] | 0.385 | [0.321, 0.454] | 0.558 | 0.776 | 0.613 | 0.714 | 0.617 | 0.694 | 0.722 |
| b2sentence | biomedbert | 4 | 0.646 | [0.550, 0.735] | 0.377 | [0.309, 0.446] | 0.572 | 0.741 | 0.614 | 0.716 | 0.612 | 0.667 | 0.718 |
| b2mixed | biomedbert | 42 | 0.611 | [0.522, 0.701] | 0.358 | [0.294, 0.428] | 0.537 | 0.709 | 0.576 | 0.650 | 0.614 | 0.667 | 0.704 |
| b2mixed | biomedbert | 1 | 0.681 | [0.628, 0.730] | 0.392 | [0.341, 0.445] | 0.619 | 0.757 | 0.665 | 0.687 | 0.724 | 0.646 | 0.713 |
| b2mixed | biomedbert | 2 | 0.658 | [0.594, 0.718] | 0.391 | [0.331, 0.448] | 0.562 | 0.792 | 0.668 | 0.675 | 0.615 | 0.650 | 0.711 |
| b2mixed | biomedbert | 3 | 0.637 | [0.574, 0.702] | 0.363 | [0.304, 0.421] | 0.589 | 0.693 | 0.629 | 0.644 | 0.640 | 0.640 | 0.674 |
| b2mixed | biomedbert | 4 | 0.643 | [0.580, 0.702] | 0.385 | [0.327, 0.440] | 0.544 | 0.787 | 0.640 | 0.680 | 0.622 | 0.588 | 0.694 |
| b2sentence | bertbase | 42 | 0.601 | [0.537, 0.669] | 0.323 | [0.269, 0.383] | 0.635 | 0.571 | 0.529 | 0.697 | 0.606 | 0.567 | 0.627 |
| b2sentence | bertbase | 1 | 0.639 | [0.581, 0.698] | 0.361 | [0.308, 0.416] | 0.601 | 0.682 | 0.611 | 0.684 | 0.636 | 0.639 | 0.672 |
| b2sentence | bertbase | 2 | 0.605 | [0.524, 0.682] | 0.354 | [0.299, 0.414] | 0.533 | 0.701 | 0.546 | 0.681 | 0.673 | 0.545 | 0.675 |
| b2sentence | bertbase | 3 | 0.627 | [0.560, 0.691] | 0.357 | [0.297, 0.416] | 0.582 | 0.679 | 0.592 | 0.716 | 0.678 | 0.455 | 0.672 |
| b2sentence | bertbase | 4 | 0.645 | [0.593, 0.701] | 0.376 | [0.323, 0.427] | 0.575 | 0.736 | 0.599 | 0.698 | 0.678 | 0.636 | 0.683 |
| b2mixed | bertbase | 42 | 0.577 | [0.515, 0.645] | 0.312 | [0.262, 0.367] | 0.598 | 0.558 | 0.505 | 0.637 | 0.615 | 0.667 | 0.608 |
| b2mixed | bertbase | 1 | 0.580 | [0.512, 0.647] | 0.319 | [0.266, 0.375] | 0.580 | 0.580 | 0.454 | 0.724 | 0.611 | 0.606 | 0.615 |
| b2mixed | bertbase | 2 | 0.587 | [0.515, 0.656] | 0.332 | [0.278, 0.388] | 0.552 | 0.625 | 0.536 | 0.682 | 0.615 | 0.460 | 0.637 |
| b2mixed | bertbase | 3 | 0.572 | [0.505, 0.647] | 0.289 | [0.239, 0.348] | 0.709 | 0.480 | 0.512 | 0.599 | 0.647 | 0.590 | 0.621 |
| b2mixed | bertbase | 4 | 0.587 | [0.534, 0.648] | 0.342 | [0.293, 0.394] | 0.522 | 0.671 | 0.569 | 0.620 | 0.587 | 0.576 | 0.639 |
| b2sentence | biobert | 42 | 0.609 | [0.512, 0.699] | 0.338 | [0.278, 0.400] | 0.597 | 0.623 | 0.538 | 0.664 | 0.704 | 0.633 | 0.675 |
| b2mixed | biobert | 42 | 0.626 | [0.563, 0.687] | 0.338 | [0.282, 0.395] | 0.649 | 0.604 | 0.559 | 0.670 | 0.690 | 0.677 | 0.662 |

## Over seeds

| system | model | pretrained | seeds | micro F1 mean | SD | range | official-set bound mean | binary F1 mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b2sentence | biomedbert | microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext | 5 | 0.654 | 0.016 | [0.634, 0.673] | 0.386 | 0.721 |
| b2mixed | biomedbert | microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext | 5 | 0.646 | 0.026 | [0.611, 0.681] | 0.378 | 0.699 |
| b2sentence | bertbase | bert-base-uncased | 5 | 0.624 | 0.020 | [0.601, 0.645] | 0.354 | 0.666 |
| b2mixed | bertbase | bert-base-uncased | 5 | 0.581 | 0.006 | [0.572, 0.587] | 0.319 | 0.624 |
| b2sentence | biobert | dmis-lab/biobert-base-cased-v1.2 | 1 | 0.609 | NA | [0.609, 0.609] | 0.338 | 0.675 |
| b2mixed | biobert | dmis-lab/biobert-base-cased-v1.2 | 1 | 0.626 | NA | [0.626, 0.626] | 0.338 | 0.662 |

## Amendment 7 panel (one seed each, test_sentence)

| checkpoint | micro F1 | 95% CI | official-set bound | binary F1 |
| --- | --- | --- | --- | --- |
| a7-panel-bertbase-marker | 0.736 | [0.675, 0.789] | 0.395 | 0.778 |
| a7-panel-bertbase-pair | 0.580 | [0.511, 0.649] | 0.310 | 0.624 |
| a7-panel-biobert-marker | 0.811 | [0.757, 0.856] | 0.440 | 0.835 |
| a7-panel-biobert-pair | 0.635 | [0.542, 0.716] | 0.361 | 0.700 |
| a7-panel-biolinkbert-marker | 0.815 | [0.755, 0.865] | 0.444 | 0.871 |
| a7-panel-biolinkbert-pair | 0.674 | [0.595, 0.746] | 0.390 | 0.727 |
| a7-panel-biomedbert_abs-marker | 0.827 | [0.776, 0.875] | 0.448 | 0.865 |
| a7-panel-biomedbert_abs-pair | 0.641 | [0.585, 0.698] | 0.372 | 0.698 |
| a7-panel-biomedbert_full-marker | 0.814 | [0.762, 0.860] | 0.436 | 0.856 |
| a7-panel-biomedbert_full-pair | 0.679 | [0.614, 0.741] | 0.383 | 0.725 |
| a7-panel-clinicalbert-marker | 0.696 | [0.622, 0.767] | 0.381 | 0.750 |
| a7-panel-clinicalbert-pair | 0.536 | [0.465, 0.614] | 0.286 | 0.570 |
| a7-panel-deberta-marker | 0.762 | [0.703, 0.814] | 0.412 | 0.820 |
| a7-panel-deberta-pair | 0.641 | [0.568, 0.710] | 0.355 | 0.697 |
| a7-panel-electra-marker | 0.696 | [0.610, 0.780] | 0.381 | 0.747 |
| a7-panel-electra-pair | 0.664 | [0.601, 0.727] | 0.374 | 0.713 |
| a7-panel-roberta-marker | 0.711 | [0.645, 0.778] | 0.388 | 0.766 |
| a7-panel-roberta-pair | 0.627 | [0.546, 0.702] | 0.372 | 0.708 |
| a7-panel-scibert-marker | 0.749 | [0.690, 0.803] | 0.395 | 0.791 |
| a7-panel-scibert-pair | 0.645 | [0.562, 0.728] | 0.386 | 0.724 |

## Published figures

Source: Gu et al. 2021, Domain-Specific Language Model Pretraining for Biomedical Natural Language Processing, arXiv 2007.15779 (published in ACM Transactions on Computing for Healthcare), Table 6 (read from the arXiv PDF on 2026-10-17). Metric: micro F1 (Table 3 lists DDI: relation extraction, train 25296, dev 2496, test 5716, micro F1). Split: the original DDI 2013 corpus with a train/dev/test split of 624/90/191 files.

| model | DDI micro F1 (Table 6) |
| --- | --- |
| PubMedBERT (uncased) | 82.36 |
| BioBERT (cased) | 80.88 |
| BERT (uncased) | 80.04 |
| BERT (cased) | 79.34 |
| RoBERTa (cased) | 79.52 |
| SciBERT (uncased) | 81.06 |
| SciBERT (cased) | 81.22 |
| ClinicalBERT (cased) | 78.20 |
| BlueBERT (cased) | 77.78 |

The comparison is not like-for-like: BLURB trains on all four entity types with its own 624/90/191-file split and scores all 5,716 test pairs, while the repository models were trained and scored on drug and drug_n pairs only, with at most five epochs of fine-tuning and no entity dummification. The BioBERT paper (Lee et al. 2020) itself was not checked for a DDI figure.

