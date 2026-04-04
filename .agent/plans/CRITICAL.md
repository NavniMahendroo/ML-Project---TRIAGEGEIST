# TriageGeist Critical Problems Tracker

This file lists the current problems we know about in the plan and model integration.
It is intentionally problem-focused so we can come back and solve items later in order.

## Critical Problems To Solve Right Now

### 1. `59` vs `61` feature mismatch
- [004-plan.md](./004-plan.md) currently says the reconstructed `v1.0.2` inference row should have `59 columns`.
- The actual saved `v1.0.2` CatBoost model expects `61 features`.
- This was verified from:
  - `ml/models/v1.0.2/model_v1.0.2.cbm`
  - `ml/notebooks/2.ipynb`
  - `ml/dataset/processed/schema_preview.csv`
- This is a hard blocker because the backend reconstruction logic must target the real model schema, not the outdated number in the plan.

### 2. Current missing-value handling does not match the temporary plan
- Temporary product decision:
  - `chief_complaint_system` will be sent as `NaN` for now.
  - `patient_history` / `hx_*` values will be sent as `NaN` when history is unavailable.
- Current problem:
  - the existing inference code does not preserve those missing values the way we want.
  - in the current wrapper, missing categorical values are converted to `"Unknown"` and missing numeric values are converted to `0`.
- This is a hard blocker because our current agreed temporary behavior is "send `NaN`", but the live inference path does not currently honor that.

### 3. Current live API contract is smaller than the real `v1.0.2` model contract
- The current backend/frontend flow only sends the simplified triage payload used by the demo app.
- The real `v1.0.2` model expects the full reconstructed feature row.
- This is a hard blocker because the new backend path must reconstruct the full `61`-feature row before calling the model.

## Known Problems Accepted For Later

### 4. `chief_complaint_system` is missing for now
- For now we will send `NaN`.
- Later we will train a separate model that predicts `chief_complaint_system` from `chief_complaint_raw`.
- Until that model exists, this remains a known serve-time gap.

### 5. `patient_history` is missing for some patients
- For existing patients with known history, we will send the stored history values.
- For new patients or patients without known history, we will send `NaN`.
- Later we will train another model that predicts triage safely without relying on those history values.
- Until that model exists, this remains a known serve-time gap.

### 6. Some patient master fields may change over time
- Fields like `height`, `weight`, and similar master-data values may change across visits.
- For now we are assuming they remain constant.
- This is not being solved right now, but it is a known data-model problem that must be revisited later.

### 7. Existing-patient search / re-entry flow is deferred
- Right now we are not building search options.
- Current focus is only on taking patient entry.
- This means duplicate-patient handling and existing-patient lookup are deferred problems.

### 8. Temporary self-registration values are not part of the final clean schema
- For now:
  - `site_id` will be hardcoded as `SITE-0001`
  - `nurse_id` will be `"self"` when the patient enters data personally
- This is accepted for now, but it is still a temporary schema compromise we may need to clean up later.

## Canonical `v1.0.2` Model Fact

The saved `v1.0.2` model currently expects exactly:
- `61 total features`
- `6 categorical features`
- `55 non-categorical / numeric features`

This `61`-feature expectation is the current source of truth.
