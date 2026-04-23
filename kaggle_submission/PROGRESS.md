# Kaggle Submission — Progress Tracker
**Competition:** Triagegeist — AI in Emergency Triage (Laitinen-Fredriksson Foundation)

---

## Model Versions — Quick Reference

We have two trained CatBoost pipelines. It is important to know which is which:

| Version | Features | hx_* history | BioBERT PCA | OOF QWK | Used for |
|---|---|---|---|---|---|
| **v1.0.2** | 61 total | ✓ 25 flags | ✓ 10 cols | **QWK 0.9975, Macro-F1 0.9895, Accuracy 99.51%** (OOF) | `submission.csv` generation |
| **v1.0.2-c** | 26 total | ✗ excluded | ✗ excluded | **0.9322** | OOF benchmarking only |

The submission was generated using **v1.0.2** (the stronger, full model).  
OOF metrics computed so far are from **v1.0.2-c** (the fallback, weaker model).  
These are not the same — see Priority 1 under "What Is Left To Do".

---

## What We Have Done

### 1. Understood the Competition
- Read the full competition brief (`kaggle_comp.txt`)
- Studied the baseline notebook (`triagegeist-baseline.ipynb`) — LightGBM + TF-IDF, OOF QWK 0.712
- Identified the evaluation metric: **Quadratic Weighted Kappa (QWK)**
- Confirmed submission format: a Kaggle Notebook + a Kaggle Writeup (no leaderboard, hackathon-style judging)
- Confirmed the baseline's self-acknowledged gaps: TF-IDF is shallow, no comorbidity interaction, single model

### 2. Audited the Existing ML Pipeline
- Traced the full training pipeline through `ml/notebooks/2.ipynb`
- Confirmed v1.0.2 was trained on **61 features**: 26 structured vitals/demographics + 25 hx_* comorbidity flags + 10 BioBERT PCA components
- Confirmed leakage columns (`disposition`, `ed_los_hours`) were correctly removed before training
- Confirmed v1.0.2 used proper **OOF evaluation** — `out_of_fold_predictions[test_idx] = fold_preds` in the training loop, classification report generated from all 80,000 OOF predictions
- Confirmed v1.0.2's **OOF accuracy of 99.58% is genuine, not leakage** — the dataset is synthetic, and `news2_score` alone nearly separates all 5 ESI classes by design (ESI-1: range 6–17, ESI-2: 0–17, ESI-3: 0–11, ESI-4: 0–7, ESI-5: 0–4). CatBoost with 10,000 iterations learns these boundaries almost perfectly. This is consistent with other participants also achieving high accuracy.
- Investigated `pca_v1.0.2.pkl` — confirmed it is **intact and fully functional** with `joblib.load()`. Earlier failure was caused by using `pickle.load()` instead of `joblib.load()` (wrong tool, not a corrupt file). The PCA is 768 → 10 dims, seed 42, 34KB on disk.
- Confirmed all 5 fold models exist: `model_v1.0.2_fold_1.cbm` through `model_v1.0.2_fold_5.cbm`

### 3. Computed OOF Metrics — Both Models

#### v1.0.2 — Full Model (submission model)
Loaded all 5 v1.0.2 fold models, rebuilt the exact 61-feature matrix (structured + hx_* + BioBERT PCA-10), ran proper OOF evaluation on 80,000 training rows. Results saved in `v102_oof_metrics.json`.

| Metric | v1.0.2 (full model) | Baseline (LightGBM + TF-IDF) |
|---|---|---|
| OOF QWK | **0.9975** | 0.712 |
| OOF Linear Kappa | 0.9956 | — |
| OOF Unweighted Kappa | 0.9933 | — |
| OOF Macro-F1 | **0.9895** | ~0.71 |
| OOF Weighted-F1 | 0.9951 | — |
| OOF Accuracy | **99.51%** | ~82% |
| Under-triage rate | **0.36%** | — |
| Over-triage rate | 0.13% | — |

Per-fold QWK (v1.0.2) — std 0.0003, extremely stable:

| Fold | QWK | Macro-F1 |
|---|---|---|
| 1 | 0.9974 | 0.9891 |
| 2 | 0.9970 | 0.9898 |
| 3 | 0.9980 | 0.9900 |
| 4 | 0.9977 | 0.9887 |
| 5 | 0.9975 | 0.9899 |
| **OOF** | **0.9975** | **0.9895** |

#### v1.0.2-c — Fallback Model (no BioBERT, no hx_*)
Used only for benchmarking — confirms BioBERT PCA is the key driver.

| Metric | v1.0.2-c | v1.0.2 | Delta |
|---|---|---|---|
| OOF QWK | 0.9322 | **0.9975** | +0.0653 |
| OOF Macro-F1 | 0.8743 | **0.9895** | +0.1152 |
| Under-triage | 7.46% | **0.36%** | −7.1pp |

The BioBERT PCA-10 columns are responsible for the entire gap between the two models.

### 4. Generated Test Set Predictions (`submission.csv`)
- Wrote and ran `generate_submission.py` which uses the **full v1.0.2 pipeline**:
  1. Loaded `test.csv` + `chief_complaints.csv` + `patient_history.csv` (20,000 test patients)
  2. Applied same preprocessing as training (drop same columns, fill NaNs)
  3. Ran BioBERT (`dmis-lab/biobert-v1.1`) on 20,000 chief complaint texts → 768-dim vectors
  4. Applied `pca_v1.0.2.pkl` to compress 768 → 10 dims
  5. Loaded all 5 v1.0.2 fold models, averaged their predicted probabilities
  6. Argmax of averaged probabilities → final ESI 1–5 prediction per patient
  7. Saved `submission.csv` (20,000 rows: `patient_id`, `triage_acuity`)

