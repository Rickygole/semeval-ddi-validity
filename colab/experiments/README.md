# Experiment notebooks

One notebook per experiment. Each mounts Google Drive, reads `ddiood_code.tgz` and `inputs.json.gz` from `MyDrive/temporal-ood-ddi`, runs its jobs with `python -m ddiood.gpu_jobs`, and writes one prediction file per job to `MyDrive/temporal-ood-ddi/runs/preds/`. Finished jobs are skipped, so a notebook can be rerun after a disconnect.

| Notebook | Experiment | Hypotheses |
|---|---|---|
| `E1_input_format_control.ipynb` | BiomedBERT and bert-base trained with the sentence, with sentence plus empty-context copies, or with names only; evaluated on SemEval, name swaps, Novel OOD and Older OOD | H1, H2, H4 |
| `E2_entity_masking.ipynb` | training and testing with both drug mentions replaced by `@DRUG$` | H2 |
| `E3_drug_disjoint_split.ipynb` | 30% of SemEval test drugs held out of training | secondary |
| `E4_retrieval_probe.ipynb` | BiomedBERT with retrieved FDA label passages, the Drug Interactions positive control and retrieval ablations | H5, H6 |
| `E5_llm_baselines.ipynb` | BioMistral-7B and Qwen2.5-7B-Instruct scored from label-word probabilities, names only and with passages | secondary |
| `E6_architecture_check.ipynb` | BioBERT with sentence and mixed inputs | secondary |
| `F1_paper_figures.ipynb` | no GPU: reads `figures_bundle.tgz` (built by `bash scripts/make_figures_bundle.sh`) and `runs/preds` (main and `a7-` files), reruns `ddiood.evaluate2`, `scripts.revision_metrics`, `scripts.residual_analysis`, `ddiood.paperfigs` (supplement) and `ddiood.paperfigs2` (main figures, graphical abstract and the compiled pipeline figure; installs TeX if missing), and writes `runs/eval` and `figures` | all (figures) |
