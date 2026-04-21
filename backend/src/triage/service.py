import logging
import math
import sys
from datetime import datetime, UTC
from pathlib import Path

from fastapi import HTTPException

from database import get_collection
from src.doctors.service import assign_doctor_for_specialty, determine_target_specialty
from src.visits.schema import VisitDocument
from src.patients.service import (
    create_patient_record,
    get_patient_by_id,
    get_patient_history,
    increment_patient_visit_counter,
)
from constants import FORM_OPTION_LABELS, MODEL_FEATURES, URGENCY_LABELS
from constants.model import HX_FIELDS
from src.triage.reconstruction import build_pre_pca_payload, prepare_visit_measurements
from src.triage.schema import TriageSubmission
from utils.id_generator import get_next_id

log = logging.getLogger(__name__)

_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

predict_api = None

try:
    from ml.src import predict_api  # noqa: E402
except Exception as exc:
    predict_api = None
    log.exception("Failed to import ML predict_api: %s", exc)


def load_ml_model():
    if predict_api is None:
        raise RuntimeError("ML pipeline could not be imported.")
    predict_api.load_all_models()
    loaded = predict_api.get_engine_status().get('loaded_versions', [])
    if not loaded:
        raise RuntimeError("No ML models loaded.")
    log.info("ML models loaded: %s", loaded)


def get_engine_status() -> dict:
    if predict_api is None:
        return {"engine": "unavailable", "ml_model_loaded": False}
    status = predict_api.get_engine_status()
    loaded = status.get('loaded_versions', [])
    return {
        "engine": "ml_pipeline" if loaded else "unavailable",
        "ml_model_loaded": bool(loaded),
        "loaded_versions": loaded,
        "bert_loaded": status.get('bert_loaded', False),
    }


def get_form_options() -> dict:
    sites = list(get_collection("sites").find({}, {"_id": 0}).sort("site_id", 1))
    nurses = list(get_collection("nurses").find({}, {"_id": 0}).sort("nurse_id", 1))

    site_options = [{"value": site["site_id"], "label": site["name"]} for site in sites]
    nurse_options = [{"value": "self", "label": "Self Registration"}]
    nurse_options.extend(
        {"value": nurse["nurse_id"], "label": nurse["name"]}
        for nurse in nurses
    )

    return {
        "field_options": {
            **FORM_OPTION_LABELS,
            "site_id": site_options,
            "nurse_id": nurse_options,
        }
    }


def _validate_context(visit_payload: dict):
    site = get_collection("sites").find_one({"site_id": visit_payload["site_id"]})
    if not site:
        raise HTTPException(status_code=400, detail=f"Unknown site_id '{visit_payload['site_id']}'.")

    if visit_payload["nurse_id"] != "self":
        nurse = get_collection("nurses").find_one({"nurse_id": visit_payload["nurse_id"]})
        if not nurse:
            raise HTTPException(status_code=400, detail=f"Unknown nurse_id '{visit_payload['nurse_id']}'.")


def _resolve_patient(submission: TriageSubmission) -> tuple[dict, bool]:
    if submission.patient_id:
        return get_patient_by_id(submission.patient_id), False
    return create_patient_record(submission.patient.model_dump()), True


def _history_is_available(pre_pca_payload: dict) -> bool:
    """Returns True if at least one hx_* field has a real value (not NaN)."""
    for field in HX_FIELDS:
        val = pre_pca_payload.get(field)
        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            return True
    return False


def _predict_triage(pre_pca_payload: dict, visit_payload: dict) -> dict:
    if predict_api is None:
        raise HTTPException(status_code=503, detail="ML model is not loaded.")

    # ── Step 1: infer chief_complaint_system via v1.0.2-b if missing ─────────
    cc_system = pre_pca_payload.get("chief_complaint_system")
    if not cc_system or str(cc_system).strip().lower() in ("none", "null", "unknown", "nan", ""):
        cc_raw = pre_pca_payload.get("chief_complaint_raw") or ""
        log.info("chief_complaint_system missing — running v1.0.2-b on: %r", cc_raw)
        inferred = predict_api.predict_chief_complaint_system(cc_raw)
        if inferred:
            pre_pca_payload = {**pre_pca_payload, "chief_complaint_system": inferred}
            visit_payload = {**visit_payload, "chief_complaint_system": inferred}
            log.info("v1.0.2-b inferred chief_complaint_system: %s", inferred)

    # ── Step 2: choose v1.0.2 (history present) or v1.0.2-c (no history) ────
    has_history = _history_is_available(pre_pca_payload)
    ml_result = predict_api.predict_triage_acuity(pre_pca_payload, has_history=has_history)

    triage_acuity = int(ml_result["triage_acuity"])
    model_version = ml_result.get("model_version", "v1.0.2")
    log.info("Acuity=%s via %s (has_history=%s)", triage_acuity, model_version, has_history)

    return {
        "triage_acuity": triage_acuity,
        "urgency_label": URGENCY_LABELS.get(triage_acuity, "Unknown"),
        "engine": f"ml_pipeline/{model_version}",
        # Pass inferred cc_system back so the visit document can store it
        "_resolved_visit_payload": visit_payload,
    }


