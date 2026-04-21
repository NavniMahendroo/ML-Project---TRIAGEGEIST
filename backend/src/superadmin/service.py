from datetime import UTC, datetime

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_collection
from src.superadmin.schema import (
    StaffDutyItem,
    SuperAdminAssignmentItem,
    SuperAdminLoginResponse,
    SuperAdminMarkAttendedResponse,
    SuperAdminReassignResponse,
    SuperAdminSummaryResponse,
)
from utils.data_utils import serialize_mongo
from utils.security import hash_password, verify_password


ASSIGNMENT_STATUS_MANUAL = "assigned_manual"


def authenticate_superadmin(admin_id: str, password: str) -> dict:
    normalized_admin_id = admin_id.strip()
    admin = get_collection("superadmins").find_one({"admin_id": normalized_admin_id})

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid superadmin ID or password.")

    stored_password = admin.get("password")
    if not stored_password:
        stored_password = hash_password("12345678")
        get_collection("superadmins").update_one(
            {"admin_id": normalized_admin_id},
            {"$set": {"password": stored_password}},
        )

    if not verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid superadmin ID or password.")

    return SuperAdminLoginResponse(
        admin_id=admin["admin_id"],
        name=admin.get("name", "Super Admin"),
    ).model_dump()


def _staff_item(document: dict, staff_id_key: str, specialty: str | None = None) -> dict:
    return StaffDutyItem(
        staff_id=document[staff_id_key],
        name=document.get("name", "Staff"),
        role=str(document.get("role") or "staff"),
        on_duty=bool(document.get("on_duty", True)),
        specialty=specialty,
    ).model_dump()


def get_dashboard_summary() -> dict:
    nurses_docs = list(get_collection("nurses").find({}, {"_id": 0}).sort("nurse_id", 1))
    doctors_docs = list(get_collection("doctors").find({}, {"_id": 0}).sort("doctor_id", 1))

    nurses = [_staff_item(document, "nurse_id") for document in nurses_docs]
    doctors = [_staff_item(document, "doctor_id", specialty=document.get("specialty")) for document in doctors_docs]

    attended_visits = get_collection("visits").count_documents({"attended_by_doctor": True})
    total_visits = get_collection("visits").count_documents({})

    return serialize_mongo(
        SuperAdminSummaryResponse(
            total_patients=get_collection("patients").count_documents({}),
            total_visits=total_visits,
            total_nurses=len(nurses_docs),
            total_doctors=len(doctors_docs),
            nurses_on_duty=sum(1 for nurse in nurses_docs if bool(nurse.get("on_duty", True))),
            nurses_off_duty=sum(1 for nurse in nurses_docs if not bool(nurse.get("on_duty", True))),
            doctors_on_duty=sum(1 for doctor in doctors_docs if bool(doctor.get("on_duty", True))),
            doctors_off_duty=sum(1 for doctor in doctors_docs if not bool(doctor.get("on_duty", True))),
            attended_visits=attended_visits,
            pending_visits=total_visits - attended_visits,
            unassigned_visits=get_collection("visits").count_documents({"assigned_doctor_id": None}),
            nurses=nurses,
            doctors=doctors,
        ).model_dump()
    )


