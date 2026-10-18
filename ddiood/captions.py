import re

AMEND = "Amendment 7 results (E7, E8, E9 and the CPU and post hoc analyses that follow it) are post hoc and exploratory and change no planned decision."
NONE7 = "This figure shows no Amendment 7 result; Amendment 7 results elsewhere are post hoc and exploratory."
C8 = ("OOD labels are unvalidated label mentions (the E8 oracle check failed); OOD AUROC measures agreement with that "
      "target, not interaction knowledge.")
SAMPLING = ("SemEval intervals are one-way cluster bootstrap over sentences, OOD intervals two-way cluster bootstrap over OOD "
            "drugs and partner drugs, 1,000 draws.")


def intervals(D):
    lo, hi = D["margin"]
    return (f"The gray band (equivalence margin {lo:.2f} to {hi:.2f}) and the thick 90% bars are drawn only for the H1 "
            f"primary cell, Mixed-input BiomedBERT on Older-clean, within-drug; every other mark has a 95% whisker only. "
            f"{SAMPLING}")


def f3(x):
    return f"{x:.3f}"


def ci(c, level="95"):
    return f"[{c['lo' + level]:.3f}, {c['hi' + level]:.3f}]"


def rng(vals, digits=3):
    lo, hi = min(vals), max(vals)
    return f"{lo:.{digits}f}" if f"{lo:.{digits}f}" == f"{hi:.{digits}f}" else f"{lo:.{digits}f} to {hi:.{digits}f}"


def pct(x):
    return f"{100 * x:.0f}%"


def entry(name, title, caption, sources, D=None):
    if D is not None and D.get("ood_cohorts", {}).get(name):
        caption = caption.rstrip() + " " + D.get("commitment8", C8)
    out = [f"### {name}.pdf / .png ({title})", "", f"**Caption draft.** {caption}", "", "**Sources.**"]
    out += [f"- {s}" for s in sources]
    return "\n".join(out) + "\n"


def fig1(D):
    v, d = D["fig1_values"], D["fig1_panel_d"]
    pf, nd = d["novel | Partner-frequency prior"], d["novel | Novel-drug prior"]
    po, no = d["older | Partner-frequency prior"], d["older | Novel-drug prior"]
    panel = (f"; the E9 panel adds {v['PanelModels']} models over {v['PanelBackbones']} backbones"
             if "PanelModels" in v else "")
    cap = (f"Study design. Every system receives only the names of two drugs that SemEval never contains, and "
           f"partner-matched negatives remove the popularity shortcut that random negatives create (D). (A) Encoders are "
           f"trained on {v['TrainPairs']} SemEval 2013 training pairs in four regimes and three backbones{panel}. (B) Novel "
           f"drugs (first FDA approval {v['NovelFrom']} to {v['NovelTo']}, {v['NovelDrugs']} drugs, {v['NovelPairs']} pairs) "
           f"and Older drugs ({v['OlderFrom']} to {v['OlderTo']}, {v['OlderDrugs']} drugs, {v['OlderPairs']} pairs). Two "
           f"Older subsets recur: Older-clean ({v['OlderCleanDrugs']} drugs) for the H1 decisions, and Older-primary "
           f"({v['OlderPrimaryDrugs']} drugs) for the Amendment 7 analyses. A pair is positive when the partner is named "
           f"under Drug Interactions in the drug's label; this is a label mention, not a validated interaction (E8 oracle "
           f"check). (C) The same name pair, for example {v['ExampleChip'].replace(' $+$ ', ' + ')}, goes to every "
           f"system. (D) Pooled AUROC of two shortcut baselines: with random negatives the partner-frequency prior reaches "
           f"{f3(pf['random'])} (Novel) and {f3(po['random'])} (Older); partner matching brings it to "
           f"{f3(pf['partner_matched'])} and {f3(po['partner_matched'])}, at the cost of a novel-drug prior of "
           f"{f3(nd['partner_matched'])} and {f3(no['partner_matched'])} (against {f3(nd['random'])} and "
           f"{f3(no['random'])} with random negatives). Panel D is pooled because a drug-level prior is constant within a "
           f"drug; the dashed line is chance. The Drug Interactions section is held out from retrieval except in the "
           f"positive controls; the analysis plan is private and version-controlled, and every amendment is disclosed. Baselines are "
           f"deterministic. {NONE7}")
    src = ["Flow diagram: `paper/figures/pipeline.tex`, compiled by `ddiood.paperfigs2 --compile`; every count is a macro "
           "in `paper/figures/pipeline_values.tex`, written by `ddiood.paperfigs2` from `semeval.load_pairs('train')`, "
           "`results/corrected/ood_summary.json` and `ood_old_summary.json` (counts asserted against "
           "`eval/drugbank_lookup.json` rows `novel` and `older_full`); Older-clean from `eval/drugbank_lookup.json` row "
           "`older_clean`, Older-primary from `post7/classshortcut/classshortcut.json` `older_primary:A.n_drugs`, the panel "
           "size from `amend7/e9.json` `e9.panel.older_primary` (`n_models`, backbones from the job names).",
           "Panel D (`fig1_panel_d.pdf`): `results/corrected/baselines.json`, `{novel, older}_random_negatives` and "
           "`{novel, older}`, `baselines.{partner_frequency_prior, novel_drug_prior}.auroc`; the partner-matched values "
           "are asserted against `eval/tables.json`, `baselines`.",
           "Example pair: asserted to be in the Novel set (`results/corrected/ood_pairs.csv`)."]
    return entry("fig1_study_design", "main text, Figure 1", cap, src, D)


