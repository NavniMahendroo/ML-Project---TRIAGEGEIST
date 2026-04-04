import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import ensure_indexes, get_collection, initialize_database  # noqa: E402
from src.nurses.schema import NurseDocument  # noqa: E402
from src.sites.schema import SiteDocument  # noqa: E402


def _seed_documents(collection_name: str, key_field: str, documents: list[dict]) -> int:
    collection = get_collection(collection_name)
    inserted = 0
    for document in documents:
        result = collection.update_one(
            {key_field: document[key_field]},
            {"$setOnInsert": document},
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1
    return inserted


def main():
    initialize_database()
    ensure_indexes()

    sites = [
        SiteDocument(site_id="SITE-0001", name="Central Emergency Department").model_dump(),
        SiteDocument(site_id="SITE-0002", name="Northside Triage Center").model_dump(),
        SiteDocument(site_id="SITE-0003", name="Riverfront Emergency Unit").model_dump(),
        SiteDocument(site_id="SITE-0004", name="West City Acute Care").model_dump(),
        SiteDocument(site_id="SITE-0005", name="South Gate Emergency Hub").model_dump(),
    ]
    nurses = [
        NurseDocument(nurse_id=f"NURSE-{index:04d}", name=f"Nurse {index:02d}").model_dump()
        for index in range(1, 11)
    ]

    site_count = _seed_documents("sites", "site_id", sites)
    nurse_count = _seed_documents("nurses", "nurse_id", nurses)

    print(f"Seed complete. Inserted {site_count} site(s) and {nurse_count} nurse(s).")


if __name__ == "__main__":
    main()
