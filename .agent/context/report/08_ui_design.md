# VII. User Interface Design

The frontend adopts a dark-theme clinical aesthetic—background #0d0d0d, surface #111111—designed to reduce eye strain in brightly lit emergency department environments. The accent palette maps directly to ESI acuity levels: red (#ef4444) for Resuscitation, orange (#f97316) for Emergent, yellow (#eab308) for Urgent, green (#22c55e) for Less Urgent, and teal (#14b8a6) for Non-Urgent, enabling sub-second visual triage prioritization.

## A. Application Pages

**Landing Page** — presents two direct entry paths: a Patient Form card and a Voice Triage (Chatbot) card, routing patients directly to their intake method. A Staff/Admin Login button routes staff to the authentication page.

**Triage Form Page (/patient/form)** — structured data entry form collecting all clinical fields with real-time ML prediction on submission. No login required for patients.

**Chatbot Page (/patient/chatbot)** — WhatsApp-style conversation interface with live Vapi transcript streaming. The page has two panels: the left chat panel (full width during conversation, 50% during review) and the right Review & Confirm panel (Step 2 of 2) that slides in when the LLM calls show_confirm. All form fields are editable by the patient before submission. The Result Screen displays the acuity badge, chief complaint system, routed specialty, assigned doctor, and queue number.

**Sign In Page (/signin)** — single authentication page for all staff roles. The backend auto-detects role from the staff ID prefix (NURSE-XXXX vs DOC-XXXX), eliminating a role-selector UI element that could be accidentally mis-set.

**Staff Portal (/staff/*)** — nurse-facing dashboard with:
- Active patient queue sorted by acuity
- Task management and outcome recording
- Shift settings

**Doctor Portal (/doctor/*)** — doctor-facing dashboard with:
- Assigned patient queue with acuity badges
- Staff roster with on-duty toggle
- Department statistics (patient volume by shift, ESI distribution, caseload)
- Outcome tracking

**Superadmin Portal (/superadmin/*)** — cross-role administration: full system oversight, all staff management, system-wide metrics.

## B. Authentication Model
TriageGeist uses JWT-based authentication for all staff roles. Nurses and doctors submit their staff ID and password; the server returns a signed JWT stored in the browser. The backend determines role automatically from the staff ID prefix. Patient intake (both form and chatbot) requires no authentication.

## C. Result Screen
The result screen (shown after chatbot or form submission) displays:
- Acuity level (large numeral, coloured by ESI level)
- Urgency label (Resuscitation / Emergent / Urgent / Less Urgent / Non-Urgent)
- Chief complaint system (e.g. "cardiovascular", inferred by v1.0.2-b if missing)
- Routed specialty (e.g. "Emergency", "Cardiology")
- Assigned doctor ID (or "Awaiting doctor allocation" if none on duty)
- Queue number derived from visit_id (e.g. #007 from VT-0007)
