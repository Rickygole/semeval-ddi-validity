# R2b: open-model label adjudication (OLMo-2-1124-7B-Instruct, Drug Interactions section only)

post hoc, descriptive; automated model adjudication from the Drug Interactions section only, not a human audit

Full run.

Items 505 (audit 255, random 250); non-answers 0 items (0 prompts, chunks included); multi-chunk items 8; decisions {"audit": {"yes": 36, "no": 219, "unsure": 0}, "random": {"yes": 56, "no": 194, "unsure": 0}}.

| set | stratum and error type | n | unsure | wrong, unsure excluded | wrong, unsure as correct | wrong or unsure |
| --- | --- | --- | --- | --- | --- | --- |
| audit (all) | positives_judged_no | 179 | 0 | 144/179 = 0.804 [0.739, 0.860] | 144/179 = 0.804 [0.739, 0.860] | 144/179 = 0.804 [0.739, 0.860] |
| audit (all) | negatives_judged_yes | 76 | 0 | 1/76 = 0.013 [0.000, 0.071] | 1/76 = 0.013 [0.000, 0.071] | 1/76 = 0.013 [0.000, 0.071] |
| audit positives, positive_oracle_below_0.5 | positives_judged_no | 136 | 0 | 102/136 = 0.750 [0.669, 0.820] | 102/136 = 0.750 [0.669, 0.820] | 102/136 = 0.750 [0.669, 0.820] |
| audit positives, positive_oracle_below_0.5 positive_rule_flag | positives_judged_no | 39 | 0 | 38/39 = 0.974 [0.865, 0.999] | 38/39 = 0.974 [0.865, 0.999] | 38/39 = 0.974 [0.865, 0.999] |
| audit positives, positive_rule_flag | positives_judged_no | 4 | 0 | 4/4 = 1.000 [0.398, 1.000] | 4/4 = 1.000 [0.398, 1.000] | 4/4 = 1.000 [0.398, 1.000] |
| audit novel | positives_judged_no | 33 | 0 | 24/33 = 0.727 [0.545, 0.867] | 24/33 = 0.727 [0.545, 0.867] | 24/33 = 0.727 [0.545, 0.867] |
| audit novel | negatives_judged_yes | 24 | 0 | 1/24 = 0.042 [0.001, 0.211] | 1/24 = 0.042 [0.001, 0.211] | 1/24 = 0.042 [0.001, 0.211] |
| audit older | positives_judged_no | 146 | 0 | 120/146 = 0.822 [0.750, 0.880] | 120/146 = 0.822 [0.750, 0.880] | 120/146 = 0.822 [0.750, 0.880] |
| audit older | negatives_judged_yes | 52 | 0 | 0/52 = 0.000 [0.000, 0.068] | 0/52 = 0.000 [0.000, 0.068] | 0/52 = 0.000 [0.000, 0.068] |
| random novel | positives_judged_no | 50 | 0 | 27/50 = 0.540 [0.393, 0.682] | 27/50 = 0.540 [0.393, 0.682] | 27/50 = 0.540 [0.393, 0.682] |
| random novel | negatives_judged_yes | 50 | 0 | 1/50 = 0.020 [0.001, 0.106] | 1/50 = 0.020 [0.001, 0.106] | 1/50 = 0.020 [0.001, 0.106] |
| random older | positives_judged_no | 75 | 0 | 43/75 = 0.573 [0.454, 0.687] | 43/75 = 0.573 [0.454, 0.687] | 43/75 = 0.573 [0.454, 0.687] |
| random older | negatives_judged_yes | 75 | 0 | 0/75 = 0.000 [0.000, 0.048] | 0/75 = 0.000 [0.000, 0.048] | 0/75 = 0.000 [0.000, 0.048] |
| random unweighted pool, not a population rate | positives_judged_no | 125 | 0 | 70/125 = 0.560 [0.468, 0.649] | 70/125 = 0.560 [0.468, 0.649] | 70/125 = 0.560 [0.468, 0.649] |
| random unweighted pool, not a population rate | negatives_judged_yes | 125 | 0 | 1/125 = 0.008 [0.000, 0.044] | 1/125 = 0.008 [0.000, 0.044] | 1/125 = 0.008 [0.000, 0.044] |

## Agreement with the earlier model adjudication (255 audit items)

| subset | n | three-way agreement | both decided | kappa three-way | kappa both decided |
| --- | --- | --- | --- | --- | --- |
| all | 255 | 161/255 = 0.631 [0.569, 0.691] | 161/249 = 0.647 [0.584, 0.706] | 0.240 | 0.251 |
| current_label_1 | 179 | 87/179 = 0.486 [0.411, 0.562] | 87/173 = 0.503 [0.426, 0.580] | 0.158 | 0.172 |
| current_label_0 | 76 | 74/76 = 0.974 [0.908, 0.997] | 74/76 = 0.974 [0.908, 0.997] | -0.013 | -0.013 |
