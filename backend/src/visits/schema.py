from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visit_id: str
    patient_id: str
    site_id: str
    nurse_id: str
    arrival_mode: str
    arrival_time: datetime
    transport_origin: str
    pain_location: str
    mental_status_triage: str
    chief_complaint_raw: str
    chief_complaint_system: str | None = None
    heart_rate: float | None = None
    respiratory_rate: float | None = None
    temperature_c: float | None = None
    spo2: float | None = None
    systolic_bp: float | None = None
    diastolic_bp: float | None = None
    gcs_total: int | None = None
    pain_score: int | None = None
    mean_arterial_pressure: float | None = None
    pulse_pressure: float | None = None
    shock_index: float | None = None
    news2_score: float | None = None
    triage_acuity: int
    urgency_label: str
    engine: str
    created_at: datetime
    updated_at: datetime
