import logging
import sys
from pathlib import Path

from triage.schema import PatientInput
from triage.fallback import rule_based_predict

log = logging.getLogger(__name__)

# Add ml/src to sys.path so we can import predict_api
_backend_dir = Path(__file__).resolve().parent.parent
_ml_src_dir = _backend_dir.parent / "ml" / "src"
if str(_ml_src_dir) not in sys.path:
    sys.path.insert(0, str(_ml_src_dir))

_ml_available = False
_ml_model_loaded = False
predict_api = None

try:
    import predict_api  # noqa: E402
    _ml_available = True
except Exception as exc:
    log.warning(f"ML pipeline import failed ({exc}). Will use rule-based fallback.")


def load_ml_model():
    """Attempt to load the ML model into memory."""
    global _ml_model_loaded
    if _ml_available:
        try:
            predict_api.load_model()
            _ml_model_loaded = predict_api._model is not None
            if _ml_model_loaded:
                log.info("ML model loaded successfully.")
            else:
                log.warning("ML model load returned None. Using rule-based fallback.")
        except Exception as exc:
            log.warning(f"ML model load failed: {exc}. Using rule-based fallback.")
    else:
        log.info("ML pipeline not available. Using rule-based clinical fallback.")


def get_prediction(patient: PatientInput) -> dict:
    """
    Run prediction - ML pipeline if loaded, otherwise rule-based fallback.
    Returns: {"triage_acuity": int, "urgency_label": str, "engine": str}
    """
    if _ml_model_loaded:
        try:
            payload = patient.model_dump()
            ml_result = predict_api.predict_patient(payload)
            return {
                "triage_acuity": ml_result["triage_acuity"],
                "urgency_label": ml_result["urgency_label"],
                "engine": "ml_pipeline",
            }
        except Exception as exc:
            log.error(f"ML prediction failed, falling back to rules: {exc}")
            ml_result = rule_based_predict(patient)
            return {
                "triage_acuity": ml_result["triage_acuity"],
                "urgency_label": ml_result["urgency_label"],
                "engine": "rule_based_fallback",
            }
    else:
        ml_result = rule_based_predict(patient)
        return {
            "triage_acuity": ml_result["triage_acuity"],
            "urgency_label": ml_result["urgency_label"],
            "engine": "rule_based_fallback",
        }

def get_engine_status() -> dict:
    return {
        "engine": "ml_pipeline" if _ml_model_loaded else "rule_based_fallback",
        "ml_model_loaded": _ml_model_loaded,
    }
