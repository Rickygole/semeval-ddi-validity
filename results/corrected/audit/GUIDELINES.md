# Label audit guidelines

You are checking whether pairs of drugs are listed as interacting on the novel drug's FDA label. Work on audit_sheet.csv only. Do not open answer_key.csv until both annotators have finished.

## Task

Each row has a novel drug and a partner drug. Open the openFDA label query link for the novel drug, read its Drug Interactions section (and Warnings, Contraindications and Clinical Pharmacology if needed), and decide whether the label says the novel drug interacts with the partner.

Fill in the columns annotator (your initials), interacts, basis and notes. Judge each row independently. Do not use your own pharmacology memory to add interactions the label does not state.

## interacts

- yes: the label states or clearly implies that taking the two together changes exposure or effect, or requires avoiding, monitoring or dose adjustment.
- no: the label does not mention the partner or its class in any interaction context, or explicitly reports no clinically relevant effect.
- unsure: the label is ambiguous and you cannot decide in a few minutes.

## basis

- named: the partner is named in the label in an interaction statement.
- class-level: the partner is not named, but a class it belongs to is, for example "strong CYP3A inhibitors" for ketoconazole. Mark interacts as yes only if the partner is clearly a member of that class under the label's own wording or a standard reference named in the label. Otherwise mark unsure.
- none: nothing in the label connects the two.

A statement that the partner was studied and showed no effect is interacts = no with basis = named.

## Cohen's kappa

Two annotators label every row independently. Drop rows where either marked unsure for the main figure and report how many were dropped, then also report kappa with unsure kept as its own category. Compute with ddiood.stats.kappa:

    from ddiood.stats import kappa
    kappa(list_of_annotator_1_interacts, list_of_annotator_2_interacts)

Then join answer_key.csv on item_id and compare each annotator, and their consensus, to the automatic label (1 = yes, 0 = no).
