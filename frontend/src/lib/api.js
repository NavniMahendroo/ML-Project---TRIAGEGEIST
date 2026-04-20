const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

export const api = {
  startSession: (vapiSessionId = null) =>
    post("/chatbot/session/start", { vapi_session_id: vapiSessionId }),

  verifyPatient: (name, age, patientId = null) =>
    post("/chatbot/verify", { name, age, patient_id: patientId }),

  submitChatbot: (payload) =>
    post("/chatbot/submit", payload),
};
