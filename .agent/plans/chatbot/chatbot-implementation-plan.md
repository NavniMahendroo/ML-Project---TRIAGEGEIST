# Chatbot Phase 1 — Implementation Plan

No code. This document explains what to build, where, and in what order.

---
## Overview of What Gets Built

```
Frontend (React)
  └── ChatbotPage
        └── Vapi SDK (voice I/O + live transcript)
        └── Chat UI (WhatsApp-style bubbles)
        └── Confirmation split-screen
        └── Result screen

Backend (FastAPI)
  └── /chatbot/session       → start a session, return session_id
  └── /chatbot/verify        → fuzzy patient lookup
  └── /chatbot/submit        → final triage submission (reuses existing /triage/predict flow)

NLP Layer (new Python module)
  └── chatbot/llm.py         → Ollama call: field extraction + CC normalization
  └── chatbot/session.py     → LangGraph state machine
  └── chatbot/fuzzy.py       → RapidFuzz patient name matching

Database (MongoDB)
  └── visits collection      → 4 new fields added
  └── chatbot_sessions       → new collection (one doc per voice session)
```

---

## Phase 1 — Backend: New Chatbot Router + Session Collection

### Step 1.1 — New collection: `chatbot_sessions`

One document per voice session. Created when the session starts, updated as the conversation progresses, finalized on submission.

Fields:
```
session_id          string        unique ID (e.g. CS-0001)
vapi_session_id     string        ID from Vapi, for audio/transcript audit
patient_id          string|null   null until verified
user_role           string        "patient" or "attendant"
status              string        "active" | "completed" | "incomplete"

conversation_raw    array         full transcript — each entry:
                                  { role: "bot"|"patient", text, ts }

collected_fields    object        running snapshot of what LangGraph has extracted so far
fields_missing      array         list of field names not yet collected
collection_confidence  float      average Llama confidence across all extracted fields

created_at          datetime
updated_at          datetime
```

This collection is separate from `visits` because the session may be abandoned, contain partial data, or need to be audited independently of the triage result.

---

### Step 1.2 — New fields on `visits` collection (VisitDocument + VisitInput)

Add to the existing visit document:
```
data_source                 string    "form" | "voice_bot"
chatbot_session_id          string    links back to chatbot_sessions
chief_complaint_normalized  string    LLM-cleaned version of chief_complaint_raw
fields_missing              array     which fields weren't collected
```

`language` and `user_role` live on `chatbot_sessions` only — not duplicated on the visit.
`site_id` is hardcoded to `SITE-0001` for Phase 1. `nurse_id` is `"self"` for all chatbot submissions.

---

### Step 1.3 — New router: `backend/src/chatbot/router.py`

Three endpoints:

**POST /chatbot/session/start**
- Creates a new `chatbot_sessions` document
- Returns `session_id`
- Called when the patient opens the chatbot page and Vapi connects

**POST /chatbot/verify**
- Receives: `{ name, age, patient_id (optional) }`
- Runs RapidFuzz against all patient names in DB
- Returns: list of `{ patient_id, name, age, score }` above 85% threshold
- Does not load the patient yet — frontend shows results, user selects

**POST /chatbot/submit**
- Receives the finalized `collected_fields` from the frontend after confirmation
- Constructs a `TriageSubmission` object (same shape as the existing form)
- `site_id` defaults to `"SITE-0001"` (hardcoded for Phase 1 single-site deployment)
- `nurse_id` defaults to `"self"` (patient self-registration via chatbot)
- Calls `submit_triage()` — exactly the same service function the form uses
- Saves `conversation_raw` and chatbot metadata to `chatbot_sessions`
- Updates the created visit document with `chatbot_session_id`, `data_source: "voice_bot"`, etc.

No new triage logic. The chatbot is just a different way to collect the same fields. The ML pipeline is untouched.

---

### Step 1.4 — New service: `backend/src/chatbot/service.py`

Functions:
- `create_session()` → insert new chatbot_sessions document, return session_id
- `fuzzy_match_patients(name, age)` → RapidFuzz query, return ranked candidates
- `finalize_session(session_id, visit_id, collected_fields, conversation_raw)` → update chatbot_sessions on completion

---

### Step 1.5 — New file: `backend/src/chatbot/fuzzy.py`

Library: `rapidfuzz`

Logic:
- Fetch all `{ patient_id, name, age }` from patients collection
- Run `process.extract(query_name, all_names, scorer=fuzz.WRatio, score_cutoff=85)`
- Return top matches with patient_id, name, age, score
- Secondary filter: if age is also provided, bump score for age match, penalize large age gaps

