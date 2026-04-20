# Frontend Context — Delhi Hospital Triage System

## Branding
- Hospital name: Delhi Hospital
- Site name: TriageGeist
- Logo: medical cross icon (blue, #2563eb)
- Theme: Dark throughout

## Design Direction
- Dark themed throughout (#0d0d0d base)
- Chatbot UI similar to ChatGPT/Gemini — message bubbles, typing indicator, clean chat window
- Simple, essential, no fancy decorations
- Focus: functional and professional

---

## User Types

| User | Entry Point | Auth |
|---|---|---|
| Patient | Landing page → Patient block | 3-digit session code |
| Nurse | Landing page → Staff block | 3-digit session code |
| Doctor | Top-right Staff Login button | Staff ID + 4-digit PIN |
| Admin | Top-right Staff Login button | Staff ID + 4-digit PIN |

### Two-Code Auth System
| Code | Digits | Used on | Purpose |
|---|---|---|---|
| Session code | 3 digits | Landing page blocks | Quick triage session start |
| Login PIN | 4 digits | Staff Login page | Full profile, dashboard, admin access |

---

## Pages

### 1) Landing Page
- Selected design: mockup-1.svg
- Header: logo + hospital name + Staff Login button (top-right only)
- Two blocks: Patient and Staff — both use 3-digit session code to begin
- Footer: hospital name + version

### 2) Patient Chatbot Page
- Full screen dark chat UI (ChatGPT style)
- Bot collects triage info conversationally
- On completion → Triage Result Page

### 3) Nurse/Staff Chatbot Page
- Same chat UI, different system prompt (more clinical)
- On completion → Triage Result Page

### 4) Triage Result Page
- Selected design: mockup-4.svg
- Shows: Acuity level (color coded 1–5), Chief complaint system (pill tag), Queue number
- Clean, minimal, readable

### 5) Staff Login Page
- Selected design: mockup-5.svg (role selector removed)
- Fields: Staff ID + 4-digit PIN only
- Role determined automatically by backend from Staff ID
- Back link to landing page

### 6) Admin Dashboard Page
- Patient stats: total visits, acuity distribution, recent patients table
- Staff stats: submissions per nurse/doctor
- System stats: model usage, fallback (v1.0.2-c) rate
- Charts: bar (acuity), line (daily volume)

---

## Approved Mockups
| File | Page |
|---|---|
| images/mockup-1.svg | Landing page |
| images/mockup-4.svg | Triage result page |
| images/mockup-5.svg | Staff login page |

---

## Out of Scope (for now)
- Mobile optimization
- Multi-site / multi-hospital
- Patient login / patient accounts
- Interactive maps
- Real-time websocket dashboard
- Lazy loading / skeleton loading
