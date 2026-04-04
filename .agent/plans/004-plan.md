# TriageGeist Website & Database Overhaul Plan (004)

## Overview
This plan covers the full redesign of the TriageGeist database schema and website flow.
The goal is to move from a single flat triage form to a properly normalized, 
multi-collection MongoDB architecture that mirrors a real Emergency Department.

---

## Phase 1: Database & Backend Setup

### Step 1.1: Drop Old MongoDB Collections
The old schema is obsolete. Drop these collections manually from local MongoDB before writing any new code:
- `patients` (old flat schema)
- `counters` (old serial number counter)

---

### Step 1.2: New Schema Reference
The new normalized MongoDB schema has **6 collections**. All are defined below.

#### Collection 1: `patients`
Stores patient master data. Created on first registration and reused across visits.
Most fields are expected to remain stable, though a later update flow may modify them if needed.

| Field | Type | Notes |
|---|---|---|
| `patient_id` | String (PK) | Auto-generated, format: `TG-0001` ... (4-digit zero-padded, ascending) |
| `name` | String | ✏️ Entered at registration |
| `age` | Int | ✏️ Entered. Dataset range: 0–120 |
| `sex` | String (Enum) | ✏️ `"M"` / `"F"` |
| `language` | String (Enum) | ✏️ `"Arabic"` / `"English"` / `"Estonian"` / `"Finnish"` / `"Other"` / `"Russian"` / `"Somali"` / `"Swedish"` |
| `insurance_type` | String (Enum) | ✏️ Entered by **nurse**. `"military"` / `"none"` / `"private"` / `"public"` / `"unknown"` |
| `num_prior_ed_visits_12m` | Int | 🧮 Auto-incremented by backend. Starts at 0. |
| `num_prior_admissions_12m` | Int | 🧮 Auto-incremented by backend when `disposition` = admitted. Range: 0–9 |
| `num_active_medications` | Int | ✏️ Entered. Range: 0–20 |
| `num_comorbidities` | Int | ✏️ Entered. Range: 0–20 |
| `weight_kg` | Float | ✏️ Entered. Range: 2.0–148.5 kg |
| `height_cm` | Float | ✏️ Entered. Range: 45.0–210.0 cm |
| `age_group` | String (Enum) | 🧮 Calculated from `age` — `"pediatric"` (0–17) / `"young_adult"` (18–39) / `"middle_aged"` (40–64) / `"elderly"` (65+) |
| `bmi` | Float | 🧮 Calculated — `weight_kg / (height_cm / 100)²`. Range: 10.0–65.0 |

---

#### Collection 2: `patient_history`
Stores the 25 medical history flags from `patient_history.csv`.
Linked to `patients` via `patient_id`. All fields prefixed with `hx_`.

> **⚠️ Usually filled AFTER admission.** This collection may not exist during first-time registration or triage.
> If prior history is already available for an existing patient, triage should use it.
> If history is unavailable, triage must still run with missing `hx_*` values.

| Field | Type | Notes |
|---|---|---|
| `patient_id` | String (FK) | Links to `patients` |
| `hx_hypertension` | Bool | ✏️ Nurse-entered |
| `hx_diabetes_type2` | Bool | ✏️ Nurse-entered |
| `hx_diabetes_type1` | Bool | ✏️ Nurse-entered |
| `hx_asthma` | Bool | ✏️ Nurse-entered |
| `hx_copd` | Bool | ✏️ Nurse-entered |
| `hx_heart_failure` | Bool | ✏️ Nurse-entered |
| `hx_atrial_fibrillation` | Bool | ✏️ Nurse-entered |
| `hx_ckd` | Bool | ✏️ Nurse-entered |
| `hx_liver_disease` | Bool | ✏️ Nurse-entered |
| `hx_malignancy` | Bool | ✏️ Nurse-entered |
| `hx_obesity` | Bool | ✏️ Nurse-entered |
| `hx_depression` | Bool | ✏️ Nurse-entered |
| `hx_anxiety` | Bool | ✏️ Nurse-entered |
| `hx_dementia` | Bool | ✏️ Nurse-entered |
| `hx_epilepsy` | Bool | ✏️ Nurse-entered |
| `hx_hypothyroidism` | Bool | ✏️ Nurse-entered |
| `hx_hyperthyroidism` | Bool | ✏️ Nurse-entered |
| `hx_hiv` | Bool | ✏️ Nurse-entered |
| `hx_coagulopathy` | Bool | ✏️ Nurse-entered |
| `hx_immunosuppressed` | Bool | ✏️ Nurse-entered |
| `hx_pregnant` | Bool | ✏️ Nurse-entered |
| `hx_substance_use_disorder` | Bool | ✏️ Nurse-entered |
| `hx_coronary_artery_disease` | Bool | ✏️ Nurse-entered |
| `hx_stroke_prior` | Bool | ✏️ Nurse-entered |
| `hx_peripheral_vascular_disease` | Bool | ✏️ Nurse-entered |

