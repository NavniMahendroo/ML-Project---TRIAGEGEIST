from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_collection
from src.nurses.schema import NurseDutyResponse, NurseLoginResponse, NurseSummaryResponse
from utils.security import hash_password, verify_password


def _nurse_summary(document: dict) -> dict:
    return NurseSummaryResponse(
        nurse_id=document["nurse_id"],
        name=document.get("name", "Nurse"),
        on_duty=bool(document.get("on_duty", True)),
        role=str(document.get("role") or "staff"),
    ).model_dump()


def authenticate_nurse(nurse_id: str, password: str, role: str = "staff") -> dict:
    normalized_nurse_id = nurse_id.strip()
    nurse = get_collection("nurses").find_one({"nurse_id": normalized_nurse_id})

    if not nurse:
        raise HTTPException(status_code=401, detail="Invalid nurse ID or password.")

    stored_password = nurse.get("password")

    # Graceful migration path for old records that do not yet have a password field.
    if not stored_password:
        stored_password = hash_password(normalized_nurse_id)
        get_collection("nurses").update_one(
            {"nurse_id": normalized_nurse_id},
            {"$set": {"password": stored_password}},
        )

    stored_role = str(nurse.get("role") or "staff")
    if stored_role not in {"staff", "admin"}:
        stored_role = "staff"
        get_collection("nurses").update_one(
            {"nurse_id": normalized_nurse_id},
            {"$set": {"role": stored_role}},
        )

    if not verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid nurse ID or password.")

    if role != stored_role:
        raise HTTPException(status_code=401, detail="Invalid nurse ID or password.")

    return NurseLoginResponse(
        nurse_id=nurse["nurse_id"],
        name=nurse.get("name", "Nurse"),
        on_duty=bool(nurse.get("on_duty", True)),
        role=stored_role,
    ).model_dump()


def list_nurses() -> list[dict]:
    cursor = get_collection("nurses").find({}, {"_id": 0}).sort("nurse_id", 1)
    return [_nurse_summary(document) for document in cursor]


def update_nurse_duty_status(nurse_id: str, on_duty: bool) -> dict:
    normalized_nurse_id = nurse_id.strip()
    updated = get_collection("nurses").find_one_and_update(
        {"nurse_id": normalized_nurse_id},
        {"$set": {"on_duty": bool(on_duty)}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Nurse '{nurse_id}' not found.")

    return NurseDutyResponse(
        nurse_id=updated["nurse_id"],
        name=updated.get("name", "Nurse"),
        on_duty=bool(updated.get("on_duty", True)),
        role=str(updated.get("role") or "staff"),
    ).model_dump()
