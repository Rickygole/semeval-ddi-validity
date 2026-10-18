# What do SemEval 2013 drug-drug interaction scores measure? Construct validity and a check of label-derived pair targets

Ricky Gole and Jamell Dacon, Morgan State University.

This repository holds the code, frozen inputs, prediction files and result files for the paper. The archive DOI will be added on publication.

## Analysis plan

The analysis plan is a private, version-controlled file (`docs/PREREGISTRATION.md`). It was not registered with a third party. It was fixed under four git tags in the private repository before the corresponding predictions were analysed. This repository has a fresh history, so the tags are not in it. The values below were computed with git from the private repository and are also in [`docs/ARCHIVE_MANIFEST.json`](docs/ARCHIVE_MANIFEST.json).

| tag | commit | commit date | SHA-256 of `docs/PREREGISTRATION.md` |
|---|---|---|---|
| `prereg-v1` | `897d448fc0053a532194da4793f13319b5df5abc` | 2026-10-16T00:36:39-04:00 | `f5cd60a9800b0f13f9aa8591fae41ee7aa396f54e058c523e1ec8bf242b1c931` |
| `prereg-v1-amend4` | `742824c7cb5b1d8e8c3bf33bb8e108bd8ddabf96` | 2026-10-16T02:58:25-04:00 | `05a54d595db19e26c6f8d63162202a103a7ff690d68c6b1700ce26bc0994da98` |
| `prereg-v1-amend6` | `cc734456c585f84180579c925a53e08fb6d8e275` | 2026-10-16T11:23:05-04:00 | `10789828b7d96bf96ea8431dacc76bddc2498c92b4ac4fd91032b9e643297f77` |
| `prereg-v1-amend7` | `fb91d06ddc930898697c02e241f419d5055b3c46` | 2026-10-16T22:06:01-04:00 | `3b435826a9c521b13f2581e0db7ea1c4a1b8c3f84e266ff45248eb5eb12a0d0f` |

The post hoc analyses in `results/revision/rev2_colab/`, `results/revision/rev2/` and `results/revision/rev3/` follow `docs/POSTHOC_REV2_PLAN.md` and `docs/POSTHOC_REV3_PLAN.md`. Every JSON file in `results/revision/rev3/` records the SHA-256 of the plan file it was run under as `plan_sha256`.

## What you can reproduce

| step | reproduces | needs | measured time |
|---|---|---|---|
| 1. Verify | the decisions H1 to H6 in `results/revision/eval/decisions.json`, recomputed from the frozen predictions, and SHA-256 checks of every prediction file | CPU, Python 3.11, network for pip and the SemEval corpus | 103 to 107 s in total, of which 72 to 74 s is the evaluation (two runs) |
| 2. Tests | unit tests and checks of the shipped result files | `requirements.txt` | about 1 minute |
| 3. DrugBank files | the two DrugBank validation CSVs that tier B, the DrugBank reference values and the figures need | a licensed DrugBank copy | 223 s for both cohorts |
| 4. Figures | the evaluation tables and every figure | step 3, TeX Live with `pdflatex`, `pdftoppm` | 370 s |
| 5. GPU jobs | new prediction files | a CUDA GPU (A100 recorded), the GPU input archives | see section 5 |

Times were measured on an Apple M1 Pro with macOS 26.5.1 and CPython 3.11.5. DrugBank is never redistributed.

## Setup