> **Storage vs Model note:** All `hx_*` fields are stored as `Bool` in MongoDB (`true`/`false`).
> When history exists, the backend casts them to `Int64` (`1`/`0`) to match the training data schema.
> When the `patient_history` document is missing, the reconstructed `hx_*` features remain `NaN`.

---

#### Collection 3: `visits`
One document per Emergency Department visit. 
Links patient to clinical event and stores all visit-specific data.

#### 3a. Visit Identity & Logistics
| Field | Type | Source |
|---|---|---|
| `visit_id` | String (PK) | Auto-generated, format: `VT-0001` ... (4-digit zero-padded, ascending) |
| `patient_id` | String (FK) | Links to `patients` |
| `site_id` | String (FK) | ✏️ Provided by the intake flow / application context. Format: `SITE-0001`. No auth in this phase. |
| `nurse_id` | String (FK) | ✏️ Provided by the submitting workflow context. Format depends on actor policy for the phase. No auth in this phase. |
| `arrival_mode` | String (Enum) | ✏️ `"ambulance"` / `"brought_by_family"` / `"helicopter"` / `"police"` / `"transfer"` / `"walk-in"` |
| `arrival_time` | Native Date | 🕒 Stored as MongoDB **Date** object. Transmitted as ISO 8601. Used for system logs (not model input for v1.0.2). |
| `transport_origin` | String (Enum) | ✏️ Entered by **nurse**. `"home"` / `"nursing_home"` / `"other_hospital"` / `"outdoor"` / `"public_space"` / `"school"` / `"workplace"` |

#### 3b. Clinical Presentation
| Field | Type | Source |
|---|---|---|
| `pain_location` | String (Enum) | ✏️ `"abdomen"` / `"back"` / `"chest"` / `"extremity"` / `"head"` / `"multiple"` / `"none"` / `"pelvis"` / `"unknown"` |
| `mental_status_triage` | String (Enum) | ✏️ `"agitated"` / `"alert"` / `"confused"` / `"drowsy"` / `"unresponsive"` |
| `chief_complaint_raw` | String | ✏️ Free text entered by nurse/patient |
| `chief_complaint_system` | String (Enum) | 🤖 Optional in the current phase. If the secondary classifier is not yet available, this value may be missing at triage time and will be normalized in the ML layer. Later, a Logistic Regression classifier (Phase 4a) will predict it from `chief_complaint_raw`. Overridable by nurse. |

#### 3c. Vitals (Entered by Nurse)
| Field | Type | Source |
|---|---|---|
| `heart_rate` | Float | ✏️ Entered. Dataset range: 30.0–207.7 bpm |
| `respiratory_rate` | Float | ✏️ Entered. Dataset range: 8.0–51.5 |
| `temperature_c` | Float | ✏️ Entered. Dataset range: 35.1–41.8 °C |
| `spo2` | Float | ✏️ Entered. Dataset range: 60.4–100.0 % |
| `systolic_bp` | Float | ✏️ Entered. Dataset range: 40.0–226.9 mmHg |
| `diastolic_bp` | Float | ✏️ Entered. Dataset range: 20.0–134.8 mmHg |
| `gcs_total` | Int | ✏️ Entered. Range: 3–15 |
| `pain_score` | Int | ✏️ Entered (patient self-reports). Range: 0–10 |

#### 3d. Derived Vitals (Auto-Calculated by Backend)
Never entered manually. Computed the moment the nurse submits vitals.

