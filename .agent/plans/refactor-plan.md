# TriageGeist Refactor Plan

This plan organizes all refactoring work into three phases.

---

## Phase 1: ML Folder Cleanup (Notebook-First Workflow)

> **Status**: Decided ✅

Currently the `ml/src/` folder contains pipeline scripts (`data_preprocessing.py`, `feature_engineering.py`, `train.py`, `evaluate.py`) that duplicate what can be done directly in notebooks.

### Step 1.1 — Delete redundant pipeline scripts
- **Delete from `ml/src/`**: `data_preprocessing.py`, `feature_engineering.py`, `train.py`, `evaluate.py` — replaced by the notebook.
- **Delete from `ml/`**: `run_train.py`, `run_kaggle.py`, `abc.py` — CLI entry points and scratch files no longer needed.
- **Keep in `ml/src/`**: Only `predict_api.py`, `config.py`, and `base_config.py` — the only files the backend imports.

### Step 1.2 — Move all training to notebooks
- All data merging, BERT embeddings, PCA, and model training will be done inside `ml/notebooks/`.
- Kaggle submission generation also done inside a notebook cell.

### Step 1.3 — Model Versioning (existing convention, keep as-is)
The repo already has a clean flat-file versioning system — **do not change this**:
- `ml/models/model_v1.0.0.cbm` — trained CatBoost model
- `ml/models/pca_v1.0.0.pkl` — fitted PCA for BERT embeddings
- `ml/params/v1.0.0.json` — all hyperparameters used for that version
- **`MODEL_VERSION = 'v1.0.0'`** in `config.py` — single line to switch which model the API uses

Each new training run saves files with a new version suffix (e.g., `v1.1.0`), then `MODEL_VERSION` is updated in `config.py` to point the API at it.

### Step 1.4 — Schema preview CSV
- Generate `ml/dataset/processed/schema_preview.csv` using `ml/scripts/make_schema_preview.py`.
- Contains field names as columns, datatype as row 2, and first 10 data rows — for human review only.

<!-- PLACEHOLDER: Add more Phase 1 steps here -->

---

## Phase 2: Backend & Database Refactor

> **Status**: Planning 🔄

The backend is currently split across only two files (`main.py`, `database.py`), with schema mismatches between the MongoDB model, the Pydantic API schema, and the training dataset fields.

### Step 2.1 — Database Resilience (Unique IDs)
Currently, if MongoDB is down, the system uses a static `"TG-TEMP-0"` ID, which creates duplicates.
- **In `database.py`**: Modify the fallback logic to generate a unique temporary ID if the database connection fails.
- **Implementation**: Use a random string or UUID prefix (e.g., `TG-OFFLINE-A1B2`).
- **Goal**: Ensure every patient case remains uniquely identifiable even during database downtime.

### Step 2.2 — Field Name & Datatype Consistency
Currently, there are mismatches between the raw CSV data, the ML model features, and the Backend API schema.
- **Unified Schema**: Standardize all field names (API, DB, and Model) to match the **`train.csv`** and **`patient_history.csv`** headers exactly.
    - **Example**: Use `hx_hypertension` instead of `hypertension`.
    - **Example**: Ensure vitals like `heart_rate` and `respiratory_rate` are treated as **`float`** in the Pydantic schema to match the raw technical data.
- **Categorical Sync**: Ensure `sex` (e.g., "M"/"F") and `arrival_mode` values match the training dataset labels precisely before being passed to the model.
- **Frontend Mapping**: Maintain user-friendly labels in the UI but map them to the correct backend fields (e.g., `hx_obesity` for "Obesity") during form submission.

### Step 2.3 — MongoDB Schema Design
Standardize the MongoDB storage format to match the **`train.csv`** and **`patient_history.csv`** fields (66 unique fields + predicting target).
- **Storage Strategy**: Store the raw patient input precisely as it appears in the training data (e.g., `heart_rate: float`).
- **Audit Logging**: Store the prediction engine used (`ml_pipeline` or `rule_based_fallback`) and the model version (`MODEL_VERSION`) for every patient record.
- **Unique IDs**: Use the resilient ID generation from Step 2.1 as the primary key.

