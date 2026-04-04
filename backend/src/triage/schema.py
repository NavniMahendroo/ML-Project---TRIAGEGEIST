from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from constants.options import (
    ARRIVAL_MODE_OPTIONS,
    INSURANCE_OPTIONS,
    LANGUAGE_OPTIONS,
    MENTAL_STATUS_OPTIONS,
    PAIN_LOCATION_OPTIONS,
    SEX_OPTIONS,
    TRANSPORT_ORIGIN_OPTIONS,
)
from utils.data_utils import normalize_enum, normalize_gender


class PatientRegistrationInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=0, le=120)
    sex: str = Field(...)
    language: str = Field(...)
    insurance_type: str = Field(...)
    num_active_medications: int = Field(..., ge=0, le=20)
    num_comorbidities: int = Field(..., ge=0, le=20)
    weight_kg: float = Field(..., ge=2.0, le=200.0)
    height_cm: float = Field(..., ge=45.0, le=250.0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Patient name is required.")
        return normalized

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str) -> str:
        normalized = normalize_gender(value)
        if normalized not in SEX_OPTIONS:
            raise ValueError("Unsupported sex value.")
        return normalized

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return normalize_enum(value, LANGUAGE_OPTIONS)

    @field_validator("insurance_type")
    @classmethod
    def validate_insurance_type(cls, value: str) -> str:
        return normalize_enum(value, INSURANCE_OPTIONS)


class VisitInput(BaseModel):
    site_id: str = Field(..., min_length=1)
    nurse_id: str = Field(..., min_length=1)
    arrival_mode: str = Field(...)
    transport_origin: str = Field(...)
    pain_location: str = Field(...)
    mental_status_triage: str = Field(...)
    chief_complaint_raw: str = Field(..., min_length=1)
    chief_complaint_system: str | None = Field(default=None)
    heart_rate: float | None = Field(default=None, ge=20, le=260)
    respiratory_rate: float | None = Field(default=None, ge=0, le=80)
    spo2: float | None = Field(default=None, ge=0, le=100)
    systolic_bp: float | None = Field(default=None, ge=40, le=300)
    diastolic_bp: float | None = Field(default=None, ge=20, le=200)
    temperature_c: float | None = Field(default=None, ge=30.0, le=45.0)
    pain_score: int | None = Field(default=None, ge=0, le=10)
    gcs_total: int | None = Field(default=None, ge=3, le=15)
    arrival_time: datetime | None = Field(default=None)

    @field_validator("site_id", "nurse_id", "chief_complaint_raw")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be empty.")
        return normalized

    @field_validator("arrival_mode")
    @classmethod
    def validate_arrival_mode(cls, value: str) -> str:
        return normalize_enum(value, ARRIVAL_MODE_OPTIONS)

    @field_validator("transport_origin")
    @classmethod
    def validate_transport_origin(cls, value: str) -> str:
        return normalize_enum(value, TRANSPORT_ORIGIN_OPTIONS)

    @field_validator("pain_location")
    @classmethod
    def validate_pain_location(cls, value: str) -> str:
        return normalize_enum(value, PAIN_LOCATION_OPTIONS)

    @field_validator("mental_status_triage")
    @classmethod
    def validate_mental_status(cls, value: str) -> str:
        return normalize_enum(value, MENTAL_STATUS_OPTIONS)


class TriageSubmission(BaseModel):
    patient_id: str | None = Field(default=None)
    patient: PatientRegistrationInput | None = Field(default=None)
    visit: VisitInput = Field(...)

    @model_validator(mode="after")
    def validate_patient_source(self):
        if not self.patient_id and not self.patient:
            raise ValueError("Provide either patient_id for an existing patient or patient data for a new patient.")
        if self.patient_id and self.patient:
            raise ValueError("Provide either patient_id or patient data, not both.")
        return self


class TriageResponse(BaseModel):
    patient_id: str
    visit_id: str
    triage_acuity: int
    urgency_label: str
    engine: str
    chief_complaint_system: str | None = None
