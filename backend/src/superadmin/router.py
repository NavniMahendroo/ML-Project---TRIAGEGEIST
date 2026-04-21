from fastapi import APIRouter, Query

from src.superadmin.schema import (
    SuperAdminLoginRequest,
    SuperAdminLoginResponse,
    SuperAdminReassignRequest,
)
from src.superadmin.service import (
    authenticate_superadmin,
    get_dashboard_summary,
    list_assignments,
    mark_assignment_attended,
    reassign_visit,
)

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.post("/login", response_model=SuperAdminLoginResponse)
def login_superadmin(body: SuperAdminLoginRequest):
    return authenticate_superadmin(admin_id=body.admin_id, password=body.password)


@router.get("/dashboard/summary")
def dashboard_summary():
    return get_dashboard_summary()


@router.get("/dashboard/assignments")
def dashboard_assignments(limit: int = Query(default=100, ge=1, le=500)):
    return {"items": list_assignments(limit=limit)}


@router.post("/dashboard/assignments/{visit_id}/attend")
def attend_assignment(visit_id: str):
    return mark_assignment_attended(visit_id)


@router.post("/dashboard/assignments/{visit_id}/reassign")
def reassign_assignment(visit_id: str, body: SuperAdminReassignRequest):
    return reassign_visit(visit_id, body.doctor_id)
