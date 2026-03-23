import pandas as pd
import numpy as np
import torch
import logging
import os
import sys
import joblib
from tqdm import tqdm
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'feature_engineering.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


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


def add_bert_features(df, tokenizer, model, device, pca, fit_pca=False):
    texts = df['chief_complaint_raw'].fillna('No Data').to_list()
    log.info(f'Extracting BERT embeddings for {len(texts)} records...')
    bert_features = get_bert_embeddings(texts, tokenizer, model, device)

    if fit_pca:
        log.info(f'Fitting PCA to {config.PCA_COMPONENTS} components...')
        bert_pca = pca.fit_transform(bert_features)
    else:
        log.info('Transforming with existing PCA...')
        bert_pca = pca.transform(bert_features)

    bert_cols = [f'bert_pca_{i}' for i in range(config.PCA_COMPONENTS)]
    df_bert = pd.DataFrame(bert_pca, columns=bert_cols, index=df.index)
    return pd.concat([df, df_bert], axis=1)


def run():
    log.info('Loading processed datasets...')
    train = pd.read_parquet(config.TRAIN_PROCESSED)
    test = pd.read_parquet(config.TEST_PROCESSED)

    log.info(f'Loading BioBERT model: {config.BERT_MODEL_NAME}')
    tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME)
    model = AutoModel.from_pretrained(config.BERT_MODEL_NAME)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log.info(f'Using device: {device}')
    model = model.to(device)

    pca = PCA(n_components=config.PCA_COMPONENTS)

    train = add_bert_features(train, tokenizer, model, device, pca, fit_pca=True)

    if device.type == 'cuda':
        torch.cuda.empty_cache()
        log.info('GPU cache cleared between train and test embedding passes.')

    test = add_bert_features(test, tokenizer, model, device, pca, fit_pca=False)

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    joblib.dump(pca, config.PCA_PATH)
    log.info(f'Saved PCA to {config.PCA_PATH}')

    train.to_parquet(config.TRAIN_ENGINEERED, index=False)
    test.to_parquet(config.TEST_ENGINEERED, index=False)
    log.info(f'Saved engineered datasets to {config.PROCESSED_DIR}')


if __name__ == '__main__':
    run()
