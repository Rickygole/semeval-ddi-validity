# Label-error screen (post hoc, exploratory)

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

Rule: results/revision/post8/criteria.json (non-interaction N, laboratory test L, heading H) applied to each positive's evidence sentence, in clauses that name the partner. The absence-of-evidence family is reported and not dropped.

| cohort | positives | negatives | rule flags | families | absence (not dropped) | positives with oracle P < 0.5 | flagged and rejected | rejected, not flagged | flagged, not rejected | negatives with oracle P > 0.5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel/all | 148 | 290 | 1 | {'N': 1} | 0 | 33 | 1 | 32 | 0 | 24 |
| older/all | 648 | 1296 | 42 | {'N': 34, 'L': 1, 'HN': 7} | 3 | 142 | 38 | 104 | 4 | 52 |
| older/older_clean | 599 | 1233 | 38 | {'N': 30, 'L': 1, 'HN': 7} | 2 | 127 | 34 | 93 | 4 | 52 |
| older/older_primary | 562 | 1159 | 37 | {'N': 29, 'L': 1, 'HN': 7} | 2 | 122 | 33 | 89 | 4 | 51 |

## Reviewer comparison

- older_positives_oracle_below_0.5: reviewer 142 of 648; here 142 of 648
- older_rule_flags: reviewer about 69 of 648; here 42 of 648
- novel_rule_flags: reviewer 2 of 148; here 1 of 148
- negatives_oracle_above_0.5: reviewer 52; here 76

## Drugs with the most rule flags

| cohort | drug | positives | rule flags | oracle-rejected positives |
| --- | --- | --- | --- | --- |
| older | raltegravir | 8 | 7 | 7 |
| older | febuxostat | 8 | 6 | 6 |
| older | darifenacin hydrobromide | 10 | 4 | 5 |
| older | belimumab | 4 | 4 | 4 |
| older | dabigatran etexilate | 6 | 4 | 1 |
| older | dutasteride | 7 | 3 | 5 |
| older | bedaquiline | 3 | 3 | 3 |
| older | asenapine | 3 | 2 | 2 |
| older | eribulin | 2 | 2 | 2 |
| older | desvenlafaxine | 10 | 1 | 6 |
| older | alvimopan | 1 | 1 | 1 |
| older | exenatide | 1 | 1 | 1 |
| older | methylnaltrexone bromide | 1 | 1 | 1 |
| older | tocilizumab | 1 | 1 | 1 |
| older | trospium chloride | 5 | 1 | 1 |
| novel | ozanimod | 5 | 1 | 1 |

## Drugs with the most oracle-rejected positives

| cohort | drug | positives | oracle-rejected | rule flags |
| --- | --- | --- | --- | --- |
| older | colesevelam | 10 | 7 | 0 |
| older | raltegravir | 8 | 7 | 7 |
| older | desvenlafaxine | 10 | 6 | 1 |
| older | febuxostat | 8 | 6 | 6 |
| older | fingolimod | 10 | 6 | 0 |
| older | tizanidine | 9 | 6 | 0 |
| older | darifenacin hydrobromide | 10 | 5 | 4 |
| older | dutasteride | 7 | 5 | 3 |
| older | milnacipran | 5 | 5 | 0 |
| older | remifentanil | 5 | 5 | 0 |
| older | belimumab | 4 | 4 | 4 |
| older | atazanavir sulfate | 10 | 3 | 0 |
| older | bedaquiline | 3 | 3 | 3 |
| older | citalopram hydrobromide | 5 | 3 | 0 |
| older | sevelamer | 3 | 3 | 0 |
| novel | fostemsavir | 10 | 6 | 0 |
| novel | amisulpride | 3 | 3 | 0 |
| novel | oliceridine | 10 | 3 | 0 |
| novel | quizartinib | 8 | 3 | 0 |
| novel | bimekizumab-bkzx | 2 | 2 | 0 |
| novel | palopegteriparatide | 2 | 2 | 0 |
| novel | sotagliflozin | 3 | 2 | 0 |
| novel | trilaciclib | 2 | 2 | 0 |
| novel | abrocitinib | 2 | 1 | 0 |
| novel | fexinidazole | 10 | 1 | 0 |
| novel | iptacopan | 2 | 1 | 0 |
| novel | lonapegsomatropin-tcgd | 1 | 1 | 0 |
| novel | osilodrostat | 5 | 1 | 0 |
| novel | ozanimod | 5 | 1 | 1 |
| novel | pacritinib | 4 | 1 | 0 |

