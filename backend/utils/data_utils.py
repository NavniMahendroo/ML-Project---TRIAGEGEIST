from datetime import date, datetime


def normalize_enum(value: str | None, allowed: list[str], fallback: str | None = None) -> str | None:
    if value is None:
        return fallback

    normalized = value.strip()
    if not normalized:
        return fallback

    lookup = {option.casefold(): option for option in allowed}
    if normalized.casefold() in lookup:
        return lookup[normalized.casefold()]

    if fallback is not None:
        return fallback

    raise ValueError(f"Unsupported value '{value}'. Allowed values: {allowed}")


def normalize_gender(value: str) -> str:
    aliases = {
        "male": "M",
        "m": "M",
        "female": "F",
        "f": "F",
    }
    normalized = value.strip().casefold()
    if normalized not in aliases:
        raise ValueError("Unsupported sex value. Expected M/F or Male/Female.")
    return aliases[normalized]


def serialize_mongo(value):
    if isinstance(value, list):
        return [serialize_mongo(item) for item in value]
    if isinstance(value, dict):
        serialized = {}
        for key, item in value.items():
            if key == "_id":
                continue
            serialized[key] = serialize_mongo(item)
        return serialized
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
