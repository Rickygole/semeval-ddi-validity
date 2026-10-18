# Post hoc round 2: two Colab experiments that answer the JBI referee

Status: written before any code was built and before anything ran on a GPU. After the code was built and smoke-tested on CPU with tiny stand-in models, two passages were updated before any run: the list of sections affected by the chunk rule and the time-estimate table. Both experiments are post hoc and descriptive. They were not part of the preregistration or of Amendments 1 to 7 (Amendment 8 was drafted and not filed). They carry no decision rule, no threshold and no pass or fail criterion, and they change none of the frozen primary analyses, frozen sets or frozen modules. Their results will be reported whatever they show, including a null, a reversal or a failed reproduction.

Code lives in `ddiood/rev2_*.py` and `scripts/rev2_*.py`. Predictions are written to `{D}/runs/preds/` with names prefixed `r2-`, with `D = /content/drive/MyDrive/temporal-ood-ddi`. Weights are written to `{D}/weights/`.

## Why these two experiments

Referee M3a asks for the missing cell of the double dissociation. The submitted contrast shows encoders trained on SemEval sentences failing on label-derived pairs of drugs they never saw (Novel, Older) and, in Amendment 7, encoders trained on label-derived pairs (the positive control) failing on SemEval. It does not show how a SemEval-trained encoder scores label-derived pairs of drugs it has seen. If it does well on seen drugs and at chance on unseen drugs, the failure is about drug identity and not about the label source. If it is near chance on seen drugs too, the failure is about the label source and the input.

Referee M10 asks whether the result depends on the input format. An entity-marker encoder is added with the Amendment 7 panel recipe.

Referee M5 asks for a label adjudicator that other people can rerun. The earlier model adjudication used an evidence column and a model that others cannot easily reproduce. R2b uses an open, ungated, permissively licensed model from a different family, and gives it only the Drug Interactions section of the OOD drug and the partner name, identically for every item, so that no label, flag or evidence column can steer it.

## R2a: SemEval-trained encoders scored on seen-drug pair labels

### Why retraining is needed

No weights were saved by the original runs. The stored files `results/revision/preds/b2mixed-biomedbert-s*.json` hold predictions only. Scoring a new pair set therefore requires retraining, with the identical recipe, and this time saving the weights.

### Models and seeds

All models are BiomedBERT (`microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`, revision `e1354b7a3a09615f6aba48dfad4b7a613eef7062`, the revision pinned in `artifacts/amend7/manifest.json` and identical to the head of the hub repository on 2026-10-17). Seeds 42, 1, 2, 3, 4. Training uses `ddiood.bert.train` with the arguments of `ddiood.gpu_jobs.bert_job` (5 epochs, patience 2, learning rate 2e-5, batch size 16, class weights `[0.1, 2.0, 2.5, 4.0, 8.0]`, validation split `bert.split_train_val(train, seed)` on the full SemEval 2013 train set), with `save_model=True`.

| Family | Job name | Training input | Matches |
| --- | --- | --- | --- |
| b2mixed | `r2-b2mixed-biomedbert-s{seed}` | `inputs.mixed_training`: each pair twice, once with its sentence and once with an empty sentence, both with the `a [SEP] b` pair | `b2mixed-biomedbert-s{seed}` |
| b2sentence | `r2-b2sentence-biomedbert-s{seed}` | `inputs.b2_sentence`: sentence plus the `a [SEP] b` pair | `b2sentence-biomedbert-s{seed}` |
| marker | `r2-marker-biomedbert-s{seed}` | `amend7_panel.marker_sentence` with the angle tags `<e1> </e1> <e2> </e2>` and annotated offsets, as in the E9 panel | `a7-panel-biomedbert_full-marker` (seed 42 only) |

Fifteen jobs. Weights go to `{D}/weights/{job name}/` as a `save_pretrained` directory, written to a temporary directory and renamed. After saving, each job reloads the saved weights and checks that they reproduce the in-memory probabilities on a fixed sample, and records the sha256 of the weight file.

### What each job scores

