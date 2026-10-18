# D7: human-gold check of the label rule against TAC 2018

Status: post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision.

Match rule: TAC label drug and OOD drug equal after lowercase and whitespace collapse (`rev3_tac.norm`); first-word overlap is a count only. Minimum: 5 overlapping drugs in a cohort. TAC labels with a Drug Interactions section: {'test1': 31, 'test2': 40}.

Check possible: False.

| cohort | OOD drugs | exact overlap | by TAC set | first-word overlap (count only) | check possible |
| --- | --- | --- | --- | --- | --- |
| novel | 48 | 0 | {'test1': 0, 'test2': 0} | 0 | False |
| older_clean | 128 | 4 | {'test1': 0, 'test2': 4} | 5 | False |
| older_primary | 121 | 4 | {'test1': 0, 'test2': 4} | 5 | False |

No cohort has at least the minimum number of overlapping drugs under the exact-name rule, so the check is not possible; no agreement figure was computed.

