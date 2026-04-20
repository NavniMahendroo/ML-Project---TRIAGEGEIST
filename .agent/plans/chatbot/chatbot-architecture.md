# Chatbot — Architecture & Tech Stack

---

## Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| Voice I/O + transcription | Vapi | Handles mic, TTS, live transcript stream |
| Conversation state machine | LangGraph | Controls which phase the bot is in, what to ask next |
| Field extraction + normalization | Ollama + Llama 3.2 8B | Extracts structured fields from free text, normalizes chief complaint |
| Cloud LLM fallback | Groq API (Llama 3.2) | Swap in if demo machine is low on VRAM |
| Chief complaint classification | BioBERT + v1.0.2-b | Maps normalized complaint to 14-class chief_complaint_system |
| Triage prediction | v1.0.2 | Predicts acuity (1–5) using full patient history |
| Triage fallback | v1.0.2-c | Used when patient history is unavailable |

---

## Data Flow

```
Vapi (voice input)
  ↓ live transcript
LangGraph state machine
  ↓ current utterance
Ollama + Llama 3.2 8B
  ↓ extracted fields + chief_complaint_normalized (terse clinical English)
BioBERT + v1.0.2-b
  ↓ chief_complaint_system
v1.0.2 (or v1.0.2-c)
  ↓ acuity (1–5)
POST /triage/predict
  ↓
MongoDB + Result Screen
```

---

## Fuzzy Name Matching (Patient Verification)

Standard string comparison fails on voice input — Vapi may transcribe "Ramesh" as "Ramish" or drop a letter. Fuzzy search handles this.

**How it works:**
- We use a distance algorithm (Levenshtein distance or RapidFuzz library) to score how similar two strings are
- e.g. "Ramish" vs "Ramesh" → distance of 1 character → high similarity score (~90%)
- A threshold is set (e.g. ≥ 85% similarity) — anything above is considered a candidate match
- All candidate matches are returned ranked by score, not just the top one

**Implementation:**
- Library: `rapidfuzz` (Python, fast, MIT license)
- Query: fuzzy match patient name against all names in DB
- Return: list of `(patient_id, name, age, score)` sorted by score descending
- If one result clearly dominates → show it to user for confirmation
- If multiple results are close → show all, user selects

---

## LangGraph State Machine

Each conversation phase is a node. LangGraph tracks state across turns.

```
State: {
  phase, language, user_role,
  patient_id, collected_fields, missing_fields,
  conversation_raw, conversation_keywords
}

Nodes:
  phase_0_role        → detect patient or attendant
  phase_1_identity    → verify patient, load record
  phase_2_complaint   → collect triage fields (loops until all collected)
  phase_3_vitals      → collect or skip
  phase_4_confirm     → show summary, wait for confirmation
  phase_5_submit      → POST to backend
```

Edges:
- Field missing → loop back to same node, bot re-asks
- Value out of range → loop back, bot asks to repeat
- All fields collected → advance to next node
- Patient volunteers multiple fields → mark all collected, skip ahead

---

## DB Schema

### New fields on `visits` document (4 additions only)
```json
{
  "data_source": "voice_bot",
  "chatbot_session_id": "CS-0001",
  "chief_complaint_normalized": "chest pain, onset morning",
  "fields_missing": ["heart_rate", "spo2"]
}
```
Everything else on the visit document is unchanged.

### New `chatbot_sessions` collection (one doc per voice session)
```json
{
  "session_id": "CS-0001",
  "vapi_session_id": "vapi_xyz123",
  "patient_id": "PT-0042",
  "user_role": "patient | attendant",
  "status": "active | completed | incomplete",

  "conversation_raw": [
    { "role": "bot",     "text": "...", "ts": "2026-04-20T10:00:00Z" },
    { "role": "patient", "text": "...", "ts": "2026-04-20T10:00:05Z" }
  ],

  "collected_fields": {
    "chief_complaint_raw":        "chest pain since morning",
    "chief_complaint_normalized": "chest pain, onset morning",
    "chief_complaint_system":     "chest_pain",
    "pain_score": 8,
    "pain_location": "chest",
    "mental_status_triage": "alert"
  },

  "fields_missing": ["heart_rate", "spo2"],
  "collection_confidence": 0.94,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## Frontend — Chat UI

- WhatsApp-style bubbles: bot messages on left, patient on right
- Live transcript streams in as Vapi transcribes — not after the call ends
- Confirmation summary card appears below the last message in the same view
- Result screen (acuity badge + queue number) shown after submission — mockup-4 design
