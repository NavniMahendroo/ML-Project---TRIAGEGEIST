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

const LOCKED_STEPS = new Set([STEPS.CONFIRM, STEPS.SUBMITTING, STEPS.DONE]);

export function useChatbot() {
  const vapiRef = useRef(null);
  const stepRef = useRef(STEPS.IDLE);

  const [step, setStep] = useState(STEPS.IDLE);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [collectedFields, setCollectedFields] = useState({});
  const [fieldsMissing, setFieldsMissing] = useState([]);
  const [patientId, setPatientId] = useState(null);
  const [userRole, setUserRole] = useState("patient");
  const collectedFieldsRef = useRef({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");

  const setStepSynced = useCallback((next) => {
    const value = typeof next === "function" ? next(stepRef.current) : next;
    stepRef.current = value;
    setStep(value);
  }, []);

  const addMessage = useCallback((role, text) => {
    setMessages((prev) => [
      ...prev,
      { role, text, ts: new Date().toISOString() },
    ]);
  }, []);

  const startCall = useCallback(async () => {
    setStepSynced(STEPS.CONNECTING);
    setError(null);

    try {
      const { session_id } = await api.startSession();
      setSessionId(session_id);

      const vapi = new Vapi(VAPI_API_KEY);
      vapiRef.current = vapi;

      vapi.on("call-start", () => {
        setStepSynced(STEPS.ACTIVE);
        addMessage("bot", "Hello! Are you the patient, or are you here for someone else?");
      });

      vapi.on("speech-start", () => setIsSpeaking(true));
      vapi.on("speech-end", () => setIsSpeaking(false));

      vapi.on("message", (msg) => {
        // Once the user is reviewing or submitting, ignore all LLM tool calls
        // so they cannot overwrite edits the patient is making in the form.
        if (LOCKED_STEPS.has(stepRef.current)) return;

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
        setStepSynced((prev) => {
          if (LOCKED_STEPS.has(prev)) return prev;
          if (Object.keys(collectedFieldsRef.current).length > 0) return STEPS.CONFIRM;
          return STEPS.IDLE;
        });
      });

      vapi.on("error", (err) => {
        setError(err?.message || "Voice connection error");
        setStepSynced((prev) => {
          if (LOCKED_STEPS.has(prev)) return prev;
          if (Object.keys(collectedFieldsRef.current).length > 0) return STEPS.CONFIRM;
          return STEPS.ERROR;
        });
      });

      await vapi.start(VAPI_ASSISTANT_ID);
    } catch (err) {
      setError(err.message || "Failed to start session");
      setStepSynced(STEPS.ERROR);
    }
  }, [addMessage]);

  const handleToolCall = useCallback(async (name, args, sid) => {
    if (name === "update_fields") {
      setCollectedFields((prev) => {
        const next = { ...prev, ...args.fields };
        collectedFieldsRef.current = next;
        return next;
      });
      if (args.patient_id) setPatientId(args.patient_id);
      if (args.user_role) setUserRole(args.user_role);
      if (args.fields_missing) setFieldsMissing(args.fields_missing);
    }

    if (name === "show_confirm") {
      const fields = args.collected_fields || {};
      collectedFieldsRef.current = fields;
      setCollectedFields(fields);
      setFieldsMissing(args.fields_missing || []);
      setPatientId(args.patient_id);
      setUserRole(args.user_role || "patient");
      setStepSynced(STEPS.CONFIRM);
    }
  }, []);

  const endCall = useCallback(() => {
    vapiRef.current?.stop();
    vapiRef.current = null;
  }, []);

  const submitTriage = useCallback(async (finalFields) => {
    setStepSynced(STEPS.SUBMITTING);
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
      setStepSynced(STEPS.DONE);
    } catch (err) {
      setError(err.message || "Submission failed");
      setStepSynced(STEPS.CONFIRM); // keep form open so user can retry
    }
  }, [sessionId, patientId, userRole, collectedFields, messages, fieldsMissing, endCall]);

  const updateField = useCallback((field, value) => {
    setCollectedFields((prev) => {
      const next = { ...prev, [field]: value };
      collectedFieldsRef.current = next;
      return next;
    });
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
