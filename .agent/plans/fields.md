# TriageGeist Dataset Field Lifecycle

This document chronicles the fate of the various columns provided in the original `master_dataset.parquet` (compiled from the Kaggle Competition data) and explains exactly how they were treated in our Production Pipeline (`v1.0.2`).

## 🎯 1. The Target Field (The Answer Key)

*   **`triage_acuity`**: **USED (As Target)**. This is the 1-5 integer label assigned by the real triage nurse. During training, we drop this from the input (`X`) and use it exclusively as the answer key (`Y`). During deployment, the CatBoost model predicts this exact integer.

## 🗑️ 2. The Dropped Fields (Deleted intentionally)

In `2.ipynb`, we explicitly deleted 13 columns before sending data to the AI. These fall into three distinct categories of useless or dangerous data:

### A. Operational Identifiers (Noise)
These are random IDs. AI systems will attempt to mathematically memorize IDs (e.g., assuming Nurse #42 always gives bad triage scores).
*   **`patient_id`**: **DROPPED**. Random patient number.
*   **`site_id`**: **DROPPED**. Hospital location code.
*   **`triage_nurse_id`**: **DROPPED**. The ID of the nurse doing the triaging. 

### B. Temporal & Demographic Bias (Noise)
These fields technically exist before triage, but they don't impact the purely clinical urgency of a patient.
*   **`arrival_hour`**, **`arrival_day`**, **`arrival_month`**, **`arrival_season`**, **`shift`**: **DROPPED**. While time of day impacts hospital crowding, clinical urgency (heart attacks) is independent of the time of day.
*   **`language`**, **`transport_origin`**, **`insurance_type`**: **DROPPED**. To prevent the AI from establishing biases based on demographics or wealth/insurance status.

### C. Target Leakage (Illegal Cheating)
These fields represent events that happen **AFTER** the triage decision is made. If the AI is allowed to see these fields, it will cheat and achieve 100% accuracy, but will immediately crash in the real world.
*   **`disposition`**: **DROPPED**. Did the patient get admitted to the ICU or discharged? (We don't know this at the triage desk!)
*   **`ed_los_hours`**: **DROPPED**. Emergency Department Length of Stay. (We don't know how long they will stay when they first arrive!)

## 🧬 3. The Natural Language Processing Field (Transformed)

*   **`chief_complaint_raw`**: **TRANSFORMED & DROPPED**. The AI cannot do math on raw text sentences. 
    1. We fed this column into **HuggingFace BioBERT** to extract mathematical context.
    2. We used **PCA** to compress the output into exactly 10 numeric columns (`biobert_pca_1` through `biobert_pca_10`).
    3. Once the 10 numeric columns were glued onto the DataFrame, the original text column was completely deleted so CatBoost wouldn't crash.

## 📊 4. The Core Medical Features (Used as Inputs)

These remaining clinical measurements were passed completely intact into CatBoost as the core `X` training features. This is the exact schema our React frontend and FastAPI backend submit:

*   **`age`**: Patient age (Numeric)
*   **`sex`**: Patient biological sex (Categorical string: "M" / "F")
*   **`arrival_mode`**: How they arrived (Categorical string: "walk-in", "ambulance", etc.)
*   **`heart_rate`**: Clinical Vital (Numeric)
*   **`respiratory_rate`**: Clinical Vital (Numeric)
*   **`spo2`**: Oxygen saturation (Numeric)
*   **`systolic_bp`**: Blood pressure high reading (Numeric)
*   **`diastolic_bp`**: Blood pressure low reading (Numeric)
*   **`temperature_c`**: Oral temperature (Numeric)
*   **`pain_score`**: Self-reported 1-10 (Numeric)
*   **`gcs_total`**: Glasgow Coma Scale (Numeric)
*   **`news2_score`**: National Early Warning Score (Numeric)
