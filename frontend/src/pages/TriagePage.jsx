import React from "react";
import { useTriage } from "../hooks/useTriage";
import { SeverityCard, EmptyState } from "../components/SeverityCard";
import { MetricCard, InputField, SelectField, TextAreaField, Spinner } from "../components/UI";

function TriagePage() {
  const {
    formData,
    result,
    loading,
    error,
    severity,
    handleChange,
    handleSubmit,
    handleReset,
  } = useTriage();

  return (
    <>
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
                  <option value="M">Male</option>
                  <option value="F">Female</option>
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
                  <option value="walk-in">Walk-in</option>
                  <option value="ambulance">Ambulance</option>
                  <option value="helicopter">Helicopter</option>
                  <option value="police">Police</option>
                  <option value="other">Other</option>
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
    </>
  );
}

export default TriagePage;
