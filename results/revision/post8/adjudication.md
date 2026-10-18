# Label audit: automated model adjudication, not a human audit

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

Disclosure: this is an automated model adjudication, not a human audit. One automated adjudicator read each of the 255 items of label_audit_sheet.csv blind to the key, following AUDIT_GUIDELINES.md. It is a third automated source, not a reference standard, and no agreement with a human standard is claimed.

Corrections applied before judging:

* rule_flag and current_label were stripped from the copy of label_audit_sheet.csv used for judging; items were judged from the text only.
* each of the 76 negative rows, which carry no evidence text, was judged against the ood_drug Drug Interactions section in artifacts/amend7/di_sections.json, from the supplied text only and never from background knowledge.

The sheet is a list of suspect items (positives the oracle scored below 0.5 or the rule flagged, negatives the oracle scored above 0.5), not a random sample, so the rates below describe those strata only and not the whole set.

## Counts

| adjudication | current label 1 | current label 0 |
| --- | --- | --- |
| yes | 114 | 1 |
| no | 59 | 75 |
| unsure | 6 | 0 |

Agreement with the current label: 189/255 = 0.741 [0.683, 0.794] with unsure counted as not confirming; 189/249 = 0.759 [0.701, 0.811] on decided items.

## Estimated label error rate (exact Clopper-Pearson 95% intervals)

| stratum | decided only | unsure as correct | unsure as error | unsure |
| --- | --- | --- | --- | --- |
| flagged positives (judged no) | 59/173 = 0.341 [0.271, 0.417] | 59/179 = 0.330 [0.261, 0.404] | 65/179 = 0.363 [0.293, 0.438] | 6 |
| positives, positive_oracle_below_0.5 | 19/130 = 0.146 [0.090, 0.219] | 19/136 = 0.140 [0.086, 0.210] | 25/136 = 0.184 [0.123, 0.259] | 6 |
| positives, positive_oracle_below_0.5 positive_rule_flag | 37/39 = 0.949 [0.827, 0.994] | 37/39 = 0.949 [0.827, 0.994] | 37/39 = 0.949 [0.827, 0.994] | 0 |
| positives, positive_rule_flag | 3/4 = 0.750 [0.194, 0.994] | 3/4 = 0.750 [0.194, 0.994] | 3/4 = 0.750 [0.194, 0.994] | 0 |
| positives, novel | 1/30 = 0.033 [0.001, 0.172] | 1/33 = 0.030 [0.001, 0.158] | 4/33 = 0.121 [0.034, 0.282] | 3 |
| positives, older | 58/143 = 0.406 [0.324, 0.491] | 58/146 = 0.397 [0.317, 0.481] | 61/146 = 0.418 [0.337, 0.502] | 3 |
| flagged negatives (judged yes) | 1/76 = 0.013 [0.000, 0.071] | 1/76 = 0.013 [0.000, 0.071] | 1/76 = 0.013 [0.000, 0.071] | 0 |
| negatives, novel | 0/24 = 0.000 [0.000, 0.142] | 0/24 = 0.000 [0.000, 0.142] | 0/24 = 0.000 [0.000, 0.142] | 0 |
| negatives, older | 1/52 = 0.019 [0.000, 0.103] | 1/52 = 0.019 [0.000, 0.103] | 1/52 = 0.019 [0.000, 0.103] | 0 |

## Agreement with the post8 rule and with the oracle

Post8 rule, on the 179 positives (flag 1 means the rule calls the positive a non-interaction):

| adjudication | rule flag 1 | rule flag 0 |
| --- | --- | --- |
| yes | 3 | 111 |
| no | 40 | 19 |
| unsure | 0 | 6 |

Agreement on decided items: 151/173 = 0.873 [0.814, 0.919]. Flagged items judged no: 40/43 = 0.930 [0.809, 0.985]. Items judged no that the rule flagged: 40/59 = 0.678 [0.544, 0.794].

Oracle (P(yes) at least 0.5 read as yes), decided items: all 58/249 = 0.233 [0.182, 0.290]; current label 1 57/173 = 0.329 [0.260, 0.405]; current label 0 1/76 = 0.013 [0.000, 0.071].

## Tier C-adjudicated

