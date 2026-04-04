from fastapi import APIRouter, Query

from src.patients.service import get_patient_summary, list_recent_patients

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/")
def list_patients(limit: int = Query(default=20, ge=1, le=100)):
    return {"items": list_recent_patients(limit=limit)}


@router.get("/{patient_id}")
def get_patient(patient_id: str):
    return get_patient_summary(patient_id)
