# TriageGeist Model Roadmap

This document serves as the master record of exactly what we have built for the learning phase (`v1.0.1`) and exactly what architectural features are missing that we must add to build the production-ready model (`v1.0.2`).

## Model v1.0.1 (The "Learning" MVP)
**Status:** Ready to train today.
**Goal:** A simplified, highly interpretable CatBoost model designed for learning the absolute fundamentals of the machine learning pipeline (Data Cleaning, Handling NaNs, Target Separation, and Decision Trees) without being overwhelmed by Deep Learning NLP infrastructure.

### What WE HAVE DONE for v1.0.1
1. **Data Lake Integration:** Combined raw `train`, `patient_history`, and `chief_complaints` files into a single master Parquet file.
2. **Bias & Leakage Purge:** Successfully identified and banished 14 toxic columns (e.g., `disposition`, `ed_los_hours`, `insurance_type`) to prevent the model from cheating or learning human biases.
3. **NaN Strategy Implementation:** Intentionally chose to leave numeric NaNs alone to let CatBoost native handling take over ("Missing data as a signal").
4. **Pandas Future-Proofing:** Implemented `include=['object', 'string']` to safely identify Categorical variables and prevent future Pandas 3.0 crashes.
5. **Basic Validation:** Implemented a single `train_test_split (80/20)` to easily validate the model's performance on hidden data.

---

## Model v1.0.2 (The "Production" Final Version)
**Status:** Up Next (After compiling the learning model).
**Goal:** Reconstruct the original `v1.0.0` architecture, bringing back advanced Natural Language Processing (NLP) deep learning layers to extract hidden clinical insights from unstructured nurse triage notes.

### What IS LEFT TO DO for v1.0.2
To upgrade from `v1.0.1` to the final `v1.0.2` production model, we must execute the following complex steps:

1. **Restore NLP Data:** We must go back into the cleaning phase and rescue the `chief_complaint_raw` column from the "dropped" list.
2. **HuggingFace BioBERT Integration:** We must download the `dmis-lab/biobert-v1.1` model (as defined in your JSON). We will feed the raw triage notes into BioBERT to convert the text sentences into $768$-dimensional mathematical vector embeddings.
3. **Dimensionality Reduction (PCA):** 768 new columns is too massive for CatBoost to efficiently process alongside our clinical data. We will implement Principal Component Analysis (`PCA(n_components=10)`) to compress the 768 columns down into exactly 10 dense mathematical "Topics". 
4. **Feature Concatenation:** We will electronically fuse our 51 clinical variables from `v1.0.1` together with the 10 new PCA embedding columns to create a massive 61-feature super-matrix.
5. **Advanced Cross-Validation:** We will throw away our simple 80/20 `train_test_split`. Following your JSON (`"CV_FOLDS": 5`), we will implement a rigorous **5-Fold Stratified Cross-Validation**. The model will train itself 5 separate times on 5 different rotating vaults of data to guarantee absolute mathematical stability.
