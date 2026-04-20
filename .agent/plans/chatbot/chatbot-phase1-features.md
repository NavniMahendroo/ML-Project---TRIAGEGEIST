# Chatbot Phase 1 — Features

## Scope
- English only
- Returning patients only (must exist in DB)
- Used by patient or their attendant (not nurse)
- Replaces the triage form entirely

---

## Step 0 — Role Detection
- Bot opens with: "Are you the patient, or are you here for someone else?"
- If the first message makes it obvious ("my father is not responding", "my friend is in pain") — extract role from that line, skip the question
- If attendant: bot frames all subsequent questions in third person ("Where is the patient's pain?")
- Role is never locked — user can correct any value on the confirmation screen before submission

---

## Step 1 — Patient Verification
- Ask for any 2 of: Patient ID, Name, Age
- Name matching is fuzzy (voice may mishear exact names)
- If fuzzy name match found: show the matched name(s) and age to the user, let them select the correct one before loading the record
- If multiple names match without age: show all matching names, user selects correct name + confirms age
- If no match at all → inform user we couldn't find a record, ask them to approach the front desk
  (new patient creation is later phase)

---

## Step 2 — Complaint Collection
- Questions asked in this order. Skip any field the patient already volunteered.

```
1. mental_status_triage    "Is the patient alert? Confused? Drowsy? Not responding?"
2. chief_complaint_raw     "What's the main problem / what brought you in today?"
3. pain_location           "Where exactly is the pain or discomfort?"
4. pain_score              "On a scale of 0 to 10, how bad is the pain?"
5. arrival_mode            "How did you get to the hospital?"  ← required by ML model
6. transport_origin        "Where were you coming from?"       ← can be skipped
```

- mental_status_triage and pain_score are always asked directly — never inferred from speech
- pain_location is silently mapped to the nearest enum value (abdomen, back, chest, extremity, head, multiple, none, pelvis, unknown) and shown on the confirmation screen
- If patient gives multiple fields in one message, extract all and skip those questions
- If a value is out of range or unrecognizable, ask to repeat once — do not loop endlessly
- If patient says "I don't know" for any field, mark it null and move on immediately

---

## Step 3 — Vitals
- height_cm and weight_kg are already on the patient record — do not ask
- Bot first asks: "Were the patient's vitals taken by a nurse?"

**If yes — collect in batches, none are mandatory:**
```
Batch 1 (basic, most available):
  heart_rate, respiratory_rate, temperature_c

Batch 2 (equipment-dependent):
  spo2
  gcs_total — only ask if the score was already measured; do not ask patient to assess it

Batch 3 (BP group — skip entire group if any one is unavailable):
  systolic_bp, diastolic_bp
  → mean_arterial_pressure and pulse_pressure are derived, never asked
```

**If no — ask basic vitals only, all skippable:**
```
  heart_rate, temperature_c
```

- Collect as many as possible — more vitals = better prediction
- If a value is missing or patient says "I don't know", accept null and move on — never block on vitals
- Flag any missing vitals in system as "Vitals pending"

---

## Step 4 — Confirmation Screen
- Form with all collected values slides to the left of the screen
- Chat moves to the right
- Patient can say "change pain score to 7" and the bot updates the value on the form in real time
- Bot asks "Should I submit now?" after each correction
- Nothing is sent to the backend until the patient explicitly confirms

---

## Step 5 — Result Screen
- Show acuity badge + queue number after submission

---

## Extraction Behaviour (applies throughout)
- Llama returns a confidence score per extracted field
- If confidence < threshold: bot asks to confirm that specific field before accepting
- "I don't know" / silence / out-of-range → mark null, move on — never loop
