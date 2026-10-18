# Adjudication guidelines for the label audit sheet

Applies to `label_audit_sheet.csv` (255 items) and, with the same decision rule, to the Amendment 8 adjudication sample. Based on `results/revision/audit/GUIDELINES.md`.

This is an automated adjudication by an independent model adjudicator. It is not a human audit. Its results are a third automated source and are reported as such.

## What the sheet is

The sheet lists drug pairs from the frozen Novel and Older OOD sets whose labels are in question: 179 positives and 76 negatives. It is a list of suspect items, not a random sample, so the share of "no" answers on it says nothing about the whole set. Do not try to balance the answers.

## Inputs the adjudicator receives

Only these columns, in the shuffled order of the sheet: `item_id`, `ood_drug`, `partner`, `evidence`, `cooccurrence_sentence`, plus the drug's own Drug Interactions section as stored in `artifacts/amend7/di_sections.json` (the sheet itself does not carry it; the run attaches it for every item, positive or negative). The columns `current_label`, `rule_flag`, `context_note` and `cohort`, and everything in `label_audit_key.csv`, are withheld, because they reveal the label or a score. The adjudicator uses no tools, no memory of other sources and no information beyond the supplied text.

## Columns

* `item_id`: row identifier (A001 to A255); the order is a seeded shuffle.
* `cohort`: `older` or `novel`. Withheld from the adjudicator.
* `ood_drug`: the drug whose label is read (Drug A).
* `partner`: the SemEval vocabulary drug it is paired with (Drug B).
* `current_label`: 1 if the frozen set calls the pair an interaction, 0 if not. Withheld. It must not influence the answer.
* `evidence`: for a positive, the sentence or sentences of the Drug Interactions section that made the pair positive. It can contain section numbers and cross references in brackets; ignore them. It is empty for a negative.
* `cooccurrence_sentence`: a sentence from another label section (not the Drug Interactions section) in which the drug and the partner co-occur. Context only. It never makes an answer "yes" and is not a basis for a quote; if it contradicts the evidence, say so in `notes`.
* `context_note`: for negatives, the construction note that the partner is not named anywhere in the label. Withheld; it does not change the rule below, and the supplied section is the only text used.
* `rule_flag`: 1 if the post8 phrase screen fired on the evidence, 0 if not, empty for negatives. Withheld. It must not influence the answer.
* `author_label`: the answer, exactly `yes`, `no` or `unsure`. The column name is kept from the sheet; the adjudicator fills it.
* `notes`: required. A tag in square brackets, then a verbatim quote in double quotes from the supplied text: for example `[noeffect] "febuxostat does not have clinically significant interactions"`. Tags: `[named]` (a yes from a named partner), `[class]` (a yes through a class the text itself places the partner in), `[noeffect]`, `[lab]`, `[third]`, `[notstudied]`, `[absent]`, `[other]`. For a "no" with the partner (and any class listing it) absent from the supplied text, the quote is the fixed string `NO MENTION`. The quote is at most 300 characters and must be an exact substring of the supplied text after whitespace normalization; code checks this, and an item whose quote fails the check is scored `unsure`.

## The question

Does the drug's own Drug Interactions section state a clinically relevant interaction between this drug and this partner? Judge each item on its own, from the supplied text only. Do not add interactions from memory.

## The rule: yes, no, unsure

`yes`: the text states or clearly implies that using the two drugs together changes the exposure or the effect of either drug, or calls for avoiding the combination, monitoring, a dose change or a contraindication. The partner must be named, or named through a class that the text itself places the partner in (the text lists the partner as a member). A cautionary statement ("may increase", "potential interaction", "should be avoided") is a yes.

`no`: any of the following, and each is "no" even though the partner is named in an interaction section.

* No effect found. The two drugs were studied or considered and the text reports no effect or no clinically significant effect, for example "does not have clinically significant interactions", "did not affect", "no dose adjustment is required", "not expected to", "unaffected", "no precautions are necessary". A pharmacokinetic change that the text itself calls not clinically significant is also "no".
* Laboratory interference. The partner is named as an analyte of a test: a false-positive or false-negative result, an immunoassay, a urine drug screen, "interference with the assay". The partner is a test target, not a co-medication, so the answer is "no".
* A third drug's interaction. The sentence is about an interaction between the partner and some other drug, or the partner appears only in a list that belongs to another statement, and the text does not say the combination of this drug with the partner matters.
* Not studied. The text says the combination has not been studied or evaluated and says nothing more.
* Absent. The partner (and any class the text lists it in) is not in the supplied text. Class names alone ("strong CYP3A inhibitors") with no listing of the partner are not enough for "yes".

`unsure`: the text is truncated or garbled so that the role of the partner cannot be determined, the sentence supports both readings equally, or no verbatim quote can support either answer within a few minutes of reading. Do not use `unsure` to avoid a decision when a rule above applies.

Mixed sentences. If one clause states a no-effect for the partner and another clause states an interaction for the same partner with this drug, the answer is `yes` and the quote is the clause that states the interaction. If the only clause naming the partner is a no-effect clause, the answer is `no`, even if another clause names an interaction of a different drug. If the sentence says the partner is a strong inhibitor but that no precautions are necessary, the answer is `no`.

Negatives. The supplied section is the only text. If the partner or a listing class is absent, the answer is `no` with `NO MENTION`. If the section lists the partner as a member of a class with an interaction statement, the answer is `yes` and the quote is that text.

## Scoring

Agreement with the frozen labels is computed afterwards by code that reads `label_audit_key.csv`; the adjudicator never sees it. Items answered `unsure` are counted separately and in the primary agreement count as not confirming the frozen label. The result is reported as an automated check, with exact 95% intervals, and no claim of agreement with a human standard is made.