def fig2(D):
    s = D["fig2_dissociation"]["series"]
    enc, db, qw, bm = s["Mixed-input BiomedBERT"], s["DrugBank lookup"], s["Qwen2.5-7B"], s["BioMistral-7B"]
    ex = db["left_excl"]
    ghosts = [v for k, v in s.items() if k not in ("Mixed-input BiomedBERT", "DrugBank lookup", "Qwen2.5-7B", "BioMistral-7B")]
    b = {r["name"]: r for r in D["fig2_dissociation"]["panel_b"]}
    neg, pos = b["SemEval negatives"], b["SemEval positives"]
    cross = (enc["right"]["value"] < enc["left"]["value"] and db["right"]["value"] > ex["value"]
             )
    if cross:
        first = (f"Against the same name-only input, systems trained on SemEval labels and systems that do not use them "
                 f"rank pairs in opposite orders on the two targets: Mixed-input BiomedBERT falls from "
                 f"{f3(enc['left']['value'])} to {f3(enc['right']['value'])} when the target changes from SemEval "
                 f"annotations to FDA label mentions, while a DrugBank lookup rises from {f3(ex['value'])} "
                 f"({f3(db['left']['value'])} with self-pairs) to {f3(db['right']['value'])}.")
    else:
        first = (f"Changing the target from SemEval annotations to FDA label mentions moves Mixed-input BiomedBERT from "
                 f"{f3(enc['left']['value'])} to {f3(enc['right']['value'])}; the DrugBank lookup scores "
                 f"{f3(ex['value'])} ({f3(db['left']['value'])} with self-pairs) and {f3(db['right']['value'])}, so the "
                 f"two kinds of system do not order the pairs in opposite ways.")
    rr = qw["right"]["range"]
    seen = D["fig2_dissociation"]["seen"]
    mt = D["fig2_dissociation"]["panel_b_random"]
    cap = (f"{first} (A) Left column: AUROC on the {pos['n'] + neg['n']:,} SemEval test pairs against SemEval labels, "
           f"names only; pooled AUROC with one-way sentence intervals. The DrugBank lookup starts at {f3(ex['value'])} "
           f"{ci(ex)} (filled black diamond) on the {ex['n']:,} pairs left after removing the {ex['n_self_pairs']} self-pairs, "
           f"which name one drug twice and are all SemEval negatives; the small gray open diamond is {f3(db['left']['value'])} "
           f"{ci(db['left'])} on all pairs. Middle column: within-drug AUROC on Novel plus Older-clean "
           f"({D['fig2_dissociation']['unseen_pairs']:,} pairs, {D['fig2_dissociation']['unseen_drugs']} drugs) against FDA "
           f"label mentions, the H1-pooled estimator, {ci(enc['right'], '95')} (95%) for the encoder. Both columns are stored "
           f"models, joined by lines except Qwen2.5-7B, which is not joined because its SemEval value "
           f"({f3(qw['left']['value'])}) and its Older-primary range are on different cohorts; they mix pooled (SemEval) and within-drug (OOD) AUROC and differ in both drugs and label "
           f"source, and panel B is the evidence that the label source matters. Qwen2.5-7B is drawn unconnected, as the planned names-only "
           f"range over {qw['right']['n_prompts']} frozen prompts on the Older-primary cohort ({qw['right']['n_drugs']} drugs, named beside the range in the artwork), {rr[0]:.3f} to {rr[1]:.3f} "
           f"(primary prompt {f3(qw['right']['value'])}, not robust), because the E8 names-only cells exist per cohort; the "
           f"other systems are pooled over Novel plus Older-clean. BioMistral-7B (thin line) goes from {f3(bm['left']['value'])} "
           f"to {f3(bm['right']['value'])}, falling rather than rising. The {len(ghosts)} other encoder configurations (light "
           f"lines) score {rng([g['left']['value'] for g in ghosts])} on SemEval pairs and "
           f"{rng([g['right']['value'] for g in ghosts])} on unseen drugs. Right column, separated by a rule and not "
           f"connected to the others: the seen-drug pairs ({seen['n_pairs']:,} pairs), scored with encoders retrained "
           f"without those pairs (R2a): Mixed-input BiomedBERT {f3(seen['b2mixed']['value'])}, Sentence-trained BiomedBERT "
           f"{f3(seen['b2sentence']['value'])}, DrugBank lookup {f3(seen['drugbank']['value'])}. Colour follows the label a "
           f"system was built on, as in every figure: blue for SemEval-trained encoders, vermilion for prompted LLMs, black for "
           f"the DrugBank lookup. (B) Counts are SemEval test instances, not distinct pairs. Among SemEval test negatives without self pairs DrugBank lists {neg['listed']:,} of the "
           f"{neg['n_resolvable']:,} instances with a drug resolved ({f3(neg['share_of_resolvable'])}, Wilson 95% "
           f"[{neg['wilson95_resolvable'][0]:.3f}, {neg['wilson95_resolvable'][1]:.3f}]), against {pos['listed']} of "
           f"{pos['n_resolvable']} positives ({f3(pos['share_of_resolvable'])}, "
           f"[{pos['wilson95_resolvable'][0]:.3f}, {pos['wilson95_resolvable'][1]:.3f}]); the dashed line is the rate for "
           f"{mt['n_resolvable']:,} random vocabulary pairs, {f3(mt['share'])}. The comparison with random pairs is "
           f"confounded by co-mention; in DDI-MedLine abstracts alone, without self pairs, the rates are {f3(neg['medline_share_of_resolvable'])} "
           f"for negatives and {f3(pos['medline_share_of_resolvable'])} for positives. Encoders average 5 seeds; LLMs "
           f"are single 4-bit runs. Whiskers are 95%. {SAMPLING} The DrugBank lookup on SemEval pairs is Amendment 7 experiment 5, and "
           f"the self-pair exclusion is a post hoc sensitivity analysis. {AMEND}")
    src = ["Encoder left column: `eval/tables.json`, `seeds`, `test_empty` (`test_names` for Names-trained), intervals "
           "computed by `ddiood.paperfigs` (one-way by sentence).",
           "Right column: recomputed by `ddiood.paperfigs2` with `evaluate2.within_stat` on Novel plus Older-clean; for "
           "`b2mixed/biomedbert` value, 90% and 95% bounds are asserted equal to `eval/decisions.json` `H1-pooled`; every "
           "cohort component is asserted against `eval/tables.json` `ood_cohorts` `auroc_within`.",
           "DrugBank lookup, left: `amend7/cpu/exp5_dissociation.json`, `auroc[0]` (asserted equal to `grid_2x2`). Open "
           "marker: `sensitivity/semeval_selfpairs.json`, row `excluding self pairs`, asserted equal to the same row of "
           "`exp5_dissociation.json` `auroc` (point, interval and n), with its all-pairs row asserted equal to `auroc[0]` "
           "and `self_pairs_positive` asserted 0. Right: scores from `artifacts/ood/drugbank_validation*.csv`; cohort "
           "components asserted against `eval/drugbank_lookup.json` `auroc_within` and `auroc`, the pooled point against "
           "`amend7/cpu/kappa_weighting.json` `H1-pooled.drugbank_within`.",
           "Qwen and BioMistral: `eval/tables.json` `seeds`, `names/qwen` and `names/biomistral`, key `test`; Qwen interval "
           "asserted against `exp5_dissociation.json` `grid_2x2`.",
           "Qwen unseen-drug range: `amend7/e8.json`, `e8_names.cohorts.older_primary` (primary prompt, min, max, robust), "
           "asserted against the five per-prompt values and against the stated 0.519 to 0.607.",
           "Seen-drug column: `rev2_colab/r2a.json` and `rev3/c2_seen_reference.json`.",
           "Panel B MedLine note: `rev3/d9_listing_conventions.json`, `self_pairs_excluded` instances, scope DDI-MedLine "
           "(negatives 0.515, positives 0.577), asserted against the stated values and the 289 self pairs.",
           "Panel B: `rev2/m3b_drugbank.json`, `listing_rates`, rows without self pairs, MedLine rows and the random "
           "vocabulary pairs; shares and Wilson intervals recomputed from the counts and asserted against the stored "
           "values, and against `by_source` (TPR, FPR) and `semeval_selfpairs.json` (289 self pairs)."]
    return entry("fig2_dissociation", "main text, Figure 2, hero", cap, src, D)


