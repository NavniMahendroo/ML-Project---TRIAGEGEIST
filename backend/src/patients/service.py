from datetime import datetime, UTC

from fastapi import HTTPException

from database import get_collection
from src.patients.schema import PatientDocument
from utils.clinical_utils import calculate_age_group, calculate_bmi
from utils.data_utils import serialize_mongo
from utils.id_generator import get_next_id


def create_patient_record(payload: dict) -> dict:
    patients = get_collection("patients")
    patient_id = get_next_id("patients", "TG")

    document = PatientDocument(
        patient_id=patient_id,
        name=payload["name"],
        age=payload["age"],
        sex=payload["sex"],
        language=payload["language"],
        insurance_type=payload["insurance_type"],
        num_prior_ed_visits_12m=0,
        num_prior_admissions_12m=0,
        num_active_medications=payload["num_active_medications"],
        num_comorbidities=payload["num_comorbidities"],
        weight_kg=payload["weight_kg"],
        height_cm=payload["height_cm"],
        age_group=calculate_age_group(payload["age"]),
        bmi=calculate_bmi(payload["weight_kg"], payload["height_cm"]),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ).model_dump()
    patients.insert_one(document)
    return document


def get_patient_by_id(patient_id: str) -> dict:
    patient = get_collection("patients").find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")
    return patient


def get_patient_history(patient_id: str) -> dict | None:
    return get_collection("patient_history").find_one({"patient_id": patient_id})


def increment_patient_visit_counter(patient_id: str) -> None:
    get_collection("patients").update_one(
        {"patient_id": patient_id},
        {
            "$inc": {"num_prior_ed_visits_12m": 1},
            "$set": {"updated_at": datetime.now(UTC)},
        },
    )


def list_recent_patients(limit: int = 20) -> list[dict]:
    cursor = (
        get_collection("patients")
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [serialize_mongo(document) for document in cursor]


def get_patient_summary(patient_id: str) -> dict:
    patient = get_patient_by_id(patient_id)
    history = get_patient_history(patient_id)
    visits = (
        get_collection("visits")
        .find({"patient_id": patient_id})
        .sort("created_at", -1)
        .limit(10)
    )

    return {
        "patient": serialize_mongo(patient),
        "patient_history": serialize_mongo(history) if history else None,
        "visits": [serialize_mongo(document) for document in visits],
    }
