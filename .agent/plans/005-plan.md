# 005 — Chief Complaint System Classifier (Model v1.0.2-b)

## Goal

Build a dedicated CatBoost classifier that predicts `chief_complaint_system` (14 classes) from only the `chief_complaint_raw` free-text field. This model will eventually auto-fill the `chief_complaint_system` dropdown in the triage form so the nurse doesn't have to manually pick it.

---

## Data Source

- **File:** `ml/dataset/raw/chief_complaints.csv`
- **Columns:** `patient_id`, `chief_complaint_raw`, `chief_complaint_system`
- **Rows:** 100,000 (no nulls)
- **Target:** `chief_complaint_system` — 14 balanced classes (~7,100 each):
  gastrointestinal, infectious, respiratory, endocrine, musculoskeletal, genitourinary, psychiatric, trauma, cardiovascular, ophthalmic, other, neurological, ENT, dermatological

---

## Pipeline Steps (Notebook 3.ipynb)

### Step 1 — Load & Prepare the 2-Column Parquet

- Read `chief_complaints.csv`.
- Drop `patient_id` — it is not a feature.
- Save as `ml/dataset/processed/cc_system_dataset.parquet` with only two columns: `chief_complaint_raw` and `chief_complaint_system`.
- Display shape, sample rows, and class distribution.

### Step 2 — BioBERT Embedding Extraction

- Load BioBERT (`dmis-lab/biobert-v1.1`) exactly as notebook 2 does (same tokenizer, max_length=64, batch_size=64).
- GPU if available, else CPU.
- Extract the `[CLS]` token embedding (768-D) for every row.
- Result: a numpy matrix of shape `(100000, 768)`.

### Step 3 — PCA Compression (768 → 10)

- Fit a new PCA transformer on the 768-D matrix, compressing to 10 components.
- This is a **separate** PCA from the one used in v1.0.2 triage training (different data distribution, different purpose).
- Create a DataFrame with columns `biobert_pca_1` through `biobert_pca_10`.
- Print explained variance ratio and total retained info.
- Save this PCA to: `ml/models/v1.0.2/pca_v1.0.2-b.pkl`

### Step 4 — Encode the Target

- `chief_complaint_system` is a string label. CatBoost can handle string targets directly (MultiClass mode).
- No manual label encoding needed — CatBoost will handle it natively.
- Define X = the 10 PCA columns, Y = `chief_complaint_system`.

### Step 5 — 5-Fold Stratified Cross Validation with CatBoost

- Use the same CatBoost hyperparameters from `params/v1.0.2.json` (iterations=10000, depth=6, lr=0.05, GPU, early_stopping_rounds=50).
- No categorical features this time — all 10 PCA columns are numeric.
- 5-Fold StratifiedKFold, shuffle=True, random_seed=42.
- Track out-of-fold predictions to compute the true pipeline accuracy.
- Save each fold model to: `ml/models/v1.0.2/model_v1.0.2-b_fold_{fold}.cbm`
- Report per-fold accuracy and overall pipeline accuracy.

### Step 6 — Metrics & Visualization

- Print the full classification report (precision, recall, f1 per class).
- Plot a confusion matrix heatmap (14x14).
- Plot feature importance bar chart (top 10 PCA dimensions).
- Save reports/plots to `ml/metrics/v1.0.2-b/`.

### Step 7 — Crown the Best Fold as Production Model

- After CV completes, the user picks the best fold based on accuracy.
- Copy/rename the best fold file to: `ml/models/v1.0.2/model_v1.0.2-b.cbm`
- This is the single model file the backend will load for inference.

---

## Output Artifacts

| Artifact | Path |
|---|---|
| 2-column parquet | `ml/dataset/processed/cc_system_dataset.parquet` |
| PCA transformer | `ml/models/v1.0.2/pca_v1.0.2-b.pkl` |
| Fold models | `ml/models/v1.0.2/model_v1.0.2-b_fold_{1-5}.cbm` |
| Production model | `ml/models/v1.0.2/model_v1.0.2-b.cbm` |
| Classification report | `ml/metrics/v1.0.2-b/classification_report.txt` |
| Confusion matrix plot | `ml/metrics/v1.0.2-b/confusion_matrix.png` |
| Feature importance plot | `ml/metrics/v1.0.2-b/feature_importance.png` |

---

## Key Differences from Notebook 2 (v1.0.2 Triage Model)

| Aspect | Notebook 2 (Triage) | Notebook 3 (CC System) |
|---|---|---|
| Target | `triage_acuity` (5 classes) | `chief_complaint_system` (14 classes) |
| Input features | 49 pre-PCA fields + 10 PCA = 59 total | 10 PCA columns only (text-only model) |
| Data source | `master_dataset.parquet` (merged) | `chief_complaints.csv` (standalone) |
| PCA file | `pca_v1.0.2.pkl` | `pca_v1.0.2-b.pkl` (separate) |
| Categorical features | 6 (arrival_mode, sex, etc.) | 0 (all numeric PCA) |
| Model file | `model_v1.0.2.cbm` | `model_v1.0.2-b.cbm` |

---

## Integration Plan (Post-Training, Not This Notebook)

Once the model is trained and saved, the backend inference path will be updated:
1. Load `pca_v1.0.2-b.pkl` and `model_v1.0.2-b.cbm` at startup alongside the existing triage model.
2. When a triage submission arrives with `chief_complaint_raw` but no `chief_complaint_system`, run the text through BioBERT → PCA-b → CatBoost-b to auto-predict the system.
3. Use the predicted `chief_complaint_system` as input to the main triage model.
