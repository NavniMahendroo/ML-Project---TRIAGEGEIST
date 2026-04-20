# Chatbot — Later Phase Features

---

## New Patient Support
- If no DB match found, create a new patient record inline during the session
- Collect: name, age, sex
- Route to v1.0.2-c (fallback model, no history)

---

## Multilingual Support
- Language selection before role detection (first thing bot asks)
- Bot messages + TTS in chosen language
- Patient input in any language → translated to English before BioBERT / ML models
- Languages to support: decide based on patient population

---

## Nurse Bot
- Separate bot with same underlying pipeline but different behaviour
- Rigid and fast — no leniency, no gentle re-asks
- Patient ID mandatory (no name/age fallback)
- GCS total collected here (not in patient bot)
- Vitals always collected (not optional)
- Skips role detection entirely
- Language always English

---

## Urgency Shortcut
- If mental_status is "unresponsive" or pain_score ≥ 9, skip remaining complaint questions
- Submit immediately with whatever is collected, flagged as high-priority
- Do not waste time asking arrival_mode when the patient may be critical

---

## Timeout Handling
- If patient goes silent for 30s mid-conversation, bot prompts once: "Are you still there?"
- After another 30s of silence, save all collected fields and flag session as incomplete
- Partial data is never lost

---

## Lazy Loading + Skeleton UI
- Implement once multiple routes exist (chatbot, admin, result pages)
- React.lazy + Suspense per page
- Skeleton placeholders while data fetches

---

## Admin Dashboard
- Charts: acuity distribution (bar), daily volume (line)
- Tables: recent patients, staff submission counts
- System stats: v1.0.2-c fallback rate, model confidence over time, chief complaint distribution
- Real-time updates via websocket (future)

---

## Open Questions

**Attendant details:**
- Do we save anything about the attendant (name, phone, relationship to patient)?
- Currently only saving `user_role: "attendant"` — is that enough?

**Vitals pending — nurse notification:**
- How does the nurse get notified that vitals are pending?
- Options: flag on patient queue, push notification to nurse dashboard, or just a DB field?

**Unconscious patient (attendant flow):**
- `pain_score` → None (not -1, ge=0 validator rejects it)
- `mental_status_triage` → "unresponsive"
- Do we need a separate field to distinguish "patient couldn't report pain" vs "pain score genuinely unknown"?
