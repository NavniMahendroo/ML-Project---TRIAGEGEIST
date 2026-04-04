import os
import json

from .base_config import *

# ── The Global Switch ────────────────────────────────────────────────────────
MODEL_VERSION = 'v1.0.2'

# ── Dynamic Parameter Loading ───────────────────────────────────────────────
params_path = os.path.join(PARAMS_DIR, f'{MODEL_VERSION}.json')

if not os.path.exists(params_path):
    raise FileNotFoundError(f"Critical Error: Parameter file for version {MODEL_VERSION} not found at {params_path}")

with open(params_path, 'r') as f:
    _params = json.load(f)

# Extract parameters into global namespace for compatibility with other scripts
BERT_MODEL_NAME = _params.get('BERT_MODEL_NAME')
BERT_MAX_LENGTH = _params.get('BERT_MAX_LENGTH')
BERT_BATCH_SIZE = _params.get('BERT_BATCH_SIZE')
PCA_COMPONENTS = _params.get('PCA_COMPONENTS')
CATBOOST_PARAMS = _params.get('CATBOOST_PARAMS')
CV_FOLDS = _params.get('CV_FOLDS')
RANDOM_SEED = _params.get('RANDOM_SEED')

# ── Derived Model Paths ──────────────────────────────────────────────────────
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_VERSION, f'model_{MODEL_VERSION}.cbm')
PCA_PATH = os.path.join(MODELS_DIR, MODEL_VERSION, f'pca_{MODEL_VERSION}.pkl')
