"""
run_train.py — Full Training Pipeline
Run this when you want to train a new model from scratch.

Usage:
    python run_train.py

What it does:
    1. Preprocesses raw datasets (merges, drops leakage)
    2. Extracts BioBERT embeddings + PCA reduction
    3. Trains CatBoost with 5-Fold CV
    4. Evaluates with SHAP and saves plots to logs/
    5. Saves the best model to models/
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import data_preprocessing
import feature_engineering
import train
import evaluate

if __name__ == '__main__':
    print('═' * 55)
    print('  TriageGeist — Full Training Pipeline')
    print('═' * 55)

    print('\n[Step 1/4] Data Preprocessing...')
    data_preprocessing.run()

    print('\n[Step 2/4] Feature Engineering (BioBERT + PCA)...')
    feature_engineering.run()

    print('\n[Step 3/4] Model Training (CatBoost CV)...')
    best_model = train.run_training()

    print('\n[Step 4/4] Evaluation & SHAP Report...')
    evaluate.generate_report(model=best_model)

    print('\n═' * 5)
    print('  Training complete. Model saved to ml/models/')
    print('═' * 55)
