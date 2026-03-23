import React, { useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const severityConfig = {
  1: {
    label: "Immediate",
    chip: "bg-rose-600 text-rose-50",
    card: "border-rose-300 bg-rose-50/90 text-rose-900",
    meter: "from-rose-500 to-red-700",
  },
  2: {
    label: "Very Urgent",
    chip: "bg-amber-600 text-amber-50",
    card: "border-amber-300 bg-amber-50/90 text-amber-900",
    meter: "from-amber-400 to-orange-600",
  },
  3: {
    label: "Urgent",
    chip: "bg-yellow-600 text-yellow-50",
    card: "border-yellow-300 bg-yellow-50/90 text-yellow-900",
    meter: "from-yellow-400 to-yellow-600",
  },
  4: {
    label: "Standard",
    chip: "bg-lime-600 text-lime-50",
    card: "border-lime-300 bg-lime-50/90 text-lime-900",
    meter: "from-lime-400 to-lime-600",
  },
  5: {
    label: "Non-Urgent",
    chip: "bg-emerald-600 text-emerald-50",
    card: "border-emerald-300 bg-emerald-50/90 text-emerald-900",
    meter: "from-emerald-400 to-emerald-700",
  },
};

const intakeDefaults = {
  age: "",
  gender: "",
  systolic_bp: "",
  diastolic_bp: "",
  heart_rate: "",
  temperature: "",
  chief_complaint: "",
};

function formatApiError(detail) {
  if (!detail) {
    return "Prediction failed";
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item?.msg) {
          return item.msg;
        }
        return JSON.stringify(item);
      })
      .join(" | ");
  }

  if (typeof detail === "object") {
    if (detail.msg) {
      return detail.msg;
    }
    return JSON.stringify(detail);
  }

  return String(detail);
}

export default function App() {
  const [formData, setFormData] = useState(intakeDefaults);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const severity = useMemo(() => {
    if (!result?.prediction) {
      return null;
    }
    return severityConfig[result.prediction] || severityConfig[3];
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
      const payload = {
        age: Number(formData.age),
        gender: formData.gender,
        systolic_bp: Number(formData.systolic_bp),
        diastolic_bp: Number(formData.diastolic_bp),
        heart_rate: Number(formData.heart_rate),
        temperature: Number(formData.temperature),
        chief_complaint: formData.chief_complaint,
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

  return (
    <main className="app-shell min-h-screen overflow-hidden px-4 py-8 md:px-10 md:py-12">
      <Backdrop />

      <div className="relative z-10 mx-auto w-full max-w-6xl">
        <section className="animate-fade-up grid gap-6 lg:grid-cols-[1.05fr_1fr]">
          <aside className="panel-soft panel-glow rounded-3xl border p-6 md:p-8">
            <p className="font-heading text-xs uppercase tracking-[0.25em] text-cyan-200">
              Triagegeist Clinical AI
            </p>
            <h1 className="font-heading mt-4 text-4xl leading-tight text-white md:text-5xl">
              Intelligent Intake,
              <br />
              Human-Centered Triage
            </h1>
            <p className="mt-4 max-w-xl text-base text-slate-200/90">
              Capture patient vitals, evaluate symptom urgency, and return a standardized severity level
              with an auto-generated serial number.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <MetricCard label="Realtime" value="~1.2s" />
              <MetricCard label="Levels" value="1-5" />
              <MetricCard label="Mode" value="Live API" />
            </div>
          </aside>

          <section className="panel-soft rounded-3xl border p-6 md:p-8">
            <div className="mb-6 flex items-center justify-between gap-3">
              <div>
                <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">Patient Intake</p>
                <h2 className="font-heading mt-1 text-2xl text-white">Clinical Form</h2>
              </div>
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/15 px-3 py-1 text-xs text-cyan-100">
                Tailwind + React
              </span>
            </div>

            <form onSubmit={handleSubmit} className="grid gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Age" name="age" type="number" value={formData.age} onChange={handleChange} required />

                <SelectField label="Gender" name="gender" value={formData.gender} onChange={handleChange} required>
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </SelectField>

                <InputField
                  label="Systolic BP"
                  name="systolic_bp"
                  type="number"
                  value={formData.systolic_bp}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Diastolic BP"
                  name="diastolic_bp"
                  type="number"
                  value={formData.diastolic_bp}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Heart Rate"
                  name="heart_rate"
                  type="number"
                  value={formData.heart_rate}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Temperature (C)"
                  name="temperature"
                  type="number"
                  step="0.1"
                  value={formData.temperature}
                  onChange={handleChange}
                  required
                />
              </div>

              <TextAreaField
                label="Chief Complaint"
                name="chief_complaint"
                value={formData.chief_complaint}
                onChange={handleChange}
                rows={4}
                placeholder="Describe presenting symptoms and concerns"
                required
              />

              <button type="submit" disabled={loading} className="btn-primary mt-2">
                {loading ? "Assessing Patient..." : "Generate Triage Assessment"}
              </button>

              {error && (
                <p className="rounded-2xl border border-rose-300/40 bg-rose-400/15 px-4 py-3 text-sm text-rose-100">
                  {error}
                </p>
              )}
            </form>
          </section>
        </section>

        {result && severity && <SeverityCard result={result} severity={severity} />}
      </div>
    </main>
  );
}

function SeverityCard({ result, severity }) {
  const clamped = Math.max(1, Math.min(5, Number(result.prediction)));
  const widthPercent = `${(clamped / 5) * 100}%`;

  return (
    <section className="animate-fade-up mt-6 rounded-3xl border border-white/20 bg-slate-900/60 p-6 shadow-2xl shadow-cyan-900/30 backdrop-blur-xl md:p-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">Severity Card</p>
          <h3 className="font-heading mt-2 text-3xl text-white">Level {result.prediction}</h3>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${severity.chip}`}>{severity.label}</span>
      </div>

      <div className={`mt-4 rounded-2xl border p-4 ${severity.card}`}>
        <p className="text-sm font-semibold">Serial Number: {result.serial_number}</p>
      </div>

      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.16em] text-slate-300">
          <span>Triage Scale</span>
          <span>{clamped} / 5</span>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-700/60">
          <div className={`h-full rounded-full bg-gradient-to-r ${severity.meter}`} style={{ width: widthPercent }} />
        </div>
      </div>
    </section>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan-100/80">{label}</p>
      <p className="font-heading mt-2 text-2xl text-white">{value}</p>
    </div>
  );
}

function InputField({ label, ...props }) {
  return (
    <label className="field-block">
      <span className="field-label">{label}</span>
      <input {...props} className="field-input" />
    </label>
  );
}

function SelectField({ label, children, ...props }) {
  return (
    <label className="field-block">
      <span className="field-label">{label}</span>
      <select {...props} className="field-input">
        {children}
      </select>
    </label>
  );
}

function TextAreaField({ label, ...props }) {
  return (
    <label className="field-block">
      <span className="field-label">{label}</span>
      <textarea {...props} className="field-input min-h-24 resize-y" />
    </label>
  );
}

function Backdrop() {
  return (
    <>
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />
      <div className="orb orb-three" aria-hidden="true" />
      <div className="scan-grid" aria-hidden="true" />
    </>
  );
}
