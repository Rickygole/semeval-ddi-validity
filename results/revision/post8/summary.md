# Post 8 summary: label-error screen and tier C-auto (post hoc, exploratory)

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

Nothing here changes a preregistered decision. Tier C-auto is a sensitivity analysis; tier A stays primary. The audit sheet is unadjudicated.

## Screen

- Rule flags (N, L, H): Novel 1 of 148; Older 42 of 648 (Older-clean 38 of 599, Older-primary 37 of 562). Reviewer: about 69 Older, 2 Novel.
- Absence-of-evidence positives (not dropped in C-auto): Novel 0, Older 3.
- Positives with oracle P(yes) < 0.5: Novel 33, Older 142 of 648 (reviewer 142). Of the Older rejections, 38 carry a rule flag and 104 do not; 4 flagged positives were accepted by the oracle.
- Negatives with oracle P(yes) > 0.5: Novel 24, Older 52 (reviewer 52).
- Audit sheet: 255 items in label_audit_sheet.csv (scores only in label_audit_key.csv).

## Primary next to sensitivity

| quantity | tier A (primary) | C-auto | C-auto-broad |
| --- | --- | --- | --- |
| E8 Older-primary within-drug, 95% CI | 0.957 [0.921, 0.983] | 0.977 [0.954, 0.993] | 0.979 [0.956, 0.994] |
| E8 bar (Older-primary lower bound) | 0.950 | 0.950 | 0.950 |
| E8 Novel point | 0.974 | 0.973 | 0.973 |
| E8 decision | fail | pass | pass |
| H1 | 0.452, 90% [0.395, 0.509], p_TOST 0.061, Holm 0.183, inconclusive | 0.455, 90% [0.397, 0.512], p_TOST 0.054, Holm 0.162, inconclusive | 0.456, 90% [0.401, 0.512], p_TOST 0.051, Holm 0.153, inconclusive |
| H1-novel | 0.523, 90% [0.411, 0.626] | 0.519, 90% [0.410, 0.625] | 0.519, 90% [0.410, 0.625] |
| H4 | -0.071, 90% [-0.192, 0.045], p_TOST 0.339, Holm 0.339, inconclusive | -0.065, 90% [-0.187, 0.056], p_TOST 0.312, Holm 0.312, inconclusive | -0.064, 90% [-0.185, 0.057], p_TOST 0.300, Holm 0.300, inconclusive |
| H6 | 0.519, 90% [0.421, 0.627], p_TOST 0.102, Holm 0.204, inconclusive | 0.521, 90% [0.420, 0.629], p_TOST 0.112, Holm 0.224, inconclusive | 0.521, 90% [0.420, 0.629], p_TOST 0.112, Holm 0.224, inconclusive |
| H1 kappa, 95% CI | -0.342 [-0.794, 0.133] | -0.316 [-0.765, 0.187] | -0.307 [-0.748, 0.188] |
| H1-novel kappa, 95% CI | 0.101 [-0.486, 0.722] | 0.085 [-0.504, 0.708] | 0.085 [-0.504, 0.708] |
| H6 kappa, 95% CI | 0.084 [-0.499, 0.682] | 0.091 [-0.493, 0.694] | 0.091 [-0.493, 0.694] |
| E9 older_primary: upper bounds <= 0.60 (of 20) | 20 | 20 | not run |
| E9 older_primary: variance ratio, old / paired reference | 0.574 / 0.670 | 0.642 / 0.752 | not run |
| E9 older_primary: kappa 95% upper bound range (97.5th / 95th percentile) | [-0.120, 0.536] / [-0.179, 0.457] | [-0.173, 0.536] / [-0.233, 0.446] | not run |
| E9 novel: upper bounds <= 0.60 (of 20) | 3 | 2 | not run |
| E9 novel: variance ratio, old / paired reference | 0.115 / 0.123 | 0.116 / 0.123 | not run |
| E9 novel: kappa 95% upper bound range (97.5th / 95th percentile) | [0.398, 0.870] / [0.311, 0.719] | [0.390, 0.856] / [0.295, 0.719] | not run |
| DrugBank lookup novel: within / pooled | 0.729 / 0.767 | 0.727 / 0.766 | not run |
| DrugBank lookup older_full: within / pooled | 0.632 / 0.661 | 0.634 / 0.668 | not run |
| DrugBank lookup older_clean: within / pooled | 0.641 / 0.680 | 0.644 / 0.687 | not run |
| DrugBank lookup older_primary: within / pooled | 0.652 / 0.692 | 0.655 / 0.700 | not run |
| Redacted oracle novel: length-only / Qwen within-drug | 1.000 / 0.731 | 1.000 / 0.728 | not run |
| Redacted oracle older_primary: length-only / Qwen within-drug | 1.000 / 0.682 | 1.000 / 0.684 | not run |

## Conclusions that change under C-auto

| item | tier | primary | sensitivity | changed |
| --- | --- | --- | --- | --- |
| E8 oracle rule | C-auto | fail | pass | yes |
| H1 (would-be label) | C-auto | inconclusive | inconclusive | no |
| H4 (would-be label) | C-auto | inconclusive | inconclusive | no |
| H6 (would-be label) | C-auto | inconclusive | inconclusive | no |
| E8 oracle rule | C-auto-broad | fail | pass | yes |
| H1 (would-be label) | C-auto-broad | inconclusive | inconclusive | no |
| H4 (would-be label) | C-auto-broad | inconclusive | inconclusive | no |
| H6 (would-be label) | C-auto-broad | inconclusive | inconclusive | no |
| E7 arm c novel/A | C-auto | neither | neither | no |
| E7 arm c novel/B | C-auto | neither | neither | no |
| E7 arm c older_primary/A | C-auto | signal | signal | no |
| E7 arm c older_primary/B | C-auto | signal | signal | no |
| E7 arm c older_clean/A | C-auto | signal | signal | no |
| E7 arm c older_clean/B | C-auto | signal | signal | no |
| E7 arm d novel/A | C-auto | neither | neither | no |
| E7 arm d novel/B | C-auto | neither | neither | no |
| E7 arm d older_primary/A | C-auto | signal | signal | no |
| E7 arm d older_primary/B | C-auto | signal | signal | no |
| E7 arm d older_clean/A | C-auto | signal | signal | no |
| E7 arm d older_clean/B | C-auto | signal | signal | no |
| E7 arm e novel/A | C-auto | neither | neither | no |
| E7 arm e novel/B | C-auto | neither | neither | no |
| E7 arm e older_primary/A | C-auto | signal | signal | no |
| E7 arm e older_primary/B | C-auto | signal | signal | no |
| E7 arm e older_clean/A | C-auto | signal | signal | no |
| E7 arm e older_clean/B | C-auto | signal | signal | no |
| E9 older_primary checkpoints with 95% upper bound <= 0.60 (of 20) | C-auto | 20 | 20 | no |
| E9 novel checkpoints with 95% upper bound <= 0.60 (of 20) | C-auto | 3 | 2 | yes |

3 of 28 checked labels change. Files: criteria.json, screen.md, label_audit_sheet.csv, label_audit_key.csv, sensitivity.md, e9.md, redacted_confound.md.
