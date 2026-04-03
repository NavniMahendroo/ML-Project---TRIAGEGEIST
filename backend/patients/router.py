from fastapi import APIRouter

from patients.service import get_next_serial_number

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/")
def list_patients():
    return {"message": "List recent patients endpoint placeholder."}
