# Plan 009 — Remove Intermediary Pages, Direct Home Navigation

## Objective

Simplify the patient-facing navigation by removing three pages and linking directly from the Landing Page to the Patient Form and Chatbot. Users should not have to click through an intermediary hub or a privacy page to reach intake.

---

## Pages to Delete

### 1. `PatientHubPage` (`/patient`)
- File: `frontend/src/pages/PatientHubPage.jsx`
- This is the "Choose Your Intake Method" screen with two cards — Voice Chatbot and Manual Patient Form.
- **Safe to delete.** The Landing Page already has both these links directly (`/patient/form` and `/patient/chatbot`). This page is a pure intermediary with no logic.
- The route `/patient` in `App.jsx` must be removed or redirected.
- The nav link `{ to: "/patient", label: "Patient" }` in `PlatformLayout.jsx` must be removed.

### 2. `PrivacyPage` (`/privacy`)
- File: `frontend/src/pages/PrivacyPage.jsx`
- Static informational page. No backend dependency whatsoever.
- **Safe to delete.** No other page fetches from it or depends on it.
- The route `/privacy` in `App.jsx` must be removed.
- The nav link `{ to: "/privacy", label: "Privacy" }` in `PlatformLayout.jsx` must be removed.

---

## Frontend Changes Required

### `App.jsx`
- Remove import of `PrivacyPage`
- Remove import of `PatientHubPage`
- Remove route: `<Route path="/privacy" element={<PrivacyPage />} />`
- Remove route: `<Route path="/patient" element={<PatientHubPage />} />`
- Keep `/patient/form` and `/patient/chatbot` routes — these are the actual destinations
- Keep the legacy redirect aliases `/triage` → `/patient/form` and `/chatbot` → `/patient/chatbot`

### `PlatformLayout.jsx`
- Remove `{ to: "/privacy", label: "Privacy" }` from the nav links array
- Remove `{ to: "/patient", label: "Patient" }` from the nav links array
- After removal the public nav will only show: Home, Sign In (or whatever remains)

### `LandingPage.jsx`
- Already links directly to `/patient/form` and `/patient/chatbot` — no changes needed here
- Optionally: improve the CTA copy or button layout to make the two entry points more prominent now that there's no hub page in between

### `Header.jsx` (Chatbot header)
- Already links to `/patient/form` — no change needed

### Files to Delete
- `frontend/src/pages/PatientHubPage.jsx`
- `frontend/src/pages/PrivacyPage.jsx`

---

## Backend Changes Required

**None.** Both pages are entirely static frontend components with no backend routes, API calls, or database interactions. Nothing in the backend references these pages.

---

## Risk Assessment

| Change | Risk | Notes |
|---|---|---|
| Delete PatientHubPage | None | Pure UI intermediary, no logic |
| Delete PrivacyPage | None | Fully static, no dependencies |
| Remove `/patient` route | Low | Add a redirect `/patient` → `/patient/form` as a safety net for any bookmarked URLs |
| Remove `/privacy` route | None | Not linked from anywhere critical |
| Removing nav links from PlatformLayout | None | Just UI cleanup |
---

## Suggested Redirect Safety Net

When removing `/patient`, instead of a hard 404, consider replacing it with:
```
<Route path="/patient" element={<Navigate to="/patient/form" replace />} />
```
This way any bookmarked or externally linked `/patient` URLs still work. Can be removed later.

---

## Summary

- Delete 2 files: `PatientHubPage.jsx`, `PrivacyPage.jsx`
- Clean up 2 routes and 2 nav links in `App.jsx` and `PlatformLayout.jsx`
- No backend work needed

---

---

# Doctor → Admin Renaming

## Context

The "Admin" portal is actually the **doctor's own portal**. The word "doctor" leaks into variable names, function names, UI labels, localStorage keys, and API method names throughout the frontend. These should all be renamed to use "admin" terminology for consistency with how the role is presented to users.

**Important constraint:** Backend API URLs (`/doctors/login`, `/doctors/:id/patients`, etc.) and database field names (`doctor_id`, `attended_by_doctor`, `assigned_doctor_id`) are **not renamed** — those are real domain entities. Only the frontend-facing role/auth/UI naming changes.

---

## UI Label Renames

These are visible strings shown in the browser:

| File | Old Label | New Label |
|---|---|---|
| `AdminPatientsPage.jsx` (adminLinks) | `"Doctor Management"` | `"Staff Management"` |
| `AdminPatientsPage.jsx` | `"Doctor Queue"` (section heading) | `"Admin Queue"` |
| `AdminPatientsPage.jsx` | `"Doctor session not found."` (error) | `"Admin session not found."` |
| `AdminDoctorsPage.jsx` (adminLinks) | `"Doctor Management"` | `"Staff Management"` |
| `AdminDoctorsPage.jsx` | title: `"Doctor Management"` | `"Staff Management"` |
| `AdminDoctorsPage.jsx` | subtitle mentions "doctor specialties" | update to "staff specialties" |
| `AdminDoctorsPage.jsx` | `"Loading doctors..."` | `"Loading staff..."` |
| `AdminStatsPage.jsx` (adminLinks) | `"Doctor Management"` | `"Staff Management"` |
| `AdminOutcomesPage.jsx` (adminLinks) | `"Doctor Management"` | `"Staff Management"` |
| `AdminSettingsPage.jsx` (adminLinks) | `"Doctor Management"` | `"Staff Management"` |
| `AdminDashboardPage.jsx` | tab label `"Doctor Management"` | `"Staff Management"` |
| `AdminDashboardPage.jsx` | section heading `"Doctor Management"` | `"Staff Management"` |
| `AdminPatientsPage.jsx` | fallback name `auth?.name \|\| "Doctor"` | `auth?.name \|\| "Admin"` |
| `SignInPage.jsx` | hint text `"Use your Doctor ID and password..."` | `"Use your Admin ID and password..."` |