---

## Phase 2 — NLP Layer: Ollama + LangGraph

### Step 2.1 — New module: `backend/src/chatbot/llm.py`

Responsibility: call Ollama (or Groq fallback) with a structured prompt to extract fields from a patient utterance.

**Model:** `llama3.2` via Ollama (local, no API key)
**Fallback:** Groq API with the same model if Ollama is unavailable

What this function does per call:
- Input: current utterance + list of fields still needed
- Output: `{ field_name: value, confidence: float }` for each field found in the utterance
- If confidence < 0.75 for a field → flag it, bot will confirm before accepting
- CC normalization happens here too: takes `chief_complaint_raw`, returns `chief_complaint_normalized` as a terse clinical phrase

Prompt structure (not actual code, just the logic):
```
System: You are a clinical triage assistant. Extract the following fields from the patient's message.
        Return JSON only. Include a confidence score (0.0–1.0) per field.
        Fields needed: [mental_status_triage, pain_score, chief_complaint_raw, ...]

User: "my chest has been hurting since this morning and I came by ambulance"

Response:
{
  "chief_complaint_raw": { "value": "chest pain since morning", "confidence": 0.95 },
  "arrival_mode": { "value": "ambulance", "confidence": 0.99 }
}
```

CC normalization — separate prompt call:
```
System: Rewrite the following as a terse clinical phrase a nurse would write.
        5–7 words max. English only.

User: "my chest has been hurting since this morning"
Response: "chest pain, onset morning"
```

---

### Step 2.2 — New module: `backend/src/chatbot/session.py` (LangGraph)

The state machine. Manages which step the bot is in and what to ask next.

**State object:**
```
{
  session_id, user_role, patient_id,
  current_step,          # which node is active
  collected_fields,      # dict of field → value
  missing_fields,        # list of fields not yet collected
  low_confidence_fields, # fields extracted but confidence < 0.75
  conversation_raw       # full transcript so far
}
```

**Nodes (one per step):**
```
node_role_detection
  → receives first utterance
  → calls llm.py to check if role is explicit
  → sets user_role in state
  → advances to node_verification

node_verification
  → asks for name/age/patient_id
  → calls fuzzy.py
  → holds state until frontend confirms patient selection
  → sets patient_id in state
  → advances to node_complaint

node_complaint
  → loops: asks for each missing field in order
  → each utterance goes to llm.py
  → updates collected_fields, missing_fields
  → if low_confidence field found: stays in node, bot asks to confirm
  → if patient says "I don't know": marks field null, moves on
  → once all required fields collected: advances to node_vitals

node_vitals
  → first asks if vitals were taken
  → if yes: loops through batches (Batch 1 → 2 → 3)
  → if no: asks heart_rate and temperature_c only
  → all optional — "I don't know" or no answer → null, move on
  → advances to node_confirm

node_confirm
  → sends current collected_fields snapshot to frontend
  → frontend shows split screen (form left, chat right)
  → patient can say corrections → each goes back through llm.py → updates state
  → bot asks "Should I submit?" after each correction
  → on confirmation → advances to node_submit

node_submit
  → constructs TriageSubmission from collected_fields
  → calls submit_triage() from existing triage service
  → saves chatbot_session
  → returns visit_id, triage_acuity to frontend
```

---

## Phase 3 — How the Three ML Models Are Used

### v1.0.2-b (BioBERT + CatBoost — Chief Complaint Classifier)
- Used in every chatbot submission
- Input: `chief_complaint_normalized` (after Ollama normalization)
- Output: `chief_complaint_system` (one of 14 classes)
- Called inside existing `predict_api.predict_patient()` — no changes needed
- If normalization fails: use `chief_complaint_raw` directly as fallback

### v1.0.2 (Full Triage Model — with history)
- Used when `patient_id` is found and history exists
- Input: full `pre_pca_payload` built by `build_pre_pca_payload()` — unchanged
- History fields (HX_FIELDS) are loaded from `patient_history` collection as usual
- Missing vitals → passed as `nan` — model already handles this

### v1.0.2-c (Fallback Triage Model — no history)
- Used when patient has no history (returning patient with no prior visits or partial history)
- In Phase 1 this case is rare (returning patients only), but the routing logic is already in the backend
- No changes to the fallback routing logic