def fig3(D):
    t = D["fig3_encoders"]
    sent = [v["value"] for k, v in t.items() if "| Sentence |" in k or "| Sentence, both" in k]
    ood = {k: v for k, v in t.items() if "Novel" in k or "Older-clean" in k}
    novel_mix = t[[k for k in ood if k.startswith("BiomedBERT | Novel") and k.endswith("Mixed-input")][0]]
    old_mix = t[[k for k in ood if k.startswith("BiomedBERT | Older-clean") and k.endswith("Mixed-input")][0]]
    names = [v["value"] for k, v in t.items() if "| Names only |" in k]
    cap = (f"Without the sentence, SemEval-trained encoders agree with FDA label mentions on unseen drug pairs at "
           f"within-drug AUROC {rng([v['value'] for v in ood.values()])} in all three architectures, against {rng(sent)} "
           f"when the sentence is given (original or pseudo-word sentence). Rows: the SemEval test sentence, the same "
           f"sentence with both names replaced by pseudo-words, SemEval pairs by name only ({rng(names)}), and names only "
           f"for Novel and Older-clean drugs. The H1 primary system (Mixed-input BiomedBERT) is {f3(old_mix['value'])}, "
           f"90% {ci(old_mix, '90')}, on Older-clean and {f3(novel_mix['value'])}, 90% {ci(novel_mix, '90')}, on Novel. "
           f"Names-trained models take no sentence, so they have no mark in the first two rows. Markers as in Figure 1A "
           f"(circle Sentence-trained, filled square Mixed-input, open triangle Names-trained); all marks are SemEval-label "
           f"systems. BiomedBERT averages 5 seeds; BERT-base 5 seeds except Names-trained (1 seed); BioBERT 1 seed. The "
           f"dashed line is chance. {intervals(D)} {NONE7}")
    src = ["SemEval rows: `eval/tables.json`, `seeds`, keys `test_sentence`, `swap_pseudo_sentence`, `test_empty` "
           "(`test_names` for Names-trained); intervals computed by `ddiood.paperfigs` and checked point by point.",
           "Unseen-drug rows: recomputed with `evaluate2.within_stat` (seed 1042 Novel, 42 Older) and asserted equal to "
           "`eval/tables.json` `ood_cohorts`, tier A, cohorts `novel` and `older_clean`, fields `auroc_within`, `lo90`, "
           "`hi90`, `lo95`, `hi95`."]
    return entry("fig3_encoders", "main text, Figure 3", cap, src, D)


