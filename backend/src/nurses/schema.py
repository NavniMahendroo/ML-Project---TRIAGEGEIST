from pydantic import BaseModel, ConfigDict


class NurseDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nurse_id: str
    name: str