def _resolve_doctor_assignment(visit_payload: dict, prediction: dict) -> dict:
    target_specialty = determine_target_specialty(
        chief_complaint_system=visit_payload.get("chief_complaint_system"),
        triage_acuity=prediction["triage_acuity"],
    )
    assigned_doctor_id, assignment_status = assign_doctor_for_specialty(target_specialty)
    return {
        "target_specialty": target_specialty,
        "assigned_doctor_id": assigned_doctor_id,
        "assignment_status": assignment_status,
    }


def _create_visit_document(
    patient_document: dict,
    visit_payload: dict,
    prediction: dict,
    routing: dict,
) -> dict:
    visit_id = get_next_id("visits", "VT")
    document = VisitDocument(
        visit_id=visit_id,
        patient_id=patient_document["patient_id"],
        site_id=visit_payload["site_id"],
        nurse_id=visit_payload["nurse_id"],
        arrival_mode=visit_payload["arrival_mode"],
        arrival_time=visit_payload["arrival_time"],
        transport_origin=visit_payload["transport_origin"],
        pain_location=visit_payload["pain_location"],
        mental_status_triage=visit_payload["mental_status_triage"],
        chief_complaint_raw=visit_payload["chief_complaint_raw"],
        chief_complaint_system=visit_payload.get("chief_complaint_system"),
        heart_rate=visit_payload["heart_rate"],
        respiratory_rate=visit_payload["respiratory_rate"],
        temperature_c=visit_payload["temperature_c"],
        spo2=visit_payload["spo2"],
        systolic_bp=visit_payload["systolic_bp"],
        diastolic_bp=visit_payload["diastolic_bp"],
        gcs_total=visit_payload["gcs_total"],
        pain_score=visit_payload["pain_score"],
        mean_arterial_pressure=visit_payload["mean_arterial_pressure"],
        pulse_pressure=visit_payload["pulse_pressure"],
        shock_index=visit_payload["shock_index"],
        news2_score=visit_payload["news2_score"],
        triage_acuity=prediction["triage_acuity"],
        urgency_label=prediction["urgency_label"],
        engine=prediction["engine"],
        target_specialty=routing["target_specialty"],
        assigned_doctor_id=routing["assigned_doctor_id"],
        assignment_status=routing["assignment_status"],
        attended_by_doctor=False,
        attended_at=None,
        attended_by_doctor_id=None,
        data_source=visit_payload.get("data_source", "form"),
        chatbot_session_id=visit_payload.get("chatbot_session_id"),
        chief_complaint_normalized=visit_payload.get("chief_complaint_normalized"),
        fields_missing=visit_payload.get("fields_missing"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ).model_dump()
    get_collection("visits").insert_one(document)
    return document


def submit_triage(submission: TriageSubmission) -> dict:
    visit_payload = prepare_visit_measurements(submission.visit.model_dump())
    _validate_context(visit_payload)
    patient_document, _ = _resolve_patient(submission)
    history_document = get_patient_history(patient_document["patient_id"])

    pre_pca_payload = build_pre_pca_payload(
        patient_document=patient_document,
        visit_document=visit_payload,
        history_document=history_document,
    )

    prediction = _predict_triage(pre_pca_payload, visit_payload)

    # Use the visit_payload that may have had chief_complaint_system filled in by v1.0.2-b
    resolved_visit_payload = prediction.pop("_resolved_visit_payload", visit_payload)

    routing = _resolve_doctor_assignment(resolved_visit_payload, prediction)
    visit_document = _create_visit_document(patient_document, resolved_visit_payload, prediction, routing)
    increment_patient_visit_counter(patient_document["patient_id"])

    log.info(
        "Created visit %s for patient %s | engine=%s | specialty=%s",
        visit_document["visit_id"],
        patient_document["patient_id"],
        prediction["engine"],
        visit_document.get("target_specialty"),
    )

    return {
        "patient_id": patient_document["patient_id"],
        "visit_id": visit_document["visit_id"],
        "triage_acuity": prediction["triage_acuity"],
        "urgency_label": prediction["urgency_label"],
        "engine": prediction["engine"],
        "chief_complaint_system": visit_document.get("chief_complaint_system"),
        "target_specialty": visit_document.get("target_specialty"),
        "assigned_doctor_id": visit_document.get("assigned_doctor_id"),
    }
