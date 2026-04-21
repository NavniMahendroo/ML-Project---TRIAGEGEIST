import sys
from pathlib import Path

from bson import json_util
from pydantic import BaseModel, ValidationError

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import ensure_indexes, get_collection, initialize_database  # noqa: E402
from src.doctors.schema import DoctorDocument  # noqa: E402
from src.nurses.schema import NurseDocument  # noqa: E402
from src.patient_history.schema import PatientHistoryDocument  # noqa: E402
from src.patients.schema import PatientDocument  # noqa: E402
from src.sites.schema import SiteDocument  # noqa: E402
from src.superadmin.schema import SuperAdminDocument  # noqa: E402
from src.visits.schema import VisitDocument  # noqa: E402

PRIMARY_KEYS = {
    "patients": "patient_id",
    "visits": "visit_id",
    "patient_history": "patient_id",
    "sites": "site_id",
    "nurses": "nurse_id",
    "doctors": "doctor_id",
    "superadmins": "admin_id",
    "chatbot_sessions": "session_id",
    "users": "username",
    "_system_counters": "_id",
}

DOCUMENT_MODELS: dict[str, type[BaseModel]] = {
    "patients": PatientDocument,
    "visits": VisitDocument,
    "patient_history": PatientHistoryDocument,
    "sites": SiteDocument,
    "nurses": NurseDocument,
    "doctors": DoctorDocument,
    "superadmins": SuperAdminDocument,
}

COUNTER_SOURCES = {
    "patients": ("patients", "patient_id", "TG"),
    "visits": ("visits", "visit_id", "VT"),
}


def _load_docs(file_path: Path) -> list[dict]:
    raw = file_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    parsed = json_util.loads(raw)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    return []


def _resolve_filter(collection_name: str, doc: dict) -> tuple[dict, str]:
    key = PRIMARY_KEYS.get(collection_name)
    if key and key in doc:
        return {key: doc[key]}, key
    if "_id" in doc:
        return {"_id": doc["_id"]}, "_id"
    raise ValueError(f"No primary key mapping found for document in collection '{collection_name}'.")


def _prepare_replacement(collection_name: str, doc: dict, filter_key: str) -> dict:
    replacement = dict(doc)
    if filter_key != "_id":
        replacement.pop("_id", None)

    model = DOCUMENT_MODELS.get(collection_name)
    if model is not None:
        replacement = model.model_validate(replacement).model_dump()

    return replacement


def _seed_collection(collection_name: str, docs: list[dict]) -> tuple[int, int, int, int]:
    collection = get_collection(collection_name)

    inserted = 0
    replaced = 0
    skipped = 0
    invalid = 0

    for doc in docs:
        try:
            query, filter_key = _resolve_filter(collection_name, doc)
            replacement = _prepare_replacement(collection_name, doc, filter_key)
        except ValueError as exc:
            skipped += 1
            print(f"{collection_name}: skipped document: {exc}")
            continue
        except ValidationError as exc:
            invalid += 1
            primary_value = query.get(filter_key, "<unknown>") if "query" in locals() else "<unknown>"
            print(f"{collection_name}: invalid {filter_key}={primary_value}: {exc.errors()}")
            continue

        result = collection.replace_one(query, replacement, upsert=True)

        if result.upserted_id is not None:
            inserted += 1
        else:
            replaced += 1

    return inserted, replaced, skipped, invalid


def _sync_counter(name: str, collection_name: str, key_field: str, prefix: str) -> None:
    max_seq = 0
    collection = get_collection(collection_name)
    for document in collection.find({key_field: {"$regex": f"^{prefix}-"}}, {key_field: 1}):
        key = document.get(key_field, "")
        if not isinstance(key, str):
            continue
        try:
            max_seq = max(max_seq, int(key.removeprefix(f"{prefix}-")))
        except ValueError:
            continue

    if max_seq == 0:
        return

    get_collection("_system_counters").update_one(
        {"_id": name},
        {"$max": {"seq": max_seq}},
        upsert=True,
    )


def main() -> None:
    initialize_database()
    ensure_indexes()

    data_dir = CURRENT_DIR / "seed2_data"
    data_files = sorted(data_dir.glob("*.json"))

    if not data_files:
        raise FileNotFoundError(f"No seed snapshot files found in: {data_dir}")

    total_docs = 0
    total_inserted = 0
    total_replaced = 0
    total_skipped = 0
    total_invalid = 0

    for data_file in data_files:
        collection_name = data_file.stem
        docs = _load_docs(data_file)
        inserted, replaced, skipped, invalid = _seed_collection(collection_name, docs)

        total_docs += len(docs)
        total_inserted += inserted
        total_replaced += replaced
        total_skipped += skipped
        total_invalid += invalid

        print(
            f"{collection_name}: loaded={len(docs)} inserted={inserted} "
            f"replaced={replaced} skipped={skipped} invalid={invalid}"
        )

    for counter_name, args in COUNTER_SOURCES.items():
        _sync_counter(counter_name, *args)

    print(
        "Seed2 complete. "
        f"collections={len(data_files)} docs={total_docs} inserted={total_inserted} "
        f"replaced={total_replaced} skipped={total_skipped} invalid={total_invalid}."
    )


if __name__ == "__main__":
    main()