### Step 2.4 — Backend Code Structure (Feature-Based Architecture)
Break out of the monolithic two-file structure (`main.py`, `database.py`) into a feature-based organization. This allows specific features to be added (like Voice Chat, Staffing Queues) without cluttering the core triage logic.

**Proposed Directory Structure:**
```
backend/
├── triage/               ← ML prediction & clinical fallback logic
│   ├── router.py         ← /predict endpoint
│   ├── schema.py         ← Pydantic models (PatientInput)
│   ├── service.py        ← Orchestrator for ML vs. Rule fallback
│   └── fallback.py       ← The Clinical-Rules Engine
├── patients/             ← Patient record management
│   ├── router.py
│   ├── schema.py
│   └── service.py
├── users/                ← Nurses, Admins, Doctors (User management)
│   ├── router.py
│   ├── schema.py         ← RBAC (Role-Based Access Control)
│   └── service.py
├── database.py           ← Shared MongoDB connection utility
├── config.py             ← Environment-wide settings
└── server.py             ← App entry point; registers all feature routers
```

**Scalability Benefits:**
- **Surge Management**: The `triage` and `queue` logic can be updated independently to handle department load shifts.
- **Voice Support**: New feature modules (e.g., `voice/`) can be added cleanly as new folders.
- **Role Isolation**: Clear separation between `patients/` (PHI data) and `users/` (staff credentials).

<!-- PLACEHOLDER: Add more Phase 2 steps here -->

---

## Phase 3: Frontend Refactor (Modular JSX Architecture)

> **Status**: Planning 🔄

The goal is to move from a monolithic `App.jsx` to a modular structure that supports future features (Voice, Admin panels) while remaining simple to navigate.

### Step 3.1 — `src/` Folder Organization
Maintain the `src/` directory as the root for all application code to keep configuration files separate.
- **Organization**: Create `src/pages/`, `src/hooks/`, and `src/constants/` to categorize code.
- **Language**: Stick strictly to **.jsx** (JavaScript) for all components.

### Step 3.2 — Screen-Based Split (Cleaning `App.jsx`)
Break down the currently monolithic `App.jsx` (573 lines) into distinct files.

- **Constants**: Move `severityConfig` and `intakeDefaults` to `src/constants/`.
- **Hooks**: Move `handleSubmit`, `handleChange`, and state logic into a custom `src/hooks/useTriage.js`.
- **Components**: Move UI utilities like `Spinner`, `InputField`, and `Backdrop` to `src/components/`. 
- **Pages**: Move the main triage layout into `src/pages/Triage.jsx`. `App.jsx` will only handle the outer shell.

### Step 3.3 — Schema Sync (1:1 Name Mapping)
⚠️ **CRITICAL**: Any changes made in Phase 2 to standardize field names (e.g., `hx_hypertension` instead of `hypertension`) must be reflected throughout the frontend layer.
- **Form Mapping**: Pydantic/MongoDB field names must be 1:1 with the `name` attributes in the HTML forms.
- **Result Mapping**: Ensure the `TriageCard` reads from the updated response keys returned by the backend.

### Step 3.4 — Logic Extraction (Optional/Advanced)
- Move `formatApiError` and other pure utility functions into a separate `src/lib/utils.js`.

<!-- PLACEHOLDER: Add more Phase 3 steps here -->

---

## Reference: Data Reorganization Notes

> These notes were decided earlier and apply across phases.

Instead of merging data on-the-fly, we use pre-processed "Golden" parquet files:
- `train_merged.parquet` / `test_merged.parquet` — raw 3-CSV merge, no extra operations
- `train_final.parquet` / `test_final.parquet` — above + BERT PCA embeddings added
- Missing values in vitals (`systolic_bp`, `diastolic_bp`, `mean_arterial_pressure`, `pulse_pressure`, `shock_index`, `respiratory_rate`, `temperature_c`) are currently unhandled in the final parquets. See `CRITICAL.md` for details.
