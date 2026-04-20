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

def get_bert_embeddings(text_list, tokenizer, model, device):
    model.eval()
    all_embeddings = []
    use_amp = device.type == 'cuda'
    for i in tqdm(range(0, len(text_list), config.BERT_BATCH_SIZE), desc='BERT Embeddings'):
        batch_texts = text_list[i:i + config.BERT_BATCH_SIZE]
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=config.BERT_MAX_LENGTH,
            return_tensors='pt',
        ).to(device)
        with torch.no_grad():
            with torch.cuda.amp.autocast(enabled=use_amp):
                outputs = model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().float().numpy()
            all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'predict_api.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# These are loaded once when the module is first imported, keeping API responses fast.
_model = None
_tokenizer = None
_bert_model = None
_pca = None
_device = None


def get_model_metadata() -> dict:
    load_model()
    feature_names = list(_model.feature_names_)
    cat_indices = _model.get_cat_feature_indices()
    categorical_features = [feature_names[index] for index in cat_indices]
    pca_features = [column for column in feature_names if column.startswith("biobert_pca_")]
    pre_pca_features = [column for column in feature_names if column not in pca_features]
    return {
        "feature_names": feature_names,
        "categorical_features": categorical_features,
        "pca_features": pca_features,
        "pre_pca_features": [*pre_pca_features, "chief_complaint_raw"],
    }


def load_model():
    global _model, _tokenizer, _bert_model, _pca, _device
    if _model is None:
        log.info('Loading CatBoost model into memory...')
        _model = CatBoostClassifier()
        _model.load_model(config.MODEL_PATH)
        
        if os.path.exists(config.PCA_PATH):
            log.info('Loading PCA transformer...')
            _pca = joblib.load(config.PCA_PATH)
            log.info(f'Loading BioBERT tokenizer and model: {config.BERT_MODEL_NAME}')
            try:
                _tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME, local_files_only=True)
                _bert_model = AutoModel.from_pretrained(config.BERT_MODEL_NAME, local_files_only=True)
            except Exception as local_exc:
                is_offline = (
                    os.getenv("HF_HUB_OFFLINE", "0") == "1"
                    or os.getenv("TRANSFORMERS_OFFLINE", "0") == "1"
                )
                if is_offline:
                    log.warning(
                        "Local BioBERT files not found while offline. Continuing without text embeddings. Error: %s",
                        local_exc,
                    )
                    _tokenizer = None
                    _bert_model = None
                else:
                    log.info("Local BioBERT files not found. Attempting to download from Hugging Face...")
                    try:
                        _tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME)
                        _bert_model = AutoModel.from_pretrained(config.BERT_MODEL_NAME)
                    except Exception as remote_exc:
                        log.warning(
                            "Failed to download BioBERT. Continuing without text embeddings. Error: %s",
                            remote_exc,
                        )
                        _tokenizer = None
                        _bert_model = None

            if _bert_model is not None:
                _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                _bert_model = _bert_model.to(_device)
            else:
                _device = None
        else:
            log.info('No PCA file found for this version. Skipping BioBERT loading.')
            
        log.info('All models loaded properly.')


def predict_patient(patient_data: dict) -> dict:
    """
    Accepts a single patient record as a dict (from website JSON payload) and
    returns a dict with the predicted triage_acuity.

    Example input:
    {
        "age": 45, "sex": "Male", "chief_complaint_raw": "chest pain",
        "heart_rate": 102, "spo2": 94, ...
    }
    """
    load_model()

    metadata = get_model_metadata()
    missing_input_fields = [
        field for field in metadata["pre_pca_features"] if field not in patient_data
    ]
    if missing_input_fields:
        raise ValueError(f"Incoming payload is missing required pre-PCA fields: {missing_input_fields}")

    df = pd.DataFrame([patient_data])

    # Extract BERT embedding for the single record.
    # If BioBERT isn't available (offline cache miss), fill PCA text features as NaN.
    if 'chief_complaint_raw' in df.columns and _pca is not None:
        bert_cols = [f'biobert_pca_{i+1}' for i in range(config.PCA_COMPONENTS)]
        if _tokenizer is not None and _bert_model is not None and _device is not None:
            texts = df['chief_complaint_raw'].fillna('No Data').to_list()
            bert_features = get_bert_embeddings(texts, _tokenizer, _bert_model, _device)
            bert_pca = _pca.transform(bert_features)
            df_bert = pd.DataFrame(bert_pca, columns=bert_cols, index=df.index)
        else:
            df_bert = pd.DataFrame(np.nan, columns=bert_cols, index=df.index)
        df = pd.concat([df, df_bert], axis=1)

    # Ensure incoming data perfectly matches the CatBoost training schema
    expected_cols = metadata["feature_names"]
    X = df.reindex(columns=expected_cols)

    # Force categorical features to be strings
    cat_col_names = metadata["categorical_features"]
    for col in cat_col_names:
        X[col] = X[col].fillna('Unknown').astype(str)

    # Force remaining features to numeric while preserving NaN for CatBoost.
    num_col_names = [c for c in expected_cols if c not in cat_col_names]
    for col in num_col_names:
        X[col] = pd.to_numeric(X[col], errors='coerce')

    prediction = int(_model.predict(X).flatten()[0])
    result = {'triage_acuity': prediction}
    log.info(f'Prediction: {result}')
    return result
