const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

async function get(path) {
  return request(path, { method: "GET" });
}

async function post(path, body) {
  return request(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export const api = {
  nurseLogin: (nurseId, password) =>
    post("/nurses/login", { nurse_id: nurseId, password, role: "staff" }),

  adminLogin: (adminId, password) =>
    post("/doctors/login", { doctor_id: adminId, password, role: "admin" }),

  superadminLogin: (adminId, password) =>
    post("/superadmin/login", { admin_id: adminId, password }),

  listDoctors: () => get("/doctors"),

  listAdminPatients: (adminId) => get(`/doctors/${adminId}/patients`),

  updateAdminDuty: (adminId, onDuty) =>
    post(`/doctors/${adminId}/duty`, { on_duty: onDuty }),

  markAdminPatientAttended: (adminId, visitId) =>
    post(`/doctors/${adminId}/patients/${visitId}/attend`, {}),

  getSuperadminSummary: () => get("/superadmin/dashboard/summary"),

  listSuperadminAssignments: (limit = 100) =>
    get(`/superadmin/dashboard/assignments?limit=${limit}`),

  markSuperadminAssignmentAttended: (visitId) =>
    post(`/superadmin/dashboard/assignments/${visitId}/attend`, {}),

  reassignSuperadminAssignment: (visitId, doctorId) =>
    post(`/superadmin/dashboard/assignments/${visitId}/reassign`, { doctor_id: doctorId }),

  startSession: (vapiSessionId = null) =>
    post("/chatbot/session/start", { vapi_session_id: vapiSessionId }),

  verifyPatient: (name, age, patientId = null) =>
    post("/chatbot/verify", { name, age, patient_id: patientId }),

  submitChatbot: (payload) =>
    post("/chatbot/submit", payload),
};
