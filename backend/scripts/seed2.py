import sys
from pathlib import Path

from bson import json_util

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import ensure_indexes, get_db, initialize_database  # noqa: E402

PRIMARY_KEYS = {
    "patients": "patient_id",
    "visits": "visit_id",
    "patient_history": "patient_id",
    "sites": "site_id",
    "nurses": "nurse_id",
    "doctors": "doctor_id",
    "_system_counters": "_id",
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


def _prepare_replacement(doc: dict, filter_key: str) -> dict:
    replacement = dict(doc)
    if filter_key != "_id":
        replacement.pop("_id", None)
    return replacement


def _seed_collection(collection_name: str, docs: list[dict]) -> tuple[int, int, int]:
    collection = get_db()[collection_name]

    inserted = 0
    replaced = 0
    skipped = 0

    for doc in docs:
        try:
            query, filter_key = _resolve_filter(collection_name, doc)
        except ValueError:
            skipped += 1
            continue

        replacement = _prepare_replacement(doc, filter_key)
        result = collection.replace_one(query, replacement, upsert=True)

        if result.upserted_id is not None:
            inserted += 1
        else:
            replaced += 1

    return inserted, replaced, skipped


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

    for data_file in data_files:
        collection_name = data_file.stem
        docs = _load_docs(data_file)
        inserted, replaced, skipped = _seed_collection(collection_name, docs)

        total_docs += len(docs)
        total_inserted += inserted
        total_replaced += replaced
        total_skipped += skipped

        print(
            f"{collection_name}: loaded={len(docs)} inserted={inserted} replaced={replaced} skipped={skipped}"
        )

    print(
        "Seed2 complete. "
        f"collections={len(data_files)} docs={total_docs} inserted={total_inserted} "
        f"replaced={total_replaced} skipped={total_skipped}."
    )


if __name__ == "__main__":
    main()
