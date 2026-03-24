"""
main.py — FastAPI backend for Triagegeist.
Tries to load the real ML pipeline (CatBoost + BioBERT).
Falls back to a clinical-rules engine so the frontend always works.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import get_next_serial_number, insert_patient_record

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Wire-up: add ml/src to sys.path so we can import predict_api ─────────────
_backend_dir = Path(__file__).resolve().parent
_ml_src_dir = _backend_dir.parent / "ml" / "src"
sys.path.insert(0, str(_ml_src_dir))

# Try importing the real ML pipeline (may fail if deps missing / model not trained)
_ml_available = False
try:
    import predict_api  # noqa: E402

    _ml_available = True
except Exception as exc:
    log.warning(f"ML pipeline import failed ({exc}). Will use rule-based fallback.")


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


# ── Request Schema — all 13 clinical features ────────────────────────────────
class PatientInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: str = Field(..., description="Male / Female / Other")
    arrival_mode: str = Field(
        ..., description="How the patient arrived (Walk-in, Ambulance, etc.)"
    )
    chief_complaint_raw: str = Field(
        ..., description="Free-text chief complaint"
    )
    heart_rate: int = Field(..., ge=20, le=260)
    respiratory_rate: int = Field(..., ge=0, le=80)
    spo2: int = Field(..., ge=0, le=100, description="Oxygen saturation %")
    systolic_bp: int = Field(..., ge=40, le=300)
    diastolic_bp: int = Field(..., ge=20, le=200)
    temperature_c: float = Field(..., ge=30.0, le=45.0, description="Body temp °C")
    pain_score: int = Field(..., ge=0, le=10, description="Self-reported pain 0-10")
    gcs_total: int = Field(
        ..., ge=3, le=15, description="Glasgow Coma Scale total"
    )
    news2_score: int = Field(
        ..., ge=0, le=20, description="NEWS2 early-warning score"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Clinical-Rules Fallback Engine
# Uses standard clinical criteria (NEWS2, GCS, vitals, keywords) to estimate
# triage acuity when the ML model is not available.
# ═══════════════════════════════════════════════════════════════════════════════

URGENCY_LABELS = {
    1: "Resuscitation",
    2: "Emergent",
    3: "Urgent",
    4: "Less Urgent",
    5: "Non-Urgent",
}

# High-acuity clinical keywords (case-insensitive)
_CRITICAL_KEYWORDS = [
    "cardiac arrest", "unresponsive", "not breathing", "cpr",
    "anaphylaxis", "severe hemorrhage", "massive bleeding",
]
_EMERGENT_KEYWORDS = [
    "chest pain", "stroke", "seizure", "overdose", "difficulty breathing",
    "shortness of breath", "severe pain", "crushing", "stabbing",
    "head injury", "unconscious", "altered mental status",
    "suicidal", "self-harm", "poisoning",
]
_URGENT_KEYWORDS = [
    "abdominal pain", "fracture", "laceration", "vomiting blood",
    "high fever", "asthma attack", "diabetic", "infection",
    "dehydration", "dizziness", "fainting",
]


def _keyword_urgency(text: str) -> int:
    """Return 1-5 based on keyword matching. 5 means no keyword match."""
    lower = text.lower()
    for kw in _CRITICAL_KEYWORDS:
        if kw in lower:
            return 1
    for kw in _EMERGENT_KEYWORDS:
        if kw in lower:
            return 2
    for kw in _URGENT_KEYWORDS:
        if kw in lower:
            return 3
    return 5  # no concerning keywords


def rule_based_predict(p: PatientInput) -> dict:
    """
    Clinical-rules triage estimator.
    Takes the worst (lowest number = most urgent) across multiple criteria.
    """
    scores = []

    # ── 1. NEWS2 Score mapping ────────────────────────────────────────────
    if p.news2_score >= 7:
        scores.append(1)
    elif p.news2_score >= 5:
        scores.append(2)
    elif p.news2_score >= 3:
        scores.append(3)
    elif p.news2_score >= 1:
        scores.append(4)
    else:
        scores.append(5)

    # ── 2. GCS mapping ───────────────────────────────────────────────────
    if p.gcs_total <= 8:
        scores.append(1)
    elif p.gcs_total <= 12:
        scores.append(2)
    elif p.gcs_total <= 14:
        scores.append(3)
    else:
        scores.append(5)

    # ── 3. SpO2 mapping ──────────────────────────────────────────────────
    if p.spo2 < 85:
        scores.append(1)
    elif p.spo2 < 90:
        scores.append(2)
    elif p.spo2 < 94:
        scores.append(3)
    else:
        scores.append(5)

    # ── 4. Heart rate mapping ─────────────────────────────────────────────
    if p.heart_rate < 40 or p.heart_rate > 150:
        scores.append(1)
    elif p.heart_rate < 50 or p.heart_rate > 130:
        scores.append(2)
    elif p.heart_rate < 60 or p.heart_rate > 110:
        scores.append(3)
    else:
        scores.append(5)

    # ── 5. Systolic BP mapping ────────────────────────────────────────────
    if p.systolic_bp < 70 or p.systolic_bp > 250:
        scores.append(1)
    elif p.systolic_bp < 80 or p.systolic_bp > 220:
        scores.append(2)
    elif p.systolic_bp < 90 or p.systolic_bp > 180:
        scores.append(3)
    else:
        scores.append(5)

    # ── 6. Respiratory rate mapping ───────────────────────────────────────
    if p.respiratory_rate < 8 or p.respiratory_rate > 35:
        scores.append(1)
    elif p.respiratory_rate < 10 or p.respiratory_rate > 30:
        scores.append(2)
    elif p.respiratory_rate < 12 or p.respiratory_rate > 24:
        scores.append(3)
    else:
        scores.append(5)

    # ── 7. Temperature mapping ────────────────────────────────────────────
    if p.temperature_c < 33.0 or p.temperature_c > 41.0:
        scores.append(1)
    elif p.temperature_c < 34.0 or p.temperature_c > 40.0:
        scores.append(2)
    elif p.temperature_c < 35.0 or p.temperature_c > 39.0:
        scores.append(3)
    else:
        scores.append(5)

    # ── 8. Pain score ─────────────────────────────────────────────────────
    if p.pain_score >= 9:
        scores.append(2)
    elif p.pain_score >= 7:
        scores.append(3)
    elif p.pain_score >= 4:
        scores.append(4)
    else:
        scores.append(5)

    # ── 9. Chief complaint keywords ───────────────────────────────────────
    scores.append(_keyword_urgency(p.chief_complaint_raw))

    # ── 10. Arrival mode ──────────────────────────────────────────────────
    arrival = p.arrival_mode.lower()
    if arrival == "helicopter":
        scores.append(1)
    elif arrival == "ambulance":
        scores.append(2)

    # ── 11. Age extremes ──────────────────────────────────────────────────
    if p.age < 1 or p.age > 85:
        scores.append(3)  # slightly more urgent for extremes

    # Final: take the most urgent (lowest number)
    acuity = min(scores) if scores else 3
    return {
        "triage_acuity": acuity,
        "urgency_label": URGENCY_LABELS.get(acuity, "Unknown"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Lifecycle & Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

_ml_model_loaded = False


@app.on_event("startup")
def startup_event():
    global _ml_model_loaded
    if _ml_available:
        try:
            predict_api.load_model()
            _ml_model_loaded = predict_api._model is not None
            if _ml_model_loaded:
                log.info("ML model loaded successfully.")
            else:
                log.warning("ML model load returned None. Using rule-based fallback.")
        except Exception as exc:
            log.warning(f"ML model load failed: {exc}. Using rule-based fallback.")
    else:
        log.info("ML pipeline not available. Using rule-based clinical fallback.")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "engine": "ml_pipeline" if _ml_model_loaded else "rule_based_fallback",
        "ml_model_loaded": _ml_model_loaded,
    }


@app.post("/predict")
def predict(patient: PatientInput):
    # 1. Generate serial number and persist to Mongo
    try:
        serial_number = get_next_serial_number()
        payload = patient.model_dump()
        insert_patient_record(payload, serial_number)
    except Exception as exc:
        log.warning(f"Database write failed (non-fatal): {exc}")
        serial_number = "TG-TEMP-0"

    # 2. Run prediction — ML pipeline if loaded, otherwise rule-based fallback
    if _ml_model_loaded:
        try:
            ml_result = predict_api.predict_patient(payload)
            engine = "ml_pipeline"
        except Exception as exc:
            log.error(f"ML prediction failed, falling back to rules: {exc}")
            ml_result = rule_based_predict(patient)
            engine = "rule_based_fallback"
    else:
        ml_result = rule_based_predict(patient)
        engine = "rule_based_fallback"

    return {
        "serial_number": serial_number,
        "triage_acuity": ml_result["triage_acuity"],
        "urgency_label": ml_result["urgency_label"],
        "engine": engine,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