def fig4(D):
    t = D["fig4_sentence_signal"]
    A, B, C = t["A"], t["B"], t["C"]
    sw = [v["value"] for lab in ("Sentence-trained", "Mixed-input") for k, v in A[lab].items() if k != "orig"]
    no = A["Names-trained"]
    m = B["Masked-trained"]
    held = [t["held_out_cost"][k] for k in ("Sentence input, Sentence-trained", "Sentence input, Mixed-input")]
    cap = (f"The sentence carries the signal. (A) Replacing both drug names with other SemEval drugs, Novel drugs or "
           f"pseudo-words leaves the sentence readers at AUROC {rng(sw)}, while the Names-trained model falls from "
           f"{f3(no['orig']['value'])} to {rng([no[k]['value'] for k in ('vocab', 'novel', 'pseudo')])}. (B) Binary F1, "
           f"names visible and masked, one line per seed: masking the names at test time removes the Sentence-trained "
           f"model's F1 (H2a {B['Sentence-trained']['decision']}), and a model trained with the names masked keeps it "
           f"(H2b {m['decision']} under the seed-mean rule, which was not in the plan; median masked to unmasked ratio "
           f"{m['median_text']}, seeds {m['range_text'][0]} to {m['range_text'][1]}; the seed-1 ratio is driven by an "
           f"unmasked F1 near zero). (C) Drug-disjoint training: each arrow runs from the model scored with all drugs seen "
           f"(open marker, drawn slightly lower in the row, with its own 95% whisker) to the same model on pairs with a held-out "
           f"drug (filled marker, drawn slightly higher, with its own whisker); "
           f"held-out drugs cost the sentence readers {rng(held)} AUROC. A and B average 5 seeds; C is seed 42. "
           f"Whiskers are 95% intervals clustered by sentence; the dashed line is chance, and no equivalence test applies "
           f"here. {NONE7}")
    src = ["A: `eval/tables.json`, `seeds`, `test_{sentence,names}` and `swap_{vocab,novel,pseudo}_{sentence,names}`; "
           "intervals computed by `ddiood.paperfigs`.",
           "B: `eval/tables.json`, `masking` (`f1_sentence`, `f1_masked`, `ratio`); decisions and the median and range "
           "from `eval/decisions.json` `H2a` and `H2b` (asserted against the per-seed ratios). The mean ratio is not shown.",
           "C: `eval/tables.json`, `disjoint`, seed 42, subsets `seen` and `unseen` (asserted point and n)."]
    return entry("fig4_sentence_signal", "main text, Figure 4", cap, src, D)


def two(p):
    return f"{f3(p[0]['value'])} (Novel) and {f3(p[1]['value'])} {ci(p[1])} (Older-primary)"


