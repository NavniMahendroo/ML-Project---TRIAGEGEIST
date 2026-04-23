# VIII. Implementation Details

## A. ML Pipeline Execution Modes
The ML component exposes three distinct entry points:

- **run_train.py** — orchestrates the full pipeline: preprocessing, BioBERT embedding extraction, 5-fold CV, SHAP evaluation, and model serialization. Each version saves a model binary (.cbm) and PCA transformer (.pkl) under ml/models/<version>/
- **run_kaggle.py** — loads a versioned binary and batch-predicts the competition test set, producing a formatted submission.csv
- **run_api.py / server.py** — starts the FastAPI server, loading all three model versions into memory once via load_all_models() and serving predictions via the REST endpoints

This separation ensures that a misconfigured training run cannot accidentally overwrite a production model binary.

## B. Multi-Model Loading and Memory Sharing
At startup, load_all_models() iterates over all three version configurations in config.ALL_VERSIONS and loads each into a _registry dict keyed by version string. The registry stores the CatBoostClassifier instance and its PCA transformer per version.

BioBERT weights (dmis-lab/biobert-v1.1) are loaded once into shared globals (_shared_tokenizer, _shared_bert_model, _shared_device). Both v1.0.2 and v1.0.2-b use these shared weights; only their PCA transformers differ. v1.0.2-c skips BioBERT entirely as it was not trained with text features.

## C. Versioned Parameter System
All hyperparameters—depth, learning rate, iteration count, PCA component count, BERT model name, batch size—are stored in versioned JSON files under ml/params/ (e.g. v1.0.2.json, v1.0.2-b.json, v1.0.2-c.json). config.py loads all three at import time into an ALL_VERSIONS dict, deriving model and PCA file paths for each. This makes adding a new model version a matter of adding a JSON file and a trained binary—no code changes required.

The 5-fold model binaries (_fold_1 through _fold_5) stored alongside each version are training artifacts used for cross-validation evaluation only. The non-fold binary (model_<version>.cbm) is the production inference model.

## D. Database Design
MongoDB was selected for its flexible document model, which accommodates the variable presence of comorbidity flags across patients and the optional chatbot session fields without requiring schema migrations. Key design decisions:

- **_system_counters collection** — stores auto-increment sequences for TG- (patients), VT- (visits), and CS- (chatbot sessions) ID generation, using MongoDB's atomic findOneAndUpdate to prevent race conditions under concurrent ED load
- **Compound indexes** on patient_id + visit_date support rapid dashboard queries at production ED data volumes
- **visit document** stores engine field (e.g. ml_pipeline/v1.0.2-c) for full audit traceability of which model produced each prediction
- **chatbot_sessions** stores the complete conversation transcript and all collected/missing fields, enabling retrospective quality review

## E. Offline and Reproducibility Features
By default, the Hugging Face transformers library is configured with TRANSFORMERS_OFFLINE=1, loading BioBERT weights from a local cache directory. This allows the inference stack to operate in fully air-gapped hospital networks without any outbound internet traffic. If the local cache is absent and offline mode is active, the system gracefully degrades: BioBERT PCA features are filled with NaN (CatBoost handles these natively), and a warning is logged. Model experiments are fully reproducible: the same JSON parameter file, fixed random seed (42), and versioned dataset Parquet files deterministically reproduce any historical training run.

## F. Patient ID Normalization
The chatbot submit endpoint normalizes patient IDs before MongoDB lookup, correcting common transcription formats: TG-2, TG-002, tg-0002 → TG-0002 (uppercase prefix, four-digit zero-padded numeric suffix). If the normalized ID is still not found, the endpoint falls back to fuzzy name + age matching rather than returning an immediate 404, improving robustness for patients who misremember or misstate their ID.
