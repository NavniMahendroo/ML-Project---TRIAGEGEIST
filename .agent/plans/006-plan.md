# 006 — Triage Acuity Model without Medical History (Model v1.0.2-c)

## Goal

Build a fallback CatBoost classifier (`v1.0.2-c`) that predicts `triage_acuity` (urgency level 1–5) similarly to our primary model (`v1.0.2`), but **strictly without** the 25 medical history features (`hx_*`). 

This model is critical for real-world ED scenarios where a patient's medical history is temporarily or permanently unavailable, yet an accurate triage prediction is still required.

---

## Data Source

- **File:** `ml/dataset/processed/master_dataset.parquet` (the primary merged training dataset).
- **Target:** `triage_acuity`.
- **Modifications:** The 25 history-related features (e.g., `hx_hypertension`, `hx_diabetes_type2`, etc.) must be explicitly dropped from the feature set before training.

---

## Pipeline Steps (Notebook 4.ipynb)

### Step 1 — Load & Prepare the Dataset

- Load the same `master_dataset.parquet` used for the initial model.
- Load the pre-computed BioBERT text embeddings / PCA components (to save time, we will reuse the NLP embeddings from the main model pipeline, or re-run PCA if specifically needed for the reduced feature space).
- Explicitly identify and drop all columns starting with `hx_` (25 columns total).
- Drop leakage columns (`ed_los_hours`, `disposition`) and non-features (`patient_id`, etc.).

### Step 2 — 5-Fold Stratified Cross Validation

- Target: `triage_acuity` (5 classes).
- Features to use: 34 features total (59 original features - 25 `hx_` features). This includes demographics, vitals, categorical fields, and the 10 BioBERT PCA dimensions.
- Use the same robust CatBoost hyperparameters from `params/v1.0.2.json` (iterations, depth, learning rate, GPU task type).
- Run 5-Fold StratifiedKFold to accurately measure the impact of dropping medical history. 
- Save the fold models to `ml/models/v1.0.2-c/model_v1.0.2-c_fold_{fold}.cbm`.

### Step 3 — Metrics & Visualization

- Generate a classification report for the out-of-fold predictions to see how much performance dropped compared to the full history model.
- Generate and save the feature importance plot. This will show which vitals or text components become relatively more important when history is taken away.
- Save metrics to `ml/metrics/v1.0.2-c/`.

### Step 4 — Crown the Best Fold as Production Model

- After CV completes, select the fold with the best accuracy.
- Save this chosen fold as the final fallback model: `ml/models/v1.0.2-c/model_v1.0.2-c.cbm`.

---

## Output Artifacts

| Artifact | Path |
|---|---|
| Fold models | `ml/models/v1.0.2-c/model_v1.0.2-c_fold_{1-5}.cbm` |
| Fallback production model | `ml/models/v1.0.2-c/model_v1.0.2-c.cbm` |
| Classification report | `ml/metrics/v1.0.2-c/classification_report.txt` |
| Feature importance plot | `ml/metrics/v1.0.2-c/feature_importance.png` |

*(Note: We will share the existing PCA transformer `pca_v1.0.2.pkl` for the text pipeline since the chief complaint vocabulary hasn't changed).*

---

## API Integration Plan (predict_api.py & runtime)

Once `v1.0.2-c` is constructed, the `predict_api.py` serving layer will be updated to a **Dual-Model Inference Architecture**:

1. **Startup / Load Runtime:**
   - Both `model_v1.0.2.cbm` (Primary, 'model a') and `model_v1.0.2-c.cbm` (Fallback, 'model c') will be loaded into RAM simultaneously.

2. **Inference Flow:**
   - When a prediction request arrives, the backend dynamically inspects the payload.
   - **Condition A:** If the 25 medical history features are populated, the payload is routed to the **Primary Model** (`v1.0.2`).
   - **Condition B:** If medical history is entirely missing or flagged as unavailable, the sparse payload is routed to the **Fallback Model** (`v1.0.2-c`).

This ensures robust capability even when patient records are incomplete directly upon ED arrival.
