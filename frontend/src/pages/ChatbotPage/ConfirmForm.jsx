import React, { useState } from "react";

const ROW_PAIRS = [
  ["patient_name", "patient_age"],
  ["patient_id", null],
  ["mental_status_triage", "arrival_mode"],
  ["pain_location", "pain_score"],
  ["chief_complaint_raw", null],
  ["chief_complaint_normalized", null],
  ["heart_rate", "respiratory_rate"],
  ["temperature_c", "spo2"],
  ["systolic_bp", "diastolic_bp"],
  ["gcs_total", "transport_origin"],
];

const FIELD_LABELS = {
  patient_name:               "Patient Name",
  patient_age:                "Age",
  patient_id:                 "Hospital Patient ID",
  mental_status_triage:       "Mental Status",
  chief_complaint_raw:        "Chief Complaint",
  chief_complaint_normalized: "Complaint (Clinical)",
  pain_location:              "Pain Location",
  pain_score:                 "Pain Score (0–10)",
  arrival_mode:               "Arrival Mode",
  transport_origin:           "Transport Origin",
  heart_rate:                 "Heart Rate (bpm)",
  respiratory_rate:           "Resp. Rate (/min)",
  temperature_c:              "Temp (°C)",
  spo2:                       "SpO₂ (%)",
  systolic_bp:                "Systolic BP (mmHg)",
  diastolic_bp:               "Diastolic BP (mmHg)",
  gcs_total:                  "GCS Total (3–15)",
};

// Validation rules per field
const VALIDATORS = {
  patient_age:      { type: "int",   min: 0,    max: 120,  label: "Age must be 0–120" },
  pain_score:       { type: "int",   min: 0,    max: 10,   label: "Pain score must be 0–10" },
  heart_rate:       { type: "float", min: 20,   max: 260,  label: "Heart rate must be 20–260 bpm" },
  respiratory_rate: { type: "float", min: 0,    max: 100,  label: "Resp. rate must be 0–100 /min" },
  temperature_c:    { type: "float", min: 30.0, max: 45.0, label: "Temperature must be 30–45 °C" },
  spo2:             { type: "float", min: 0,    max: 100,  label: "SpO₂ must be 0–100%" },
  systolic_bp:      { type: "float", min: 40,   max: 300,  label: "Systolic BP must be 40–300" },
  diastolic_bp:     { type: "float", min: 20,   max: 200,  label: "Diastolic BP must be 20–200" },
  gcs_total:        { type: "int",   min: 3,    max: 15,   label: "GCS must be 3–15" },
  mental_status_triage: {
    type: "enum",
    options: ["alert", "confused", "unresponsive"],
    label: 'Must be "alert", "confused", or "unresponsive"',
  },
  arrival_mode: {
    type: "enum",
    options: ["walk-in", "ambulance", "brought by friend", "brought by family"],
    label: 'Must be "walk-in", "ambulance", "brought by friend", or "brought by family"',
  },
};

function validateField(field, value) {
  if (value === null || value === undefined || value === "") return null;
  const rule = VALIDATORS[field];
  if (!rule) return null;

  if (rule.type === "enum") {
    if (!rule.options.includes(String(value).toLowerCase().trim())) return rule.label;
    return null;
  }

  const num = rule.type === "int" ? parseInt(value, 10) : parseFloat(value);
  if (isNaN(num)) return `Must be a number`;
  if (num < rule.min || num > rule.max) return rule.label;
  return null;
}

function validateAll(fields) {
  const errors = {};
  for (const field of Object.keys(VALIDATORS)) {
    const err = validateField(field, fields[field]);
    if (err) errors[field] = err;
  }
  if (!fields.patient_name?.trim()) errors.patient_name = "Patient name is required";
  if (!fields.chief_complaint_raw?.trim()) errors.chief_complaint_raw = "Chief complaint is required";
  return errors;
}

