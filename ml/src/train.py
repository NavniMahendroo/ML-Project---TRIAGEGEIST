import pandas as pd
import numpy as np
import torch
import logging
import os
import sys
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'training.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def run_training():
    log.info('Loading engineered training dataset...')
    train = pd.read_parquet(config.TRAIN_ENGINEERED)

    X = train.drop(columns=config.DROP_COLS_TRAINING)
    y = train[config.TARGET]

    cat_features = X.select_dtypes(include=['object']).columns.tolist()
    log.info(f'Total features: {X.shape[1]} | Categorical: {cat_features}')

    kf = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_SEED)
    cv_scores = []
    best_model = None
    best_score = 0

    params = config.CATBOOST_PARAMS.copy()
    params['task_type'] = 'GPU' if torch.cuda.is_available() else 'CPU'

    log.info(f'Starting {config.CV_FOLDS}-Fold Cross Validation...')
    for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        train_pool = Pool(X_train, y_train, cat_features=cat_features)
        val_pool = Pool(X_val, y_val, cat_features=cat_features)

        model = CatBoostClassifier(**params)
        model.fit(train_pool, eval_set=val_pool)

        preds = model.predict(X_val)
        score = accuracy_score(y_val, preds)
        cv_scores.append(score)
        log.info(f'Fold {fold + 1} Accuracy: {score:.4f}')

        if score > best_score:
            best_score = score
            best_model = model

    mean_score = np.mean(cv_scores)
    log.info(f'Mean CV Accuracy: {mean_score:.4f}')

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    best_model.save_model(config.MODEL_PATH)
    log.info(f'Best model (score={best_score:.4f}) saved to {config.MODEL_PATH}')
    return best_model


if __name__ == '__main__':
    run_training()