| Field | Type | Formula |
|---|---|---|
| `mean_arterial_pressure` | Float | `(systolic_bp + 2 × diastolic_bp) / 3`. Range: 30.7–145.1 |
| `pulse_pressure` | Float | `systolic_bp − diastolic_bp`. Range: −51.0–163.7 |
| `shock_index` | Float | `heart_rate / systolic_bp`. Range: 0.19–4.77 |
| `news2_score` | Int | Standard NHS formula from HR, RR, SpO₂, Temp, BP, GCS. Range: 0–17 |

#### 3e. Prediction Output & Backend-Derived Fields
| Field | Type | Source |
|---|---|---|
| `triage_acuity` | Int (1–5) | 🤖 Predicted (ml_v1.0.2) |
| `urgency_label` | String (Enum) | 🧮 Backend-Derived from acuity mapping |
| `engine` | String (Enum) | ⚙️ Backend-Set (ml_pipeline/fallback) |

#### 3f. Post-Visit Fields (Entered Later by Nurse / Doctor)
| Field | Type | Source |
|---|---|---|
| `disposition` | String (Enum) | ✏️ `"admitted"` / `"deceased"` / `"discharged"` / `"lama"` / `"lwbs"` / `"observation"` / `"transferred"` |
| `ed_los_hours` | Float | ✏️ Entered after visit concludes. Range: 0.0–17.51 hrs |

---

#### Collection 4: `sites`
| Field | Type | Notes |
|---|---|---|
| `site_id` | String (PK) | Format: `SITE-0001` |
| `name` | String | ✏️ Admin-seeded |

---

#### Collection 5: `nurses`
| Field | Type | Notes |
|---|---|---|
| `nurse_id` | String (PK) | Format: `NURSE-0001` |
| `name` | String | ✏️ Admin-seeded |

---

#### Collection 6: `doctors`
| Field | Type | Notes |
|---|---|---|
| `doctor_id` | String (PK) | Format: `DOC-0001` |
| `name` | String | ✏️ Admin-seeded |

---

### Step 1.3: Refactor `backend/database.py` & Create `backend/utils/`
Update the backend core to handle unified logic and clinical calculations:

1. **Create `backend/utils/` Organization**:
   - `id_generator.py`: Unified `get_next_id(name, prefix)` using atomic `find_one_and_update`.
   - `clinical_utils.py`: **Backend-only** clinical math (`BMI`, `MAP`, `Shock Index`, `NEWS2`).
   - `data_utils.py`: `normalize_enum` and `normalize_gender` sanitizers.
2. **Refactor `database.py`**:
   - Register ALL 6 collections: `patients`, `visits`, `patient_history`, `sites`, `nurses`, `doctors`.
   - **Remove Fallback**: The "Offline Mode" logic is deleted. If MongoDB is disconnected, return a `500 Server Error`.

---

### Step 1.4: Create & Run Seed Script
Create `backend/scripts/seed.py` to pre-populate MongoDB with initial lookup data.

- Create folder: `backend/scripts/`
- Seed **5 Sites** (`SITE-0001` through `SITE-0005`) into `sites` collection
- Seed **10 Nurses** (`NURSE-0001` through `NURSE-0010`) into `nurses` collection
- Script must be **idempotent** — skips records that already exist

```bash
python scripts/seed.py
```

---

## Phase 2: Runtime Flow

### 2a. Runtime ML Contract
To keep responsibilities clean, the **backend** will own non-ML reconstruction and the **ML layer (`ml/src/predict_api.py`)** will own text embedding, PCA, and final schema verification.

1. **Backend Service**: Fetches raw data from `patients`, `visits`, and `patient_history` when available; computes derived clinical features; and sends the ML layer the reconstructed pre-PCA payload.
2. **History Rule**: If `patient_history` exists, triage uses those values. If it does not exist, triage still runs and the `hx_*` fields remain `NaN`.
3. **Chief Complaint System Rule**: In the current phase, `chief_complaint_system` is optional. If unavailable, the ML layer will normalize the missing categorical value to `"Unknown"`.
4. **ML predict_api**: Converts `chief_complaint_raw` to BioBERT embeddings, applies PCA, verifies the final **61-feature** model schema, normalizes missing categorical values, and returns only `triage_acuity`.
5. **Backend Response Rule**: After ML returns `triage_acuity`, the backend derives `urgency_label` from the acuity mapping and returns both values to the frontend.

