# Plan 010 — Multi-Model ML Routing

## What Exists Now

There are now **3 trained models** under `ml/models/`, each with a distinct role:

| Version | Files | Description |
|---|---|---|
| `v1.0.2` | `model_v1.0.2.cbm` + `pca_v1.0.2.pkl` + 5 fold `.cbm` files | **Primary triage acuity classifier.** Structured vitals + BioBERT (PCA 10) + 25 hx_* history fields → predicts ESI acuity 1–5 |
| `v1.0.2-b` | `model_v1.0.2-b.cbm` + `pca_v1.0.2-b.pkl` + 5 fold `.cbm` files | **Chief complaint system classifier.** Text-only model: BioBERT → PCA(10) → CatBoost → predicts which of 14 body-system classes the complaint belongs to (e.g. `cardiovascular`, `neurological`) |
| `v1.0.2-c` | `model_v1.0.2-c.cbm` + 5 fold `.cbm` files | **Fallback triage acuity classifier.** Same as v1.0.2 but trained *without* the 25 `hx_*` history features. Used when patient history is unavailable at ED arrival |

Each version has a matching params file at `ml/params/<version>.json`.

---

## The Problem

Currently `ml/src/config.py` has a single hardcoded `MODEL_VERSION = 'v1.0.2'` that drives everything — one model path, one PCA path. The `predict_api.py` module loads one CatBoost model and one PCA into module-level globals (`_model`, `_pca`, `_bert_model`). There is no mechanism to load or call the other two models.

The backend's `triage/service.py` calls `predict_api.predict_patient(pre_pca_payload)` which always hits whatever the single loaded model is. It has no concept of selecting between models.

---

## What Needs to Be Built

### Decision Logic — which model to call when

```
Incoming triage submission
        │
        ├── Does patient have history (hx_* fields)?
        │       YES → use v1.0.2  (primary, full-feature)
        │       NO  → use v1.0.2-c (fallback, no-history)
        │
        └── Is chief_complaint_system missing/null from the submission?
                YES → call v1.0.2-b first to classify it, then proceed above
                NO  → skip v1.0.2-b, use the value already provided
```

So in the worst case (no history, no chief complaint system) the call order is:
1. `v1.0.2-b` → infer `chief_complaint_system` from free text
2. `v1.0.2-c` → predict acuity without history

In the best case (history present, complaint system known):
1. `v1.0.2` directly

### Changes Required

#### `ml/src/predict_api.py`
- Replace the single-model globals with a dict of model instances keyed by version string
- Add a `load_all_models()` function that loads v1.0.2, v1.0.2-b, and v1.0.2-c
- Each model entry holds its own `CatBoostClassifier`, `PCA`, `BERT tokenizer/model` (v1.0.2-b and v1.0.2 share the same BioBERT weights but have separate PCA transformers; v1.0.2-c has no PCA at all)
- Add a `predict_with_model(version, patient_data)` function to call a specific version
- Keep `predict_patient()` as the old entrypoint for backwards compatibility (routes to v1.0.2)

#### `ml/src/config.py`
- Load all three param files at import time into a dict `ALL_VERSIONS`
- Derive model/PCA paths for each version dynamically
- Keep `MODEL_VERSION` pointing to v1.0.2 as the default

#### `backend/src/triage/service.py`
- Replace the single `_predict_triage(pre_pca_payload)` call with a new `_run_ml_pipeline(pre_pca_payload, history_document)` function that:
  1. Checks if `chief_complaint_system` is missing → calls v1.0.2-b if so, injects the result into the payload
  2. Checks if history is all NaN → selects v1.0.2-c, otherwise v1.0.2
  3. Calls the selected model and returns the prediction

#### `backend/src/triage/service.py` — `load_ml_model()`
- Change to call `predict_api.load_all_models()` on startup instead of `predict_api.load_model()`
- Update `get_engine_status()` to report which versions are loaded

#### `backend/server.py`
- No route changes needed; the multi-model logic is fully internal to the service layer

---

## Key Constraints to Keep in Mind

- `v1.0.2-b` is **text-only** — it only needs `chief_complaint_raw` + its own BioBERT+PCA. It does NOT use structured vitals or hx_* fields.
- `v1.0.2-c` has **no PCA file** (`pca_v1.0.2-c.pkl` does not exist) — confirmed by file listing. It was trained without BioBERT features entirely, so `predict_api` must skip the BERT step for this version.
- `v1.0.2` and `v1.0.2-b` both use BioBERT (`dmis-lab/biobert-v1.1`) — the tokenizer and BERT weights can be **shared** in memory; only the PCA transformers are separate.
- The 5 fold `.cbm` files (`_fold_1` through `_fold_5`) are **training artifacts for cross-validation** — the production model to call for inference is the non-fold file (`model_<version>.cbm`).
- `history_available` is determined by checking whether all 25 `hx_*` fields in the payload are `NaN` — if they are all NaN it means no history record was found in MongoDB for this patient.

---

## Files to Change

| File | Change |
|---|---|
| `ml/src/predict_api.py` | Multi-model loading and dispatch |
| `ml/src/config.py` | Load all param files, derive all paths |
| `backend/src/triage/service.py` | Model selection logic, call `load_all_models()` |

No frontend changes. No schema changes. No new API routes.

---

## Status

| Task | Status |
|---|---|
| Understand model roles and files | ✅ Done |
| Write this plan | ✅ Done |
| Implement `ml/src/config.py` multi-version loading | ✅ Done |
| Implement `ml/src/predict_api.py` multi-model dispatch | ✅ Done |
| Implement `backend/src/triage/service.py` routing logic | ✅ Done |
| Test end-to-end: form submit with history | ⬜ Pending |
| Test end-to-end: chatbot submit without history | ⬜ Pending |
| Test end-to-end: missing chief_complaint_system | ⬜ Pending |
