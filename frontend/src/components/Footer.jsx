import React from "react";

export default function Footer() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 32px", background: "#1e3a5f", borderTop: "1px solid #2563eb" }}>
      <span style={{ fontSize: "12px", color: "#93c5fd" }}>© 2025 TriageGeist · Delhi Hospital</span>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "#93c5fd" }}>
        <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
        System Online
      </div>
      <span style={{ fontSize: "12px", color: "#93c5fd" }}>
        Medical emergencies: <span style={{ color: "#f87171", fontWeight: "700" }}>112</span>
      </span>
    </div>
  );
}
