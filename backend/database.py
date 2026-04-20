import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "triagegeist")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

log = logging.getLogger(__name__)

_client = None
_db = None
_collections = {}


def initialize_database():
    global _client, _db, _collections

    if _db is not None:
        return _db

    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")
    _db = _client[MONGO_DB_NAME]
    _collections = {
        "patients": _db["patients"],
        "visits": _db["visits"],
        "patient_history": _db["patient_history"],
        "sites": _db["sites"],
        "nurses": _db["nurses"],
        "doctors": _db["doctors"],
        "_system_counters": _db["_system_counters"],
        "chatbot_sessions": _db["chatbot_sessions"],
    }
    log.info("Connected to MongoDB at %s/%s", MONGO_URI, MONGO_DB_NAME)
    return _db


def get_db():
    return initialize_database()


def get_collection(name: str):
    initialize_database()
    try:
        return _collections[name]
    except KeyError as exc:
        raise KeyError(f"Unknown collection requested: {name}") from exc


def ping_database():
    initialize_database()
    _client.admin.command("ping")
    return True


def ensure_indexes():
    initialize_database()

    get_collection("patients").create_index("patient_id", unique=True)
    get_collection("visits").create_index("visit_id", unique=True)
    get_collection("visits").create_index("patient_id")
    get_collection("visits").create_index("assigned_doctor_id")
    get_collection("visits").create_index([("assigned_doctor_id", 1), ("attended_by_doctor", 1)])
    get_collection("patient_history").create_index("patient_id", unique=True)
    get_collection("sites").create_index("site_id", unique=True)
    get_collection("nurses").create_index("nurse_id", unique=True)
    get_collection("doctors").create_index("doctor_id", unique=True)
    get_collection("doctors").create_index("specialty")
    get_collection("doctors").create_index("on_duty")
    # MongoDB already guarantees uniqueness for _id automatically.
    get_collection("_system_counters").create_index("_id")
    get_collection("chatbot_sessions").create_index("session_id", unique=True)
    get_collection("chatbot_sessions").create_index("patient_id")
