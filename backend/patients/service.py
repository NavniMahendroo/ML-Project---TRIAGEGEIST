import uuid
import logging
from datetime import datetime
from pymongo import ReturnDocument

from database import _patients_collection, _counters_collection

log = logging.getLogger(__name__)

def get_next_serial_number() -> str:
    """Generate a serial number using TG-YYYY-Index format.
    Falls back to a resilient offline UUID if the database connection fails."""
    try:
        year = datetime.utcnow().year
        counter_id = f"TG-{year}"

        if _counters_collection is None:
            raise Exception("Database collection is None")

        counter_doc = _counters_collection.find_one_and_update(
            {"_id": counter_id},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        index = counter_doc["seq"]
        return f"TG-{year}-{index}"
    except Exception as exc:
        log.warning(f"Failed to generate sequential ID: {exc}. Using UUID fallback.")
        # Fallback resilient unique ID
        offline_uuid = str(uuid.uuid4()).upper()[:8]
        return f"TG-OFFLINE-{offline_uuid}"

def insert_patient_record(payload: dict, serial_number: str, prediction_data: dict) -> None:
    """Store patient intake data with metadata in MongoDB."""
    try:
        document = {
            **payload,
            "serial_number": serial_number,
            "created_at": datetime.utcnow(),
            # Step 2.3: Add prediction details
            "triage_acuity": prediction_data.get("triage_acuity"),
            "urgency_label": prediction_data.get("urgency_label"),
            "engine_used": prediction_data.get("engine"),
        }
        if _patients_collection is not None:
            _patients_collection.insert_one(document)
        else:
            log.warning("Patients collection is None, skipping document insertion.")
    except Exception as exc:
        log.warning(f"Database write failed (non-fatal): {exc}")
