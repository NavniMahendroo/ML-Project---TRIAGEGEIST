import os

# ── Directories ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, 'dataset', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'dataset', 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
PARAMS_DIR = os.path.join(BASE_DIR, 'params')

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

# ── Target & Leakage ─────────────────────────────────────────────────────────
TARGET = 'triage_acuity'
LEAKAGE_COLS = ['ed_los_hours', 'disposition']
DROP_COLS_TRAINING = ['patient_id', 'triage_nurse_id', 'chief_complaint_raw', TARGET]
DROP_COLS_INFERENCE = ['patient_id', 'triage_nurse_id', 'chief_complaint_raw']