---

### 2b. User Flow

#### Who Can Register a Patient
Both a **patient themselves** and a **nurse** can initiate the registration and triage flow.
No authentication is required in this phase. Auth for nurses, doctors, and admins will be added later.

---

#### New Patient Flow
When a new patient arrives and has never been registered before:

```
1. New Patient arrives at ED
2. Patient / Nurse opens the registration form
3. Patient details are entered (age, sex, language, insurance, weight, height, etc.)
4. Vitals are entered (heart rate, BP, SpO2, etc.)
5. Chief complaint is typed in free text
6. On submit:
   a. Backend creates a new `patients` document         ← One-time record
   b. Backend auto-calculates BMI, age_group
   c. Backend auto-calculates MAP, pulse_pressure, shock_index, news2_score from vitals
   d. Backend reconstructs the model payload with missing `hx_*` values because no history is available yet
   e. Backend calls ML model → gets triage_acuity
   f. Backend derives urgency_label from triage_acuity
   g. Backend creates a new `visits` document            ← Per-visit record
   h. Triage result is displayed on screen with serial number
7. patient_history is NOT collected at this point
```

---

#### Later Expansion: Existing Patient Flow
When a patient has already been registered in a previous visit:

```
1. Patient / Nurse searches by patient_id (or name)
2. Patient record is fetched from `patients` collection
   — No re-entry of static fields needed
3. Nurse enters vitals + chief complaint for this specific visit
4. On submit:
   a. Backend fetches existing `patients` document
   b. Backend fetches existing `patient_history` document if it exists
   c. Backend auto-calculates derived vitals
   d. Backend calls ML model → gets triage_acuity
      - with history values if history exists
      - without history values if history does not exist
   e. Backend derives urgency_label from triage_acuity
   f. Backend creates a NEW `visits` document only       ← patients doc untouched
   g. Triage result displayed
```

---

#### Post-Admission: Medical History Entry
After a patient has been admitted and diagnosed by a doctor:

```
1. Nurse opens the patient record
2. Nurse fills in the 25 hx_* medical history fields
3. Backend creates / updates the `patient_history` document for that patient_id
```
This step is decoupled from the current visit's triage submission, but it can improve future triage predictions when history becomes available for later visits.

---

## Resolved Questions
- ✅ **Registration Flow**: New patient → create `patients` + `visits` simultaneously.
  Existing patient → create `visits` only, fetch `patients` data via `patient_id`.
- ✅ **Auth**: No auth in this phase. Will be added later for nurses, doctors, admins.
- ✅ **Medical History**: If history exists, use it during triage. If not, triage still runs with missing `hx_*` values.
- ✅ **`chief_complaint_system`**: Optional for now. If unavailable at triage time, the ML layer normalizes it to `"Unknown"`. A secondary classifier will be added later. See Phase 4a.

---

### 2c. ML Integrity & Feature Reconstruction

#### 2c.1 The "De-normalization" Strategy
The CatBoost model (`v1.0.2`) was trained on a flat source row, but the actual saved production model expects exactly **61 inference features**. To maintain "Perfect Prediction" with our 3-table split, the backend must reconstruct the exact pre-PCA feature payload in RAM, and the ML layer must append the 10 PCA columns before calling `.predict()`.

| Group | Strategy |
|---|---|
| **Demographics** | Pulled from the `patients` document. |
| **Current Vitals** | Pulled from the incoming `visits` form. |
| **Medical History** | Use stored history when available. If unavailable, keep the 25 `hx_*` features as `NaN`. |
| **Temporal** | **NONE**: Model `v1.0.2` does not use time. |
| **Derived** | **From Backend/DB**: Read directly from the `visits` record (BMI, MAP, Shock Index, NEWS2). |
| **System Label** | Optional in the current phase. If missing, the ML layer normalizes it to `"Unknown"`. Later this can be replaced by the Secondary Pipeline (Phase 4a). |