## Flagged positives

| cohort | drug | partner | flag | absence | families | patterns |
| --- | --- | --- | --- | --- | --- | --- |
| novel | ozanimod | cyclosporine | 1 | 0 | N | n17 s01 s02 |
| older | alvimopan | morphine | 1 | 0 | N | n05 |
| older | asenapine | lithium | 1 | 0 | N | n10 |
| older | asenapine | valproic acid | 1 | 0 | N | n10 |
| older | atazanavir sulfate | nifedipine | 0 | 1 |  | s01 s02 |
| older | bedaquiline | cycloserine | 1 | 0 | N | n09 |
| older | bedaquiline | ethambutol | 1 | 0 | N | n09 |
| older | bedaquiline | ofloxacin | 1 | 0 | N | n09 |
| older | belimumab | azathioprine | 1 | 0 | N | n04 |
| older | belimumab | cyclophosphamide | 1 | 0 | N | n04 |
| older | belimumab | methotrexate | 1 | 0 | N | n04 |
| older | belimumab | mycophenolate | 1 | 0 | N | n04 |
| older | dabigatran etexilate | amiodarone | 1 | 0 | N | n13 |
| older | dabigatran etexilate | clarithromycin | 1 | 0 | N | n13 |
| older | dabigatran etexilate | quinidine | 1 | 0 | N | n13 |
| older | dabigatran etexilate | verapamil | 1 | 0 | N | n13 |
| older | darifenacin hydrobromide | duloxetine | 1 | 0 | N | n12 |
| older | darifenacin hydrobromide | fluoxetine | 1 | 0 | N | n12 |
| older | darifenacin hydrobromide | midazolam | 1 | 0 | N | n07 |
| older | darifenacin hydrobromide | paroxetine | 1 | 0 | N | n12 |
| older | desvenlafaxine | amphetamine | 1 | 0 | L | l01 l02 l03 l05 |
| older | dutasteride | cholestyramine | 1 | 0 | N | n05 |
| older | dutasteride | digoxin | 1 | 0 | N | n05 |
| older | dutasteride | tamsulosin | 0 | 1 |  | s01 s02 |
| older | dutasteride | terazosin | 0 | 1 |  | s01 s02 |
| older | dutasteride | warfarin | 1 | 0 | N | n05 |
| older | eribulin | ketoconazole | 1 | 0 | N | n11 |
| older | eribulin | rifampin | 1 | 0 | N | n11 |
| older | etravirine | nelfinavir | 1 | 0 | N | n14 |
| older | exenatide | warfarin | 1 | 0 | N | n07 |
| older | febuxostat | colchicine | 1 | 0 | N | n07 |
| older | febuxostat | desipramine | 1 | 0 | N | n07 |
| older | febuxostat | hydrochlorothiazide | 1 | 0 | N | n07 |
| older | febuxostat | indomethacin | 1 | 0 | N | n07 |
| older | febuxostat | naproxen | 1 | 0 | N | n07 |
| older | febuxostat | warfarin | 1 | 0 | N | n07 |
| older | methylnaltrexone bromide | dextromethorphan | 1 | 0 | N | n05 |
| older | raltegravir | estradiol | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | ethinyl estradiol | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | lamivudine | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | methadone | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | midazolam | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | ritonavir | 1 | 0 | HN | h01 n04 n07 |
| older | raltegravir | tenofovir disoproxil fumarate | 1 | 0 | HN | h01 n04 n07 |
| older | tocilizumab | methotrexate | 1 | 0 | N | n08 |
| older | trospium chloride | digoxin | 1 | 0 | N | n06 |

Audit sheet: label_audit_sheet.csv, 255 items ({'positive_oracle_below_0.5': 175, 'negative_oracle_above_0.5': 76, 'positive_rule_flag': 43}), shuffled with seed 42; the author fills author_label (yes, no or unsure) and notes. Scores are only in label_audit_key.csv. Nothing has been adjudicated.
