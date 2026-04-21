from fastapi import APIRouter

from src.nurses.schema import NurseDutyUpdateRequest, NurseLoginRequest, NurseLoginResponse
from src.nurses.service import authenticate_nurse, list_nurses, update_nurse_duty_status

router = APIRouter(prefix="/nurses", tags=["nurses"])


@router.post("/login", response_model=NurseLoginResponse)
def login_nurse(body: NurseLoginRequest):
    return authenticate_nurse(nurse_id=body.nurse_id, password=body.password, role=body.role)


@router.get("")
def get_nurses():
    return {"items": list_nurses()}


@router.post("/{nurse_id}/duty")
def update_nurse_duty(nurse_id: str, body: NurseDutyUpdateRequest):
    return update_nurse_duty_status(nurse_id, body.on_duty)
