from datetime import datetime, UTC
import math

from constants.model import HX_FIELDS, PRE_PCA_FIELDS
from utils.clinical_utils import (
    calculate_mean_arterial_pressure,
    calculate_news2_score,
    calculate_pulse_pressure,
    calculate_shock_index,
)


def prepare_visit_measurements(visit_payload: dict) -> dict:
    measurements = dict(visit_payload)

    measurements["mean_arterial_pressure"] = calculate_mean_arterial_pressure(
        measurements["systolic_bp"],
        measurements["diastolic_bp"],
    )
    measurements["pulse_pressure"] = calculate_pulse_pressure(
        measurements["systolic_bp"],
        measurements["diastolic_bp"],
    )
    measurements["shock_index"] = calculate_shock_index(
        measurements["heart_rate"],
        measurements["systolic_bp"],
    )
    measurements["news2_score"] = calculate_news2_score(
        heart_rate=measurements["heart_rate"],
        respiratory_rate=measurements["respiratory_rate"],
        spo2=measurements["spo2"],
        temperature_c=measurements["temperature_c"],
        systolic_bp=measurements["systolic_bp"],
        gcs_total=measurements["gcs_total"],
    )
    measurements["arrival_time"] = visit_payload.get("arrival_time") or datetime.now(UTC)
    return measurements


def history_to_model_features(history_document: dict | None) -> dict:
    if not history_document:
        return {field: math.nan for field in HX_FIELDS}

    history_features = {}
    for field in HX_FIELDS:
        value = history_document.get(field)
        if value is None:
            history_features[field] = math.nan
        else:
            history_features[field] = int(bool(value))
    return history_features


def build_pre_pca_payload(patient_document: dict, visit_document: dict, history_document: dict | None) -> dict:
    payload = {
        "arrival_mode": visit_document["arrival_mode"],
        "age": patient_document["age"],
        "age_group": patient_document["age_group"],
        "sex": patient_document["sex"],
        "pain_location": visit_document["pain_location"],
        "mental_status_triage": visit_document["mental_status_triage"],
        "chief_complaint_system": visit_document.get("chief_complaint_system"),
        "num_prior_ed_visits_12m": patient_document["num_prior_ed_visits_12m"],
        "num_prior_admissions_12m": patient_document["num_prior_admissions_12m"],
        "num_active_medications": patient_document["num_active_medications"],
        "num_comorbidities": patient_document["num_comorbidities"],
        "systolic_bp": visit_document["systolic_bp"],
        "diastolic_bp": visit_document["diastolic_bp"],
        "mean_arterial_pressure": visit_document["mean_arterial_pressure"],
        "pulse_pressure": visit_document["pulse_pressure"],
        "heart_rate": visit_document["heart_rate"],
        "respiratory_rate": visit_document["respiratory_rate"],
        "temperature_c": visit_document["temperature_c"],
        "spo2": visit_document["spo2"],
        "gcs_total": visit_document["gcs_total"],
        "pain_score": visit_document["pain_score"],
        "weight_kg": patient_document["weight_kg"],
        "height_cm": patient_document["height_cm"],
        "bmi": patient_document["bmi"],
        "shock_index": visit_document["shock_index"],
        "news2_score": visit_document["news2_score"],
        "chief_complaint_raw": visit_document["chief_complaint_raw"],
    }
    payload.update(history_to_model_features(history_document))

    # Keep one explicit shape for the hand-off into ML before PCA columns are appended.
    return {field: payload.get(field, math.nan) for field in PRE_PCA_FIELDS}
