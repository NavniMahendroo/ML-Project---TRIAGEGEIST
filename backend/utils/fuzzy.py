from rapidfuzz import fuzz, process

from database import get_collection

_SCORE_CUTOFF = 85


def fuzzy_match_patients(name: str, age: int | None = None) -> list[dict]:
    patients = list(
        get_collection("patients").find(
            {},
            {"patient_id": 1, "name": 1, "age": 1, "_id": 0},
        )
    )

    if not patients:
        return []

    name_map = {p["name"]: p for p in patients}
    raw_results = process.extract(
        name,
        name_map.keys(),
        scorer=fuzz.WRatio,
        limit=5,
        score_cutoff=_SCORE_CUTOFF,
    )

    candidates = []
    for matched_name, score, _ in raw_results:
        patient = name_map[matched_name]
        age_score = _age_score(age, patient["age"]) if age is not None else 0
        candidates.append({
            "patient_id": patient["patient_id"],
            "name": patient["name"],
            "age": patient["age"],
            "name_score": round(score, 1),
            "age_match": age is not None and abs(age - patient["age"]) <= 2,
            "combined_score": round(score + age_score, 1),
        })

    candidates.sort(key=lambda c: c["combined_score"], reverse=True)
    return candidates


def _age_score(query_age: int, record_age: int) -> float:
    diff = abs(query_age - record_age)
    if diff == 0:
        return 10.0
    if diff <= 2:
        return 5.0
    if diff <= 5:
        return 0.0
    return -5.0
