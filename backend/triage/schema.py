from typing import Literal
from pydantic import BaseModel, Field

class PatientInput(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["M", "F"] = Field(...)
    arrival_mode: Literal["walk-in", "ambulance", "police", "helicopter", "other"] = Field(...)
    chief_complaint_raw: str = Field(...)
    heart_rate: int = Field(..., ge=20, le=260)
    respiratory_rate: int = Field(..., ge=0, le=80)
    spo2: int = Field(..., ge=0, le=100)
    systolic_bp: int = Field(..., ge=40, le=300)
    diastolic_bp: int = Field(..., ge=20, le=200)
    temperature_c: float = Field(..., ge=30.0, le=45.0)
    pain_score: int = Field(..., ge=0, le=10)
    gcs_total: int = Field(..., ge=3, le=15)
    news2_score: int = Field(..., ge=0, le=20)
