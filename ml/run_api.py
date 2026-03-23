"""
run_api.py — Website Backend Inference Gateway
Run this when the website needs to accept patient inputs and return predictions.
Does NOT retrain the model. Loads the model once and keeps it in memory.

Usage:
    python run_api.py

What it does:
    1. Loads the pre-trained model into memory (one-time startup cost)
    2. Accepts a patient dict payload
    3. Runs real-time inference via predict_api.py
    4. Returns the triage_acuity prediction and urgency label

Note: In production, this will be wrapped in a FastAPI/Flask web server
that exposes an HTTP endpoint callable by the frontend.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import predict_api

if __name__ == '__main__':
    print('═' * 55)
    print('  TriageGeist — Website API Gateway (Test Mode)')
    print('═' * 55)

    # Example single patient dict as would arrive from a frontend form
    sample_patient = {
        'age': 62,
        'sex': 'Male',
        'arrival_mode': 'Ambulance',
        'chief_complaint_raw': 'severe chest pain and shortness of breath',
        'heart_rate': 112,
        'respiratory_rate': 22,
        'spo2': 92,
        'systolic_bp': 90,
        'diastolic_bp': 60,
        'temperature_c': 37.1,
        'pain_score': 8,
        'gcs_total': 14,
        'news2_score': 7,
    }

    print(f'\nInput patient data: {sample_patient}')
    result = predict_api.predict_patient(sample_patient)
    print('\n--- Prediction Result ---')
    print(f'  Triage Acuity : {result["triage_acuity"]}')
    print(f'  Urgency Level : {result["urgency_label"]}')
    print('═' * 55)
