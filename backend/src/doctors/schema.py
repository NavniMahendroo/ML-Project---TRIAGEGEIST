from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DoctorDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doctor_id: str
    name: str
    password: str
    specialty: str
    on_duty: bool = True
    role: Literal["staff", "admin"] = "admin"


class DoctorLoginRequest(BaseModel):
    doctor_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Literal["staff", "admin"] = "admin"


class DoctorLoginResponse(BaseModel):
    doctor_id: str
    name: str
    role: Literal["staff", "admin"]
    specialty: str | None = None
    on_duty: bool = True


class DoctorSummaryResponse(BaseModel):
    doctor_id: str
    name: str
    specialty: str
    on_duty: bool
    role: Literal["staff", "admin"]


class DoctorDutyUpdateRequest(BaseModel):
    on_duty: bool


class DoctorDutyResponse(BaseModel):
    doctor_id: str
    name: str
    specialty: str
    on_duty: bool
    role: Literal["staff", "admin"]


class DoctorAssignedPatientResponse(BaseModel):
    visit_id: str
    patient_id: str
    patient_name: str
    triage_acuity: int
    urgency_label: str
    target_specialty: str | None = None
    assignment_status: str
    attended_by_doctor: bool
    attended_at: datetime | None = None
    attended_by_doctor_id: str | None = None
    chief_complaint_system: str | None = None
    created_at: datetime


class DoctorAttendResponse(BaseModel):
    visit_id: str
    patient_id: str
    patient_name: str
    attended_by_doctor: bool
    attended_at: datetime | None = None
    attended_by_doctor_id: str | None = None
    assignment_status: str