---

## File Renames

These are the page component files renamed to reflect that they belong to the doctor/admin portal:

| Old Filename | New Filename |
|---|---|
| `AdminPatientsPage.jsx` | `DoctorPatientsPage.jsx` |
| `AdminDoctorsPage.jsx` | `DoctorStaffPage.jsx` |
| `AdminStatsPage.jsx` | `DoctorStatsPage.jsx` |
| `AdminOutcomesPage.jsx` | `DoctorOutcomesPage.jsx` |
| `AdminSettingsPage.jsx` | `DoctorSettingsPage.jsx` |
| `AdminDashboardPage.jsx` | `DoctorDashboardPage.jsx` |

Export function names inside each file are updated to match (e.g. `AdminPatientsPage` → `DoctorPatientsPage`).
Imports and JSX usage in `App.jsx` updated accordingly.

Files moved into `pages/DoctorPage/` folder. Staff pages moved into `pages/StaffPage/` folder. All relative imports updated from `../` to `../../`.

### `frontend/src/lib/api.js` — method renames

| Old Name | New Name | Notes |
|---|---|---|
| `api.doctorLogin(...)` | `api.adminLogin(...)` | Still calls `/doctors/login` endpoint |
| `api.listDoctorPatients(adminId)` | `api.listAdminPatients(adminId)` | Still calls `/doctors/:id/patients` |
| `api.updateDoctorDuty(adminId, onDuty)` | `api.updateAdminDuty(adminId, onDuty)` | Still calls `/doctors/:id/duty` |
| `api.markDoctorPatientAttended(adminId, visitId)` | `api.markAdminPatientAttended(adminId, visitId)` | Still calls `/doctors/:id/patients/:vid/attend` |

### `DoctorPatientsPage.jsx` — internal variable renames

| Old Name | New Name |
|---|---|
| `const doctorId = auth?.doctor_id` | `const adminId = auth?.doctor_id` |
| `const doctorName = auth?.name \|\| "Doctor"` | `const adminName = auth?.name \|\| "Admin"` |
| All uses of `doctorId` | `adminId` |
| All uses of `doctorName` | `adminName` |

### `DoctorStaffPage.jsx` — internal variable renames

| Old Name | New Name |
|---|---|
| `const [doctors, setDoctors]` | `const [staff, setStaff]` |
| `async function loadDoctors()` | `async function loadStaff()` |
| `doctors.map((doctor) => ...)` | `staff.map((member) => ...)` |

### `SignInPage.jsx`

| Old | New |
|---|---|
| `api.doctorLogin(...)` | `api.adminLogin(...)` |
| hint text "Use your Doctor ID..." | "Use your Admin ID..." |

---

## localStorage Key Renames

These are currently fine (`adminAuth`, `staffAuth`) — **no change needed**. They already use the right terminology.

---

## Files That Do NOT Need Changes

- `backend/` — all backend files keep `doctor_id`, `nurse_id`, `/doctors/*` routes. These are real domain names, not role names.
- `frontend/src/components/SeverityCard.jsx` — "Assigned Doctor" label refers to an actual doctor assignment, not the role. Keep as-is.
- `frontend/src/pages/ChatbotPage/index.jsx` — "Assigned Doctor" label same reason. Keep as-is.
- `frontend/src/hooks/useTriage.js` — `nurse_id` is a real form field. Keep as-is.
- `frontend/src/constants/triageSettings.js` — `nurse_id` is a real field key. Keep as-is.

---

## Status — All Implemented

| Change | Status |
|---|---|
| Delete `PatientHubPage.jsx`, `PrivacyPage.jsx` | ✅ Done |
| Remove `/privacy` route, redirect `/patient` → `/patient/form` | ✅ Done |
| Remove Privacy/Patient nav links from `PlatformLayout.jsx` | ✅ Done |
| Rename all `Admin*Page` files to `Doctor*Page` | ✅ Done |
| Move Doctor pages into `pages/DoctorPage/` | ✅ Done |
| Move Staff pages into `pages/StaffPage/` | ✅ Done |
| Fix relative imports after folder move (`../` → `../../`) | ✅ Done |
| `api.doctorLogin` → `api.adminLogin` | ✅ Done |
| `api.listDoctorPatients` → `api.listAdminPatients` | ✅ Done |
| `api.markDoctorPatientAttended` → `api.markAdminPatientAttended` | ✅ Done |
| `api.updateDoctorDuty` → `api.updateAdminDuty` | ✅ Done |
| `doctorId`/`doctorName` → `adminId`/`adminName` in `DoctorPatientsPage` | ✅ Done |
| `doctors`/`loadDoctors` → `staff`/`loadStaff` in `DoctorStaffPage` | ✅ Done |
| "Doctor Management" → "Staff Management" across all pages | ✅ Done |
| "Doctor Queue" → "Admin Queue" in `DoctorPatientsPage` | ✅ Done |
| "Doctor session not found" → "Admin session not found" | ✅ Done |
| `SignInPage` hint text updated to "Admin ID" | ✅ Done |
| Backend API URLs — not touched | ✅ Intentional |