b2mixed and b2sentence reproduce every key of the original `bert_job` evaluation: `test_sentence`, `test_masked`, `test_empty`, `test_names`, `ood_empty`, `ood_names`, `ood_sentence`, `ood_swap_sentence`, `oodold_empty`, `oodold_sentence`, `swap_vocab_sentence`, `swap_novel_sentence`, `swap_pseudo_sentence`. New keys: `train_empty` and `train_names`, the names-only inputs for the 4,643 seen-drug pairs of `artifacts/amend7/train_pairs.csv` (anchor drug `drug_a`, partner `drug_b`, 1,542 positive; the Drug Interactions sections of SemEval-vocabulary drugs).

The marker family scores `test_sentence`, `test_empty`, `ood_empty`, `oodold_empty`, `ood_sentence`, `oodold_sentence` as in the E9 panel job, and the new `train_empty`. Names-only input for the marker family is `<e1>a</e1> and <e2>b</e2>.`.

The frozen Novel set (438 pairs) and Older set (1,944 pairs) are checked against the hashes in the Amendment 7 manifest before any job starts. The train pairs are checked against the manifest training hash.

### Statistics

- Primary quantity: within-drug AUROC by anchor drug. Pairs are stratified by the OOD or anchor drug (`drug_a`), the Mann-Whitney statistic is summed over strata and divided by the total number of positive-negative pairs in strata that have both classes (`amend7_analysis.fast_within`, mode `within`).
- Interval: the two-way cluster bootstrap of Amendment 7 (`amend7_analysis.draws`), resampling anchor drugs and partner drugs, 1,000 draws, seed 1042 for Novel and seed 42 for Older primary and for the seen cohorts (the seeds of `amend7_analysis.BOOT_SEED`), percentile 95% interval.
- Cohorts, all names only: seen-drug train pairs; Novel; Older primary (Older minus the 7 artifact and 7 missed-vocabulary drugs of `primary_sets.json`). For every family the score is the mean probability over the five seeds, and the per-seed values are listed beside it.
- Reference points: pooled SemEval test AUROC for `test_sentence` and `test_empty`.
- Reproducibility check for b2mixed and b2sentence, per seed and per original key: the pair-level Spearman correlation between the retrained and the stored probability vectors, the maximum absolute difference, the share of identical predicted classes, and for the Novel and Older primary names-only keys the difference (retrained minus stored) in within-drug AUROC. GPU training is not bitwise reproducible, so a nonzero difference is expected. No tolerance is set in advance, and the differences are reported as they are.
- No test of seen against unseen is run. The cohorts contain different drugs and are not paired, so only the two intervals and their difference in point estimates are shown.

### Interpretation rule

None is attached. The table of within-drug AUROC, by family and cohort, with intervals, is the result.

## R2b: a reproducible open-model label adjudicator

### Model

`allenai/OLMo-2-1124-7B-Instruct`, a different family from Qwen2.5 and from BioMistral. Checked on 2026-10-17 against the hub API and model card:

- exists, `gated: false`, `private: false`;
- license `apache-2.0` in the card metadata and in the card text ("License: Apache 2.0");
- pinned revision `470b1fba1ae01581f270116362ee4aa1b97f4c84` (head of `main` on 2026-10-17, last modified 2025-01-06);
- 7,298,617,344 bf16 parameters, maximum position embeddings 4,096.

The license of the training data was not audited. Loading follows `amend7_jobs.load_qwen` (4-bit NF4, double quantization, bfloat16 compute), with the pinned revision. The 4,096-token context is handled by the chunk rule below.

### Items

All items use only `ood_drug` and `partner`.

1. The 255 items of `results/revision/post8/label_audit_sheet.csv` (item ids A001 to A255).
2. A random sample, drawn once with `random.Random(17)`: from the Older primary cohort 75 pairs with label 1 and 75 with label 0, then from the Novel cohort 50 with label 1 and 50 with label 0. Within each cohort and class the candidate rows are listed in frozen file order and sampled with `rng.sample`, in the order older class 1, older class 0, novel class 1, novel class 0. This gives 150 Older-primary and 100 Novel pairs. Item ids are `S001` to `S250`. The full item list (505 items, 459 distinct pairs), serialised with `json.dumps(items, sort_keys=True)`, has sha256 `2f4410cb00e0a8bb3b098493e4a5d15460e2d1f3da2112bac44a6a4f96097cf4`; the frozen prompt configuration (`rev2_adjudicator.prompt_sha256`) has sha256 `eade2527898604e24481e235a7ea17e73a23fa64b05e823fb18edda0f6a29d93`. The sample is independent of the audit sheet, and some pairs may appear in both. A pair that appears twice is scored once and reported under both ids.

