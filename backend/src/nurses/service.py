from fastapi import HTTPException

from database import get_collection
from src.nurses.schema import NurseLoginResponse
from utils.security import hash_password, verify_password


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
        role=stored_role,
    ).model_dump()
