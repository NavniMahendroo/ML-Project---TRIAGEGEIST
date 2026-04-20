from fastapi import APIRouter

from src.nurses.schema import NurseLoginRequest, NurseLoginResponse
from src.nurses.service import authenticate_nurse

router = APIRouter(prefix="/nurses", tags=["nurses"])


@router.post("/login", response_model=NurseLoginResponse)
def login_nurse(body: NurseLoginRequest):
    return authenticate_nurse(nurse_id=body.nurse_id, password=body.password, role=body.role)
