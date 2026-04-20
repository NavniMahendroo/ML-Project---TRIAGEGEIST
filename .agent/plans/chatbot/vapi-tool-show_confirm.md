# Vapi Tool — show_confirm

Called by Riley at the end of the conversation to trigger the confirmation screen on the frontend.

---

## Tool Settings

| Field       | Value                                                   |
|-------------|---------------------------------------------------------|
| Tool Name   | `show_confirm`                                          |
| Description | `Show confirmation screen with collected triage data`   |
| Async       | OFF                                                     |
| Strict      | OFF                                                     |

---

## Parameters JSON

Paste this in the JSON tab of the Parameters section:

```json
{
  "type": "object",
  "properties": {
    "collected_fields": {
      "type": "object",
      "description": "All collected triage field values",
      "properties": {
        "patient_name": { "type": "string" },
        "patient_age": { "type": "number" },
        "mental_status_triage": { "type": "string" },
        "chief_complaint_raw": { "type": "string" },
        "pain_location": { "type": "string" },
        "pain_score": { "type": "number" },
        "arrival_mode": { "type": "string" },
        "heart_rate": { "type": "number" },
        "respiratory_rate": { "type": "number" },
        "temperature_c": { "type": "number" },
        "spo2": { "type": "number" },
        "gcs_total": { "type": "number" },
        "systolic_bp": { "type": "number" },
        "diastolic_bp": { "type": "number" }
      }
    },
    "fields_missing": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Fields that could not be collected"
    },
    "patient_id": {
      "type": "string",
      "description": "Verified patient ID — pass null if unknown"
    },
    "user_role": {
      "type": "string",
      "description": "patient or attendant"
    }
  },
  "required": ["collected_fields"]
}
```

---

## When Riley Should Call This

- Only once, at STEP 10 — after all vitals batches are complete.
- Always pass ALL fields collected so far in `collected_fields`.
- Always pass `patient_id: null` (backend does fuzzy lookup by name).
- List any unknowns in `fields_missing`.

Example call:
```json
{
  "collected_fields": {
    "patient_name": "Saumy",
    "patient_age": 27,
    "mental_status_triage": "alert",
    "chief_complaint_raw": "severe headache",
    "pain_location": "head",
    "pain_score": 7,
    "arrival_mode": "walk-in",
    "heart_rate": 74,
    "respiratory_rate": 18,
    "temperature_c": 37.2,
    "spo2": 98,
    "gcs_total": 15,
    "systolic_bp": 120,
    "diastolic_bp": 80
  },
  "patient_id": null,
  "user_role": "patient",
  "fields_missing": []
}
```

---

## Change Log

| Date       | Change                                           |
|------------|--------------------------------------------------|
| 2026-04-20 | Initial schema with explicit field names + types |