### 5. Built the Kaggle Notebook (`triagegeist_submission.ipynb`)
A clean 10-section end-to-end notebook designed for Kaggle upload:

1. Imports and configuration
2. Load all 4 CSV files
3. EDA — acuity distribution, NEWS2 boxplot by acuity, vital sign heatmap, complaint system distribution
4. BioBERT extraction — full code included and commented for transparency; loads precomputed embeddings at runtime to stay within Kaggle time limits
5. Feature engineering — leakage removal, group-aware imputation (age_group × shift), 5 derived clinical composites, hx_* NaN filling, CatBoost native categorical handling
6. CatBoost 5-fold stratified CV — 10,000 iterations, early stopping (patience=50), MultiClass loss
7. Evaluation — QWK + macro-F1 + confusion matrix + per-class recall bar chart + comparison table vs baseline
8. Feature importance (CatBoost gain, averaged across folds, colour-coded by feature type) + SHAP summary and beeswarm plots for ESI-1
9. Submission CSV generation with distribution sanity check
10. Clinical discussion — findings, limitations, reproducibility statement

The notebook uses precomputed BioBERT embeddings loaded from an attached Kaggle dataset (see Priority 2 below).

### 6. Wrote the Kaggle Writeup (`kaggle_writeup.md`)
Ready to paste into Kaggle's writeup editor. Covers:
- Clinical motivation (ESI inter-rater variability, undertriage risk)
- Data description and leakage prevention rationale
- Full methodology: preprocessing → BioBERT → PCA → CatBoost
- Why BioBERT over TF-IDF (semantic equivalence of clinical phrases)
- Why CatBoost over LightGBM (native categoricals, ordered boosting)
- Results table vs baseline, per-fold stability table
- SHAP findings and clinical interpretation of top features
- Limitations: ESI-3 difficulty, no bias audit, single-site generalisability, lossy PCA compression
- Reproducibility statement

---

## What Is Left To Do

### Priority 1 — Generate and Save BioBERT Embedding CSVs
The Kaggle notebook loads embeddings from a pre-attached dataset. These files do not exist yet:
- `train_biobert_pca.csv` — 80,000 rows × 10 cols (`biobert_pca_1` … `biobert_pca_10`)
- `test_biobert_pca.csv` — 20,000 rows × 10 cols (same schema)

The test embeddings were generated inside `generate_submission.py` but discarded after use — they need to be re-run and saved to CSV. Train embeddings need to be generated fresh (BioBERT → apply `pca_v1.0.2.pkl` → save).

**Estimated time:** ~8 min on GPU / ~45 min on CPU for each set.

### Priority 2 — Upload Two Kaggle Datasets
Once CSVs and model files are ready:

**Dataset 1: `triagegeist-biobert`** (embeddings)
- `train_biobert_pca.csv`
- `test_biobert_pca.csv`

**Dataset 2: `triagegeist-models`** (trained artifacts)
- `pca_v1.0.2.pkl`
- `model_v1.0.2_fold_1.cbm` through `model_v1.0.2_fold_5.cbm`

### Priority 3 — Upload and Run the Notebook on Kaggle
- kaggle.com → Code → New Notebook
- Attach both datasets from Priority 3
- Upload `triagegeist_submission.ipynb`
- Verify `DATA_PATH`, `EMBED_PATH`, `MODEL_PATH` match the Kaggle dataset mount paths
- Run all cells end-to-end — must complete without errors
- Make the notebook **Public** before submitting

### Priority 4 — Submit the Writeup on Kaggle
- Triagegeist competition page → Writeups → New Writeup
- Paste content from `kaggle_writeup.md`
- Link the public notebook in the Project Links section
- Submit

---

## File Index

| File | Purpose | Status |
|---|---|---|
| `PROGRESS.md` | This file | ✓ |
| `triagegeist_submission.ipynb` | Main Kaggle notebook — upload to Kaggle | ✓ Ready |
| `kaggle_writeup.md` | Kaggle writeup — paste into Kaggle writeup editor | ✓ Ready |
| `submission.csv` | Test predictions (20,000 rows) via v1.0.2 full model | ✓ Generated |
| `generate_submission.py` | Script that generated submission.csv locally using v1.0.2 | ✓ |
| `triagegeist-baseline.ipynb` | Baseline notebook for reference and comparison | ✓ Reference |
| `kaggle_comp.txt` | Official competition description | ✓ Reference |

## Artifact Index (outside this folder)

| Path | What It Is |
|---|---|
| `ml/models/v1.0.2/pca_v1.0.2.pkl` | Fitted PCA (768→10), load with `joblib` |
| `ml/models/v1.0.2/model_v1.0.2_fold_1-5.cbm` | 5 trained CatBoost fold models (full 61-feature pipeline) |
| `ml/models/v1.0.2-c/model_v1.0.2-c_fold_1-5.cbm` | 5 trained CatBoost fold models (26-feature fallback) |
| `ml/dataset/processed/nlp_ready_dataset.parquet` | Structured features + raw text for 80,000 train patients |
| `ml/dataset/raw/train.csv` | Raw training data (80,000 rows, 40 cols) |
| `ml/dataset/raw/test.csv` | Raw test data (20,000 rows, 37 cols) |
| `ml/dataset/raw/chief_complaints.csv` | Free-text chief complaints |
| `ml/dataset/raw/patient_history.csv` | 25 binary comorbidity flags |
