import pandas as pd
import numpy as np
import logging
import os

# Default to offline mode unless explicitly overridden in the runtime environment.
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import joblib
import torch
from catboost import CatBoostClassifier
from transformers import AutoTokenizer, AutoModel

from . import config
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'predict_api.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ── Shared BioBERT weights (v1.0.2 and v1.0.2-b use the same BERT model) ────
_shared_tokenizer = None
_shared_bert_model = None
_shared_device = None

# ── Per-version registry ─────────────────────────────────────────────────────
# Each entry: { 'model': CatBoostClassifier, 'pca': joblib|None }
_registry: dict[str, dict] = {}

# Legacy single-model reference kept so existing callers of _model don't break.
_model = None


def _load_bert(bert_model_name: str):
    """Load BioBERT tokenizer + model into shared globals (only once)."""
    global _shared_tokenizer, _shared_bert_model, _shared_device
    if _shared_bert_model is not None:
        return
    log.info('Loading shared BioBERT: %s', bert_model_name)
    try:
        _shared_tokenizer = AutoTokenizer.from_pretrained(bert_model_name, local_files_only=True)
        _shared_bert_model = AutoModel.from_pretrained(bert_model_name, local_files_only=True)
    except Exception as local_exc:
        is_offline = (
            os.getenv("HF_HUB_OFFLINE", "0") == "1"
            or os.getenv("TRANSFORMERS_OFFLINE", "0") == "1"
        )
        if is_offline:
            log.warning("Local BioBERT not found (offline). Text embeddings disabled. Error: %s", local_exc)
            return
        log.info("Local BioBERT not found — downloading from Hugging Face...")
        try:
            _shared_tokenizer = AutoTokenizer.from_pretrained(bert_model_name)
            _shared_bert_model = AutoModel.from_pretrained(bert_model_name)
        except Exception as remote_exc:
            log.warning("BioBERT download failed. Text embeddings disabled. Error: %s", remote_exc)
            return

    _shared_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _shared_bert_model = _shared_bert_model.to(_shared_device)
    log.info('BioBERT loaded on %s.', _shared_device)


def _load_version(ver: str):
    """Load a single model version into the registry if not already loaded."""
    if ver in _registry:
        return
    vcfg = config.ALL_VERSIONS.get(ver)
    if not vcfg:
        raise RuntimeError(f"Version '{ver}' not found in config.ALL_VERSIONS.")

    log.info('Loading CatBoost model: %s', ver)
    cb = CatBoostClassifier()
    cb.load_model(vcfg['model_path'])

    pca = None
    if vcfg['pca_path']:
        log.info('Loading PCA for %s', ver)
        pca = joblib.load(vcfg['pca_path'])
        # Load shared BioBERT if this version needs it
        if vcfg['bert_model_name']:
            _load_bert(vcfg['bert_model_name'])

    _registry[ver] = {'model': cb, 'pca': pca, 'vcfg': vcfg}
    log.info('Version %s ready.', ver)


def load_all_models():
    """Load all three production versions. Called once at server startup."""
    global _model
    for ver in config.ALL_VERSIONS:
        _load_version(ver)
    # Keep legacy _model pointing at the primary version
    _model = _registry.get('v1.0.2', {}).get('model')
    log.info('All ML models loaded: %s', list(_registry.keys()))


def load_model():
    """Legacy entrypoint — loads only v1.0.2. Kept for backwards compatibility."""
    _load_version('v1.0.2')
    global _model
    _model = _registry['v1.0.2']['model']


def get_engine_status() -> dict:
    return {
        'loaded_versions': list(_registry.keys()),
        'bert_loaded': _shared_bert_model is not None,
    }


def get_model_metadata() -> dict:
    """Returns metadata for the primary triage model (v1.0.2)."""
    _load_version('v1.0.2')
    cb = _registry['v1.0.2']['model']
    feature_names = list(cb.feature_names_)
    cat_indices = cb.get_cat_feature_indices()
    categorical_features = [feature_names[i] for i in cat_indices]
    pca_features = [c for c in feature_names if c.startswith("biobert_pca_")]
    pre_pca_features = [c for c in feature_names if c not in pca_features]
    return {
        "feature_names": feature_names,
        "categorical_features": categorical_features,
        "pca_features": pca_features,
        "pre_pca_features": [*pre_pca_features, "chief_complaint_raw"],
    }


