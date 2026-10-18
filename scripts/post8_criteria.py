import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "revision" / "post8"
CRITERIA = OUT / "criteria.json"

LABEL = "post hoc and exploratory; changes no preregistered decision (H1, H4 and H6 stay inconclusive, H5 stays falsified, the Amendment 7 E8 oracle check stays failed)"

NONINTERACTION = [
    ["n01", r"\bno clinically (significant|relevant|meaningful|important)\b"],
    ["n02", r"\bnot clinically (significant|relevant|meaningful|important)\b"],
    ["n03", r"\bnot considered (to be )?clinically (significant|relevant|meaningful|important)\b"],
    ["n04", r"\bwithout (evidence of )?(a |any )?clinically (significant|relevant|meaningful|important)\b"],
    ["n05", r"\b(does|did|do) not (appear to )?(significantly )?(alter|affect|change|modify|impact|influence)\b"],
    ["n06", r"\bnot to (significantly )?(alter|affect|change|modify)\b"],
    ["n07", r"\b(does|did|do) not have (a |any )?(clinically )?(significant|meaningful|relevant|major|important)\b"],
    ["n08", r"\b(did|does|do) not detect any (effect|change|difference)\b"],
    ["n09", r"\bno (major |significant |meaningful |relevant |apparent |notable )?(effect|impact|change|difference|influence)s?\b"],
    ["n10", r"\black of (an? )?(\w+ )?(effect|interaction)"],
    ["n11", r"\b(were|was) not observed\b"],
    ["n12", r"\bno (dose|dosage|dosing) adjustments?\b"],
    ["n13", r"\b(does|do|did) not require (a |any )?(dose|dosage|dosing) adjustments?\b"],
    ["n14", r"\bwithout (a |any )?(dose|dosage|dosing) adjustments?\b"],
    ["n15", r"\bno meaningful\b"],
    ["n16", r"\bnot expected to\b"],
    ["n17", r"\bno (pharmacokinetic |pharmacodynamic |drug |clinically \w+ )?interactions?\b"],
    ["n18", r"\b(does|do|did) not interact\b"],
    ["n19", r"\bunaffected\b|\bnot (impacted|affected)\b"],
    ["n20", r"\bno precautions are necessary\b"],
]

LABTEST = [
    ["l01", r"\bdrug[- ]laboratory test"],
    ["l02", r"\blaboratory test interactions?\b"],
    ["l03", r"\bfalse[- ]positive"],
    ["l04", r"\bfalse[- ]negative"],
    ["l05", r"\bimmunoassay"],
    ["l06", r"\binterfere\w* with (the )?(\w+ ){0,3}(assay|test|measurement|determination)s?\b"],
    ["l07", r"\burine (drug )?screen"],
]

HEADING = [
    ["h01", r"\b(drugs|agents|medications)( with)? (without|with no) clinically (significant|relevant|meaningful|important) (drug )?interactions\b"],
    ["h02", r"\bno clinically (significant|relevant|meaningful) (drug )?interactions\b"],
]

ABSENCE = [
    ["s01", r"\b(has|have) not been (studied|evaluated|established|investigated)\b"],
    ["s02", r"\bnot been (studied|evaluated)\b"],
]

CLAUSE_SPLIT = r";|•|\s(?=(?:but|however|whereas|except)\b)|\s(?=(?:although|though|while)\b)"
CONCESSIVE = r"^(although|though|while)\b"
SUBSECTION = r"(?<![\d.(])\b\d{1,2}\.\d{1,2}\s+(?=[A-Z])"

