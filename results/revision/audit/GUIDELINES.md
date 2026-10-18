# Two-annotator label audit

Built by `python scripts/audit_sheet.py`. Scored by `python scripts/audit_kappa.py` once both annotators have finished.

## Files

* `audit_sheet.csv`: the items. Each annotator works on a separate copy, saved as `annotator_1.csv` or `annotator_2.csv` in this folder.
* `answer_key.csv`: the FDA-derived label of each item. Annotators must not open it. Only `scripts/audit_kappa.py` reads it.
* `manifest.json`: sampling settings and SHA-256 hashes of the sheet, the key and the frozen pair file.

## Task

Each row names a novel drug and a partner drug. The row gives the novel drug's Drug Interactions section as stored in the local openFDA snapshot, and an openFDA query link to the full label. Decide whether the label says that taking the two drugs together calls for clinical action. Judge each row on its own, from the label only. Do not add interactions from memory or from other sources. Annotators work independently and do not discuss items.

Fill in four columns:

* `annotator`: your initials.
* `interacts`: `yes` if the label states or clearly implies that co-administration changes exposure or effect, or requires avoiding, monitoring or a dose change; `no` if the label does not mention the partner or a class it belongs to in an interaction context, or reports no clinically relevant effect; `unsure` if you cannot decide within a few minutes.
* `basis`: `named` if the partner is named in an interaction statement; `class-level` if only a class is named (for example "strong CYP3A inhibitors") and the label's own wording places the partner in it; `none` if nothing in the label connects the two. A partner that was studied and showed no effect is `interacts = no`, `basis = named`.
* `notes`: optional, for example the section or sentence you relied on.

## Scoring

`scripts/audit_kappa.py` reports Cohen's kappa on items where neither annotator chose `unsure` (with the number dropped), kappa with `unsure` as a third category, 95% bootstrap intervals over items, the annotator-by-annotator table, and the agreement of each annotator and of the consensus with the FDA label. Tier C is the set of items on which both annotators chose the same `yes` or `no`. There is no third rater; disagreements are excluded from tier C and counted.