def fig5(D):
    t = D["fig5_positive_controls"]
    g = lambda c, lab: t[f"{c} | {lab}"]
    key = lambda prefix: [k.split(" | ")[1] for k in t if k.startswith("novel | " + prefix) and k.count(" | ") == 1][0]
    e7a, e7b, ora = key("E7a"), key("E7b"), key("E8 oracle")
    a = g("novel", e7a)
    rule = t["e7a_rule"]
    thr = t[f"novel | {e7a} | threshold"]
    ideal = t[f"novel | {e7a} | ideal reader"]
    word = lambda ok: "pass" if ok else "fail"
    bn, bo = g("novel", e7b), g("older_primary", e7b)
    on, oo = g("novel", ora), g("older_primary", ora)
    orule = t["e8_oracle_rule"]
    bar_n, bar_o = orule["novel"]["bar"], orule["older_primary"]["bar"]
    regex = orule["older_primary"]["grep"]
    ctrl = {lab: (g("novel", lab), g("older_primary", lab)) for lab in
            ("Name-masked oracle", "Wrong drug's section", "Partner sentences removed (confounded)")}
    sens = t["sensitivity"]
    sens_drop = re.search(r"(\d+) Older-primary", sens["label"]).group(1)
    can, cao = g("novel", sens["label"]), g("older_primary", sens["label"])
    red = "Partner sentences removed (confounded)"
    red_len = t.get(f"older_primary | {red} | length only")
    db = (g("novel", "DrugBank lookup"), g("older_primary", "DrugBank lookup"))
    mix = (g("novel", "Mixed-input BiomedBERT, names only"), g("older_primary", "Mixed-input BiomedBERT, names only"))
    h5 = key("H5")
    h5c = g("novel", h5)
    cap = (f"Integrity and oracle controls for the label-mention target. Trained on the label-mention targets, "
           f"BiomedBERT scores within-drug AUROC {f3(bn['value'])} on Novel and {f3(bo['value'])} on Older-primary when "
           f"the answer is placed in its input (E7b). E7b and the regex baseline score 1.000 by construction, because the "
           f"labels were defined by the same text match; they show the rule was applied consistently, not that it is "
           f"correct. E7a, the H5 input with label-mention targets, reaches pooled AUROC {f3(a['value'])} {ci(a)} against "
           f"the {thr:.2f} threshold: {word(rule['auroc'] >= rule['thresholds'][0])} on AUROC, "
           f"{word(rule['mcc'] >= rule['thresholds'][1])} on MCC ({f3(rule['mcc'])} against {rule['thresholds'][1]:.2f}); "
           f"an ideal reader of the same input reaches pooled {f3(ideal)} (gray open circle on the E7a row, legend ideal reader (E7a), {f3(ideal)}). Given its own Drug "
           f"Interactions section, Qwen2.5-7B scores {f3(on['value'])} on Novel, where the rule is a point rule at "
           f"{bar_n:.2f}, and {f3(oo['value'])} {ci(oo)} on Older-primary, where the rule needs the 95% lower bound to "
           f"reach {bar_o:.3f}: the lower bound is {f3(oo['lo95'])}, so the pre-specified E8 oracle check "
           f"{orule['decision']}s and tier A stays primary. On a post hoc corrected tier (C-auto, with the {sens_drop} flagged Older-primary positives dropped; gray label, "
           f"open marker) the oracle scores {f3(can['value'])} and {f3(cao['value'])} {ci(cao)}, and the check would "
           f"{sens['decision']}; this is a sensitivity analysis only, and tier A stays primary. Oracle controls: "
           f"name-masked {two(ctrl['Name-masked oracle'])}, wrong drug's section " + two(ctrl["Wrong drug's section"])
           + f", partner sentences removed {two(ctrl[red])}; the redacted arm is confounded, because removing the "
           f"partner sentences shortens only the positives' context and context length alone ranks the pairs at "
           f"within-drug AUROC {f3(red_len) if red_len is not None else 'n/a'} (gray tick), so it is not read as "
           f"evidence. SemEval-label rows: Mixed-input BiomedBERT {two(mix)}; the H5 control (pooled, Novel, open "
           f"pentagon) {f3(h5c['value'])} {ci(h5c)} against {t[f'novel | {h5} | threshold']:.2f}, "
           f"{h5.split(': ')[1]}. External reference: DrugBank lookup {two(db)}. Black ticks mark a pass threshold or "
           f"bar; gray ticks mark the regex baseline (oracle) and the length-only score (redacted), both 1.000 because they "
           f"separate the labels perfectly, and the gray open circle marks the ideal reader (E7a). H5 and E7a were not run on Older-primary, and that panel prints not run at 0.5 on their rows. Whiskers are 95% two-way cluster bootstrap intervals over OOD drugs and partners, 1,000 draws; "
           f"the dashed line is chance, and no equivalence test applies in this figure. E7a and H5 are pooled AUROC; "
           f"every other row is within-drug, tier A. E7 arms average 5 seeds; Qwen is a single run. The pair-label arms "
           f"(E7c to E7e), the Qwen arms without the answer, the DrugBank operating-point comparison and the stem control "
           f"are in Figure S5. The E9 'no pair signal' and E7 'signal' labels are superseded by Commitment 8. {AMEND}")
    src = ["E7a and E7b: `amend7/e7.json` (`e7a.pooled_auroc`, `e7a.mcc_majority_vote`, `e7a.thresholds`, "
           "`e7b.{novel,older_primary}.within`); point estimates recomputed from the `a7-e7*` predictions with "
           "`amend7_analysis.seed_average` and `point`; the E7a decision is asserted to follow from both thresholds, and "
           "E7b is asserted to be 1.000 before the by-construction label is printed.",
           "Ideal reader tick: `sensitivity/control_ideal_reader.json`, contaminated, `ideal_reader.auroc_pooled`.",
           "E8: `amend7/e8.json`, `e8_oracle_rule` (bar, statistic, regex baseline, decision; the Older-primary rule is "
           "asserted to be the lower-bound rule), `e8_evidence.{masked,wrong,redacted}.{cohort}/A.within`; point "
           "estimates recomputed from the `a7-qwen-*` predictions.",
           "Mixed-input row: `classshortcut.json` `systems.b2mixed`, recomputed with `amend7_analysis.estimate` and asserted "
           "equal, point and both intervals. H5: `eval/decisions.json` `H5`.",
           "DrugBank row: `classshortcut.json` `drugbank_operating_point.drugbank_auroc_from_placements`, asserted against "
           "`e7.json` `drugbank_within` and `eval/drugbank_lookup.json`.",
           "C-auto oracle row: `post8/sensitivity.json` `e8.C-auto`; tier A values asserted against `e8.A`. Redacted "
           "confound tick: `post8/redacted_confound.json` `tiers.A.{cohort}.length_only_within`, with "
           "`qwen_redacted_within` asserted equal to the plotted arm."]
    return entry("fig5_positive_controls", "main text, Figure 5", cap, src, D)


