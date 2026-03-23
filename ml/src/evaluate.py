import pandas as pd
import numpy as np
import shap
import logging
import os
import sys
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier, Pool
from sklearn.metrics import accuracy_score, classification_report

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'evaluation.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

TARGET_NAMES = ['1 (Resuscitation)', '2 (Emergent)', '3 (Urgent)', '4 (Less Urgent)', '5 (Non-Urgent)']


def explain_prediction(patient_index, X_val, shap_vals, preds):
    pred_class_original = int(preds[patient_index].flatten()[0])
    pred_class_idx = pred_class_original - 1

    if isinstance(shap_vals, np.ndarray) and shap_vals.ndim == 3:
        current_shap = shap_vals[patient_index, :, pred_class_idx]
    elif isinstance(shap_vals, list):
        current_shap = shap_vals[pred_class_idx][patient_index]
    else:
        raise ValueError('Unexpected shap_values structure.')

    importance = pd.DataFrame({'feature': X_val.columns.tolist(), 'importance': current_shap.flatten()})
    positives = importance[importance['importance'] > 0].sort_values('importance', ascending=False)
    negatives = importance[importance['importance'] < 0].sort_values('importance')

    lines = [f'[Prediction Result] Predicted Class: {TARGET_NAMES[pred_class_idx]}\n']
    lines.append('[Main Factors Increasing Urgency]')
    if not positives.empty:
        for _, row in positives.head(3).iterrows():
            val = X_val.iloc[patient_index][row['feature']]
            lines.append(f'  - {row["feature"]} (Value: {val}) -> Contribution: +{row["importance"]:.3f}')
    else:
        lines.append('  (None in particular)')

    lines.append('\n[Main Factors Decreasing Urgency]')
    if not negatives.empty:
        for _, row in negatives.head(3).iterrows():
            val = X_val.iloc[patient_index][row['feature']]
            lines.append(f'  - {row["feature"]} (Value: {val}) -> Contribution: {row["importance"]:.3f}')
    else:
        lines.append('  (None in particular)')

    return '\n'.join(lines)


def generate_report(model=None):
    log.info('Loading engineered dataset for evaluation...')
    train = pd.read_parquet(config.TRAIN_ENGINEERED)
    X = train.drop(columns=config.DROP_COLS_TRAINING)
    y = train[config.TARGET]

    if model is None:
        log.info(f'Loading saved model from {config.MODEL_PATH}')
        model = CatBoostClassifier()
        model.load_model(config.MODEL_PATH)

    # Use the last 20% of data as a representative validation slice for SHAP
    split = int(len(X) * 0.8)
    X_val = X.iloc[split:]
    y_val = y.iloc[split:]

    preds = model.predict(X_val)
    score = accuracy_score(y_val, preds)
    log.info(f'Evaluation Accuracy: {score:.4f}')
    log.info('\n' + classification_report(y_val, preds, target_names=TARGET_NAMES))

    log.info('Calculating SHAP values (this may take a moment)...')
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_val)

    log.info('\n--- Individual Patient Explanation (Patient 0) ---')
    log.info('\n' + explain_prediction(0, X_val, shap_values, preds))

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_val, show=False)
    plt.title('SHAP Beeswarm Plot')
    plt.tight_layout()
    plt.savefig(os.path.join(config.LOGS_DIR, 'shap_beeswarm.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_val, plot_type='bar', show=False)
    plt.title('SHAP Bar Plot: Feature Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(config.LOGS_DIR, 'shap_importance_bar.png'))
    plt.close()
    log.info(f'SHAP plots saved to {config.LOGS_DIR}')


if __name__ == '__main__':
    generate_report()