```
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`requirements-verify.txt` pins only what step 1 needs. `requirements.txt` pins the direct dependencies of the CPU code, `requirements-lock.txt` is the full environment the analyses ran in, and `requirements-gpu.txt` lists the extra GPU packages.

## 1. Verify

```
bash verify.sh
```

`verify.sh` creates `.venv` from `requirements-verify.txt` if it does not exist, then runs `scripts/verify_release.py`, which

1. checks the SHA-256 of the 61 files in `results/revision/preds/`, the 58 Amendment 7 GPU files and 21 further GPU files in `runs/preds/`, and the 17 files in `artifacts/amend7/preds_cpu/` against their manifests, and those manifests against `docs/ARCHIVE_MANIFEST.json`;
2. downloads the SemEval 2013 DDI corpus at commit `819b0fa` into `data/DDICorpus/` (git clone, once);
3. reruns `ddiood.evaluate2` on `results/revision/preds/` with 1,000 bootstrap draws into a temporary directory;
4. compares the new `decisions.json` byte for byte with `results/revision/eval/decisions.json`.

The output ends with

```
[OK] recomputed decisions.json is byte-identical to results/revision/eval/decisions.json
       reference  a13f1c45472447893edd3401981de2e3f8507e8aa16209db50ea633bf6c2199a
       recomputed a13f1c45472447893edd3401981de2e3f8507e8aa16209db50ea633bf6c2199a
       DrugBank files used: none; evaluation took 72.4 s
