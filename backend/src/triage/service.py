import logging
import sys
from datetime import datetime, UTC
from pathlib import Path

from fastapi import HTTPException

from database import get_collection
from src.visits.schema import VisitDocument
from src.patients.service import (
    create_patient_record,
    get_patient_by_id,
    get_patient_history,
    increment_patient_visit_counter,
)
from constants import FORM_OPTION_LABELS, MODEL_FEATURES, URGENCY_LABELS
from src.triage.reconstruction import build_pre_pca_payload, prepare_visit_measurements
from src.triage.schema import TriageSubmission
from utils.id_generator import get_next_id

log = logging.getLogger(__name__)

_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

_ml_model_loaded = False
predict_api = None

try:
    from ml.src import predict_api  # noqa: E402
except Exception as exc:  # pragma: no cover - import path/runtime environment issue
    predict_api = None
    log.exception("Failed to import ML predict_api: %s", exc)


def load_ml_model():
    global _ml_model_loaded
    if predict_api is None:
        raise RuntimeError("ML pipeline could not be imported.")

    predict_api.load_model()
    _ml_model_loaded = predict_api._model is not None
    if not _ml_model_loaded:
        raise RuntimeError("ML model failed to load.")
    log.info("ML model loaded successfully.")


def get_engine_status() -> dict:
    return {
        "engine": "ml_pipeline" if _ml_model_loaded else "unavailable",
        "ml_model_loaded": _ml_model_loaded,
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


def _predict_triage(pre_pca_payload: dict) -> dict:
    if not _ml_model_loaded:
        raise HTTPException(status_code=503, detail="ML model is not loaded.")

    ml_result = predict_api.predict_patient(pre_pca_payload)
    triage_acuity = int(ml_result["triage_acuity"])
    return {
        "triage_acuity": triage_acuity,
        "urgency_label": URGENCY_LABELS.get(triage_acuity, "Unknown"),
        "engine": "ml_pipeline",
    }


def _create_visit_document(patient_document: dict, visit_payload: dict, prediction: dict) -> dict:
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
    prediction = _predict_triage(pre_pca_payload)
    visit_document = _create_visit_document(patient_document, visit_payload, prediction)
    increment_patient_visit_counter(patient_document["patient_id"])

    log.info(
        "Created visit %s for patient %s with %s-feature payload.",
        visit_document["visit_id"],
        patient_document["patient_id"],
        len(MODEL_FEATURES),
    )

    return {
        "patient_id": patient_document["patient_id"],
        "visit_id": visit_document["visit_id"],
        "triage_acuity": prediction["triage_acuity"],
        "urgency_label": prediction["urgency_label"],
        "engine": prediction["engine"],
        "chief_complaint_system": visit_document.get("chief_complaint_system"),
    }