def figS(D):
    t = D["figS_amend7_detail"]
    g = lambda c, lab: t[f"{c} | {lab}"]
    pair = lambda lab: (g("novel", lab), g("older_primary", lab))
    qn = [k.split(" | ")[1] for k in t if k.startswith("novel | Names only") and k.count(" | ") == 1][0]
    rn, ro = t[f"novel | {qn} | prompt range"], t[f"older_primary | {qn} | prompt range"]
    B, C = t["B"], t["C"]
    arms = [k.split(" | ")[1] for k in t if k.startswith("novel | ") and k.count(" | ") == 1
            and k.split(" | ")[1] != "DrugBank lookup"]
    up = sum(g("older_primary", k)["value"] > g("novel", k)["value"] for k in arms)
    cap = (f"Amendment 7 detail moved from Figure 5. (A) Pair-label arms (E7, exploratory, no pass rule), BiomedBERT "
           f"trained on the label-mention targets: E7c, names only, {two(pair('E7c, names only'))}; "
           f"{two(pair('E7c, adjusted for drug class'))} after adjusting for drug class (rank residual on the joint class "
           f"score); E7d, other drugs' labels retrieved, " + two(pair("E7d, other drugs' labels retrieved"))
           + f"; E7e, clean retrieval, {two(pair('E7e, clean retrieval'))}. Qwen2.5-7B arms (E8, exploratory): names only "
           f"{two(pair(qn))} with the primary prompt; the pale vermilion bar behind the marker is the range over 5 frozen prompts, "
           f"{rn[0]:.3f} to {rn[1]:.3f} on Novel and {ro[0]:.3f} to {ro[1]:.3f} on Older-primary, so the result is "
           f"{qn.split(': ')[1].rstrip(')')}; contaminated retrieval {two(pair('Contaminated retrieval'))}; other drugs' "
           f"labels " + two(pair("Other drugs' labels")) + f"; clean retrieval {two(pair('Clean retrieval'))}. External "
           f"reference: DrugBank lookup {two(pair('DrugBank lookup'))}. The Older-primary point is above the Novel point "
           f"for {up} of {len(arms)} exploratory arms; this is described, not tested. (B) At the DrugBank operating point, E7c's within-drug "
           f"true positive rate minus DrugBank's is {f3(B['novel']['difference']['value'])} {ci(B['novel']['difference'])} "
           f"on Novel and {f3(B['older_primary']['difference']['value'])} {ci(B['older_primary']['difference'])} on "
           f"Older-primary; this replaces a kappa ratio, which is undefined as a share when an arm exceeds the lookup. "
           f"(C) Stem control on the {C['n_drugs']} stem-bearing drugs of Novel and Older-primary, pooled: keeping the "
           f"drug-name stem against scrambling it changes the within-drug AUROC by {f3(C['difference']['value'])} "
           f"{ci(C['difference'])}, a {C['verdict']} against the pre-stated expectation of a drop of at least "
           f"{C['expected_drop']:.2f} with a 95% interval excluding 0. E7 arms average 5 seeds; Qwen is a single run. "
           f"Whiskers are 95% two-way cluster bootstrap intervals over OOD drugs and partners, 1,000 draws; the dashed "
           f"line is chance, and no equivalence test applies in this figure. Every row is within-drug, tier A. The E9 "
           f"'no pair signal' and E7 'signal' labels are superseded by Commitment 8. {AMEND}")
    src = ["E7c to E7e: `amend7/e7.json` `knowledge.{c,d,e}.{cohort}/A.within`; point estimates recomputed from the "
           "`a7-e7*` predictions, and the arms asserted against `post7/classshortcut/classshortcut.json`.",
           "E7c class-adjusted: `post7/classshortcut/classshortcut.json`, `cells.{cohort}:A.partial.rank:joint.residual_within`.",
           "Qwen arms: `amend7/e8.json` `e8_names.cohorts` (primary prompt, min, max, robust) and "
           "`e8_evidence.{contam,other,clean}.{cohort}/A.within`; point estimates recomputed from the `a7-qwen-*` predictions.",
           "Panel B: `classshortcut.json` `drugbank_operating_point`.",
           "Panel C: `amend7/e8.json` `e8_stem_control`; the expectation threshold is `amend7_analysis.STEM_DROP`."]
    return entry("figS_amend7_detail", "supplement, Figure S5", cap, src, D)


