import React, { useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/* ═══════════════════════════════════════════════════════════════════════════
   Severity configuration
   ═══════════════════════════════════════════════════════════════════════════ */
const severityConfig = {
  1: {
    label: "Resuscitation",
    sublabel: "Immediate life-saving intervention required",
    chip: "bg-rose-600 text-rose-50",
    card: "border-rose-400/50 bg-rose-950/60 text-rose-100",
    meter: "from-rose-500 to-red-700",
    glow: "shadow-rose-500/30",
    icon: "🔴",
  },
  2: {
    label: "Emergent",
    sublabel: "Time-critical condition — attend within 10 min",
    chip: "bg-orange-600 text-orange-50",
    card: "border-orange-400/50 bg-orange-950/60 text-orange-100",
    meter: "from-orange-400 to-orange-600",
    glow: "shadow-orange-500/30",
    icon: "🟠",
  },
  3: {
    label: "Urgent",
    sublabel: "Significant condition — attend within 30 min",
    chip: "bg-yellow-600 text-yellow-50",
    card: "border-yellow-400/50 bg-yellow-950/60 text-yellow-100",
    meter: "from-yellow-400 to-yellow-600",
    glow: "shadow-yellow-500/25",
    icon: "🟡",
  },
  4: {
    label: "Less Urgent",
    sublabel: "Non-critical — attend within 60 min",
    chip: "bg-lime-600 text-lime-50",
    card: "border-lime-400/50 bg-lime-950/60 text-lime-100",
    meter: "from-lime-400 to-lime-600",
    glow: "shadow-lime-500/20",
    icon: "🟢",
  },
  5: {
    label: "Non-Urgent",
    sublabel: "Minor concern — standard queue",
    chip: "bg-emerald-600 text-emerald-50",
    card: "border-emerald-400/50 bg-emerald-950/60 text-emerald-100",
    meter: "from-emerald-400 to-emerald-700",
    glow: "shadow-emerald-500/20",
    icon: "🟢",
  },
};

/* ═══════════════════════════════════════════════════════════════════════════
   Form defaults — 13 clinical features
   ═══════════════════════════════════════════════════════════════════════════ */
const intakeDefaults = {
  age: "",
  sex: "",
  arrival_mode: "",
  chief_complaint_raw: "",
  heart_rate: "",
  respiratory_rate: "",
  spo2: "",
  systolic_bp: "",
  diastolic_bp: "",
  temperature_c: "",
  pain_score: "",
  gcs_total: "",
  news2_score: "",
};

/* ═══════════════════════════════════════════════════════════════════════════
   Helpers
   ═══════════════════════════════════════════════════════════════════════════ */
function formatApiError(detail) {
  if (!detail) return "Prediction failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail
      .map((item) => (typeof item === "string" ? item : item?.msg || JSON.stringify(item)))
      .join(" | ");
  if (typeof detail === "object") return detail.msg || JSON.stringify(detail);
  return String(detail);
}

/* ═══════════════════════════════════════════════════════════════════════════
   Main App
   ═══════════════════════════════════════════════════════════════════════════ */
export default function App() {
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

  return (
    <main className="app-shell min-h-screen overflow-hidden px-4 py-8 md:px-10 md:py-12">
      <Backdrop />

      <div className="relative z-10 mx-auto w-full max-w-7xl">
        {/* ── Header Hero ─────────────────────────────────────────── */}
        <header className="animate-fade-up mb-8">
          <div className="panel-soft panel-glow rounded-3xl border p-6 md:p-8">
            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-heading text-xs uppercase tracking-[0.25em] text-cyan-200">
                  Triagegeist Clinical AI
                </p>
                <h1 className="font-heading mt-3 text-3xl leading-tight text-white md:text-5xl">
                  Intelligent Triage,
                  <br />
                  <span className="bg-gradient-to-r from-cyan-300 to-teal-300 bg-clip-text text-transparent">
                    Powered by ML
                  </span>
                </h1>
                <p className="mt-3 max-w-xl text-base text-slate-200/90">
                  CatBoost classification enhanced with BioBERT clinical NLP embeddings.
                  Submit a clinical intake form to receive an instant triage severity assessment.
                </p>
              </div>

              <div className="flex shrink-0 gap-3">
                <MetricCard label="Model" value="CatBoost" />
                <MetricCard label="NLP" value="BioBERT" />
                <MetricCard label="Levels" value="1–5" />
              </div>
            </div>
          </div>
        </header>

        {/* ── Two-Column Layout: Form + Result ────────────────────── */}
        <section className="animate-fade-up grid gap-6 lg:grid-cols-[1.15fr_1fr]">
          {/* ── Clinical Form ─────────────────────────────────────── */}
          <section className="panel-soft rounded-3xl border p-6 md:p-8">
            <div className="mb-6 flex items-center justify-between gap-3">
              <div>
                <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">
                  Patient Intake
                </p>
                <h2 className="font-heading mt-1 text-2xl text-white">Clinical Form</h2>
              </div>
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/15 px-3 py-1 text-xs text-cyan-100">
                13 Features
              </span>
            </div>

            <form onSubmit={handleSubmit} className="grid gap-5">
              {/* ── Demographics ───────────────────────────────── */}
              <fieldset className="fieldset-wrapper">
                <legend className="fieldset-legend">Demographics</legend>
                <div className="grid gap-4 sm:grid-cols-3">
                  <InputField
                    label="Age"
                    name="age"
                    type="number"
                    min="0"
                    max="120"
                    placeholder="e.g. 62"
                    value={formData.age}
                    onChange={handleChange}
                    required
                  />
                  <SelectField
                    label="Sex"
                    name="sex"
                    value={formData.sex}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </SelectField>
                  <SelectField
                    label="Arrival Mode"
                    name="arrival_mode"
                    value={formData.arrival_mode}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select</option>
                    <option value="Walk-in">Walk-in</option>
                    <option value="Ambulance">Ambulance</option>
                    <option value="Helicopter">Helicopter</option>
                    <option value="Transferred">Transferred</option>
                    <option value="Other">Other</option>
                  </SelectField>
                </div>
              </fieldset>

              {/* ── Vitals ─────────────────────────────────────── */}
              <fieldset className="fieldset-wrapper">
                <legend className="fieldset-legend">Vital Signs</legend>
                <div className="grid gap-4 sm:grid-cols-3">
                  <InputField
                    label="Heart Rate (bpm)"
                    name="heart_rate"
                    type="number"
                    min="20"
                    max="260"
                    placeholder="e.g. 88"
                    value={formData.heart_rate}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="Respiratory Rate"
                    name="respiratory_rate"
                    type="number"
                    min="0"
                    max="80"
                    placeholder="e.g. 18"
                    value={formData.respiratory_rate}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="SpO₂ (%)"
                    name="spo2"
                    type="number"
                    min="0"
                    max="100"
                    placeholder="e.g. 97"
                    value={formData.spo2}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="Systolic BP"
                    name="systolic_bp"
                    type="number"
                    min="40"
                    max="300"
                    placeholder="e.g. 130"
                    value={formData.systolic_bp}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="Diastolic BP"
                    name="diastolic_bp"
                    type="number"
                    min="20"
                    max="200"
                    placeholder="e.g. 82"
                    value={formData.diastolic_bp}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="Temperature (°C)"
                    name="temperature_c"
                    type="number"
                    step="0.1"
                    min="30"
                    max="45"
                    placeholder="e.g. 37.2"
                    value={formData.temperature_c}
                    onChange={handleChange}
                    required
                  />
                </div>
              </fieldset>

              {/* ── Clinical Scores ────────────────────────────── */}
              <fieldset className="fieldset-wrapper">
                <legend className="fieldset-legend">Clinical Scores</legend>
                <div className="grid gap-4 sm:grid-cols-3">
                  <InputField
                    label="Pain Score (0–10)"
                    name="pain_score"
                    type="number"
                    min="0"
                    max="10"
                    placeholder="e.g. 5"
                    value={formData.pain_score}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="GCS Total (3–15)"
                    name="gcs_total"
                    type="number"
                    min="3"
                    max="15"
                    placeholder="e.g. 15"
                    value={formData.gcs_total}
                    onChange={handleChange}
                    required
                  />
                  <InputField
                    label="NEWS2 Score (0–20)"
                    name="news2_score"
                    type="number"
                    min="0"
                    max="20"
                    placeholder="e.g. 3"
                    value={formData.news2_score}
                    onChange={handleChange}
                    required
                  />
                </div>
              </fieldset>

              {/* ── Chief Complaint ────────────────────────────── */}
              <fieldset className="fieldset-wrapper">
                <legend className="fieldset-legend">Chief Complaint</legend>
                <TextAreaField
                  label="Presenting Complaint (free text)"
                  name="chief_complaint_raw"
                  value={formData.chief_complaint_raw}
                  onChange={handleChange}
                  rows={3}
                  placeholder="e.g. Severe chest pain radiating to left arm, shortness of breath, diaphoresis"
                  required
                />
              </fieldset>

              {/* ── Actions ────────────────────────────────────── */}
              <div className="mt-1 flex gap-3">
                <button type="submit" disabled={loading} className="btn-primary flex-1">
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Spinner /> Analyzing…
                    </span>
                  ) : (
                    "Generate Triage Assessment"
                  )}
                </button>
                <button type="button" onClick={handleReset} className="btn-ghost">
                  Reset
                </button>
              </div>

              {error && (
                <p className="rounded-2xl border border-rose-300/40 bg-rose-400/15 px-4 py-3 text-sm text-rose-100">
                  ⚠ {error}
                </p>
              )}
            </form>
          </section>

          {/* ── Right column: Result Card ─────────────────────────── */}
          <div className="flex flex-col gap-6">
            {result && severity ? (
              <SeverityCard result={result} severity={severity} />
            ) : (
              <EmptyState />
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SeverityCard — the main ML output card
   ═══════════════════════════════════════════════════════════════════════════ */
function SeverityCard({ result, severity }) {
  const level = result.triage_acuity;
  const clamped = Math.max(1, Math.min(5, Number(level)));
  // Invert: level 1 = most urgent = full bar, level 5 = least
  const widthPercent = `${((6 - clamped) / 5) * 100}%`;

  return (
    <section
      className={`animate-fade-up rounded-3xl border border-white/20 bg-slate-900/60 p-6 shadow-2xl backdrop-blur-xl md:p-8 ${severity.glow}`}
    >
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">
            Triage Result
          </p>
          {result.engine === "rule_based_fallback" && (
            <span className="mt-1 inline-block rounded-full border border-amber-400/30 bg-amber-400/15 px-2.5 py-0.5 text-[0.65rem] text-amber-200">
              Rule-Based · ML model not trained yet
            </span>
          )}
          <h3 className="font-heading mt-2 flex items-center gap-3 text-3xl text-white">
            <span className="text-4xl">{severity.icon}</span>
            Level {level}
          </h3>
        </div>
        <span className={`rounded-full px-4 py-1.5 text-sm font-bold ${severity.chip}`}>
          {severity.label}
        </span>
      </div>

      {/* Urgency box */}
      <div className={`mt-5 rounded-2xl border p-5 ${severity.card}`}>
        <p className="text-lg font-semibold">{result.urgency_label}</p>
        <p className="mt-1 text-sm opacity-80">{severity.sublabel}</p>
      </div>

      {/* Serial Number */}
      <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase tracking-[0.16em] text-slate-400">
            Serial Number
          </span>
          <span className="font-heading text-lg font-semibold text-white">
            {result.serial_number}
          </span>
        </div>
      </div>

      {/* Urgency Meter */}
      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.16em] text-slate-300">
          <span>Urgency Scale</span>
          <span>{clamped} / 5</span>
        </div>
        <div className="h-3.5 w-full overflow-hidden rounded-full bg-slate-700/60">
          <div
            className={`h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out ${severity.meter}`}
            style={{ width: widthPercent }}
          />
        </div>
        <div className="mt-1.5 flex justify-between text-[0.65rem] text-slate-500">
          <span>Non-Urgent</span>
          <span>Resuscitation</span>
        </div>
      </div>

      {/* Info grid */}
      <div className="mt-6 grid grid-cols-3 gap-3">
        <MiniStat label="Acuity" value={level} />
        <MiniStat label="Label" value={result.urgency_label} />
        <MiniStat label="Engine" value={result.engine === "ml_pipeline" ? "CatBoost" : "Clinical Rules"} />
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   Empty State placeholder
   ═══════════════════════════════════════════════════════════════════════════ */
function EmptyState() {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-slate-900/30 p-8 text-center backdrop-blur-lg">
      <div className="text-6xl opacity-40">🩺</div>
      <p className="font-heading mt-4 text-xl text-white/60">
        Awaiting Patient Data
      </p>
      <p className="mt-2 max-w-xs text-sm text-slate-400">
        Fill in the clinical intake form and submit to receive an
        AI-powered triage severity assessment.
      </p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   Tiny components
   ═══════════════════════════════════════════════════════════════════════════ */
function MiniStat({ label, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-center">
      <p className="text-[0.65rem] uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="font-heading mt-1 text-base font-semibold text-white">{value}</p>
    </div>
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

function Spinner() {
  return (
    <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
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
      <textarea {...props} className="field-input min-h-20 resize-y" />
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
