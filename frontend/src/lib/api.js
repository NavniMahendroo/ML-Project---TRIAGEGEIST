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

  doctorLogin: (doctorId, password) =>
    post("/doctors/login", { doctor_id: doctorId, password, role: "admin" }),

  listDoctors: () => get("/doctors"),

  listDoctorPatients: (doctorId) => get(`/doctors/${doctorId}/patients`),

  updateDoctorDuty: (doctorId, onDuty) =>
    post(`/doctors/${doctorId}/duty`, { on_duty: onDuty }),

  markDoctorPatientAttended: (doctorId, visitId) =>
    post(`/doctors/${doctorId}/patients/${visitId}/attend`, {}),

  startSession: (vapiSessionId = null) =>
    post("/chatbot/session/start", { vapi_session_id: vapiSessionId }),

  verifyPatient: (name, age, patientId = null) =>
    post("/chatbot/verify", { name, age, patient_id: patientId }),

  submitChatbot: (payload) =>
    post("/chatbot/submit", payload),
};