#### 2c.2 Canonical `v1.0.2` Inference Schema
The saved `v1.0.2` model currently expects these exact **61 features**:

#### Categorical Features (6)
- `arrival_mode`
- `age_group`
- `sex`
- `pain_location`
- `mental_status_triage`
- `chief_complaint_system`

#### Numeric Features (55)
- `age`
- `num_prior_ed_visits_12m`
- `num_prior_admissions_12m`
- `num_active_medications`
- `num_comorbidities`
- `systolic_bp`
- `diastolic_bp`
- `mean_arterial_pressure`
- `pulse_pressure`
- `heart_rate`
- `respiratory_rate`
- `temperature_c`
- `spo2`
- `gcs_total`
- `pain_score`
- `weight_kg`
- `height_cm`
- `bmi`
- `shock_index`
- `news2_score`
- `hx_hypertension`
- `hx_diabetes_type2`
- `hx_diabetes_type1`
- `hx_asthma`
- `hx_copd`
- `hx_heart_failure`
- `hx_atrial_fibrillation`
- `hx_ckd`
- `hx_liver_disease`
- `hx_malignancy`
- `hx_obesity`
- `hx_depression`
- `hx_anxiety`
- `hx_dementia`
- `hx_epilepsy`
- `hx_hypothyroidism`
- `hx_hyperthyroidism`
- `hx_hiv`
- `hx_coagulopathy`
- `hx_immunosuppressed`
- `hx_pregnant`
- `hx_substance_use_disorder`
- `hx_coronary_artery_disease`
- `hx_stroke_prior`
- `hx_peripheral_vascular_disease`
- `biobert_pca_1`
- `biobert_pca_2`
- `biobert_pca_3`
- `biobert_pca_4`
- `biobert_pca_5`
- `biobert_pca_6`
- `biobert_pca_7`
- `biobert_pca_8`
- `biobert_pca_9`
- `biobert_pca_10`

#### Reconstruction Ownership
- **Backend owns**:
  - fetching patient / visit / history data
  - clinical derived values (`age_group`, `BMI`, `MAP`, `pulse_pressure`, `shock_index`, `NEWS2`)
  - reconstructing the pre-PCA feature payload
  - preserving `NaN` for unavailable numeric/history values
- **ML `predict_api` owns**:
  - BioBERT embedding from `chief_complaint_raw`
  - PCA transformation
  - final schema alignment against the saved CatBoost model
  - categorical normalization to `"Unknown"`

#### 2c.3 Step-by-Step ML Safety Plan
To ensure the transition doesn't break the model:

1. **Schema Alignment**: Validate the final reconstructed inference DataFrame has exactly **61 columns** and matches the saved `v1.0.2` model feature order.
2. **Median Imputation (Vitals Only)**: If a mandatory vital is missing (e.g., failed BP cuff), use the dataset medians stored in ML config/constants.
3. **History Handling**: If `patient_history` exists, pass the actual values. If it does not exist, preserve `NaN` for the 25 `hx_*` features.
4. **Categorical Strings**: Pass categorical values exactly as the model expects. If a categorical feature is unavailable for now (especially `chief_complaint_system`), normalize it to `"Unknown"` in the ML layer.

#### 2c.4 Simulation Test
Before going live, we will run a **Model Integrity Script**:
- Load 10 rows from the original `train.csv`.
- Run one pass with real history values intact.
- Run a second pass with the 25 `hx_*` columns forced to `NaN`.
- Feed both through the new backend reconstruction logic.
- Verify that the model runs correctly in both modes: with history when available, and without history when unavailable.
- **Success Criteria**: The pipeline produces valid predictions in both modes, and missing history does not crash reconstruction or inference.

---

## Phase 3: Frontend Website Integration & Testing

### Goal
Build the new frontend on top of the Phase 1 + Phase 2 backend flow so the website can be tested end to end before we add more ML work.

### Scope For This Phase
- Connect the frontend to the new normalized backend flow.
- Support the **new patient** registration + triage path first.
- Display the returned triage result clearly.
- Confirm that the website can create the right backend records and render the result without manual DB work.