Tier C-adjudicated is tier A without the positives adjudicated no; unsure items are kept and nothing is flipped. All negatives are kept, including any adjudicated yes. Reference values for tiers A and C-auto are read from sensitivity.json and e9.json, which reproduce the primary files.

| cohort | positives | negatives | positives dropped |
| --- | --- | --- | --- |
| novel | 147 | 290 | 1 |
| older_primary | 510 | 1159 | 52 |
| older_clean | 545 | 1233 | 54 |

### H1, H1-novel, H4, H6

| row | tier | n | AUROC | 95% CI | p_TOST | p_Holm | would-be label | kappa | kappa 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | A | 1832 | 0.452 | [0.389, 0.518] | 0.061 | 0.183 | inconclusive | -0.342 | [-0.794, 0.133] |
| H1 | C-auto | 1794 | 0.455 | [0.390, 0.524] | 0.054 | 0.162 | inconclusive | -0.316 | [-0.765, 0.187] |
| H1 | C-adjudicated | 1778 | 0.462 | [0.394, 0.530] | 0.039 | 0.117 | inconclusive | -0.259 | [-0.696, 0.228] |
| H1-novel | A | 438 | 0.523 | [0.397, 0.650] | not tested | NA | estimate only | 0.101 | [-0.486, 0.722] |
| H1-novel | C-auto | 437 | 0.519 | [0.393, 0.650] | not tested | NA | estimate only | 0.085 | [-0.504, 0.708] |
| H1-novel | C-adjudicated | 437 | 0.519 | [0.393, 0.650] | not tested | NA | estimate only | 0.085 | [-0.504, 0.708] |
| H4 | A |  | -0.071 | [-0.220, 0.068] | 0.339 | 0.339 | inconclusive | NA | NA |
| H4 | C-auto |  | -0.065 | [-0.213, 0.076] | 0.312 | 0.312 | inconclusive | NA | NA |
| H4 | C-adjudicated |  | -0.057 | [-0.210, 0.084] | 0.270 | 0.270 | inconclusive | NA | NA |
| H6 | A | 438 | 0.519 | [0.393, 0.647] | 0.102 | 0.204 | inconclusive | 0.084 | [-0.499, 0.682] |
| H6 | C-auto | 437 | 0.521 | [0.393, 0.648] | 0.112 | 0.224 | inconclusive | 0.091 | [-0.493, 0.694] |
| H6 | C-adjudicated | 437 | 0.521 | [0.393, 0.648] | 0.112 | 0.224 | inconclusive | 0.091 | [-0.493, 0.694] |

### E8 oracle rule

| tier | cohort | within-drug AUROC | 95% CI | statistic | pass | decision |
| --- | --- | --- | --- | --- | --- | --- |
| A | novel | 0.974 | [0.916, 1.000] | point | True | fail |
| A | older_primary | 0.957 | [0.921, 0.983] | lower95 | False | fail |
| C-auto | novel | 0.973 | [0.915, 1.000] | point | True | pass |
| C-auto | older_primary | 0.977 | [0.954, 0.993] | lower95 | True | pass |
| C-adjudicated | novel | 0.973 | [0.915, 1.000] | point | True | pass |
| C-adjudicated | older_primary | 0.986 | [0.968, 0.998] | lower95 | True | pass |

### E7 arms c, d, e, Older-primary

