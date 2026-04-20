from datetime import datetime, UTC

from database import get_collection
from utils.id_generator import get_next_id
from utils.data_utils import serialize_mongo


def create_session(vapi_session_id: str | None = None) -> dict:
    session_id = get_next_id("chatbot_sessions", "CS")
    now = datetime.now(UTC)
    document = {
        "session_id": session_id,
        "vapi_session_id": vapi_session_id,
        "patient_id": None,
        "user_role": None,
        "status": "active",
        "conversation_raw": [],
        "collected_fields": {},
        "fields_missing": [],
        "collection_confidence": None,
        "created_at": now,
        "updated_at": now,
    }
    get_collection("chatbot_sessions").insert_one(document)
    return {"session_id": session_id}


def finalize_session(
    session_id: str,
    visit_id: str,
    patient_id: str,
    user_role: str,
    collected_fields: dict,
    conversation_raw: list,
    fields_missing: list[str],
    collection_confidence: float | None,
) -> None:
    get_collection("chatbot_sessions").update_one(
        {"session_id": session_id},
        {
            "$set": {
                "patient_id": patient_id,
                "user_role": user_role,
                "visit_id": visit_id,
                "status": "completed",
                "collected_fields": collected_fields,
                "conversation_raw": conversation_raw,
                "fields_missing": fields_missing,
                "collection_confidence": collection_confidence,
                "updated_at": datetime.now(UTC),
            }
        },
    )


def get_session(session_id: str) -> dict | None:
    doc = get_collection("chatbot_sessions").find_one({"session_id": session_id})
    return serialize_mongo(doc) if doc else None
