from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NurseDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nurse_id: str
    name: str
    password: str
    on_duty: bool = True
    role: Literal["staff", "admin"] = "staff"


class NurseLoginRequest(BaseModel):
    nurse_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Literal["staff", "admin"] = "staff"


class NurseLoginResponse(BaseModel):
    nurse_id: str
    name: str
    on_duty: bool = True
    role: Literal["staff", "admin"] = "staff"


class NurseSummaryResponse(BaseModel):
    nurse_id: str
    name: str
    on_duty: bool
    role: Literal["staff", "admin"]


class NurseDutyUpdateRequest(BaseModel):
    on_duty: bool


class NurseDutyResponse(BaseModel):
    nurse_id: str
    name: str
    on_duty: bool
    role: Literal["staff", "admin"]
