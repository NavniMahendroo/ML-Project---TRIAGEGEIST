import pandas as pd
import numpy as np
import logging
import os
import sys
import joblib
import torch
from catboost import CatBoostClassifier
from transformers import AutoTokenizer, AutoModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from feature_engineering import get_bert_embeddings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'predict_kaggle.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def generate_submission():
    log.info('Loading Kaggle test dataset...')
    test = pd.read_parquet(config.TEST_ENGINEERED)

    log.info(f'Loading saved model from {config.MODEL_PATH}')
    model = CatBoostClassifier()
    model.load_model(config.MODEL_PATH)

    patient_ids = test['patient_id']
    X = test.drop(columns=config.DROP_COLS_INFERENCE, errors='ignore')

    log.info(f'Running batch predictions on {len(X)} records...')
    predictions = model.predict(X).flatten()

    submission = pd.read_csv(config.SAMPLE_SUBMISSION_CSV)
    submission[config.TARGET] = predictions

    output_path = os.path.join(config.BASE_DIR, '..', 'submission.csv')
    output_path = os.path.normpath(output_path)
    submission.to_csv(output_path, index=False)
    log.info(f'Kaggle submission saved to {output_path} ({len(submission)} rows)')


if __name__ == '__main__':
    generate_submission()
