import os
import pickle
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import get_next_serial_number, insert_patient_record


app = FastAPI(title="Triagegeist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatientInput(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: str
    systolic_bp: int = Field(..., ge=40, le=300)
    diastolic_bp: int = Field(..., ge=20, le=200)
    heart_rate: int = Field(..., ge=20, le=260)
    temperature: float = Field(..., ge=30.0, le=45.0)
    chief_complaint: str


MODEL = None


def _load_model():
    backend_dir = Path(__file__).resolve().parent
    model_candidates = [
        backend_dir / "triage_model.pkl",
        backend_dir.parent / "triage_model.pkl",
    ]

    for model_path in model_candidates:
        if model_path.exists():
            with open(model_path, "rb") as f:
                return pickle.load(f)

    return None


def _build_feature_frame(patient: PatientInput) -> pd.DataFrame:
    gender_value = patient.gender.strip().lower()
    gender_encoded = 1 if gender_value in {"male", "m"} else 0

    candidate_features = {
        "Age": patient.age,
        "age": patient.age,
        "Gender": patient.gender,
        "gender": patient.gender,
        "gender_encoded": gender_encoded,
        "SystolicBP": patient.systolic_bp,
        "systolic_bp": patient.systolic_bp,
        "DiastolicBP": patient.diastolic_bp,
        "diastolic_bp": patient.diastolic_bp,
        "BP_Systolic": patient.systolic_bp,
        "BP_Diastolic": patient.diastolic_bp,
        "HeartRate": patient.heart_rate,
        "heart_rate": patient.heart_rate,
        "HR": patient.heart_rate,
        "Temp": patient.temperature,
        "Temperature": patient.temperature,
        "temperature": patient.temperature,
        "ChiefComplaint": patient.chief_complaint,
        "chief_complaint": patient.chief_complaint,
        "Chief Complaint": patient.chief_complaint,
    }

    if hasattr(MODEL, "feature_names_in_"):
        expected = list(MODEL.feature_names_in_)
        row = {}
        for feature_name in expected:
            row[feature_name] = candidate_features.get(feature_name, 0)
        return pd.DataFrame([row])

    return pd.DataFrame([candidate_features])


@app.on_event("startup")
def startup_event():
    global MODEL
    MODEL = _load_model()


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": MODEL is not None}


@app.post("/predict")
def predict(patient: PatientInput):
    if MODEL is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Model file not found. Place triage_model.pkl in /backend or project root."
            ),
        )

    serial_number = get_next_serial_number()
    payload = patient.model_dump()
    insert_patient_record(payload, serial_number)

    try:
        features = _build_feature_frame(patient)
        raw_prediction = MODEL.predict(features)[0]
        severity = int(float(raw_prediction))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        )

    return {
        "serial_number": serial_number,
        "prediction": severity,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
