from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NurseDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nurse_id: str
    name: str
    password: str
    role: Literal["staff", "admin"] = "staff"


class NurseLoginRequest(BaseModel):
    nurse_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Literal["staff", "admin"] = "staff"


class NurseLoginResponse(BaseModel):
    nurse_id: str
    name: str
    role: Literal["staff", "admin"] = "staff"
