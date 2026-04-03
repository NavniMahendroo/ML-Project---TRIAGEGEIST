from triage.schema import PatientInput

URGENCY_LABELS = {
    1: "Resuscitation",
    2: "Emergent",
    3: "Urgent",
    4: "Less Urgent",
    5: "Non-Urgent",
}

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


def rule_based_predict(p: PatientInput) -> dict:
    """
    Clinical-rules triage estimator.
    Takes the worst (lowest number = most urgent) across multiple criteria.
    """
    scores = []

    # 1. NEWS2 Score mapping
    if p.news2_score >= 7:
        scores.append(1)
    elif p.news2_score >= 5:
        scores.append(2)
    elif p.news2_score >= 3:
        scores.append(3)
    elif p.news2_score >= 1:
        scores.append(4)
    else:
        scores.append(5)

    # 2. GCS mapping
    if p.gcs_total <= 8:
        scores.append(1)
    elif p.gcs_total <= 12:
        scores.append(2)
    elif p.gcs_total <= 14:
        scores.append(3)
    else:
        scores.append(5)

    # 3. SpO2 mapping
    if p.spo2 < 85:
        scores.append(1)
    elif p.spo2 < 90:
        scores.append(2)
    elif p.spo2 < 94:
        scores.append(3)
    else:
        scores.append(5)

    # 4. Heart rate mapping
    if p.heart_rate < 40 or p.heart_rate > 150:
        scores.append(1)
    elif p.heart_rate < 50 or p.heart_rate > 130:
        scores.append(2)
    elif p.heart_rate < 60 or p.heart_rate > 110:
        scores.append(3)
    else:
        scores.append(5)

    # 5. Systolic BP mapping
    if p.systolic_bp < 70 or p.systolic_bp > 250:
        scores.append(1)
    elif p.systolic_bp < 80 or p.systolic_bp > 220:
        scores.append(2)
    elif p.systolic_bp < 90 or p.systolic_bp > 180:
        scores.append(3)
    else:
        scores.append(5)

    # 6. Respiratory rate mapping
    if p.respiratory_rate < 8 or p.respiratory_rate > 35:
        scores.append(1)
    elif p.respiratory_rate < 10 or p.respiratory_rate > 30:
        scores.append(2)
    elif p.respiratory_rate < 12 or p.respiratory_rate > 24:
        scores.append(3)
    else:
        scores.append(5)

    # 7. Temperature mapping
    if p.temperature_c < 33.0 or p.temperature_c > 41.0:
        scores.append(1)
    elif p.temperature_c < 34.0 or p.temperature_c > 40.0:
        scores.append(2)
    elif p.temperature_c < 35.0 or p.temperature_c > 39.0:
        scores.append(3)
    else:
        scores.append(5)

    # 8. Pain score
    if p.pain_score >= 9:
        scores.append(2)
    elif p.pain_score >= 7:
        scores.append(3)
    elif p.pain_score >= 4:
        scores.append(4)
    else:
        scores.append(5)

    # 9. Chief complaint keywords
    scores.append(_keyword_urgency(p.chief_complaint_raw))

    # 10. Arrival mode
    arrival = p.arrival_mode.lower()
    if arrival == "helicopter":
        scores.append(1)
    elif arrival == "ambulance":
        scores.append(2)

    # 11. Age extremes
    if p.age < 1 or p.age > 85:
        scores.append(3)  # slightly more urgent for extremes

    # Final: take the most urgent (lowest number)
    acuity = min(scores) if scores else 3
    return {
        "triage_acuity": acuity,
        "urgency_label": URGENCY_LABELS.get(acuity, "Unknown"),
    }
