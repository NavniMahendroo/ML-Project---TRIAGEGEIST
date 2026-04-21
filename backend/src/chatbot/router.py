import logging
from datetime import datetime, UTC

from fastapi import APIRouter, HTTPException

from src.chatbot.schema import SessionStartRequest, VerifyPatientRequest, ChatbotSubmitRequest
from src.chatbot.service import create_session, finalize_session
from utils.fuzzy import fuzzy_match_patients
from src.patients.service import get_patient_by_id
from src.triage.schema import TriageSubmission, VisitInput
from src.triage.service import submit_triage
from constants.options import ARRIVAL_MODE_OPTIONS, PAIN_LOCATION_OPTIONS, MENTAL_STATUS_OPTIONS

log = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

_SITE_ID = "SITE-0001"
_NURSE_ID = "self"


def _normalize_patient_id(patient_id: str) -> str:
    """Normalize patient ID to canonical format: TG-0002, TG-0015, etc."""
    pid = patient_id.strip().upper()
    if "-" in pid:
        prefix, num = pid.rsplit("-", 1)
        if num.isdigit():
            return f"{prefix}-{num.zfill(4)}"
    return pid


def _clean(value):
    """Convert LLM string 'null'/'none'/'unknown' to Python None, and coerce numeric strings."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in ("null", "none", "unknown", "n/a", ""):
        return None
    return value


def _clean_num(value):
    """Return None if value is null-like, otherwise return the value for Pydantic to coerce."""
    cleaned = _clean(value)
    if cleaned is None:
        return None
    try:
        f = float(str(cleaned))
        return f
    except (ValueError, TypeError):
        return None


@router.post("/session/start")
def start_session(body: SessionStartRequest):
    session = create_session(vapi_session_id=body.vapi_session_id)
    log.info("[CHATBOT] Session started: %s (vapi_id=%s)", session.get("session_id"), body.vapi_session_id)
    return session


@router.post("/verify")
def verify_patient(body: VerifyPatientRequest):
    log.info("[CHATBOT] Verify patient: name=%s age=%s patient_id=%s", body.name, body.age, body.patient_id)
    if body.patient_id:
        try:
            patient = get_patient_by_id(body.patient_id)
            log.info("[CHATBOT] Verified by ID: %s → %s", body.patient_id, patient.get("name"))
            return {
                "matches": [{
                    "patient_id": patient["patient_id"],
                    "name": patient["name"],
                    "age": patient["age"],
                    "name_score": 100.0,
                    "age_match": True,
                    "combined_score": 110.0,
                }]
            }
        except HTTPException:
            pass

    matches = fuzzy_match_patients(name=body.name, age=body.age)
    log.info("[CHATBOT] Fuzzy match results: %d candidates for name=%s", len(matches), body.name)
    return {"matches": matches}


@router.post("/submit")
def submit_chatbot_triage(body: ChatbotSubmitRequest):
    fields = body.collected_fields
    log.info("[CHATBOT] Submit received — session=%s patient_id=%s user_role=%s fields=%s",
             body.session_id, body.patient_id, body.user_role, list(fields.keys()))

    arrival_mode = _resolve_enum(_clean(fields.get("arrival_mode")), ARRIVAL_MODE_OPTIONS, "walk-in")
    pain_location = _resolve_enum(_clean(fields.get("pain_location")), PAIN_LOCATION_OPTIONS, "unknown")
    mental_status = _resolve_enum(_clean(fields.get("mental_status_triage")), MENTAL_STATUS_OPTIONS, "alert")
    transport_origin = _clean(fields.get("transport_origin"))

    cc_for_model = (
        _clean(fields.get("chief_complaint_normalized"))
        or _clean(fields.get("chief_complaint_raw"))
        or "not provided"
    )

    try:
        visit_input = VisitInput(
            site_id=_SITE_ID,
            nurse_id=_NURSE_ID,
            arrival_mode=arrival_mode,
            transport_origin=transport_origin,
            pain_location=pain_location,
            mental_status_triage=mental_status,
            chief_complaint_raw=cc_for_model,
            chief_complaint_system=_clean(fields.get("chief_complaint_system")),
            heart_rate=_clean_num(fields.get("heart_rate")),
            respiratory_rate=_clean_num(fields.get("respiratory_rate")),
            spo2=_clean_num(fields.get("spo2")),
            systolic_bp=_clean_num(fields.get("systolic_bp")),
            diastolic_bp=_clean_num(fields.get("diastolic_bp")),
            temperature_c=_clean_num(fields.get("temperature_c")),
            pain_score=_clean_num(fields.get("pain_score")),
            gcs_total=_clean_num(fields.get("gcs_total")),
            arrival_time=datetime.now(UTC),
            data_source="voice_bot",
            chatbot_session_id=body.session_id,
            chief_complaint_normalized=_clean(fields.get("chief_complaint_normalized")) or _clean(fields.get("chief_complaint_raw")),
            fields_missing=body.fields_missing if body.fields_missing else None,
        )
    except Exception as exc:
        log.error("[CHATBOT] VisitInput validation failed: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))

    # Resolve patient: body.patient_id → fields.patient_id → fuzzy name match
    patient_id = body.patient_id or _clean(fields.get("patient_id"))

    if patient_id:
        # Normalize ID format: "TG-2" or "TG-002" → "TG-0002" (4-digit zero-padded)
        patient_id = _normalize_patient_id(patient_id)
        log.info("[CHATBOT] Patient ID resolved: %s", patient_id)
        # Verify the ID actually exists; if not, fall through to fuzzy match
        try:
            get_patient_by_id(patient_id)
        except HTTPException:
            log.warning("[CHATBOT] Patient ID %s not found — falling back to fuzzy match", patient_id)
            patient_id = None

    if not patient_id:
        name = _clean(fields.get("patient_name"))
        age = _clean_num(fields.get("patient_age"))
        log.info("[CHATBOT] Fuzzy matching name=%s age=%s", name, age)
        if name:
            matches = fuzzy_match_patients(name=name, age=int(age) if age else None)
            if matches:
                patient_id = matches[0]["patient_id"]
                log.info("[CHATBOT] Fuzzy match found: %s (score=%.1f)", patient_id, matches[0].get("combined_score", 0))

    if not patient_id:
        log.warning("[CHATBOT] Patient not identified — name=%s", fields.get("patient_name"))
        raise HTTPException(status_code=400, detail="Patient could not be identified. Please provide your registered name.")

    submission = TriageSubmission(patient_id=patient_id, visit=visit_input)

    try:
        result = submit_triage(submission)
        log.info("[CHATBOT] Triage complete — visit=%s patient=%s acuity=%s",
                 result.get("visit_id"), patient_id, result.get("triage_acuity"))
    except Exception as exc:
        log.exception("[CHATBOT] submit_triage failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        finalize_session(
            session_id=body.session_id,
            visit_id=result["visit_id"],
            patient_id=patient_id,
            user_role=body.user_role,
            collected_fields=fields,
            conversation_raw=[m.model_dump() for m in body.conversation_raw],
            fields_missing=body.fields_missing,
            collection_confidence=body.collection_confidence,
        )
        log.info("[CHATBOT] Session finalized: %s", body.session_id)
    except Exception as exc:
        log.warning("[CHATBOT] Session finalize failed (non-critical): %s", exc)

    return result


def _resolve_enum(value: str | None, allowed: list[str], fallback: str) -> str:
    if not value:
        return fallback
    lower = value.strip().casefold()
    for option in allowed:
        if option.casefold() == lower:
            return option
    return fallback
