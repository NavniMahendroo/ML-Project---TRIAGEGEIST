from datetime import UTC, datetime

from fastapi import HTTPException
from pymongo import ReturnDocument

from constants.routing import EMERGENCY_ACUITY_LEVELS, SPECIALTY_FALLBACK, SPECIALTY_KEYWORDS
from database import get_collection
from src.doctors.schema import (
    DoctorAssignedPatientResponse,
    DoctorAttendResponse,
    DoctorDutyResponse,
    DoctorLoginResponse,
    DoctorSummaryResponse,
)
from utils.data_utils import serialize_mongo
from utils.security import hash_password, verify_password


ASSIGNMENT_STATUS_ASSIGNED = "assigned"
ASSIGNMENT_STATUS_NO_MATCH = "unassigned_no_match"
ASSIGNMENT_STATUS_NO_ON_DUTY = "unassigned_no_on_duty_doctor"


def _normalize_specialty(specialty: str | None) -> str:
    normalized = (specialty or "").strip()
    return normalized or SPECIALTY_FALLBACK


def _doctor_summary(document: dict) -> dict:
    return DoctorSummaryResponse(
        doctor_id=document["doctor_id"],
        name=document.get("name", "Doctor"),
        specialty=_normalize_specialty(document.get("specialty")),
        on_duty=bool(document.get("on_duty", True)),
        role=str(document.get("role") or "admin"),
    ).model_dump()


def _patient_item(visit: dict, patient_name: str) -> dict:
    return DoctorAssignedPatientResponse(
        visit_id=visit["visit_id"],
        patient_id=visit["patient_id"],
        patient_name=patient_name,
        triage_acuity=int(visit["triage_acuity"]),
        urgency_label=visit["urgency_label"],
        target_specialty=visit.get("target_specialty"),
        assignment_status=visit.get("assignment_status", ASSIGNMENT_STATUS_NO_MATCH),
        attended_by_doctor=bool(visit.get("attended_by_doctor", False)),
        attended_at=visit.get("attended_at"),
        attended_by_doctor_id=visit.get("attended_by_doctor_id"),
        chief_complaint_system=visit.get("chief_complaint_system"),
        created_at=visit["created_at"],
    ).model_dump()


def authenticate_doctor(doctor_id: str, password: str, role: str = "admin") -> dict:
    normalized_doctor_id = doctor_id.strip()
    doctor = get_collection("doctors").find_one({"doctor_id": normalized_doctor_id})

    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid doctor ID or password.")

    stored_password = doctor.get("password")

    if not stored_password:
        stored_password = hash_password(normalized_doctor_id)
        get_collection("doctors").update_one(
            {"doctor_id": normalized_doctor_id},
            {"$set": {"password": stored_password}},
        )

    stored_role = str(doctor.get("role") or "admin")
    if stored_role not in {"staff", "admin"}:
        stored_role = "admin"
        get_collection("doctors").update_one(
            {"doctor_id": normalized_doctor_id},
            {"$set": {"role": stored_role}},
        )

    if not verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid doctor ID or password.")

    if role != stored_role:
        raise HTTPException(status_code=401, detail="Invalid doctor ID or password.")

    return DoctorLoginResponse(
        doctor_id=doctor["doctor_id"],
        name=doctor.get("name", "Doctor"),
        role=stored_role,
        specialty=doctor.get("specialty"),
        on_duty=bool(doctor.get("on_duty", True)),
    ).model_dump()


def list_doctors() -> list[dict]:
    cursor = get_collection("doctors").find({}, {"_id": 0}).sort([("specialty", 1), ("doctor_id", 1)])
    return [_doctor_summary(document) for document in cursor]