def fig6(D):
    t = D["fig6_model_panel"]
    if t.get("pending"):
        return entry("fig6_model_panel", "main text, Figure 6", "Pending: E9 results not available.", [])
    ext = [v for v in t["extra"].values() if v["kind"] == "external"]
    msk = [v for v in t["extra"].values() if v["kind"] == "masked"]
    f1 = [v["semeval_binary_f1"] for v in t["models"].values()]
    au = [v["auroc_within"] for v in t["models"].values()]
    nov = t["novel"]
    nb = D["fig1_values"].get("PanelBackbones")
    cap = (f"Across {t['n_models']} SemEval-trained models ({nb} backbones, two input formats, one recipe), SemEval test "
           f"binary F1 ({rng(f1)}) does not order agreement with FDA label mentions on new drugs: Spearman rho "
           f"{t['rho']:.3f}, 95% [{t['rho_ci95'][0]:.3f}, {t['rho_ci95'][1]:.3f}] on Older-primary"
           + (f" and {nov['rho']:.3f} [{nov['rho_lo95']:.3f}, {nov['rho_hi95']:.3f}] on Novel" if nov else "")
           + f". Within-drug AUROC, names only, is {rng(au)}; {t['k_upper_at_most_bound']} of {t['n_models']} models have "
           f"a 95% upper bound of at most {t['bound']:.2f} (dotted line, the E9 rule), and "
           + ("every model lies below" if max(au) < t["drugbank_within"] else "not every model lies below")
           + f" the DrugBank lookup ({f3(t['drugbank_within'])}, the external reference). The between-model variance is "
           f"{t['variance_ratio']:.3f} times the mean bootstrap variance"
           + (f" and {t['variance_ratio_paired']:.3f} times the paired-difference reference (post hoc)"
              if t.get("variance_ratio_paired") is not None else "")
           + f". Open blue diamonds (the Masked-trained marker): the {len(msk)} models trained with names masked, which "
           f"tie at {rng([v['auroc_within'] for v in msk])} and are left out of rho. Open circle: the one public checkpoint "
           f"that "
           + (f"passed the static checks (F1 {ext[0]['semeval_binary_f1']:.3f}, AUROC {f3(ext[0]['auroc_within'])}), also "
              f"outside rho. " if ext else "passed the static checks. ")
           + f"Seed 42 per model. Whiskers are 95% two-way cluster bootstrap intervals with draws shared across models; "
           f"the rho interval uses the same draws. The dashed line is chance; no equivalence test applies here. {AMEND}")
    src = ["AUROC, intervals, rho, its interval, the bound count and the variance ratio: `amend7/e9.json`, `e9.panel.older_primary` "
           "(and `novel` for the caption).",
           "Binary F1: recomputed with `metrics.binary_f1` from `test_sentence` predictions of each `a7-panel-*` file against "
           "the SemEval test labels (`label_id != 0`); asserted by recomputing rho and matching `e9.json`, and against "
           "`semeval_binary_f1` for the masked and external models, and against `post8/e9.json` `per_checkpoint` "
           "`semeval_binary_f1` for every panel model.",
           "Paired-difference variance ratio: `post8/e9.json` `tiers.A.older_primary.ratio_paired`.",
           "Masked and external points: `e9.json` `e9.masked` and `e9.external`.",
           "DrugBank line: `classshortcut.json` `older_primary:A.drugbank_operating_point.drugbank_auroc_from_placements`, "
           "asserted against `e7.json` `drugbank_within`."]
    return entry("fig6_model_panel", "main text, Figure 6", cap, src, D)


