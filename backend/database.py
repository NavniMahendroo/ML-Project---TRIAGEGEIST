from datetime import datetime
import os

from pymongo import MongoClient, ReturnDocument


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "triagegeist")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]
_patients_collection = _db["patients"]
_counters_collection = _db["counters"]


def get_next_serial_number() -> str:
    """Generate a serial number using TG-YYYY-Index format."""
    year = datetime.utcnow().year
    counter_id = f"TG-{year}"

    counter_doc = _counters_collection.find_one_and_update(
        {"_id": counter_id},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    index = counter_doc["seq"]
    return f"TG-{year}-{index}"


def insert_patient_record(payload: dict, serial_number: str) -> None:
    """Store patient intake data with serial metadata in MongoDB."""
    document = {
        **payload,
        "serial_number": serial_number,
        "created_at": datetime.utcnow(),
    }
    _patients_collection.insert_one(document)