CRITERIA_DOC = {
    "status": "written before any statistic of results/revision/post8 was computed and before the rule was applied to any score; " + LABEL,
    "written": "2026-10-17",
    "already_known_when_written": {
        "e8": "results/revision/amend7/e8.json: Qwen oracle Older-primary within-drug 0.957, 95% [0.921, 0.983] against a bar of 0.950 (fail); Novel 0.974 point (pass); redacted oracle Novel 0.731, Older-primary 0.682",
        "decisions": "results/revision/eval/decisions.md: H1 0.452, 90% [0.395, 0.509], 95% [0.389, 0.518], p_TOST 0.061, Holm 0.183; H1-novel 0.523 [0.397, 0.650]; H4 -0.071, p_TOST 0.339; H6 0.519 [0.393, 0.647], p_TOST 0.102",
        "kappa": "results/revision/amend7/cpu/kappa_weighting.md: H1 kappa -0.342, 95% [-0.794, 0.133], DrugBank within-drug 0.641",
        "e9": "results/revision/amend7/e9.json: panel of 20 checkpoints, Novel variance ratio 0.115",
        "reviewer_report": "142 of 648 Older positives with oracle P(yes) < 0.5; about 69 of 648 Older and 2 of 148 Novel positives flagged by the reviewer's regex; 52 negatives with oracle P(yes) > 0.5; per-checkpoint kappa upper bounds about -0.13 to 0.46",
        "what_was_read_before_writing": "the evidence column of the positives in results/corrected/ood_pairs.csv and ood_old_pairs.csv was read (text only, no score of any system) to draft the phrase list, including every positive evidence sentence that contains not, no, without, lack, unaffected, comparable, similar, neither, nor or false; the reviewer's examples were read; ddiood/ood.py shows that the pair builder already skipped sentences matching its own NULL_EFFECT pattern, which misses phrasings such as 'does not have clinically significant interactions'; no oracle score, no model score and no count of flagged items was looked at"
    },
    "rule": {
        "unit": "each positive (label 1) of both cohorts; the text is the evidence column (the Drug Interactions sentence that made the pair positive); the cooccurrence sentence comes from other label sections and is used only descriptively",
        "case": "all patterns are matched case-insensitively on whitespace-normalized text",
        "noninteraction_patterns": NONINTERACTION,
        "noninteraction_note": "covers the requested phrases: no clinically significant (n01), not clinically significant (n02), does not alter, does not affect, did not affect (n05), no effect (n09), lack of effect (n10), were not observed (n11), no dose adjustment (n12), without clinically significant (n04), no meaningful (n15), not expected to (n16); added before seeing scores, each justified by a sentence read in the evidence column: does not have clinically significant interactions (n07, febuxostat), did not have a significant impact or effect (n07, darifenacin, exenatide), not considered clinically relevant (n03, etravirine), not to affect (n06, trospium), did not modify (n05), did not detect any effect (n08, tocilizumab), no major impact (n09, bedaquiline), without evidence of a clinically meaningful (n04, belimumab), does not require a dosage adjustment (n13, dabigatran), without dose adjustments (n14, etravirine), no pharmacokinetic interaction (n17, ozanimod), does not interact (n18), unaffected or not affected (n19), no precautions are necessary (n20, rivaroxaban)",
        "labtest_patterns": LABTEST,
        "labtest_note": "laboratory or urine test interference: the partner is an analyte of a test, not a co-medication",
        "heading_patterns": HEADING,
        "heading_scope": "a heading pattern fires when it matches the evidence sentence itself or the heading of the Drug Interactions subsection that contains the evidence sentence; the subsection heading is the text from the last subsection number (regex SUBSECTION) before the evidence sentence, within the drug's Drug Interactions section in artifacts/amend7/di_sections.json, up to the evidence sentence and at most 300 characters; the evidence is located by exact match after whitespace normalization, else by its first 80 characters, else the heading part is not evaluated",
        "subsection_regex": SUBSECTION,
        "not_patterns": "phrases that state an interaction or a precaution are not non-interaction phrases: not recommended, should not, do not exceed, do not co-administer, do not use, not be used; none of them matches a pattern above",
        "scope": "the sentence is split into clauses at semicolons, bullets, and before but, however, whereas, except, although, though and while (regex CLAUSE_SPLIT); a clause that starts with although, though or while is further split at its first comma; a clause names the partner when any surface form of the partner (ddiood.amend7_evidence.partner_forms over artifacts/amend7/lookup.json, matched with ddiood.textnorm.mentions) occurs in it",
        "clause_regex": CLAUSE_SPLIT,
        "concessive_regex": CONCESSIVE,
        "flag": "a positive is flagged (rule flag = 1) when the heading rule fires, or when at least one clause names the partner and every clause that names the partner matches a non-interaction or a laboratory-test pattern; a clause naming the partner without such a phrase (for example 'coadministration with warfarin increases the risk of bleeding') vetoes the flag",
        "partner_not_located": "if no clause names the partner, the whole sentence is treated as one clause and the flag records scope 'sentence'",
        "families": {"N": "non-interaction (n01 to n20)", "L": "laboratory test (l01 to l07)", "H": "heading (h01, h02)"},
        "secondary_absence_family": {"patterns": ABSENCE, "use": "absence-of-evidence statements ('has not been evaluated'); same clause scope; reported, NOT dropped in tier C-auto, dropped only in the broader sensitivity tier C-auto-broad"},
        "secondary_descriptive": {"ood_drug_not_named": "the OOD drug's name (the full name or its first token of at least 4 letters) is absent from the evidence sentence; a crude marker of a sentence about a third drug's partners (e.g. the probenecid sentence of cidofovir); reported only, never dropped, because labels often use brand names",
                                  "cooccurrence_also_flags": "the N or L rule applied to the cooccurrence sentence with the same clause scope; reported only"},
        "precision_stance": "the rule is written for precision, not recall: it does not claim to find every label error (for example a concessive 'although clarithromycin is a strong inhibitor, no precautions are necessary' names the partner only in the concessive clause and is not flagged); every positive that Qwen rejects is on the author's audit sheet whatever the rule says"
    },
    "screen_counts": {
        "rule_flags": "count of flagged positives per cohort (Novel 148 positives, Older 648 positives; also Older-clean and Older-primary), per family, per drug; the drugs with the most flags are listed",
        "oracle_rejections": "count of positives with Qwen oracle P(yes) < 0.5 per cohort (runs/preds/a7-qwen-oracle.json, eval ood and oodold, row order checked against the frozen sets by the ood_hash and ood_old_hash fields and by the context partner_in_context vector matching the labels)",
        "negatives_accepted": "count of negatives with oracle P(yes) > 0.5 per cohort",
        "cross_tab": "flag by oracle rejection, per cohort"
    },
    "audit_sheet": {
        "rows": "every positive (both cohorts) with oracle P(yes) < 0.5 or a rule flag, and every negative with oracle P(yes) > 0.5",
        "columns": ["item_id", "cohort", "ood_drug", "partner", "current_label", "evidence", "cooccurrence_sentence", "context_note", "rule_flag", "author_label", "notes"],
        "author_columns": "author_label (interacts yes, no or unsure) and notes are empty; no score and no flag in them",
        "order": "shuffled with numpy RandomState(42).permutation",
        "key_file": "label_audit_key.csv carries item_id, the oracle P(yes), the rule flag, families, matched patterns, scope and the reason the item was selected; no adjudication is fabricated"
    },
    "tier_c_auto": {
        "definition": "tier A with every positive that carries a rule flag (families N, L or H) removed; all negatives kept",
        "tier_c_auto_broad": "tier C-auto with the absence-of-evidence positives also removed; reported for the E8 oracle rule and the H1, H1-novel, H4 and H6 rows only",
        "label": "sensitivity; the primary analyses on tier A stay primary and are shown next to every C-auto value"
    },
    "primary_reanalysis_targets": {
        "H1": "b2mixed (seed mean over 42, 1, 2, 3, 4, oodold_empty), Older-clean, within-drug AUROC with the two-way bootstrap (seed 42, 1,000 draws, drug copies as strata, as ddiood.evaluate2), 90% and 95% intervals, p_TOST against [0.40, 0.60], and the kappa against the DrugBank lookup with paired draws and its 95% interval",
        "H1-novel": "the same on Novel (ood_empty), seed 1042",
        "H6": "krag hybrid k5 c400 (ood), Novel, seed 1042, p_TOST and kappa",
        "H4": "Older-clean minus Novel draws, p_TOST against +/- 0.10; Holm over H1, H4 and H6 recomputed on C-auto; the decision text of ddiood.evaluate2.decide_equivalence applied to the C-auto values is reported as a would-be label, not a decision",
        "E8_oracle_rule": "ddiood.amend7_analysis.oracle_rule unchanged on C-auto rows: bar = max(0.90, grep within-drug AUROC on the same rows - 0.05); Older-primary uses the 95% lower bound, Novel the point estimate; bootstrap seeds Novel 1042, Older 42",
        "E7_arms_c_d_e": "ddiood.amend7_analysis.knowledge_arms and add_kappas unchanged on C-auto rows (Novel, Older-primary, Older-clean; tiers A and B); the arm label rule (signal, no signal, neither) is reported for primary and C-auto",
        "E9": "per-checkpoint within-drug AUROC and 95% upper bound on Older-primary and Novel, from ddiood.amend7_panel.panel_stats on C-auto rows; count of upper bounds at most 0.60",
        "DrugBank_lookup": "within-drug AUROC with the two-way interval (paired draws as H1) and pooled AUROC with ddiood.evaluate2.boot_auroc over drugs and partners (seed 42), for Novel, Older full, Older-clean and Older-primary"
    },
    "e9_additions": {
        "semeval_f1": "per checkpoint, ddiood.metrics.binary_f1 of eval test_sentence preds against SemEval test labels label_id != 0, exported",
        "paired_within_reference": "on the shared two-way draws of panel_stats, for every pair of checkpoints i < j, Var_b(A_i - A_j) (ddof 1); the within reference is the mean over pairs of Var_b(A_i - A_j) / 2, which is the bootstrap variance of a single model with the covariance shared by all models removed; ratio = between-checkpoint variance of point estimates (ddof 1) / that reference; the old ratio (mean single-model bootstrap variance) is shown beside it",
        "kappa_bounds": "per checkpoint, kappa_b = (A_i,b - 0.5) / (D_b - 0.5) with D_b the DrugBank lookup within-drug AUROC on the same draw and rows; point kappa and the 95% interval (2.5 and 97.5 percentiles); reported on Older-primary and Novel, tier A, and on C-auto",
        "seeds": "panel_stats seeds (Novel 1042, Older-primary 42); the draw loop is reproduced so that the per-checkpoint upper bounds equal results/revision/amend7/e9.json"
    },
    "redacted_confound": {
        "reconstruction": "the redacted-oracle evidence of every row is rebuilt with ddiood.amend7_evidence.EvidenceBuilder (condition redacted) from artifacts/amend7/di_sections.json and artifacts/amend7/lookup.json with the Qwen2.5-7B-Instruct tokenizer and the 6,000-token cap; the reconstruction is accepted only if the mean prompt token count reproduces the answer.tokens_mean of runs/preds/a7-qwen-redactedoracle.json within 0.01",
        "lengths": "per row, Qwen tokens of the evidence as fed (after redaction and truncation) and characters; per row, tokens removed relative to the unredacted oracle evidence",
        "by_class": "mean and median tokens and tokens removed by class, per cohort (Novel, Older-primary); per drug, the mean negative length minus the mean positive length, summarized over drugs",
        "within_auroc": "within-drug AUROC of the score -tokens (shorter context ranks higher) with the two-way bootstrap (Novel 1042, Older-primary 42), tier A and C-auto; beside it the redacted Qwen within-drug AUROC and the paired difference Qwen minus length on shared draws",
        "reading": "if the length-only AUROC is at least the redacted Qwen AUROC, the above-chance redacted result cannot be read as knowledge without a length control; no decision rule is attached"
    },
    "what_counts_as_a_changed_conclusion": "a conclusion changes when the same rule applied to C-auto gives a different label from the primary: E8 pass or fail; H1 and H6 supported, inconclusive or falsified (would-be); E7 arm labels; the number of E9 checkpoints with an upper bound at most 0.60; for estimates without a rule, the shift is reported without a label"
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if CRITERIA.exists() and not a.force:
        raise SystemExit(f"{CRITERIA} exists; criteria are written once")
    OUT.mkdir(parents=True, exist_ok=True)
    CRITERIA.write_text(json.dumps(CRITERIA_DOC, indent=1) + "\n")
    print(CRITERIA)


if __name__ == "__main__":
    main()
