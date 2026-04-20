from fastapi import APIRouter

from src.doctors.schema import DoctorDutyUpdateRequest, DoctorLoginRequest, DoctorLoginResponse
from src.doctors.service import (
    authenticate_doctor,
    list_doctor_patients,
    list_doctors,
    mark_patient_attended,
    update_doctor_duty_status,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/login", response_model=DoctorLoginResponse)
def login_doctor(body: DoctorLoginRequest):
    return authenticate_doctor(doctor_id=body.doctor_id, password=body.password, role=body.role)


@router.get("")
def get_doctors():
    return {"items": list_doctors()}


@router.get("/{doctor_id}/patients")
def get_doctor_patients(doctor_id: str):
    return {"items": list_doctor_patients(doctor_id)}


@router.post("/{doctor_id}/patients/{visit_id}/attend")
def attend_doctor_patient(doctor_id: str, visit_id: str):
    return mark_patient_attended(doctor_id, visit_id)


@router.post("/{doctor_id}/duty")
def update_doctor_duty(doctor_id: str, body: DoctorDutyUpdateRequest):
    return update_doctor_duty_status(doctor_id, body.on_duty)
