SEX_OPTIONS = ["M", "F"]
LANGUAGE_OPTIONS = ["Arabic", "English", "Estonian", "Finnish", "Other", "Russian", "Somali", "Swedish"]
INSURANCE_OPTIONS = ["military", "none", "private", "public", "unknown"]
ARRIVAL_MODE_OPTIONS = ["ambulance", "brought_by_family", "helicopter", "police", "transfer", "walk-in"]
TRANSPORT_ORIGIN_OPTIONS = ["home", "nursing_home", "other_hospital", "outdoor", "public_space", "school", "workplace"]
PAIN_LOCATION_OPTIONS = ["abdomen", "back", "chest", "extremity", "head", "multiple", "none", "pelvis", "unknown"]
MENTAL_STATUS_OPTIONS = ["agitated", "alert", "confused", "drowsy", "unresponsive"]

FORM_OPTION_LABELS = {
    "sex": [
        {"value": "M", "label": "Male"},
        {"value": "F", "label": "Female"},
    ],
    "language": [{"value": value, "label": value} for value in LANGUAGE_OPTIONS],
    "insurance_type": [{"value": value, "label": value.replace("_", " ").title()} for value in INSURANCE_OPTIONS],
    "arrival_mode": [{"value": value, "label": value.replace("_", " ").title()} for value in ARRIVAL_MODE_OPTIONS],
    "transport_origin": [{"value": value, "label": value.replace("_", " ").title()} for value in TRANSPORT_ORIGIN_OPTIONS],
    "pain_location": [{"value": value, "label": value.replace("_", " ").title()} for value in PAIN_LOCATION_OPTIONS],
    "mental_status_triage": [{"value": value, "label": value.replace("_", " ").title()} for value in MENTAL_STATUS_OPTIONS],
}