def ga(D):
    g = D["graphical_abstract"]
    lines = "; ".join(f"{k} {f3(v['left'])} to {f3(v['right'])}" for k, v in g["lines"].items())
    px = g["size_px_by_role"]
    ints = "; ".join(f"{k} [{f3(v[0])}, {f3(v[2])}]" for k, v in g["intervals"].items())
    cap = (f"No caption (submission file, 2000 x 800 px at 300 dpi, ratio 2.50; sizes in design pixels: title {px['title']}, "
           f"end labels {px['end_labels']}, lines {px['lines']}). Title: \"{g['title']}\" Drawn line: \"{g['note']}\" Small text: \"{g['convention']}\" Column subtitles: {' / '.join(c.replace(chr(10), ' ') for c in g['columns'])}. Every plotted point has a 95% interval drawn ({ints}). Lines (SemEval labels to FDA label "
           f"mentions, names only): {lines}; the DrugBank SemEval value excludes self-pairs. The two columns differ in drugs and "
           f"in label source, so the title states what is drawn and not a cause. Labels: {'; '.join(g['labels'].values())}. "
           f"Caveat for the submission text, not drawn because it is not legible at 500 x 200: \"{g['footer']}\" "
           f"Earlier titles: \"{g['prior_title']}\"; \"{g['old_title']}\" {AMEND}")
    src = ["Every value is the Figure 2 value (`figure_data_main.json`, `fig2_dissociation`), with the DrugBank SemEval "
           "point taken from the self-pair-excluded row; every drawn 95% interval is the Figure 2 interval of the same point, asserted "
           "to bracket the point and to match the drawn segment. The code stops unless the encoder is above the DrugBank lookup on "
           "SemEval labels and below it on label mentions, only these two series are drawn, no range bar is drawn, and the "
           "pixel size, the aspect ratio and the text sizes are as stated."]
    return entry("graphical_abstract", "submission file", cap, src, D)


def build(D):
    lo, hi = D["margin"]
    head = ["# Figures", "",
            "Generated by `python -m ddiood.paperfigs2 --compile` (locally, or in `colab/experiments/F1_paper_figures.ipynb`). "
            "Every main figure is a vector PDF with embedded fonts and a 300 dpi PNG, set in Latin Modern Roman at 90 or "
            "190 mm. One encoding holds across figures: blue `#0072B2` for SemEval-trained encoders, vermilion `#D55E00` for "
            "prompted LLMs and label-trained arms, black for the DrugBank lookup and gray `#7F7F7F` for shortcuts; markers are "
            "a filled circle (sentence-trained), filled square (mixed-input), open up-triangle (names-trained), open diamond "
            "(masked-trained), filled down-triangle (Qwen), open down-triangle (BioMistral), filled black diamond (DrugBank) "
            "and open pentagon (H5). The gray band is the equivalence margin "
            f"({lo:.2f} to {hi:.2f}) and appears only on the Mixed-input BiomedBERT Older-clean within-drug row, the H1 "
            "primary cell, which alone carries 90% bars; every other interval is 95%. The dashed line is chance in every figure. Decision words appear only on planned "
            "or Amendment 7 pre-specified rules on tier A; scores that hold by construction say so. Every number below is "
            "filled in by `ddiood/captions.py` from the plotted values, so captions and figures cannot drift apart. Each "
            "caption with an OOD number ends with the Commitment 8 sentence.", "",
            f"Assertion layer. `ddiood.paperfigs2` recomputes each plotted value with the `evaluate2` or `amend7_analysis` "
            f"function that produced the stored value and stops if they differ. The last run made "
            f"{sum(v for k, v in D['checks'].items() if k != 'read')} such checks, plus "
            f"{sum(D['checks_paperfigs_cells'].values())} seed-aggregated cell checks inside `ddiood.paperfigs.Data`; the "
            f"full ledger is in `figure_data_main.json`.", "",
            "Paths are relative to `results/revision/`; `eval/` is `results/revision/eval/`. " + AMEND, "",
            "## Main text (6 figures; with Tables A and B, 8 items)", ""]
    body = [fig1(D), fig2(D), fig3(D), fig4(D), fig5(D), fig6(D), "## Amendment 7 detail (Figure S5)", "", figS(D),
            "## Submission", "", ga(D)]
    return "\n".join(head) + "\n" + "\n".join(body)
