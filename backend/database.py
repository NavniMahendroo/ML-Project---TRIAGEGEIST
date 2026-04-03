import os
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "triagegeist")

# API Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

log = logging.getLogger(__name__)

_client = None
_db = None
_patients_collection = None
_counters_collection = None

try:
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # Check if connection holds quickly
    _client.server_info()
    _db = _client[MONGO_DB_NAME]
    _patients_collection = _db["patients"]
    _counters_collection = _db["counters"]
    log.info(f"Connected to MongoDB at {MONGO_URI}/{MONGO_DB_NAME}")
except Exception as e:
    log.warning(f"Could not connect to MongoDB. Running in offline/fallback mode. Error: {e}")