The random sample exists so that population error rates can be estimated. The audit sheet was selected for suspected errors, so its rates are not population rates and are never pooled with the random sample.

### Input and frozen prompt

The model sees the full Drug Interactions section of the OOD drug (`artifacts/amend7/di_sections.json`, field `text`) and the partner name. It does not see the label, the evidence column, the rule flag, the co-occurrence sentence, the selection reason or the cohort. The prompt is applied through the model chat template as one user turn:

<!-- PROMPT-BEGIN -->
```
Read the Drug Interactions section of a drug label and answer one question about it, using only the text below.

Drug Interactions section for {drug}:
{section}

Question: Does this section state a clinically relevant interaction between {drug} and {partner}? Answer with one word only: yes, no or unsure.

Answer:
```
<!-- PROMPT-END -->

### Scoring

Label-token probability as in `amend7_llm`: the logits at the last position are restricted to the first token of each case variant of `no`, `yes` and `unsure` (with and without a leading space), summed per label with log-sum-exp, and renormalised with a softmax over the three labels. `unsure` is split by this tokenizer into two tokens, except with a leading space, so the first token of each form is used (`uns`, `Un`, ` unsure`, ` Unsure`), which makes the `unsure` probability a first-token proxy. `yes` and `no` are single tokens. A collision between the first tokens of two labels is an error. The decision is the label with the highest renormalised probability. The mass of the three labels over the full vocabulary is recorded, and answers with mass below 0.5 are counted as non-answers and reported, not removed.

Sections that do not fit the context (with the prompt, at most 4,000 tokens) are split at sentence boundaries into consecutive chunks that each fit, every chunk is scored with the same prompt, and the item takes the chunk with the highest probability of `yes`. This rule does not use the partner or the label. On the current 505 items (459 distinct prompts, 46 pairs appear in both sets) it affects only the sections of darunavir, etravirine and atazanavir sulfate, two chunks each.

### Scorer (written now, run later)

`scripts/rev2_score_adjudicator.py` reads the prediction file and writes JSON and a table:

- agreement of the decision with the current label (`yes` with 1, `no` with 0), with `unsure` treated as not confirming, and with `unsure` excluded;
- error rates, each with a Clopper-Pearson exact 95% interval: positives judged `no`, negatives judged `yes`, in three treatments of `unsure` (excluded, counted as correct, counted as an error), for the audit sheet by selection reason and cohort, and separately for the random sample by cohort and class (the population estimates);
- agreement with the earlier model adjudication (`results/revision/post8/model_adjudication.csv`) on the 255 audit items: raw agreement, agreement on items both decided, Cohen's kappa and the confusion table.

The earlier adjudication used an evidence column and a different model, so differences between the two adjudications are not evidence that either is correct. Neither is a human audit.

## Jobs and notebooks

Estimates use the `seconds` fields of the stored `results/revision/preds` files of the same family and seeds (b2mixed 457 to 494 s, b2sentence 175 to 255 s; the marker family is estimated from b2sentence because it trains on the same number of sentences). Low value: stored seconds plus 60 s per job for the train-pair scoring, the weight save, the reload check and the checksum. High value: 1.6 times the stored seconds plus 120 s, a factor taken from the spread of the Amendment 7 estimates (1.5 to 1.7) for a slower GPU. The adjudicator is 600 s plus tokens / 13,000 per second (low) and 1,200 s plus tokens / 5,000 per second (high), the rates used for the Amendment 7 language-model jobs, with 391,062 prompt tokens counted with the pinned tokenizer; the 600 and 1,200 s cover downloading and quantizing the 7B model. These are estimates, not measurements. The b2sentence seed 42 stored run stopped after 3 epochs, so its low estimate is optimistic. Each notebook is built to stay under about 2 hours at the high value, and the notebooks are independent and can run in parallel on separate Colab sessions.

| Notebook | Jobs | Low (h) | High (h) |
| --- | --- | --- | --- |
| `R2a_b2mixed` | `r2-b2mixed-biomedbert-s{42,1,2,3,4}` | 0.73 | 1.20 |
| `R2a_sentence_marker` | `r2-b2sentence-biomedbert-s{42,1,2,3,4}`, `r2-marker-biomedbert-s{42,1,2,3,4}` | 0.82 | 1.38 |
| `R2b_adjudicator` | `r2-olmo-adjudication` | 0.17 | 0.35 |

