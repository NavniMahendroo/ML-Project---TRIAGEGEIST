# IV. Methodology

## A. Data Preprocessing
All four data files are merged on patient_id using left joins. Columns that constitute target leakage—disposition, ed_los_hours, and any post-triage outcomes—are removed before model training. Missing continuous values are imputed with per-column medians; missing categorical values receive an explicit 'Unknown' category treated natively by CatBoost.

Five derived features are engineered from raw vitals:
- mean_arterial_pressure = (systolic_bp + 2×diastolic_bp) / 3
- pulse_pressure = systolic_bp − diastolic_bp
- shock_index = heart_rate / systolic_bp
- bmi = weight_kg / (height_cm / 100)²
- num_comorbidities = sum of all active hx_* flags

## B. BioBERT Embedding Extraction
Each patient's chief_complaint_raw string is tokenized and passed through the frozen BioBERT encoder (dmis-lab/biobert-v1.1). The [CLS] token's 768-dimensional hidden state is extracted as a fixed-length sentence representation. The encoder is loaded once at startup with TRANSFORMERS_OFFLINE=1 to avoid network calls during inference, enabling deployment in air-gapped hospital networks. A fitted PCA transformer—serialized to disk alongside the model binary—reduces embeddings from 768 to 10 components that capture the majority of complaint variance.

## C. Three-Model ML Pipeline

TriageGeist deploys three specialized CatBoost classifiers, each trained for a distinct role. Runtime model selection is automatic based on data availability at inference time.

### C.1 — v1.0.2: Primary Triage Acuity Classifier
The primary model is a CatBoostClassifier trained on the merged feature matrix of 57 columns: 47 structured variables (including 25 hx_* comorbidity flags) and 10 BioBERT PCA components. CatBoost's native categorical feature handler is used for six columns: arrival_mode, age_group, sex, pain_location, mental_status_triage, and chief_complaint_system. No manual encoding is required, eliminating a common source of target leakage.

- **Input:** 47 structured features + 25 hx_* history flags + 10 BioBERT PCA components = 57 total features
- **Output:** ESI acuity level 1–5
- **Used when:** patient history exists in MongoDB (at least one hx_* field is non-NaN)

### C.2 — v1.0.2-b: Chief Complaint System Classifier
A text-only CatBoost model trained exclusively on BioBERT embeddings of chief_complaint_raw. It maps free-text complaints to one of 14 body-system categories (cardiovascular, neurological, respiratory, gastrointestinal, musculoskeletal, infectious, dermatological, psychiatric, urological, obstetric, ophthalmological, ENT, endocrine, trauma). It uses its own separately fitted PCA transformer but shares BioBERT weights in memory with v1.0.2.

- **Input:** chief_complaint_raw text → BioBERT → PCA(10) only
- **Output:** one of 14 chief_complaint_system class labels
- **Used when:** chief_complaint_system is absent or null in the submission — its output is injected into the payload before the acuity model runs, improving primary model accuracy

### C.3 — v1.0.2-c: History-Free Fallback Acuity Classifier
Identical in architecture to v1.0.2 but trained on a feature matrix that excludes all 25 hx_* comorbidity flags. Because the model has never seen history features, its internal weights are correctly calibrated for the no-history scenario rather than treating 25 NaN values as noise injected into an otherwise complete feature vector.

- **Input:** 47 structured features + 10 BioBERT PCA components (no hx_* fields)
- **Output:** ESI acuity level 1–5
- **Used when:** no patient history record exists in MongoDB (all hx_* fields would be NaN)
- **Note:** No PCA file is needed separately; it uses the same BioBERT-derived components but the model was trained without any hx_* columns in the schema

### C.4 — Model Comparison Table

| Aspect | v1.0.2 | v1.0.2-b | v1.0.2-c |
|---|---|---|---|
| Role | Primary acuity predictor | Complaint classifier | Fallback acuity predictor |
| Output | ESI 1–5 | 14 body-system classes | ESI 1–5 |
| Uses BioBERT | Yes | Yes | Yes |
| Uses separate PCA | Yes (own .pkl) | Yes (own .pkl) | Yes (own .pkl) |
| Uses hx_* history | Yes (25 fields) | No | No |
| Total features | 57 | 10 (PCA only) | 32 |
| Triggered when | History available | cc_system missing | No history in DB |

TABLE II. THREE-MODEL PIPELINE COMPARISON

### C.5 — Runtime Routing Logic

At inference time, the backend executes the following decision sequence for every submission (both triage form and chatbot):

1. If chief_complaint_system is missing or null → call v1.0.2-b on chief_complaint_raw, inject the predicted class into the payload
2. Check MongoDB for patient history:
   - At least one hx_* field is non-NaN → use v1.0.2 (full model)
   - All hx_* fields are NaN → use v1.0.2-c (no-history fallback)
3. The engine field stored in the visit document records which model was used (e.g. ml_pipeline/v1.0.2-c)

BioBERT weights (dmis-lab/biobert-v1.1) are loaded once at server startup into shared memory and reused by both v1.0.2 and v1.0.2-b. Only the PCA transformers (.pkl) are model-specific.

## D. Training and Validation
Training uses 5-fold stratified cross-validation with a fixed random seed (42). Stratification ensures that all five ESI classes are proportionally represented in every fold, which is critical given the natural rarity of Level 1 (Resuscitation) encounters. Per-fold metrics recorded to ml/logs/ include: macro-averaged F1, weighted F1, and per-class precision and recall. The final production model is retrained on the complete training set using the optimal hyperparameter configuration identified during cross-validation. All hyperparameters are stored in versioned JSON files under ml/params/ (one file per version). Full pipeline execution—including BioBERT embedding extraction across ~80,000 records—requires approximately 30 minutes on an NVIDIA RTX 4050 laptop GPU.

## E. SHAP Explainability
Post-training, SHAP TreeExplainer [7] values are computed for a stratified sample of the training set. Per-feature SHAP summary plots and waterfall diagrams are saved to ml/logs/. Clinicians can inspect the precise contribution of each input—for instance, how a depressed spo2 value or a high news2_score shifted a prediction from Acuity 3 (Urgent) to Acuity 2 (Emergent)—supporting institutional trust and regulatory auditability.

## F. Inference API
At inference time, a single patient JSON payload arrives at POST /predict (triage form) or POST /chatbot/submit (voice bot). The payload is validated via Pydantic, the three-model routing logic executes, BioBERT embeddings are extracted (if required by the selected model), PCA is applied using the version-specific transformer, and the merged vector is scored by the selected CatBoost model. The response includes the predicted ESI class (1–5), its human-readable urgency label, the engine identifier recording which model version was used, and the assigned doctor and specialty. End-to-end latency on CPU-only hardware is under 150 ms.
