import { useState, useMemo } from "react";
import { intakeDefaults, severityConfig } from "../constants/triageSettings";
import { formatApiError } from "../lib/utils";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function useTriage() {
  const [formData, setFormData] = useState(intakeDefaults);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const severity = useMemo(() => {
    if (!result?.triage_acuity) return null;
    return severityConfig[result.triage_acuity] || severityConfig[3];
  }, [result]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // In a real app we might want to do standard mapping here if the fields mismatched,
      // but since we updated the backend to match the form fields strictly through Phase 2/3,
      // mapping directly is sufficient.
      const payload = {
        age: Number(formData.age),
        sex: formData.sex,
        arrival_mode: formData.arrival_mode,
        chief_complaint_raw: formData.chief_complaint_raw,
        heart_rate: Number(formData.heart_rate),
        respiratory_rate: Number(formData.respiratory_rate),
        spo2: Number(formData.spo2),
        systolic_bp: Number(formData.systolic_bp),
        diastolic_bp: Number(formData.diastolic_bp),
        temperature_c: Number(formData.temperature_c),
        pain_score: Number(formData.pain_score),
        gcs_total: Number(formData.gcs_total),
        news2_score: Number(formData.news2_score),
      };

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(formatApiError(data.detail));

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(intakeDefaults);
    setResult(null);
    setError("");
  };

  return {
    formData,
    result,
    loading,
    error,
    severity,
    handleChange,
    handleSubmit,
    handleReset,
  };
}

export { useTriage };
