from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DoctorDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doctor_id: str
    name: str
    password: str
    role: Literal["staff", "admin"] = "admin"


class DoctorLoginRequest(BaseModel):
    doctor_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Literal["staff", "admin"] = "admin"


class DoctorLoginResponse(BaseModel):
    doctor_id: str
    name: str
    role: Literal["staff", "admin"]
