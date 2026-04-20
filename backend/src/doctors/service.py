from fastapi import HTTPException

from database import get_collection
from src.doctors.schema import DoctorLoginResponse
from utils.security import hash_password, verify_password


def authenticate_doctor(doctor_id: str, password: str, role: str = "admin") -> dict:
    normalized_doctor_id = doctor_id.strip()
    doctor = get_collection("doctors").find_one({"doctor_id": normalized_doctor_id})

    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid doctor ID or password.")

    stored_password = doctor.get("password")

    # Graceful migration path for old records that do not yet have a password field.
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
    ).model_dump()
