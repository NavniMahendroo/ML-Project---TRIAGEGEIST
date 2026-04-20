from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    vapi_session_id: str | None = Field(default=None)


class VerifyPatientRequest(BaseModel):
    name: str = Field(..., min_length=1)
    age: int | None = Field(default=None, ge=0, le=120)
    patient_id: str | None = Field(default=None)


class ConversationMessage(BaseModel):
    role: str
    text: str
    ts: str


class ChatbotSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    patient_id: str | None = Field(default=None)
    user_role: str = Field(...)
    collected_fields: dict = Field(...)
    conversation_raw: list[ConversationMessage] = Field(default_factory=list)
    fields_missing: list[str] = Field(default_factory=list)
    collection_confidence: float | None = Field(default=None)
