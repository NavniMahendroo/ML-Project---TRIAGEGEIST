import { useCallback, useEffect, useRef, useState } from "react";
import Vapi from "@vapi-ai/web";
import { api } from "../lib/api";

const VAPI_API_KEY = import.meta.env.VITE_VAPI_API_KEY || "";
const VAPI_ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID || "";

const STEPS = {
  IDLE: "idle",
  CONNECTING: "connecting",
  ACTIVE: "active",
  CONFIRM: "confirm",
  SUBMITTING: "submitting",
  DONE: "done",
  ERROR: "error",
};

export function useChatbot() {
  const vapiRef = useRef(null);

  const [step, setStep] = useState(STEPS.IDLE);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [collectedFields, setCollectedFields] = useState({});
  const [fieldsMissing, setFieldsMissing] = useState([]);
  const [patientId, setPatientId] = useState(null);
  const [userRole, setUserRole] = useState("patient");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");

  const addMessage = useCallback((role, text) => {
    setMessages((prev) => [
      ...prev,
      { role, text, ts: new Date().toISOString() },
    ]);
  }, []);

  const startCall = useCallback(async () => {
    setStep(STEPS.CONNECTING);
    setError(null);

    try {
      const { session_id } = await api.startSession();
      setSessionId(session_id);

      const vapi = new Vapi(VAPI_API_KEY);
      vapiRef.current = vapi;

      vapi.on("call-start", () => {
        setStep(STEPS.ACTIVE);
        addMessage("bot", "Hello! Are you the patient, or are you here for someone else?");
      });

      vapi.on("speech-start", () => setIsSpeaking(true));
      vapi.on("speech-end", () => setIsSpeaking(false));

      vapi.on("message", (msg) => {
        if (msg.type === "transcript") {
          if (msg.transcriptType === "partial") {
            setTranscript(msg.transcript);
          } else if (msg.transcriptType === "final") {
            setTranscript("");
            addMessage(msg.role === "assistant" ? "bot" : "patient", msg.transcript);
          }
        }

        if (msg.type === "tool-calls") {
          const toolCall = msg.toolCallList?.[0];
          if (!toolCall) return;
          const args = toolCall.function?.arguments || {};
          handleToolCall(toolCall.function?.name, args, session_id);
        }
      });

      vapi.on("call-end", () => {
        setIsSpeaking(false);
        setTranscript("");
        // If confirm panel is open, keep it open — call ending is expected at this point
        setStep((prev) => (prev === STEPS.CONFIRM || prev === STEPS.SUBMITTING || prev === STEPS.DONE) ? prev : STEPS.IDLE);
      });

      vapi.on("error", (err) => {
        setError(err?.message || "Voice connection error");
        // Only go to ERROR if we haven't reached the confirm step yet
        setStep((prev) => (prev === STEPS.CONFIRM || prev === STEPS.SUBMITTING || prev === STEPS.DONE) ? prev : STEPS.ERROR);
      });

      await vapi.start(VAPI_ASSISTANT_ID);
    } catch (err) {
      setError(err.message || "Failed to start session");
      setStep(STEPS.ERROR);
    }
  }, [addMessage]);

  const handleToolCall = useCallback(async (name, args, sid) => {
    if (name === "update_fields") {
      setCollectedFields((prev) => ({ ...prev, ...args.fields }));
      if (args.patient_id) setPatientId(args.patient_id);
      if (args.user_role) setUserRole(args.user_role);
      if (args.fields_missing) setFieldsMissing(args.fields_missing);
    }

    if (name === "show_confirm") {
      setCollectedFields(args.collected_fields || {});
      setFieldsMissing(args.fields_missing || []);
      setPatientId(args.patient_id);
      setUserRole(args.user_role || "patient");
      setStep(STEPS.CONFIRM);
    }
  }, []);

  const endCall = useCallback(() => {
    vapiRef.current?.stop();
    vapiRef.current = null;
  }, []);

  const submitTriage = useCallback(async (finalFields) => {
    setStep(STEPS.SUBMITTING);
    endCall();

    try {
      const payload = {
        session_id: sessionId,
        patient_id: patientId,
        user_role: userRole,
        collected_fields: finalFields || collectedFields,
        conversation_raw: messages,
        fields_missing: fieldsMissing,
        collection_confidence: null,
      };
      const data = await api.submitChatbot(payload);
      setResult(data);
      setStep(STEPS.DONE);
    } catch (err) {
      setError(err.message || "Submission failed");
      setStep(STEPS.CONFIRM); // keep form open so user can retry
    }
  }, [sessionId, patientId, userRole, collectedFields, messages, fieldsMissing, endCall]);

  const updateField = useCallback((field, value) => {
    setCollectedFields((prev) => ({ ...prev, [field]: value }));
  }, []);

  useEffect(() => {
    return () => {
      vapiRef.current?.stop();
    };
  }, []);

  return {
    step,
    STEPS,
    messages,
    transcript,
    isSpeaking,
    collectedFields,
    fieldsMissing,
    result,
    error,
    startCall,
    endCall,
    submitTriage,
    updateField,
  };
}