### Frontend Work Items
#### Step 1: Build the new intake flow
```
1. Create the new patient registration / triage form
2. Capture the required patient master data
3. Capture the required visit-time vitals and presentation fields
4. Submit the payload to the new backend flow
```

#### Step 2: Build the result view
```
1. Show serial number / visit identifier context
2. Show triage_acuity and the backend-derived urgency_label
3. Show engine used
4. Keep chief_complaint_system optional for now
```

#### Step 3: Validate the website flow
```
1. Submit a new patient from the website
2. Verify patients and visits documents are created correctly
3. Verify triage result is returned and displayed correctly
4. Verify the website works as the primary testing surface for the system
```

### Pass Criteria
- A user can complete the new patient triage flow from the website without manual backend intervention.
- The backend stores the expected records correctly.
- The frontend displays the prediction result correctly.
- The end-to-end website flow is stable enough to serve as the baseline before later ML enhancements.

---

## Phase 4: Later ML Improvements

### 4a. Secondary ML Pipeline — Chief Complaint System Classifier (Later)

#### Goal
Automatically predict the clinical body system (e.g. "Cardiovascular", "Respiratory")
from the nurse's free-text `chief_complaint_raw` entry.
This is displayed as a suggestion alongside the triage result — the nurse can override it.

#### Current Status
This is a later enhancement, not a blocker for the current `v1.0.2` integration.
Until this classifier is built, `chief_complaint_system` may be missing at triage time and will be normalized to `"Unknown"` by the ML layer.

#### Why This Works Without Extra Data
The original Kaggle dataset already contains both:
- `chief_complaint_raw` — the raw text sentence
- `chief_complaint_system` — the labeled body system category

This means we have pre-labeled training data with zero extra effort.

#### Implementation Plan

##### Step 1: Training (new `ml/notebooks/3.ipynb`)
```
1. Load the master_dataset.parquet
2. Reuse the already-computed BioBERT embeddings (768-dim) from notebook 2
3. Use chief_complaint_system as the target label Y
4. Train a Logistic Regression classifier on the 768-dim embeddings
   (No PCA needed here — more dimensions = better text classification)
5. Save the classifier to ml/models/complaint_classifier/complaint_clf.pkl
```

##### Step 2: Inference (predict_api.py)
```
When a visit is submitted:
1. BioBERT already produces the 768-dim embedding for chief_complaint_raw
2. Pass the SAME embedding to the Logistic Regression classifier
3. Get predicted chief_complaint_system label
4. Return the predicted chief_complaint_system to the backend
5. The main triage model still returns only triage_acuity
6. The backend derives urgency_label and builds the final API response
```

##### Step 3: Backend Response Update
The backend builds the `/predict` response payload after ML returns `triage_acuity`.
At this stage, the backend also adds `chief_complaint_system` when that classifier exists.
In this payload:
- `triage_acuity` comes from the ML model
- `urgency_label` is derived by the backend from `triage_acuity`
```json
{
  "serial_number": "TG-00042",
  "triage_acuity": 2,
  "urgency_label": "Emergent",
  "chief_complaint_system": "Cardiovascular",
  "engine": "ml_pipeline"
}
```

##### Step 4: Frontend Display
Show the backend response on the result card.
This includes the ML-predicted `triage_acuity`, the backend-derived `urgency_label`, and the optional `chief_complaint_system` badge.
Mark it clearly as AI-suggested so the nurse can override if needed.

---

### 4b. Future Triage Model For Missing History (Later)

#### Goal
Train a future triage model that is explicitly optimized for patients whose `patient_history` is unavailable at triage time.

#### Current Status
This is a later improvement, not a blocker for the current website launch.
For now, the system continues using `v1.0.2` with real history when available and `NaN` history values when unavailable.

#### Why This Is A Separate Future Step
- The current `v1.0.2` model was trained with the history features present in the dataset schema.
- The current serving plan allows missing history at runtime.
- A dedicated future model can be trained and evaluated specifically for the no-history scenario instead of relying only on missing-value behavior.

#### Future Implementation Direction
```
1. Build a training dataset / training strategy that does not depend on patient_history availability
2. Train and evaluate a triage model designed for missing-history cases
3. Compare it against current v1.0.2 behavior on no-history patients
4. Decide later whether to replace or route between models
```
