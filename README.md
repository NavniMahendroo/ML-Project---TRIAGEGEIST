# TriageGeist Machine Learning Pipeline

source .venv/bin/activate


This repository contains the modular Machine Learning pipeline for the TriageGeist project. The architecture is split cleanly into data preprocessing, BioBERT feature engineering, CatBoost model training, and distinct gateways for inference.

This structure prevents heavy model-training code from ever crashing or tangling with the lightweight website API inference code.

---

## 📦 1. Getting Started: Heavy File Placement
Because of GitHub's file size limits (100MB+), the large raw dataset CSVs and the trained model binaries are **NOT** included in this repository. 

Before running any code on a new machine, you must obtain these files (via our team's Google Drive or Kaggle) and place them exactly here:

*   **Raw Datasets:** Place all CSV files (`train.csv`, `test.csv`, `patient_history.csv`, `chief_complaints.csv`, `sample_submission.csv`) and the Stata file (`ed00.dta`) into the **`ml/dataset/raw/`** folder.
*   **Trained Models:** Place the `model_v1.0.0.cbm` and `pca_v1.0.0.pkl` files into the **`ml/models/`** folder.

---

## 🛠️ 2. Installation
Ensure you have an active Python virtual environment (Python 3.10+ recommended), and install the identical library versions we used:

```bash
pip install -r requirements.txt
```

---

## 🚀 3. Execution Gateways
We have separated the architecture into three dedicated execution gateways at the root of the `ml/` folder. Choose the command that matches what you are trying to do:

### Option A: Running the Website API Gateway (Inference)
**When to use:** When you want to boot up the backend to serve real-time predictions for the frontend website.
**What it does:** Instantly loads the `v1.0.0.cbm` model into memory, translates a single patient JSON payload using BioBERT, and returns a `triage_acuity` prediction almost instantly. *(Does not train the model).*

```bash
python ml/run_api.py
```

### Option B: Generating a Kaggle Submission
**When to use:** When you need a CSV file to upload to the Kaggle dashboard.
**What it does:** Loads the trained `v1.0.0.cbm` model, runs lightning-fast batch predictions across the 20,000 rows in `test.csv`, and saves the formatted `submission.csv` to your computer.
```bash
python ml/run_kaggle.py
```

### Option C: Training a New Model From Scratch
**When to use:** ONLY when you have modified the original datasets or want to re-train the core model with different hyperparameters in `ml/src/config.py`.
**What it does:** Cleans the data, extracts 80,000 new BioBERT text embeddings, runs thorough 5-Fold Cross Validation, generates SHAP explainability reports in `ml/logs/`, and completely overwrites the existing master model.
**Warning:** This takes ~30 minutes on an RTX 4050 GPU.

```bash
python ml/run_train.py
```