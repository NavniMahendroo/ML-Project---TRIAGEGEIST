"""
run_kaggle.py — Kaggle Submission Generator
Run this when you want to create a submission.csv from the saved trained model.
Does NOT retrain the model.

Usage:
    python run_kaggle.py

What it does:
    1. Loads the pre-trained model from ml/models/
    2. Runs batch predictions on test.csv (pre-engineered)
    3. Saves submission.csv ready for Kaggle upload
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import predict_kaggle

if __name__ == '__main__':
    print('═' * 55)
    print('  TriageGeist — Kaggle Submission Generator')
    print('═' * 55)

    print('\nGenerating submission.csv from saved model...')
    predict_kaggle.generate_submission()

    print('\n═' * 55)
    print('  Done. Upload submission.csv to Kaggle dashboard.')
    print('═' * 55)
