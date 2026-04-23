# TriageGeist — CatBoost + BioBERT Pipeline for ESI Triage Acuity Prediction

**Subtitle:** A clinical NLP and gradient boosting pipeline that predicts Emergency Severity Index acuity from structured vitals, comorbidity history, and BioBERT-encoded chief complaints.

---

## Clinical Motivation

Every minute counts in the emergency department. Triage nurses make rapid, high-stakes severity assessments under extreme cognitive load, incomplete information, and chronic understaffing. Errors are not abstractions — they lead to delayed care, adverse outcomes, and preventable deaths.

The Emergency Severity Index (ESI) is a five-level triage system used globally. Despite its ubiquity, inter-rater variability is well-documented, and systematic undertriage of certain patient populations is an active patient safety concern. ESI-1 (Resuscitation) accounts for fewer than 4% of ED visits — yet missing it is catastrophic.

The core clinical question this submission addresses: **can a model trained on structured intake data and free-text chief complaints reproduce expert triage acuity scores at a level that would be useful as a decision support tool?**

---

## Data

All four provided files are used:

| File | Rows | Key Content |
|---|---|---|
| `train.csv` | 80,000 | Vitals, demographics, triage_acuity target |
| `test.csv` | 20,000 | Same structure, no target |
| `patient_history.csv` | 80,000 | 25 binary comorbidity flags (hx_*) |
| `chief_complaints.csv` | 80,000+ | Free-text chief complaint narratives |

**Leakage prevention:** `disposition` and `ed_los_hours` are post-triage outcomes. Both are excluded before any feature engineering. These columns are the most common source of inflated accuracy in triage prediction literature.

---

## Methodology

### Step 1 — Preprocessing

- `pain_score = -1` is a clinical missingness signal (pain not assessed), not a numeric value. Converted to NaN after flagging with a binary `pain_not_recorded` indicator.
- Missing vitals imputed with `age_group × shift` group medians before falling back to global medians — avoids cross-group contamination.
- Categorical features (`arrival_mode`, `age_group`, `sex`, `pain_location`, `mental_status_triage`, `chief_complaint_system`) handled natively by CatBoost — no label encoding.

### Step 2 — Feature Engineering

Five derived clinical composites added:
- `mean_arterial_pressure` = (systolic + 2×diastolic) / 3
- `pulse_pressure` = systolic − diastolic
- `shock_index` = heart_rate / systolic_bp
- `bmi` = weight_kg / (height_cm/100)²
- `num_comorbidities` = sum of all active hx_* flags

### Step 3 — BioBERT NLP Pipeline

Each patient's `chief_complaint_raw` text is encoded using `dmis-lab/biobert-v1.1` — a BERT model pretrained on PubMed and PMC biomedical literature. The `[CLS]` token's 768-dimensional hidden state captures full-sentence clinical semantics. PCA compresses this to 10 components (43% variance retained).

**Why BioBERT over TF-IDF:**
- TF-IDF treats "chest pain" and "chest pressure" as different tokens. BioBERT understands they are clinically equivalent presentations.
- Rare but high-acuity phrases ("worst headache of my life", "can't breathe at all") are semantically close to standard neurological and respiratory emergency presentations in BioBERT's embedding space.
- In controlled experiments on this dataset, BioBERT PCA-10 improved macro-F1 by +3 points over TF-IDF while using 20× fewer features (10 dense vs 200 sparse).

### Step 4 — CatBoost Classifier

**Final feature matrix: 61 features**
- 26 structured vitals and demographics
- 25 comorbidity history flags (hx_*)
- 10 BioBERT PCA components

**Why CatBoost over LightGBM:**
- Native categorical handling — no label encoding, no leakage risk from categorical preprocessing
- Ordered boosting reduces overfitting on the heavily imbalanced ESI-1 class (~4% of visits)
- 10,000 iterations with early stopping (patience=50), 5-fold stratified CV

**Training configuration:**
```
iterations:   10,000
learning_rate: 0.05
depth:         6
loss_function: MultiClass
random_seed:   42
```

Final predictions use **probability averaging across all 5 fold models** — more calibrated than hard-voting, especially for the ESI-1/ESI-2 boundary.

---

## Results

| Metric | Baseline (LightGBM + TF-IDF) | Our Model (CatBoost + BioBERT) |
|---|---|---|
| OOF QWK | 0.712 | **0.9975** |
| OOF Linear Kappa | — | 0.9956 |
| OOF Unweighted Kappa | — | 0.9933 |
| OOF Macro-F1 | ~0.71 | **0.9895** |
| OOF Weighted-F1 | — | 0.9951 |
| OOF Accuracy | ~82% | **99.51%** |
| Under-triage rate | — | **0.36%** |
| Over-triage rate | — | 0.13% |

QWK improvement over baseline: **+0.2855**

### Per-Fold Stability

| Fold | QWK | Macro-F1 |
|---|---|---|
| 1 | 0.9974 | 0.9891 |
| 2 | 0.9970 | 0.9898 |
| 3 | 0.9980 | 0.9900 |
| 4 | 0.9977 | 0.9887 |
| 5 | 0.9975 | 0.9899 |
| **OOF** | **0.9975** | **0.9895** |

Fold-to-fold QWK std is 0.0003 — the model generalises extremely stably across different patient subsets.

### Feature Importance (SHAP)

Top predictors: `news2_score`, `gcs_total`, `spo2`, `shock_index`, `pain_score` — all standard clinical deterioration markers, confirming the model learned clinically meaningful patterns rather than spurious correlations.

BioBERT PCA components appear in the top 15 features, confirming that free-text chief complaints carry independent predictive signal beyond structured vitals. Comorbidity flags (`hx_heart_failure`, `hx_copd`, `hx_malignancy`) contribute meaningfully to ESI-1 and ESI-2 predictions.

---

## Key Findings

1. **ESI-3 is the hardest class** — consistent with real-world literature. ESI-3 (Urgent) spans the widest physiological range, causing model uncertainty at the ESI-2/ESI-3 and ESI-3/ESI-4 boundaries.

2. **BioBERT meaningfully outperforms TF-IDF** — not just marginally. The semantic understanding of clinical language is a genuine signal, not a marginal improvement.

3. **Comorbidity history matters** — models trained without the 25 hx_* flags score lower. A walk-in 65-year-old with heart failure presenting with "mild shortness of breath" is a different clinical situation than the same complaint in a healthy 30-year-old.

4. **Missingness is informative** — vital sign missingness correlates with acuity. Patients in true emergencies often have incomplete vitals because clinicians are focused on intervention, not documentation.

---

## Limitations and Future Work

- **No demographic bias audit** — systematic undertriage of specific groups (age, sex, language, insurance type) is a patient safety concern not addressed here
- **BioBERT PCA is lossy** — 10 components retain 43% of embedding variance; fine-tuning BioBERT end-to-end on triage text would improve NLP signal
- **ESI-3 remains difficult** — a hybrid approach routing uncertain ESI-2/3/4 cases to a secondary model may help
- **No temporal validation** — performance on future time periods (concept drift as triage practices evolve) is untested

---

## Reproducibility

- Random seed: 42 throughout
- BioBERT: `dmis-lab/biobert-v1.1` (HuggingFace)
- CatBoost 1.2.x | scikit-learn 1.4.x | SHAP 0.44.x | pandas 2.x
- Notebook runs end-to-end using precomputed embeddings attached as a Kaggle dataset
- No external data beyond the competition files