def update_doctor_duty_status(doctor_id: str, on_duty: bool) -> dict:
    normalized_doctor_id = doctor_id.strip()
    updated = get_collection("doctors").find_one_and_update(
        {"doctor_id": normalized_doctor_id},
        {"$set": {"on_duty": bool(on_duty)}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Doctor '{doctor_id}' not found.")

    return serialize_mongo(
        DoctorDutyResponse(
            doctor_id=updated["doctor_id"],
            name=updated.get("name", "Doctor"),
            specialty=_normalize_specialty(updated.get("specialty")),
            on_duty=bool(updated.get("on_duty", True)),
            role=str(updated.get("role") or "admin"),
        ).model_dump()
    )


def determine_target_specialty(chief_complaint_system: str | None, triage_acuity: int) -> str:
    if triage_acuity in EMERGENCY_ACUITY_LEVELS:
        return SPECIALTY_FALLBACK

    normalized = (chief_complaint_system or "").strip().lower().replace("_", " ")
    if not normalized:
        return SPECIALTY_FALLBACK

    for specialty, keywords in SPECIALTY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return specialty

    return SPECIALTY_FALLBACK


def assign_doctor_for_specialty(specialty: str) -> tuple[str | None, str]:
    doctors = list(
        get_collection("doctors")
        .find({"specialty": specialty}, {"doctor_id": 1, "on_duty": 1, "_id": 0})
        .sort("doctor_id", 1)
    )
    if not doctors:
        return None, ASSIGNMENT_STATUS_NO_MATCH

    eligible = [doctor for doctor in doctors if bool(doctor.get("on_duty", True))]
    if not eligible:
        return None, ASSIGNMENT_STATUS_NO_ON_DUTY

    counter = get_collection("_system_counters").find_one_and_update(
        {"_id": f"doctor_assignment:{specialty}"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    index = (int(counter["seq"]) - 1) % len(eligible)
    return eligible[index]["doctor_id"], ASSIGNMENT_STATUS_ASSIGNED


def list_doctor_patients(doctor_id: str) -> list[dict]:
    normalized_doctor_id = doctor_id.strip()
    doctor = get_collection("doctors").find_one({"doctor_id": normalized_doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor '{doctor_id}' not found.")

    visits = list(
        get_collection("visits")
        .find({"assigned_doctor_id": normalized_doctor_id})
        .sort("created_at", -1)
    )
    if not visits:
        return []

    patient_ids = [visit["patient_id"] for visit in visits]
    patients = {
        document["patient_id"]: document.get("name", "Patient")
        for document in get_collection("patients").find({"patient_id": {"$in": patient_ids}}, {"patient_id": 1, "name": 1})
    }

    return [serialize_mongo(_patient_item(visit, patients.get(visit["patient_id"], "Patient"))) for visit in visits]


def mark_patient_attended(doctor_id: str, visit_id: str) -> dict:
    normalized_doctor_id = doctor_id.strip()
    visit = get_collection("visits").find_one({"visit_id": visit_id})
    if not visit:
        raise HTTPException(status_code=404, detail=f"Visit '{visit_id}' not found.")

    if visit.get("assigned_doctor_id") != normalized_doctor_id:
        raise HTTPException(status_code=403, detail="Only the assigned doctor can mark this patient as attended.")

    patient = get_collection("patients").find_one({"patient_id": visit["patient_id"]}, {"name": 1, "patient_id": 1})
    patient_name = patient.get("name", "Patient") if patient else "Patient"

    if visit.get("attended_by_doctor"):
        return serialize_mongo(
            DoctorAttendResponse(
                visit_id=visit["visit_id"],
                patient_id=visit["patient_id"],
                patient_name=patient_name,
                attended_by_doctor=True,
                attended_at=visit.get("attended_at"),
                attended_by_doctor_id=visit.get("attended_by_doctor_id"),
                assignment_status=visit.get("assignment_status", ASSIGNMENT_STATUS_ASSIGNED),
            ).model_dump()
        )

    attended_at = datetime.now(UTC)
    updated_visit = get_collection("visits").find_one_and_update(
        {"visit_id": visit_id, "assigned_doctor_id": normalized_doctor_id},
        {
            "$set": {
                "attended_by_doctor": True,
                "attended_at": attended_at,
                "attended_by_doctor_id": normalized_doctor_id,
                "updated_at": attended_at,
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    return serialize_mongo(
        DoctorAttendResponse(
            visit_id=updated_visit["visit_id"],
            patient_id=updated_visit["patient_id"],
            patient_name=patient_name,
            attended_by_doctor=bool(updated_visit.get("attended_by_doctor", False)),
            attended_at=updated_visit.get("attended_at"),
            attended_by_doctor_id=updated_visit.get("attended_by_doctor_id"),
            assignment_status=updated_visit.get("assignment_status", ASSIGNMENT_STATUS_ASSIGNED),
        ).model_dump()
    )