def list_assignments(limit: int = 100) -> list[dict]:
    visits = list(
        get_collection("visits")
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )

    if not visits:
        return []

    patient_ids = [visit["patient_id"] for visit in visits]
    nurse_ids = [visit["nurse_id"] for visit in visits if visit.get("nurse_id")]
    doctor_ids = [visit["assigned_doctor_id"] for visit in visits if visit.get("assigned_doctor_id")]

    patient_names = {
        document["patient_id"]: document.get("name", "Patient")
        for document in get_collection("patients").find(
            {"patient_id": {"$in": patient_ids}},
            {"patient_id": 1, "name": 1},
        )
    }
    nurse_names = {
        document["nurse_id"]: document.get("name", "Nurse")
        for document in get_collection("nurses").find(
            {"nurse_id": {"$in": nurse_ids}},
            {"nurse_id": 1, "name": 1},
        )
    }
    doctor_names = {
        document["doctor_id"]: document.get("name", "Doctor")
        for document in get_collection("doctors").find(
            {"doctor_id": {"$in": doctor_ids}},
            {"doctor_id": 1, "name": 1},
        )
    }

    items = []
    for visit in visits:
        items.append(
            serialize_mongo(
                SuperAdminAssignmentItem(
                    visit_id=visit["visit_id"],
                    patient_id=visit["patient_id"],
                    patient_name=patient_names.get(visit["patient_id"], "Patient"),
                    nurse_id=visit["nurse_id"],
                    nurse_name=nurse_names.get(visit["nurse_id"]),
                    assigned_doctor_id=visit.get("assigned_doctor_id"),
                    assigned_doctor_name=doctor_names.get(visit.get("assigned_doctor_id")),
                    target_specialty=visit.get("target_specialty"),
                    assignment_status=visit.get("assignment_status", "unassigned_no_match"),
                    triage_acuity=int(visit.get("triage_acuity", 3)),
                    urgency_label=visit.get("urgency_label", "Unknown"),
                    attended_by_doctor=bool(visit.get("attended_by_doctor", False)),
                    attended_at=visit.get("attended_at"),
                    attended_by_doctor_id=visit.get("attended_by_doctor_id"),
                    created_at=visit["created_at"],
                ).model_dump()
            )
        )
    return items


def mark_assignment_attended(visit_id: str) -> dict:
    visit = get_collection("visits").find_one({"visit_id": visit_id})
    if not visit:
        raise HTTPException(status_code=404, detail=f"Visit '{visit_id}' not found.")

    attended_at = datetime.now(UTC)
    attended_by_doctor_id = visit.get("attended_by_doctor_id") or visit.get("assigned_doctor_id")

    updated_visit = get_collection("visits").find_one_and_update(
        {"visit_id": visit_id},
        {
            "$set": {
                "attended_by_doctor": True,
                "attended_at": attended_at,
                "attended_by_doctor_id": attended_by_doctor_id,
                "updated_at": attended_at,
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    return serialize_mongo(
        SuperAdminMarkAttendedResponse(
            visit_id=updated_visit["visit_id"],
            attended_by_doctor=bool(updated_visit.get("attended_by_doctor", False)),
            attended_at=updated_visit.get("attended_at"),
            attended_by_doctor_id=updated_visit.get("attended_by_doctor_id"),
            assignment_status=updated_visit.get("assignment_status", "unassigned_no_match"),
        ).model_dump()
    )


def reassign_visit(visit_id: str, doctor_id: str) -> dict:
    normalized_doctor_id = doctor_id.strip()
    if not normalized_doctor_id:
        raise HTTPException(status_code=422, detail="Doctor ID is required.")

    visit = get_collection("visits").find_one({"visit_id": visit_id})
    if not visit:
        raise HTTPException(status_code=404, detail=f"Visit '{visit_id}' not found.")

    if visit.get("attended_by_doctor"):
        raise HTTPException(status_code=409, detail="Cannot reassign an attended visit.")

    doctor = get_collection("doctors").find_one({"doctor_id": normalized_doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor '{doctor_id}' not found.")

    updated_at = datetime.now(UTC)
    updated_visit = get_collection("visits").find_one_and_update(
        {"visit_id": visit_id},
        {
            "$set": {
                "assigned_doctor_id": normalized_doctor_id,
                "assignment_status": ASSIGNMENT_STATUS_MANUAL,
                "attended_by_doctor": False,
                "attended_at": None,
                "attended_by_doctor_id": None,
                "updated_at": updated_at,
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    assigned_name = doctor.get("name", "Doctor")

    return serialize_mongo(
        SuperAdminReassignResponse(
            visit_id=updated_visit["visit_id"],
            assigned_doctor_id=updated_visit.get("assigned_doctor_id"),
            assigned_doctor_name=assigned_name,
            assignment_status=updated_visit.get("assignment_status", ASSIGNMENT_STATUS_MANUAL),
            attended_by_doctor=bool(updated_visit.get("attended_by_doctor", False)),
            attended_at=updated_visit.get("attended_at"),
            attended_by_doctor_id=updated_visit.get("attended_by_doctor_id"),
        ).model_dump()
    )