function Field({ field, value, isMissing, onFieldChange, error }) {
  const isEmpty = value === undefined || value === null || value === "";
  const borderColor = error ? "#ef4444" : isMissing && isEmpty ? "#7f1d1d" : "#2a2a2a";

  return (
    <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: "2px" }}>
      <div style={{
        background: "#151515",
        border: `1px solid ${borderColor}`,
        borderRadius: "10px",
        padding: "10px 14px",
      }}>
        <p style={{ fontSize: "10px", textTransform: "uppercase", letterSpacing: "0.08em", color: "#6b7280", marginBottom: "4px" }}>
          {FIELD_LABELS[field] || field}
        </p>
        <input
          style={{ width: "100%", background: "transparent", border: "none", outline: "none", fontSize: "14px", color: isEmpty ? "#6b7280" : "#f5f5f5", fontWeight: "500" }}
          placeholder={isMissing && isEmpty ? "Not provided — enter manually" : ""}
          value={value ?? ""}
          onChange={(e) => onFieldChange(field, e.target.value)}
        />
      </div>
      {error && (
        <p style={{ fontSize: "10px", color: "#ef4444", paddingLeft: "4px" }}>{error}</p>
      )}
    </div>
  );
}

export function ConfirmForm({ collectedFields, fieldsMissing, onFieldChange, onSubmit, submitting }) {
  const [errors, setErrors] = useState({});
  const missing = new Set(fieldsMissing || []);

  const handleSubmit = () => {
    const errs = validateAll(collectedFields);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return; // block submit
    onSubmit();
  };

  const handleFieldChange = (field, value) => {
    onFieldChange(field, value);
    // Clear error for this field as user edits
    if (errors[field]) {
      setErrors((prev) => { const next = { ...prev }; delete next[field]; return next; });
    }
  };

  const rows = ROW_PAIRS.filter(([a, b]) => {
    const aVisible = collectedFields[a] !== undefined || missing.has(a);
    const bVisible = b ? (collectedFields[b] !== undefined || missing.has(b)) : false;
    return aVisible || bVisible;
  });

  const errorCount = Object.keys(errors).length;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: "0" }}>

      {/* Scrollable fields */}
      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "8px", paddingRight: "4px", paddingBottom: "4px" }}>
        {rows.map(([a, b]) => {
          const aVisible = collectedFields[a] !== undefined || missing.has(a);
          const bVisible = b && (collectedFields[b] !== undefined || missing.has(b));

          return (
            <div key={a} style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
              {aVisible && (
                <Field
                  field={a}
                  value={collectedFields[a]}
                  isMissing={missing.has(a)}
                  onFieldChange={handleFieldChange}
                  error={errors[a]}
                />
              )}
              {bVisible && (
                <Field
                  field={b}
                  value={collectedFields[b]}
                  isMissing={missing.has(b)}
                  onFieldChange={handleFieldChange}
                  error={errors[b]}
                />
              )}
              {aVisible && b && !bVisible && <div style={{ flex: 1 }} />}
            </div>
          );
        })}
      </div>

      {/* Pending vitals notice */}
      {fieldsMissing?.length > 0 && (
        <div style={{ marginTop: "10px", padding: "10px 14px", background: "#1c1200", border: "1px solid #713f12", borderRadius: "10px", flexShrink: 0 }}>
          <p style={{ fontSize: "11px", color: "#ca8a04" }}>
            Vitals not provided: {fieldsMissing.join(", ")}
          </p>
        </div>
      )}

      {/* Validation error summary */}
      {errorCount > 0 && (
        <div style={{ marginTop: "10px", padding: "10px 14px", background: "#1a0000", border: "1px solid #ef4444", borderRadius: "10px", flexShrink: 0 }}>
          <p style={{ fontSize: "12px", color: "#ef4444", fontWeight: "600" }}>
            {errorCount} field{errorCount > 1 ? "s have" : " has"} invalid values — please correct before submitting.
          </p>
        </div>
      )}

      {/* Submit — never auto-triggers, always visible */}
      <button
        onClick={handleSubmit}
        disabled={submitting}
        style={{
          marginTop: "12px",
          width: "100%",
          padding: "14px",
          background: submitting ? "#1e3a5f" : "#2563eb",
          border: "none",
          borderRadius: "10px",
          fontSize: "14px",
          fontWeight: "700",
          color: "white",
          cursor: submitting ? "not-allowed" : "pointer",
          opacity: submitting ? 0.7 : 1,
          flexShrink: 0,
        }}
      >
        {submitting ? "Submitting…" : "Confirm & Submit"}
      </button>
    </div>
  );
}