| arm and cell | tier | within | 95% CI | residual within | 95% CI | paired vs prior | 95% CI | TOST 90% | kappa | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c older_primary/A | A | 0.695 | [0.630, 0.762] | 0.706 | [0.642, 0.767] | 0.198 | [0.104, 0.286] | [0.638, 0.750] eq=False | 1.284 | signal |
| c older_primary/A | C-auto | 0.692 | [0.620, 0.763] | 0.700 | [0.629, 0.766] | 0.200 | [0.100, 0.290] | [0.632, 0.752] eq=False | 1.238 | signal |
| c older_primary/A | C-adjudicated | 0.684 | [0.615, 0.754] | 0.691 | [0.618, 0.759] | 0.197 | [0.099, 0.288] | [0.624, 0.743] eq=False | 1.168 | signal |
| c older_primary/B | A | 0.754 | [0.649, 0.841] | 0.736 | [0.633, 0.821] | 0.307 | [0.151, 0.447] | [0.668, 0.829] eq=False | NA | signal |
| c older_primary/B | C-auto | 0.750 | [0.642, 0.840] | 0.717 | [0.608, 0.806] | 0.308 | [0.136, 0.461] | [0.662, 0.827] eq=False | NA | signal |
| c older_primary/B | C-adjudicated | 0.741 | [0.636, 0.836] | 0.707 | [0.601, 0.802] | 0.303 | [0.130, 0.458] | [0.648, 0.820] eq=False | NA | signal |
| d older_primary/A | A | 0.671 | [0.601, 0.737] | 0.675 | [0.601, 0.747] | 0.175 | [0.073, 0.264] | [0.614, 0.725] eq=False | 1.130 | signal |
| d older_primary/A | C-auto | 0.667 | [0.594, 0.735] | 0.667 | [0.582, 0.740] | 0.175 | [0.068, 0.269] | [0.604, 0.724] eq=False | 1.081 | signal |
| d older_primary/A | C-adjudicated | 0.662 | [0.583, 0.733] | 0.661 | [0.579, 0.731] | 0.175 | [0.065, 0.269] | [0.597, 0.719] eq=False | 1.026 | signal |
| d older_primary/B | A | 0.731 | [0.630, 0.816] | 0.712 | [0.608, 0.802] | 0.283 | [0.115, 0.435] | [0.646, 0.806] eq=False | NA | signal |
| d older_primary/B | C-auto | 0.728 | [0.614, 0.819] | 0.704 | [0.598, 0.800] | 0.286 | [0.108, 0.448] | [0.635, 0.806] eq=False | NA | signal |
| d older_primary/B | C-adjudicated | 0.722 | [0.612, 0.821] | 0.692 | [0.587, 0.789] | 0.283 | [0.116, 0.442] | [0.632, 0.808] eq=False | NA | signal |
| e older_primary/A | A | 0.734 | [0.665, 0.802] | 0.756 | [0.694, 0.819] | 0.238 | [0.129, 0.335] | [0.676, 0.789] eq=False | 1.545 | signal |
| e older_primary/A | C-auto | 0.726 | [0.653, 0.796] | 0.740 | [0.672, 0.808] | 0.233 | [0.120, 0.331] | [0.665, 0.784] eq=False | 1.457 | signal |
| e older_primary/A | C-adjudicated | 0.720 | [0.644, 0.793] | 0.734 | [0.663, 0.799] | 0.233 | [0.117, 0.336] | [0.659, 0.781] eq=False | 1.395 | signal |
| e older_primary/B | A | 0.777 | [0.681, 0.860] | 0.773 | [0.675, 0.855] | 0.330 | [0.176, 0.472] | [0.696, 0.849] eq=False | NA | signal |
| e older_primary/B | C-auto | 0.774 | [0.666, 0.863] | 0.759 | [0.661, 0.847] | 0.333 | [0.170, 0.482] | [0.688, 0.849] eq=False | NA | signal |
| e older_primary/B | C-adjudicated | 0.767 | [0.666, 0.856] | 0.747 | [0.641, 0.835] | 0.328 | [0.164, 0.486] | [0.684, 0.845] eq=False | NA | signal |

### E9 count

| cohort | tier | rows | positives | checkpoints with upper 95% bound at most 0.60 | of |
| --- | --- | --- | --- | --- | --- |
| older_primary | A | 1721 | 562 | 20 | 20 |
| older_primary | C-auto | 1684 | 525 | 20 | 20 |
| older_primary | C-adjudicated | 1669 | 510 | 20 | 20 |
| novel | A | 438 | 148 | 3 | 20 |
| novel | C-auto | 437 | 147 | 2 | 20 |
| novel | C-adjudicated | 437 | 147 | 2 | 20 |

## Conclusions

| item | compared with | reference | C-adjudicated |
| --- | --- | --- | --- |
| E8 decision | A | fail | pass |
| E8 older_primary pass | A | False | True |
| E9 novel count upper95 <= 0.60 | A | 3 | 2 |

3 of 64 compared conclusions differ from the reference tier named in each row.
