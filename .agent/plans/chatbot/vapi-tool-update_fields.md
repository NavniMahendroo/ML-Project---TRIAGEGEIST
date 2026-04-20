# Vapi Tool — update_fields

Called by Riley after every patient answer to store collected data.

---

## Tool Settings

| Field       | Value                                              |
|-------------|----------------------------------------------------|
| Tool Name   | `update_fields`                                    |
| Description | `Update collected triage fields during conversation` |
| Async       | OFF                                                |
| Strict      | OFF                                                |

---

## Parameters JSON

Paste this in the JSON tab of the Parameters section:

```json
{
  "type": "object",
  "properties": {
    "fields": {
      "type": "object",
      "description": "Collected triage field values",
      "properties": {
        "patient_id": { "type": "string" },
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
    "user_role": {
      "type": "string",
      "description": "patient or attendant"
    },
    "patient_id": {
      "type": "string",
      "description": "Patient ID if verified"
    },
    "fields_missing": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Fields the patient said they don't know"
    }
  },
  "required": ["fields"]
}
```

---

## When Riley Should Call This

- After EVERY patient answer, immediately — do not batch multiple steps.
- Example calls:

After step 1 (role):
```json
{ "fields": {}, "user_role": "patient" }
```

After step 2 (name + age):
```json
{ "fields": { "patient_name": "Saumy", "patient_age": 27 }, "user_role": "patient" }
```

After step 4 (complaint):
```json
{ "fields": { "chief_complaint_raw": "severe headache since morning" } }
```

After step 7 (vitals batch 1):
```json
{ "fields": { "heart_rate": 74, "respiratory_rate": 18, "temperature_c": 37.2 } }
```

---

## Change Log

| Date       | Change                                           |
|------------|--------------------------------------------------|
| 2026-04-20 | Initial schema with explicit field names + types |
