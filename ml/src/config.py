import os

# ── Directories ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, 'dataset', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'dataset', 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# ── Raw Dataset Paths ─────────────────────────────────────────────────────────
TRAIN_CSV = os.path.join(RAW_DIR, 'train.csv')
TEST_CSV = os.path.join(RAW_DIR, 'test.csv')
PATIENT_HISTORY_CSV = os.path.join(RAW_DIR, 'patient_history.csv')
CHIEF_COMPLAINTS_CSV = os.path.join(RAW_DIR, 'chief_complaints.csv')
SAMPLE_SUBMISSION_CSV = os.path.join(RAW_DIR, 'sample_submission.csv')

# ── Processed Dataset Paths ───────────────────────────────────────────────────
TRAIN_PROCESSED = os.path.join(PROCESSED_DIR, 'train_merged.parquet')
TEST_PROCESSED = os.path.join(PROCESSED_DIR, 'test_merged.parquet')
TRAIN_ENGINEERED = os.path.join(PROCESSED_DIR, 'train_final.parquet')
TEST_ENGINEERED = os.path.join(PROCESSED_DIR, 'test_final.parquet')

# ── Model Versioning ──────────────────────────────────────────────────────────
MODEL_VERSION = 'v1.0.0'
MODEL_PATH = os.path.join(MODELS_DIR, f'model_{MODEL_VERSION}.cbm')
PCA_PATH = os.path.join(MODELS_DIR, f'pca_{MODEL_VERSION}.pkl')

# ── Target & Leakage ─────────────────────────────────────────────────────────
TARGET = 'triage_acuity'
LEAKAGE_COLS = ['ed_los_hours', 'disposition']
DROP_COLS_TRAINING = ['patient_id', 'triage_nurse_id', 'chief_complaint_raw', TARGET]
DROP_COLS_INFERENCE = ['patient_id', 'triage_nurse_id', 'chief_complaint_raw']

# ── BioBERT / NLP ─────────────────────────────────────────────────────────────
BERT_MODEL_NAME = 'dmis-lab/biobert-v1.1'
BERT_MAX_LENGTH = 64
BERT_BATCH_SIZE = 64
PCA_COMPONENTS = 10

# ── CatBoost Hyperparameters ──────────────────────────────────────────────────
CATBOOST_PARAMS = {
    'iterations': 10000,
    'learning_rate': 0.05,
    'depth': 6,
    'loss_function': 'MultiClass',
    'early_stopping_rounds': 50,
    'verbose': 100,
    'random_seed': 42,
}
CV_FOLDS = 5
RANDOM_SEED = 42
