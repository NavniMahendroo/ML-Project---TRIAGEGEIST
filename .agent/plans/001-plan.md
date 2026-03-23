# TriageGeist Machine Learning Pipeline: Refactoring Plan (001)

## Overview
This plan establishes a modular, production-ready structure for the Machine Learning (ML) component of the TriageGeist project, preparing the central repository to also support `frontend/` and `backend/` web application folders in the future.

All directory changes, data storage, and machine learning scripts will reside strictly inside the `ml/` directory.

---

## 📂 Phase 0: Subdirectory Restructuring (Inside `ml/`)
Prior to writing or modifying any code, the physical files must be organized into a clean structure inside the `ml/` target directory.

1.  **Keep `ml/abc.py` as-is:**
    *   Leave the current monolithic script exactly where it is for reference purposes while we build out the modular pipeline.
2.  **Create `ml/dataset/` directory:**
    *   Move `train.csv`, `test.csv`, `patient_history.csv`, `chief_complaints.csv`, and the raw historical `ed00.dta` data into the `ml/dataset/raw/` subfolder.
    *   Processed files will navigate to `ml/dataset/processed/`.
3.  **Create `ml/models/` directory:**
    *   Establish a centralized location to store all trained ML models.
    *   *Naming Convention Requirement:* Models must be saved with version numbers to track experiments (e.g., `v1.0.0.cbm`, `v1.0.1.cbm`).
4.  **Create `ml/src/` directory:**
    *   Move all core Python executing modules into this folder.
5.  **Create `ml/notebooks/` directory:**
    *   Move the `no-no-no-more-leak.ipynb` and `triagist leak_solve.ipynb` files into this `ml/notebooks/` folder to isolate EDA and scratchpad work.
6.  **Create `ml/logs/` directory:**
    *   Save training outputs automatically using Python's `logging` module to track errors and historical CV accuracy over time.
7.  **Verify `requirements.txt`:**
    *   Ensure all necessary libraries are listed so standard environments replicate flawlessly.

---

## 🐍 Phase 1: Modular Python Breakdown (Execution Order)

### Step 1: `ml/src/config.py` (Configuration settings)
Centralizes all hardcoded variables, paths, and hyperparameters.

### Step 2: `ml/src/data_preprocessing.py` (Data Cleaning & Merging)
Loads CSVs from `ml/dataset/raw/`, removes leakage columns, merges datasets, and saves to `ml/dataset/processed/`.

### Step 3: `ml/src/feature_engineering.py` (Embeddings & Feature Extraction)
Loads the processed dataset, extracts 768-D BioBERT text embeddings, applies PCA (10 dimensions), and re-saves the ML-ready dataset to `ml/dataset/processed/`.

### Step 4: `ml/src/train.py` (Model Training Pipeline)
Loads the ML-ready dataset, uses `config.py` parameters to train a `CatBoostClassifier` with 5-fold CV, logs metrics to `ml/logs/`, and saves the model to `ml/models/v1.0.0.cbm`.

### Step 5: `ml/src/evaluate.py` (Explainability & Insights)
Loads the saved `ml/models/` version, computes `.shap_values()`, and generates English feature importance evaluations.

### Step 6: `ml/src/predict_kaggle.py` (Batch Inference Engine)
Contains the exact formatting logic to load `test.csv`, load the pre-trained model, generate batch predictions, and save the exact `submission.csv` format required by Kaggle.

### Step 7: `ml/src/predict_api.py` (Real-Time Web API Engine)
Contains the specialized formatting logic to accept a single patient JSON dictionary, clean the record, pass it through the pre-trained NLP/model pipeline, and instantly return a single `triage_acuity` prediction score.

---

## 🚀 Phase 2: Pipeline Execution Gateways

To guarantee that the heavy model training code never accidentally interferes with the fast website API code, we have entirely split the `main.py` concept into three distinct, dedicated root scripts. 

### 1. `ml/run_train.py` (Building the Master Model)
*   **What it does:** Orchestrates the entire top-to-bottom learning pipeline. Imports from `ml/src/` to execute Data Preprocessing -> NLP Feature Engineering -> Model Training -> SHAP Evaluation.
*   **When to use it:** Only when you have a new dataset or want to adjust hyperparameters to create `v1.0.1.cbm`.
*   **Terminal Command:** `python ml/run_train.py`

### 2. `ml/run_kaggle.py` (Kaggle Submission Generator)
*   **What it does:** Bypasses training completely. Loads your best `v1.0.0.cbm` model and simply runs `predict_kaggle.py` on the `test.csv` file to spit out your `submission.csv`.
*   **When to use it:** When you need a CSV file to upload to the Kaggle dashboard.
*   **Terminal Command:** `python ml/run_kaggle.py`

### 3. `ml/run_api.py` (Website Backend Endpoint)
*   **What it does:** Dedicated strictly to your future web application. It acts as the routing script that loads the model into memory just once upon startup, listens for incoming patient JSON payloads from your frontend, runs `predict_api.py`, and shoots back the `triage_acuity` prediction to the user's browser.
*   **When to use it:** When you are actively running your frontend/backend website.
*   **Terminal Command:** `python ml/run_api.py`
