# 008 — Frontend, Admin, Schema & NLP Pipeline Discussion

Items to discuss and finalize one by one. Nothing implemented yet.

---

## 1) Lazy Loading + Skeleton Loading (Future)

- Implement once admin page and multiple routes exist
- Lazy loading: each page loads only when navigated to (`React.lazy` + `Suspense`)
- Skeleton loading: show placeholder UI while data fetches (replaces blank screens)
- Not worth doing now — only one page exists

---

## 2) Admin Page

### MVP Scope
A protected page showing activity across all patients, doctors, and nurses.

**Patient Statistics**
- Total visits, acuity distribution (bar chart)
- Daily/weekly volume (line chart)
- Recent patients table (sortable)
- Average triage score over time

**Staff Statistics**
- Triage submissions per nurse/doctor
- Shift activity breakdown

**System Statistics**
- Model prediction confidence over time
- v1.0.2-c (fallback) usage rate — how often history was missing
- BioBERT + v1.0.2-b chief complaint classification distribution

**Charts library:** Recharts (lightweight, React-native)

### Future Scope
- Interactive maps showing patient origin by site/ward
- Real-time live dashboard with websocket updates

---

## 3) Frontend Redesign & User Flow

- Current design has no clear user flow
- Needs proper discussion — to be detailed out separately
- Key areas: form layout, navigation, result display, mobile responsiveness

---

## 4) NLP vs Chatbot — Definitions & Interrelation

### Definitions
- **NLP** — converts raw text into structured data. No conversation. Pure transformation.
  Example: `chief_complaint_raw` → BioBERT → 10 PCA dims → `chief_complaint_system`
- **Chatbot** — conversational interface that collects information through dialogue.
  Example: Vapi voice bot asking "where is your pain?" and extracting the answer.

### How they connect in our system
```
Chatbot (Vapi voice bot)
    ↓  raw conversational speech
Ollama + Llama 3.2 8B  ← LLM normalization layer
    ↓  terse clinical phrase ("chest pain radiating to left arm")
BioBERT + v1.0.2-b     ← NLP classification model
    ↓  chief_complaint_system (14 classes)
v1.0.2 or v1.0.2-c     ← triage acuity prediction
    ↓  acuity level (1–5)
```

### What already exists
- BioBERT + v1.0.2-b — NLP classification model ✅
- v1.0.2 and v1.0.2-c — triage models ✅
- Manual triage form — data entry ✅

### What does not exist yet
- Vapi voice bot integration — not built
- Ollama + LangGraph LLM normalization layer — not built
- Schema fields for chatbot metadata — not added

---

## 5) Ollama + LangGraph LLM Normalization Layer

*(Originally discussed in session, captured in 007-voice-bot-plan.md Phase 2 Step 3)*

### The Problem (Domain Shift)
- v1.0.2-b trained on terse nurse-typed phrases: `"chest pain radiating to left arm"`
- Voice bot produces verbose conversational text: `"my chest has been hurting and it goes into my left arm"`
- Different text style → shifted BioBERT embeddings → degraded classification accuracy

### The Solution
Add an LLM normalization step between voice extraction and BioBERT inference:

1. Raw conversational chief complaint arrives from Vapi
2. Ollama + Llama 3.2 8B rewrites it as a terse clinical phrase
3. Normalized phrase → BioBERT → PCA-b → v1.0.2-b → `chief_complaint_system`

### Recommended Stack
- **Ollama** — local, free, offline-capable, no API key needed
- **Llama 3.2 8B** — capable enough for clinical text normalization
- **LangGraph** — manages multi-turn conversation state as a state machine
- **Groq API** — free cloud fallback if demo machine is low on VRAM (same Llama model, faster)

### Why LangGraph over LangChain
- LangChain: simple linear chains (input → LLM → output)
- LangGraph: multi-step state machine — better for triage flow (collect → validate → confirm → submit)

---

## 6) New Schema Fields for Chatbot Integration

Fields to add to `VisitInput` / `TriageSubmission` schema:

| Field | Type | Purpose |
|---|---|---|
| `data_source` | `"form"` or `"voice_bot"` | Tracks how data was collected |
| `chief_complaint_normalized` | string | LLM-cleaned version of raw voice input |
| `voice_session_id` | string (optional) | Vapi session ID for audit trail |
| `fields_missing` | list of strings | Which fields weren't collected — triggers v1.0.2-c routing |
| `collection_confidence` | float (optional) | Vapi confidence score for extracted values |
