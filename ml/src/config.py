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

# ── All Production Versions ──────────────────────────────────────────────────
# Loaded at import time so predict_api can reference paths without re-parsing JSON.
_ALL_VERSIONS = {}

for _ver in ('v1.0.2', 'v1.0.2-b', 'v1.0.2-c'):
    _p = os.path.join(PARAMS_DIR, f'{_ver}.json')
    if not os.path.exists(_p):
        continue
    with open(_p, 'r') as _f:
        _vparams = json.load(_f)
    _model_path = os.path.join(MODELS_DIR, _ver, f'model_{_ver}.cbm')
    _pca_path = os.path.join(MODELS_DIR, _ver, f'pca_{_ver}.pkl')
    _ALL_VERSIONS[_ver] = {
        'params': _vparams,
        'model_path': _model_path,
        'pca_path': _pca_path if os.path.exists(_pca_path) else None,
        'bert_model_name': _vparams.get('BERT_MODEL_NAME'),
        'bert_max_length': _vparams.get('BERT_MAX_LENGTH', 64),
        'bert_batch_size': _vparams.get('BERT_BATCH_SIZE', 64),
        'pca_components': _vparams.get('PCA_COMPONENTS'),
    }

ALL_VERSIONS = _ALL_VERSIONS
