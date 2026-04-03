from fastapi import APIRouter
import logging

from triage.schema import PatientInput
from triage.service import get_prediction
from patients.service import get_next_serial_number, insert_patient_record

log = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["triage"])

@router.post("/predict")
def predict(patient: PatientInput):
    # 1. Run prediction — ML pipeline if loaded, otherwise rule-based fallback
    prediction_data = get_prediction(patient)

    # 2. Generate serial number (Resilient IDs)
    serial_number = get_next_serial_number()

    # 3. Persist to MongoDB
    insert_patient_record(patient.model_dump(), serial_number, prediction_data)

    return {
        "serial_number": serial_number,
        "triage_acuity": prediction_data["triage_acuity"],
        "urgency_label": prediction_data["urgency_label"],
        "engine": prediction_data["engine"],
    }