VERIFY PASSED
```

The evaluation time varies between runs.

Options: `--hashes-only` skips the evaluation, `--out DIR` keeps the recomputed outputs, and `--boot N` changes the number of draws (only 1000 matches the reference). The decisions do not use DrugBank, so this check is complete without it.

## 2. Tests

```
pytest -q
```

Without DrugBank, in a git clone of this repository: 269 passed, 10 skipped. In a copy without `.git`: 268 passed, 11 skipped. The skipped tests need the DrugBank files of step 3, the GPU input bundle or git. With the DrugBank files of step 3, `pytest -q tests scripts/gate8_test.py` gives 281 passed, 5 skipped.

## 3. DrugBank files

Obtain DrugBank (full database XML; the zip as distributed works) under its license, then

```
mkdir -p artifacts/vocab artifacts/ood
cp results/corrected/drug_lookup.json artifacts/vocab/
cp results/corrected/ood_pairs.csv results/corrected/ood_old_pairs.csv artifacts/ood/
python -m ddiood.pipeline drugbank --drugbank PATH/TO/drugbank_all_full_database.xml.zip --cohort novel
python -m ddiood.pipeline drugbank --drugbank PATH/TO/drugbank_all_full_database.xml.zip --cohort old
```

With DrugBank 5.1 exported on 2026-03-05, both CSVs are byte-identical to the ones the paper used, and both summaries are byte-identical to `results/corrected/drugbank_validation*_summary.json`. A different release can change tier B and the DrugBank reference values. Four result files are redacted in this copy, see [`docs/REDACTIONS.md`](docs/REDACTIONS.md).

## 4. Figures and evaluation tables

```
python -m ddiood.evaluate2 --preds results/revision/preds --out OUT/eval --boot 1000
python -m scripts.revision_metrics --preds results/revision/preds --out OUT/eval --boot 1000 --resamples 1000
python -m scripts.residual_analysis --preds results/revision/preds --out OUT/eval/residual_analysis.json --boot 1000
python -m ddiood.paperfigs --preds results/revision/preds --eval OUT/eval --baselines results/corrected/baselines.json --out OUT/figures --boot 1000
cp results/revision/figures/FIGURES.md OUT/figures/
python -m ddiood.paperfigs2 --preds results/revision/preds --a7preds runs/preds --eval OUT/eval --out OUT/figures --figures-md OUT/figures/FIGURES.md --boot 1000 --final --compile
```

`paperfigs2` asserts every plotted value against the result files, stops on any mismatch, and compiles Figure 1 from `paper/figures/pipeline.tex`. With the DrugBank files of step 3 it reports 431 checks, all passing. In that run, 12 of the 13 files in `results/revision/eval/` and `figure_data.json`, `figure_data_main.json`, `FIGURES.md` and `pipeline_values.tex` were byte-identical to the shipped copies. `residual_analysis.json` differed in 9 of its 316 floating point values, by at most 4.4e-16. PDF and PNG files were not compared byte for byte.

The other scripts in `scripts/` regenerate the remaining folders of `results/revision/`; each writes to the folder named in its default `--out`. Some of them need the DrugBank files, the GPU input bundle from the archive or the TAC 2018 data; these were not rerun for this release.

## 5. GPU jobs

The notebooks in `colab/experiments/` run the training and inference jobs: E1 to E6, E7 to E9 (Amendment 7), R2a, R2b, R2c and R3b. Each reads its input archive from `MyDrive/temporal-ood-ddi/`, writes one prediction file per job to `runs/preds/` there, and skips finished jobs. `colab/experiments/README.md` lists the jobs per notebook. The input archives (`ddiood_code.tgz`, `inputs.json.gz`, `amend7_bundle.tgz`) will be in the archive; the R2 and R3 bundles are built with `scripts/rev2_build_bundle.sh`, `scripts/rev3_build_bundle.sh` and `scripts/rev3b_build_bundle.sh`. R2c downloads the TAC 2018 drug interaction data from NLM; its prediction file is not included here.

Recorded compute, the sum of the `seconds` field of the shipped prediction files: 6.4 h for the 61 files in `results/revision/preds/`, 3.7 h for the 58 Amendment 7 files, 1.3 h for the 16 R2 files and 0.04 h for the 5 R3b files. The R2 and R3b files record an NVIDIA A100-SXM4-40GB.

## Determinism

* Seeds: every trained system uses seeds 42, 1, 2, 3 and 4 (`ddiood/config.py`, `SEEDS`).
* Bootstrap: `numpy.random.RandomState(42)` with 1,000 draws for every interval and TOST p-value, so the CPU evaluation is exactly reproducible; step 1 checks this byte for byte.
* GPU training and LLM inference are not bit-reproducible across GPU models and CUDA, PyTorch and transformers versions. Retrained predictions should reproduce the decisions within bootstrap noise, not the file hashes. The frozen prediction files are the reference.
* The Amendment 7 files record a code version hash, the OOD pair hashes, the training pair hash and the prompt hash, which the analysis checks before use.

## Data and licenses

The MIT License in [`LICENSE`](LICENSE) covers the code. Data files keep the terms of their sources, summarized in [`DATA_LICENSE`](DATA_LICENSE).

| source | used for | in this repository | terms |
|---|---|---|---|
| SemEval 2013 DDI corpus, `isegura/DDICorpus` commit `819b0fa` | training and in-distribution test | downloaded on demand; derived pair labels and predictions | CC BY-NC 4.0 |
| openFDA drug labels | retrieval corpus and OOD labels | quoted evidence sentences | CC0 1.0 |
| FDA CDER novel approvals | novel drug list | `data/fda_novel_approvals.csv`, `data/prior_approvals.csv` | public U.S. government data |
| RxNorm via RxNav | vocabulary normalization | RxCUIs and names | NLM notice in `DATA_LICENSE` |
| DrugBank | validation of OOD labels | aggregate counts and metrics only | not redistributed |
| TAC 2018 drug interaction data (NLM) | calibration of the R2b adjudicator | aggregate counts and metrics only | not redistributed |

Quoted FDA text is verbatim, including its dash characters, because the frozen Amendment 7 training pairs are hash-checked. Labels and predictions are for research on evaluation methods, not for clinical decisions.

## Layout

```
ddiood/             library: corpus, vocabulary, labels, retrieval, OOD construction, models, metrics, evaluation, figures
scripts/            analysis and verification scripts
tests/              unit tests and result checks
colab/              GPU notebooks
data/               FDA approval lists
artifacts/amend7/   Amendment 7 frozen inputs and CPU prediction files
artifacts/bundle/   Amendment 7 retrieval delta
runs/preds/         GPU prediction files of Amendment 7, R2 and R3b
results/corrected/  OOD sets, baselines and label audit
results/revision/   prediction files, evaluation, post hoc analyses and figures
paper/figures/      TikZ source of Figure 1
docs/               analysis plans, archive manifest, redactions
```
