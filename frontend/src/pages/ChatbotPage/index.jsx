import React, { useEffect, useRef } from "react";
import { useChatbot } from "../../hooks/useChatbot";
import { ChatBubble, TypingBubble } from "./ChatBubble";
import { ConfirmForm } from "./ConfirmForm";
import { severityConfig } from "../../constants/triageSettings";
import Header from "../../components/Header";
import Footer from "../../components/Footer";

const ACUITY_COLORS = {
  1: "#ef4444",
  2: "#f97316",
  3: "#eab308",
  4: "#22c55e",
  5: "#14b8a6",
};

export default function ChatbotPage() {
  const {
    step, STEPS,
    messages, transcript, isSpeaking,
    collectedFields, fieldsMissing,
    result, error,
    startCall, endCall, submitTriage, updateField,
  } = useChatbot();

  const bottomRef = useRef(null);
  const isConfirm = step === STEPS.CONFIRM;
  const isDone = step === STEPS.DONE;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, transcript]);

  if (isDone && result) {
    return <ResultScreen result={result} />;
  }

  return (
    <div className="flex flex-col h-screen w-full overflow-hidden" style={{ background: "#0d0d0d" }}>

      <Header status={step} isSpeaking={isSpeaking} onEndCall={endCall} />

      {/* ── Main content area ─────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Chat panel ──────────────────────────────────────────── */}
        <div
          className="flex flex-col transition-all duration-500"
          style={{ width: isConfirm ? "50%" : "100%" }}
        >
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-8 py-6 space-y-3">
            {step === STEPS.IDLE && (
              <div className="flex h-full flex-col items-center justify-center gap-6 text-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[#1d3461] text-4xl text-[#2563eb]">
                  ✚
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-[#f5f5f5]">Voice Triage</h2>
                  <p className="mt-2 text-sm text-[#6b7280] max-w-xs">
                    Speak to our AI assistant to complete your medical triage assessment
                  </p>
                </div>
                <button
                  onClick={startCall}
                  className="rounded-xl bg-[#2563eb] px-10 py-3 text-sm font-semibold text-white transition hover:bg-[#1d4ed8] shadow-lg shadow-blue-900/30"
                >
                  Start Voice Triage
                </button>
                <p className="text-xs text-[#374151]">Ensure your microphone is enabled</p>
              </div>
            )}

            {step === STEPS.CONNECTING && (
              <div className="flex h-full flex-col items-center justify-center gap-3">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#2563eb] border-t-transparent" />
                <p className="text-sm text-[#6b7280]">Connecting to Riley…</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatBubble key={i} role={msg.role} text={msg.text} />
            ))}

            {(step === STEPS.ACTIVE || isSpeaking) && (
              <TypingBubble transcript={transcript} />
            )}

            <div ref={bottomRef} />
          </div>

          {/* Status bar */}
          {step !== STEPS.IDLE && step !== STEPS.CONNECTING && (
            <div
              className="flex items-center gap-2 border-t px-8 py-3 shrink-0"
              style={{ borderColor: "#1f1f1f", background: "#0a0a0a" }}
            >
              <span className={`h-2 w-2 rounded-full shrink-0 ${step === STEPS.ACTIVE ? "bg-[#22c55e] animate-pulse" : "bg-[#6b7280]"}`} />
              <span className="text-xs text-[#6b7280]">
                {step === STEPS.ACTIVE && "Listening — speak clearly into your microphone"}
                {step === STEPS.CONFIRM && "Review your details on the right before submitting"}
                {step === STEPS.SUBMITTING && "Submitting triage assessment…"}
                {step === STEPS.ERROR && "Connection error — please refresh and try again"}
              </span>
            </div>
          )}
        </div>

        {/* ── Confirm panel ───────────────────────────────────────── */}
        {isConfirm && (
          <div
            className="flex flex-col border-l shrink-0"
            style={{
              width: "50%",
              borderColor: "#1f1f1f",
              background: "#0d0d0d",
            }}
          >
            {/* Confirm panel header */}
            <div
              className="flex items-center justify-between px-6 py-4 border-b shrink-0"
              style={{ borderColor: "#1f1f1f", background: "#0a0a0a" }}
            >
              <div>
                <p className="text-xs uppercase tracking-widest text-[#6b7280]">Step 2 of 2</p>
                <h3 className="text-sm font-semibold text-[#f5f5f5] mt-0.5">Review & Confirm</h3>
              </div>
              <span className="text-xs text-[#4b5563] border border-[#1f1f1f] rounded-full px-3 py-1">
                Triage Summary
              </span>
            </div>

            <div style={{ flex: 1, overflow: "hidden", padding: "20px 24px", display: "flex", flexDirection: "column" }}>
              <ConfirmForm
                collectedFields={collectedFields}
                fieldsMissing={fieldsMissing}
                onFieldChange={updateField}
                onSubmit={() => submitTriage(collectedFields)}
                submitting={step === STEPS.SUBMITTING}
              />
            </div>
          </div>
        )}
      </div>

      <Footer />

      {error && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 rounded-xl border border-red-800 bg-red-950 px-4 py-2 text-sm text-red-300 whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
}

function ResultScreen({ result }) {
  const acuity = result.triage_acuity;
  const color = ACUITY_COLORS[acuity] || "#6b7280";
  const severity = severityConfig[acuity];

  return (
    <div className="flex flex-col h-screen w-full" style={{ background: "#0d0d0d" }}>
      <Header status="done" isSpeaking={false} onEndCall={null} />

      {/* Result card */}
      <div className="flex flex-1 items-center justify-center p-6">
        <div
          className="w-full max-w-md rounded-2xl border p-8 text-center"
          style={{ borderColor: "#1f1f1f", background: "#111111" }}
        >
          <p className="text-xs uppercase tracking-widest" style={{ color }}>
            Acuity Level
          </p>
          <p className="mt-2 text-7xl font-black" style={{ color }}>
            {acuity}
          </p>
          <p className="mt-1 text-base font-semibold" style={{ color }}>
            {severity?.label}
          </p>
          <p className="mt-1 text-xs text-[#6b7280]">{severity?.sublabel}</p>

          {result.chief_complaint_system && (
            <div className="mt-6">
              <p className="text-xs uppercase tracking-widest text-[#9ca3af]">Chief Complaint</p>
              <span
                className="mt-2 inline-block rounded-full px-4 py-1 text-sm font-semibold text-[#93c5fd]"
                style={{ background: "#1e3a5f" }}
              >
                {result.chief_complaint_system.replace(/_/g, " ")}
              </span>
            </div>
          )}

          <div className="mt-6">
            <p className="text-xs uppercase tracking-widest text-[#9ca3af]">Queue Number</p>
            <p className="mt-1 text-5xl font-black text-[#f5f5f5]">
              #{String(result.visit_id?.replace(/\D/g, "")).padStart(3, "0")}
            </p>
            <p className="mt-1 text-xs text-[#4b5563]">
              Please wait — a nurse will call your number
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
