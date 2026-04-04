from pymongo import ReturnDocument

from database import get_collection


def get_next_id(name: str, prefix: str, width: int = 4) -> str:
    counters = get_collection("_system_counters")
    counter = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return f"{prefix}-{counter['seq']:0{width}d}"
