import React from "react";

export default function Header({ status, isSpeaking, onEndCall }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 32px", background: "#1e3a5f", borderBottom: "1px solid #2563eb" }}>
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{ width: "40px", height: "40px", borderRadius: "10px", background: "#2563eb", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px", color: "white", fontWeight: "900" }}>
          ✚
        </div>
        <div>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "#ffffff", lineHeight: "1.2" }}>TriageGeist</div>
          <div style={{ fontSize: "11px", color: "#93c5fd" }}>Delhi Hospital · Clinical Intake</div>
        </div>
      </div>

      {/* Center */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "#1d4ed8", borderRadius: "999px", padding: "6px 16px" }}>
        <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#4ade80" }} />
        <span style={{ fontSize: "12px", color: "#bfdbfe", fontWeight: "500" }}>Voice Triage · AI Assisted</span>
      </div>

      {/* Right */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {isSpeaking && (
          <span style={{ fontSize: "12px", color: "#4ade80", fontWeight: "600", display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
            Speaking
          </span>
        )}
        {status === "active" && onEndCall && (
          <button
            onClick={onEndCall}
            style={{ background: "#7f1d1d", border: "1px solid #ef4444", borderRadius: "8px", padding: "6px 14px", fontSize: "12px", color: "#fca5a5", cursor: "pointer", fontWeight: "600" }}
          >
            End Call
          </button>
        )}
        <a
          href="/patient/form"
          style={{ fontSize: "12px", color: "#93c5fd", background: "#1e40af", borderRadius: "8px", padding: "6px 14px", fontWeight: "600", textDecoration: "none", border: "1px solid #3b82f6" }}
        >
          Patient Form
        </a>
        <a
          href="/signin"
          style={{ fontSize: "12px", color: "#c7d2fe", background: "#312e81", borderRadius: "8px", padding: "6px 14px", fontWeight: "600", textDecoration: "none", border: "1px solid #6366f1" }}
        >
          Staff/Admin Login
        </a>
      </div>
    </div>
  );
}
