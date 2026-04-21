from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SuperAdminDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    admin_id: str
    name: str
    password: str
    role: Literal["superadmin"] = "superadmin"


class SuperAdminLoginRequest(BaseModel):
    admin_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class SuperAdminLoginResponse(BaseModel):
    admin_id: str
    name: str
    role: Literal["superadmin"] = "superadmin"


class StaffDutyItem(BaseModel):
    staff_id: str
    name: str
    role: str
    on_duty: bool
    specialty: str | None = None


class SuperAdminSummaryResponse(BaseModel):
    total_patients: int
    total_visits: int
    total_nurses: int
    total_doctors: int
    nurses_on_duty: int
    nurses_off_duty: int
    doctors_on_duty: int
    doctors_off_duty: int
    attended_visits: int
    pending_visits: int
    unassigned_visits: int
    nurses: list[StaffDutyItem]
    doctors: list[StaffDutyItem]


class SuperAdminAssignmentItem(BaseModel):
    visit_id: str
    patient_id: str
    patient_name: str
    nurse_id: str
    nurse_name: str | None = None
    assigned_doctor_id: str | None = None
    assigned_doctor_name: str | None = None
    target_specialty: str | None = None
    assignment_status: str
    triage_acuity: int
    urgency_label: str
    attended_by_doctor: bool
    attended_at: datetime | None = None
    attended_by_doctor_id: str | None = None
    created_at: datetime


class SuperAdminMarkAttendedResponse(BaseModel):
    visit_id: str
    attended_by_doctor: bool
    attended_at: datetime | None = None
    attended_by_doctor_id: str | None = None
    assignment_status: str


class SuperAdminReassignRequest(BaseModel):
    doctor_id: str = Field(..., min_length=1)


class SuperAdminReassignResponse(BaseModel):
    visit_id: str
    assigned_doctor_id: str | None = None
    assigned_doctor_name: str | None = None
    assignment_status: str
    attended_by_doctor: bool
    attended_at: datetime | None = None
    attended_by_doctor_id: str | None = None
