# VI. Conversational Triage Chatbot

The voice chatbot provides an alternative intake pathway that lowers literacy and language barriers at the point of registration. Patients or their attendants can describe symptoms in natural speech; the system extracts structured clinical fields automatically and feeds them into the same triage prediction pipeline used by the structured form—no manual data entry required.

## A. Architecture Overview

The chatbot pipeline spans four distinct layers: cloud voice I/O (Vapi), a React frontend state machine, a FastAPI session and submit backend, and the shared ML inference engine.

```
Patient speaks
      │
      ▼
Vapi Voice Platform (cloud)
  ├── Real-time Speech-to-Text (ASR)
  ├── LLM Assistant (configured on Vapi)
  │     ├── Extracts clinical fields from dialogue
  │     ├── Tool call: update_fields({fields, fields_missing})
  │     └── Tool call: show_confirm({collected_fields, patient_id})
  └── Text-to-Speech → streams audio back to patient
      │
      ▼
Frontend (React + Vapi Web SDK)
  ├── Live transcript streamed to WhatsApp-style chat UI
  ├── update_fields tool call → updates collectedFields state
  ├── show_confirm tool call → renders Review & Confirm panel (Step 2 of 2)
  ├── stepRef pattern: locks state on CONFIRM — no further LLM overwrites
  ├── call-end / timeout → preserves collected fields, transitions to CONFIRM
  └── Patient edits form fields manually, clicks Confirm & Submit
      │
      ▼
POST /chatbot/session/start
  └── Creates chatbot_sessions document (CS-XXXX) in MongoDB
      │
POST /chatbot/submit
  ├── Cleans LLM output (null/none/unknown → None)
  ├── Normalizes patient ID format (TG-2 / TG-002 → TG-0002)
  ├── Resolves patient:
  │     1. Direct ID lookup in MongoDB
  │     2. If not found → fuzzy name + age match (RapidFuzz Levenshtein)
  │     3. If still not found → HTTP 400
  ├── Builds VisitInput (Pydantic validated, missing vitals → None)
  └── Calls submit_triage() — same function as triage form
      │
      ▼
submit_triage() — unified inference pipeline
  ├── prepare_visit_measurements()
  │     Computes: MAP, pulse_pressure, shock_index, NEWS2 score
  ├── get_patient_history() — fetches hx_* from MongoDB
  ├── build_pre_pca_payload() — assembles all PRE_PCA_FIELDS dict
  │
  ├── _predict_triage() — three-model routing
  │     ├── chief_complaint_system missing? → v1.0.2-b infers from text
  │     ├── history available? → v1.0.2 (full) : v1.0.2-c (fallback)
  │     └── returns { triage_acuity, urgency_label, engine }
  │
  ├── _resolve_doctor_assignment()
  │     Specialty routing + round-robin doctor assignment
  ├── _create_visit_document()
  │     Writes visit to MongoDB with data_source: "voice_bot"
  └── finalize_session()
        Updates chatbot_sessions with visit_id, transcript, fields
      │
      ▼
Frontend ResultScreen
  ├── Acuity badge (colour-coded by ESI level 1–5)
  ├── Chief complaint system (inferred or provided)
  ├── Routed specialty + assigned doctor ID
  └── Queue number (derived from visit_id)
```

## B. Vapi Integration
Vapi manages the full voice I/O layer: microphone capture, cloud ASR, LLM inference, and text-to-speech playback. The LLM assistant is configured on Vapi's platform with a clinical intake system prompt and two tool definitions:

- **update_fields** — called incrementally as the patient provides information; carries a partial fields object and a fields_missing list of outstanding required fields
- **show_confirm** — called when the assistant has collected sufficient information; carries the complete collected_fields dict and triggers the Review & Confirm panel on the frontend

The frontend uses the Vapi Web SDK to receive these tool calls as JavaScript events. No local GPU or LLM inference is required on the server side for the conversation layer.

## C. Frontend State Machine and the stepRef Pattern
The chatbot UI is controlled by a step state machine with seven states: IDLE → CONNECTING → ACTIVE → CONFIRM → SUBMITTING → DONE / ERROR.

A critical design challenge arises from Vapi's asynchronous event model: JavaScript event handlers capture state values at the time of registration (stale closure problem). If the patient reaches the CONFIRM step and continues editing the form, a delayed update_fields tool call from the LLM could overwrite the patient's manual changes.

This is solved with a stepRef pattern: a useRef mirror of the step state is maintained synchronously alongside the React state. All Vapi event handlers read from stepRef.current rather than the captured state value. A LOCKED_STEPS set {CONFIRM, SUBMITTING, DONE} causes the message handler to immediately return without processing any tool calls, guaranteeing that the patient's form edits are never overwritten.

Similarly, a collectedFieldsRef mirrors collectedFields synchronously, so the call-end event handler can correctly decide whether to transition to CONFIRM or IDLE regardless of React's async state batching.

## D. Patient Resolution and Robustness
The submit endpoint applies three layers of patient resolution:

1. **Direct ID lookup** — if the patient or LLM provided a patient_id, it is normalized first (TG-002 → TG-0002, four-digit zero-padding) then looked up in MongoDB
2. **Fuzzy name + age match** — if the ID lookup fails or no ID was provided, RapidFuzz Levenshtein similarity is run against all patient names, weighted by age proximity
3. **Failure** — if neither resolves a patient, HTTP 400 is returned with a descriptive message; the frontend keeps the form open for retry

## E. Session Persistence
Every chatbot session creates a document in the chatbot_sessions MongoDB collection storing: session_id (CS-XXXX), vapi_session_id, full conversation transcript, all collected fields, fields_missing list, collection_confidence score, linked visit_id, patient_id, and user_role (patient or attendant). The corresponding visit document stores data_source: "voice_bot", chatbot_session_id, chief_complaint_normalized, and fields_missing for full audit traceability.

## F. Missing Vitals Handling
Vitals not collected during the voice conversation (spo2, systolic_bp, etc.) are submitted as None. The backend converts these to NaN in the pre_pca_payload. CatBoost handles NaN natively without imputation, so the model still produces a valid prediction. The fields_missing list is stored in the visit document and displayed as a warning in the frontend confirmation panel, prompting bedside measurement.