def get_bert_embeddings(text_list, tokenizer, model, device, batch_size: int = 64, max_length: int = 64):
    model.eval()
    all_embeddings = []
    use_amp = device.type == 'cuda'
    for i in tqdm(range(0, len(text_list), batch_size), desc='BERT Embeddings'):
        batch_texts = text_list[i:i + batch_size]
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt',
        ).to(device)
        with torch.no_grad():
            with torch.cuda.amp.autocast(enabled=use_amp):
                outputs = model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().float().numpy()
            all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)


def _run_inference(ver: str, patient_data: dict) -> int:
    """
    Core inference for a single version. Returns raw integer prediction.
    Handles BERT+PCA when the version has a PCA file, skips it otherwise.
    """
    _load_version(ver)
    entry = _registry[ver]
    cb: CatBoostClassifier = entry['model']
    pca = entry['pca']
    vcfg = entry['vcfg']

    feature_names = list(cb.feature_names_)
    cat_indices = cb.get_cat_feature_indices()
    cat_cols = [feature_names[i] for i in cat_indices]
    num_cols = [c for c in feature_names if c not in cat_cols]

    df = pd.DataFrame([patient_data])

    # Append BioBERT PCA columns if this version uses them
    if pca is not None and vcfg.get('pca_components'):
        n_components = vcfg['pca_components']
        bert_cols = [f'biobert_pca_{i+1}' for i in range(n_components)]
        if _shared_tokenizer is not None and _shared_bert_model is not None and _shared_device is not None:
            texts = df['chief_complaint_raw'].fillna('No Data').tolist() if 'chief_complaint_raw' in df.columns else ['No Data']
            raw_embeddings = get_bert_embeddings(
                texts,
                _shared_tokenizer,
                _shared_bert_model,
                _shared_device,
                batch_size=vcfg['bert_batch_size'],
                max_length=vcfg['bert_max_length'],
            )
            bert_pca = pca.transform(raw_embeddings)
        else:
            bert_pca = np.full((1, n_components), np.nan)
        df_bert = pd.DataFrame(bert_pca, columns=bert_cols, index=df.index)
        df = pd.concat([df, df_bert], axis=1)

    X = df.reindex(columns=feature_names)
    for col in cat_cols:
        X[col] = X[col].fillna('Unknown').astype(str)
    for col in num_cols:
        X[col] = pd.to_numeric(X[col], errors='coerce')

    return int(cb.predict(X).flatten()[0])


def predict_chief_complaint_system(chief_complaint_raw: str) -> str:
    """
    Use v1.0.2-b to classify a free-text complaint into one of the 14 body-system classes.
    Returns the predicted class label as a string.
    """
    _load_version('v1.0.2-b')
    cb = _registry['v1.0.2-b']['model']
    pca = _registry['v1.0.2-b']['pca']
    vcfg = _registry['v1.0.2-b']['vcfg']

    if pca is None or _shared_tokenizer is None or _shared_bert_model is None:
        log.warning('v1.0.2-b: BERT/PCA unavailable — cannot classify chief complaint system.')
        return None

    n_components = vcfg['pca_components']
    bert_cols = [f'biobert_pca_{i+1}' for i in range(n_components)]

    raw_embeddings = get_bert_embeddings(
        [chief_complaint_raw or 'No Data'],
        _shared_tokenizer,
        _shared_bert_model,
        _shared_device,
        batch_size=vcfg['bert_batch_size'],
        max_length=vcfg['bert_max_length'],
    )
    bert_pca = pca.transform(raw_embeddings)
    df = pd.DataFrame(bert_pca, columns=bert_cols)

    feature_names = list(cb.feature_names_)
    X = df.reindex(columns=feature_names)

    prediction = cb.predict(X).flatten()[0]
    log.info('v1.0.2-b chief_complaint_system prediction: %s', prediction)
    return str(prediction)


def predict_triage_acuity(patient_data: dict, has_history: bool) -> dict:
    """
    Select v1.0.2 (with history) or v1.0.2-c (without history) and predict acuity.
    Returns { 'triage_acuity': int, 'model_version': str }.
    """
    ver = 'v1.0.2' if has_history else 'v1.0.2-c'
    log.info('Predicting triage acuity with %s (has_history=%s)', ver, has_history)
    acuity = _run_inference(ver, patient_data)
    return {'triage_acuity': acuity, 'model_version': ver}


def predict_patient(patient_data: dict) -> dict:
    """Legacy entrypoint — always uses v1.0.2. Kept for backwards compatibility."""
    _load_version('v1.0.2')
    acuity = _run_inference('v1.0.2', patient_data)
    result = {'triage_acuity': acuity}
    log.info('predict_patient (legacy): %s', result)
    return result