The weights are about 440 MB per model in float32, so the 15 models need about 6.6 GB on Drive.

Files expected on Drive before running: `rev2_bundle.tgz` (built by `scripts/rev2_build_bundle.sh`) and `inputs.json.gz` (already there from Amendment 7). The notebooks need internet access to clone the SemEval 2013 corpus at the pinned commit and to download the pinned model revisions.

## Handling of failures and reruns

Each job writes `r2-*.json` atomically on success and `r2-*.failed.txt` on failure; the loop continues after a failure. A finished job is skipped on rerun, and a stored result made with a different configuration is an error. The last cell of each notebook asserts that nothing failed.

## What is reported

Every number the scripts produce, including the reproducibility differences and any `unsure` or non-answer counts. If a job fails, the failure is reported with its traceback. If the retrained models do not reproduce the stored predictions closely, that is reported next to the R2a result.

## Addendum before any run (2026-10-17)

Written after code review and before any job ran. The text above is unchanged except the bootstrap seed wording.

(a) Overlap of the seen pairs with SemEval train. A code review found that 581 of the 4,643 seen-drug pairs also occur as a pair in SemEval 2013 train, and 213 of those 581 have at least one positive SemEval instance (206 of them are also positive in `train_pairs.csv`). A pair matches when the unordered pair of names, each lowercased and stripped of surrounding spaces (the normalization in `pair_key` of `scripts/rev2_analyze_a.py`), equals the unordered pair of any SemEval train instance. A sensitivity cohort "seen, pair not in SemEval train" (4,062 pairs, counted by `scripts/rev2_analyze_a.py` and recorded in its output) is therefore reported beside the full seen cohort. Both cohorts are reported, with the same statistic and bootstrap, and neither is preferred in advance.

(b) 175 seen drugs act as both anchor and partner. The two-way bootstrap treats anchor drugs and partner drugs as independent clusters, so for the seen cohort the interval may be narrower than for Novel and Older.

(c) The `Un` first token of `Unsure` also begins Unclear, Unknown and Unable, so it adds to the `unsure` probability. The `unsure` score is a first-token proxy and is reported as such.

(d) The chunk token budget depends on the length of the partner name through the prompt overhead. On the current items the chunk boundaries are identical for every partner, checked with the pinned tokenizer: darunavir (3 partners), etravirine (2) and atazanavir sulfate (3) each give exactly one distinct chunking across their partners.

(e) The pooled-over-cohorts error rate of the random sample is an unweighted pool of the stratum samples, not a population rate. It is labelled that way in the scorer output (`errors_unweighted_pool_by_class`); the population estimates are the per-cohort and per-class rows.

(f) The configuration hash includes the code version. Any code edit after a partial run changes the hash, and the first finished r2 output then stops the rerun with an error. If the code is edited after any job has finished, delete the earlier `r2-*` outputs in `{D}/runs/preds` before rerunning.

(g) Extra reproducibility row: `r2-marker-biomedbert-s42` is compared with the stored `a7-panel-biomedbert_full-marker` (Spearman, maximum absolute difference, same-class share, and within-drug AUROC difference on Novel and Older primary), next to the b2mixed and b2sentence rows.

Run-time safeguards added: the Drive is always mounted and `D` is always the Drive path, so nothing is written only to local disk; the notebook asserts a GPU (R2b also native bfloat16, compute capability 8 or higher, so an L4 or A100); R2a fails before training with under 8 GB free on the Drive; stale `.tmp` weight folders are removed at start and after a failed copy; R2b asserts the item-list sha256 `2f4410cb00e0a8bb3b098493e4a5d15460e2d1f3da2112bac44a6a4f96097cf4` (sha256 of the sorted-key JSON of the 505 items) and the prompt sha256 `eade2527898604e24481e235a7ea17e73a23fa64b05e823fb18edda0f6a29d93` before loading the model; every output JSON records the torch, transformers, bitsandbytes and accelerate versions and the GPU name; the R2b model is loaded with `torch_dtype=torch.bfloat16` for the layers that are not quantized, in addition to the 4-bit NF4 quantization; the last cell unmounts the Drive with `flush_and_unmount()` after the status asserts. The `non_answers` figure in the model output counts prompts (chunks included), and the scorer also reports the per-item count.
