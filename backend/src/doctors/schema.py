from pydantic import BaseModel, ConfigDict


class DoctorDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doctor_id: str
    name: str
