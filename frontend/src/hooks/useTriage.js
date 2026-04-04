import { useEffect, useState } from "react";
import { buildInitialFormData, fallbackFieldOptions, severityConfig } from "../constants/triageSettings";
import { formatApiError } from "../lib/utils";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function toOptionalNumber(value) {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  return Number(value);
}

function useTriage() {
  const [fieldOptions, setFieldOptions] = useState(fallbackFieldOptions);
  const [formData, setFormData] = useState(() => buildInitialFormData(fallbackFieldOptions));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    async function loadFieldOptions() {
      try {
        const response = await fetch(`${API_BASE_URL}/triage/options`);
        const data = await response.json();
        if (!response.ok) {
          throw new Error(formatApiError(data.detail));
        }

        if (!isActive) {
          return;
        }

        const nextOptions = data.field_options || fallbackFieldOptions;
        setFieldOptions(nextOptions);
        setFormData((prev) => ({
          ...buildInitialFormData(nextOptions),
          ...prev,
          site_id: prev.site_id || nextOptions.site_id?.[0]?.value || "SITE-0001",
          nurse_id: prev.nurse_id || nextOptions.nurse_id?.[0]?.value || "self",
        }));
      } catch (err) {
        if (isActive) {
          setFieldOptions(fallbackFieldOptions);
        }
      } finally {
        if (isActive) {
          setOptionsLoading(false);
        }
      }
    }

    loadFieldOptions();
    return () => {
      isActive = false;
    };
  }, []);

  const severity = result?.triage_acuity
    ? severityConfig[result.triage_acuity] || severityConfig[3]
    : null;

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
      const payload = {
        patient: {
          name: formData.name,
          age: Number(formData.age),
          sex: formData.sex,
          language: formData.language,
          insurance_type: formData.insurance_type,
          num_active_medications: Number(formData.num_active_medications),
          num_comorbidities: Number(formData.num_comorbidities),
          weight_kg: Number(formData.weight_kg),
          height_cm: Number(formData.height_cm),
        },
        visit: {
          site_id: formData.site_id,
          nurse_id: formData.nurse_id,
          arrival_mode: formData.arrival_mode,
          transport_origin: formData.transport_origin,
          pain_location: formData.pain_location,
          mental_status_triage: formData.mental_status_triage,
          chief_complaint_raw: formData.chief_complaint_raw,
          chief_complaint_system: null,
          heart_rate: toOptionalNumber(formData.heart_rate),
          respiratory_rate: toOptionalNumber(formData.respiratory_rate),
          spo2: toOptionalNumber(formData.spo2),
          systolic_bp: toOptionalNumber(formData.systolic_bp),
          diastolic_bp: toOptionalNumber(formData.diastolic_bp),
          temperature_c: toOptionalNumber(formData.temperature_c),
          pain_score: toOptionalNumber(formData.pain_score),
          gcs_total: toOptionalNumber(formData.gcs_total),
        },
      };

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(formatApiError(data.detail));
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(buildInitialFormData(fieldOptions));
    setResult(null);
    setError("");
  };

  return {
    fieldOptions,
    formData,
    result,
    loading,
    optionsLoading,
    error,
    severity,
    handleChange,
    handleSubmit,
    handleReset,
  };
}

export { useTriage };
