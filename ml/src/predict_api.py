import pandas as pd
import numpy as np
import logging
import os
import sys

# Force offline mode to prevent any HTTP requests on startup
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

import joblib
import torch
from catboost import CatBoostClassifier
from transformers import AutoTokenizer, AutoModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
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


def load_model():
    global _model, _tokenizer, _bert_model, _pca, _device
    if _model is None:
        log.info('Loading CatBoost model into memory...')
        _model = CatBoostClassifier()
        _model.load_model(config.MODEL_PATH)
        log.info('Loading PCA transformer...')
        _pca = joblib.load(config.PCA_PATH)
        log.info(f'Loading BioBERT tokenizer and model: {config.BERT_MODEL_NAME}')
        try:
            _tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME, local_files_only=True)
            _bert_model = AutoModel.from_pretrained(config.BERT_MODEL_NAME, local_files_only=True)
        except Exception:
            log.info("Local BioBERT files not found. Attempting to download from Hugging Face...")
            _tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME)
            _bert_model = AutoModel.from_pretrained(config.BERT_MODEL_NAME)
        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        _bert_model = _bert_model.to(_device)
        log.info(f'All models loaded. Device: {_device}')


def predict_patient(patient_data: dict) -> dict:
    """
    Accepts a single patient record as a dict (from website JSON payload) and
    returns a dict with the predicted triage_acuity and urgency label.

    Example input:
    {
        "age": 45, "sex": "Male", "chief_complaint_raw": "chest pain",
        "heart_rate": 102, "spo2": 94, ...
    }
    """
    load_model()

    df = pd.DataFrame([patient_data])

    # Extract BERT embedding for the single record
    if 'chief_complaint_raw' in df.columns:
        texts = df['chief_complaint_raw'].fillna('No Data').to_list()
        bert_features = get_bert_embeddings(texts, _tokenizer, _bert_model, _device)
        bert_pca = _pca.transform(bert_features)
        bert_cols = [f'bert_pca_{i}' for i in range(config.PCA_COMPONENTS)]
        df_bert = pd.DataFrame(bert_pca, columns=bert_cols, index=df.index)
        df = pd.concat([df, df_bert], axis=1)

    # Ensure incoming data perfectly matches the CatBoost training schema
    expected_cols = _model.feature_names_
    X = df.reindex(columns=expected_cols)

    # Force categorical features to be strings
    cat_indices = _model.get_cat_feature_indices()
    cat_col_names = [expected_cols[i] for i in cat_indices]
    for col in cat_col_names:
        X[col] = X[col].fillna('Unknown').astype(str)

    # Force remaining features to numeric, filling missing heavily with 0
    num_col_names = [c for c in expected_cols if c not in cat_col_names]
    for col in num_col_names:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)

    prediction = int(_model.predict(X).flatten()[0])
    urgency_labels = {1: 'Resuscitation', 2: 'Emergent', 3: 'Urgent', 4: 'Less Urgent', 5: 'Non-Urgent'}
    result = {'triage_acuity': prediction, 'urgency_label': urgency_labels.get(prediction, 'Unknown')}
    log.info(f'Prediction: {result}')
    return result
