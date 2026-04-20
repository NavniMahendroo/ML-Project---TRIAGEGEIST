from fastapi import APIRouter

from src.doctors.schema import DoctorLoginRequest, DoctorLoginResponse
from src.doctors.service import authenticate_doctor

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/login", response_model=DoctorLoginResponse)
def login_doctor(body: DoctorLoginRequest):
    return authenticate_doctor(doctor_id=body.doctor_id, password=body.password, role=body.role)
