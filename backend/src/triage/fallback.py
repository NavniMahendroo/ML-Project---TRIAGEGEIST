from constants.labels import URGENCY_LABELS

# High-acuity clinical keywords (case-insensitive)
_CRITICAL_KEYWORDS = [
    "cardiac arrest", "unresponsive", "not breathing", "cpr",
    "anaphylaxis", "severe hemorrhage", "massive bleeding",
]
_EMERGENT_KEYWORDS = [
    "chest pain", "stroke", "seizure", "overdose", "difficulty breathing",
    "shortness of breath", "severe pain", "crushing", "stabbing",
    "head injury", "unconscious", "altered mental status",
    "suicidal", "self-harm", "poisoning",
]
_URGENT_KEYWORDS = [
    "abdominal pain", "fracture", "laceration", "vomiting blood",
    "high fever", "asthma attack", "diabetic", "infection",
    "dehydration", "dizziness", "fainting",
]


def _keyword_urgency(text: str) -> int:
    """Return 1-5 based on keyword matching. 5 means no keyword match."""
    lower = text.lower()
    for kw in _CRITICAL_KEYWORDS:
        if kw in lower:
            return 1
    for kw in _EMERGENT_KEYWORDS:
        if kw in lower:
            return 2
    for kw in _URGENT_KEYWORDS:
        if kw in lower:
            return 3
    return 5  # no concerning keywords


def rule_based_predict(payload: dict) -> dict:
    """
    Clinical-rules triage estimator.
    Takes the worst (lowest number = most urgent) across multiple criteria.
    """
    scores = []

    # 1. NEWS2 Score mapping
    news2_score = payload.get("news2_score", 0)
    gcs_total = payload.get("gcs_total", 15)
    spo2 = payload.get("spo2", 100)
    heart_rate = payload.get("heart_rate", 90)
    systolic_bp = payload.get("systolic_bp", 120)
    respiratory_rate = payload.get("respiratory_rate", 16)
    temperature_c = payload.get("temperature_c", 37)
    pain_score = payload.get("pain_score", 0)
    chief_complaint_raw = payload.get("chief_complaint_raw", "")
    arrival_mode = str(payload.get("arrival_mode", "")).lower()
    age = payload.get("age", 40)

    if news2_score >= 7:
        scores.append(1)
    elif news2_score >= 5:
        scores.append(2)
    elif news2_score >= 3:
        scores.append(3)
    elif news2_score >= 1:
        scores.append(4)
    else:
        scores.append(5)

    # 2. GCS mapping
    if gcs_total <= 8:
        scores.append(1)
    elif gcs_total <= 12:
        scores.append(2)
    elif gcs_total <= 14:
        scores.append(3)
    else:
        scores.append(5)

    # 3. SpO2 mapping
    if spo2 < 85:
        scores.append(1)
    elif spo2 < 90:
        scores.append(2)
    elif spo2 < 94:
        scores.append(3)
    else:
        scores.append(5)

    # 4. Heart rate mapping
    if heart_rate < 40 or heart_rate > 150:
        scores.append(1)
    elif heart_rate < 50 or heart_rate > 130:
        scores.append(2)
    elif heart_rate < 60 or heart_rate > 110:
        scores.append(3)
    else:
        scores.append(5)

    # 5. Systolic BP mapping
    if systolic_bp < 70 or systolic_bp > 250:
        scores.append(1)
    elif systolic_bp < 80 or systolic_bp > 220:
        scores.append(2)
    elif systolic_bp < 90 or systolic_bp > 180:
        scores.append(3)
    else:
        scores.append(5)

    # 6. Respiratory rate mapping
    if respiratory_rate < 8 or respiratory_rate > 35:
        scores.append(1)
    elif respiratory_rate < 10 or respiratory_rate > 30:
        scores.append(2)
    elif respiratory_rate < 12 or respiratory_rate > 24:
        scores.append(3)
    else:
        scores.append(5)

    # 7. Temperature mapping
    if temperature_c < 33.0 or temperature_c > 41.0:
        scores.append(1)
    elif temperature_c < 34.0 or temperature_c > 40.0:
        scores.append(2)
    elif temperature_c < 35.0 or temperature_c > 39.0:
        scores.append(3)
    else:
        scores.append(5)

    # 8. Pain score
    if pain_score >= 9:
        scores.append(2)
    elif pain_score >= 7:
        scores.append(3)
    elif pain_score >= 4:
        scores.append(4)
    else:
        scores.append(5)

    # 9. Chief complaint keywords
    scores.append(_keyword_urgency(chief_complaint_raw))

    # 10. Arrival mode
    if arrival_mode == "helicopter":
        scores.append(1)
    elif arrival_mode == "ambulance":
        scores.append(2)

    # 11. Age extremes
    if age < 1 or age > 85:
        scores.append(3)  # slightly more urgent for extremes

    # Final: take the most urgent (lowest number)
    acuity = min(scores) if scores else 3
    return {
        "triage_acuity": acuity,
        "urgency_label": URGENCY_LABELS.get(acuity, "Unknown"),
    }
