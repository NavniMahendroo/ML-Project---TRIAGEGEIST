from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatientDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    name: str
    age: int
    sex: str
    language: str
    insurance_type: str
    num_prior_ed_visits_12m: int
    num_prior_admissions_12m: int
    num_active_medications: int
    num_comorbidities: int
    weight_kg: float
    height_cm: float
    age_group: str
    bmi: float
    created_at: datetime
    updated_at: datetime