### Derived fields — calculated by backend, never asked:
```
mean_arterial_pressure   = (systolic_bp + 2 × diastolic_bp) / 3
pulse_pressure           = systolic_bp − diastolic_bp
shock_index              = heart_rate / systolic_bp
news2_score              = calculated from HR, RR, SpO2, temp, SBP, GCS
```
If `systolic_bp` or `diastolic_bp` is null → MAP, pulse_pressure, shock_index all null.
`news2_score` calculated from whatever vitals are available, null fields skipped.

---

## Phase 4 — Frontend

### Step 4.1 — New page: `ChatbotPage`

Route: `/chatbot`

Two sub-views within the same page:

**Active conversation view:**
- Full screen chat UI
- Bot bubbles left, patient bubbles right
- Live transcript from Vapi streams in word-by-word (not after call ends)
- "Listening..." indicator when mic is active
- Vapi SDK handles mic + TTS — no custom audio code needed

**Confirmation view (split screen):**
- Triggered when LangGraph reaches `node_confirm`
- Form card slides to left showing all collected fields
- Chat stays on right
- Patient speaks corrections → bot updates form fields in real time
- "Submit" button disabled until patient confirms verbally or by button

### Step 4.2 — New hook: `useChatbot`

Manages:
- Vapi connection lifecycle (start/stop call)
- Sending each transcript turn to LangGraph via backend WebSocket or polling
- Receiving bot response text + TTS back from backend
- Updating `collected_fields` state as conversation progresses
- Triggering split screen when confirmation step is reached

### Step 4.3 — Vapi integration

- Install `@vapi-ai/web`
- System prompt defined in code (not Vapi dashboard) — version controlled
- Custom tool defined in Vapi: the JSON schema of `collected_fields`
- Vapi calls our `/chatbot/submit` webhook when the tool is triggered
- Live transcript events → streamed to chat UI

---

## Phase 5 — Data Flow End to End

```
1. Patient opens /chatbot → useChatbot calls POST /chatbot/session/start
   → chatbot_sessions document created with status: "active"

2. Vapi connects → mic opens → conversation begins

3. Each patient utterance:
   → Vapi transcribes in real time → chat UI updates
   → LangGraph node receives utterance
   → llm.py (Ollama) extracts fields, returns { field: value, confidence }
   → low confidence fields flagged → bot asks to confirm
   → high confidence fields added to collected_fields
   → missing_fields updated
   → bot generates next question → Vapi speaks it

4. node_verification:
   → name/age sent to POST /chatbot/verify
   → rapidfuzz returns candidates
   → frontend shows list → patient selects → patient_id locked in state

5. node_complaint + node_vitals:
   → chief_complaint_raw collected
   → llm.py runs CC normalization → chief_complaint_normalized stored
   → vitals collected in batches, null where missing

6. node_confirm:
   → frontend splits: form left, chat right
   → patient corrects values via voice → llm.py re-extracts → form updates

7. Patient confirms → POST /chatbot/submit:
   → collected_fields → TriageSubmission constructed
   → transport_origin: default "unknown" if skipped
   → submit_triage() called (existing service, no changes)
     → build_pre_pca_payload() → predict_patient()
     → v1.0.2-b classifies CC → v1.0.2 predicts acuity
   → visit document created with data_source: "voice_bot", chatbot_session_id
   → chatbot_sessions updated: status: "completed", visit_id linked

8. Frontend shows result screen: acuity badge + queue number
```

---

## New Files Summary

```
backend/src/chatbot/
  __init__.py
  router.py          → 3 endpoints: start, verify, submit
  service.py         → create_session, fuzzy_match_patients, finalize_session
  session.py         → LangGraph state machine (nodes + edges)
  llm.py             → Ollama/Groq field extraction + CC normalization

frontend/src/
  pages/ChatbotPage/
    index.tsx          → page layout, split screen logic
    ChatBubble.tsx     → single message bubble component
    ConfirmForm.tsx    → editable form card for confirmation view
  hooks/
    useChatbot.ts      → Vapi lifecycle + state management
```

## Existing Files Modified

```
backend/src/visits/schema.py       → add: data_source, chatbot_session_id,
                                          chief_complaint_normalized, fields_missing
backend/src/triage/service.py      → minor: accept data_source field, pass through to visit document
backend/server.py                  → register chatbot router
```

## New Dependencies

```
Backend:
  rapidfuzz          → fuzzy name matching
  langgraph          → conversation state machine
  ollama             → local LLM client

Frontend:
  @vapi-ai/web       → voice I/O SDK
```
