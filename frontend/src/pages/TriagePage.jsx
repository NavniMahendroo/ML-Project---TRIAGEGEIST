import React from "react";
import { useTriage } from "../hooks/useTriage";
import { SeverityCard, EmptyState } from "../components/SeverityCard";
import { MetricCard, InputField, SelectField, TextAreaField, Spinner } from "../components/UI";

function renderOptions(options = []) {
  return options.map((option) => (
    <option key={option.value} value={option.value}>
      {option.label}
    </option>
  ));
}

function TriagePage() {
  const {
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
  } = useTriage();

  return (
    <>
      <header className="animate-fade-up mb-8">
        <div className="panel-soft panel-glow rounded-3xl border p-6 md:p-8">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="font-heading text-xs uppercase tracking-[0.25em] text-cyan-200">
                Triagegeist Phase 1-3
              </p>
              <h1 className="font-heading mt-3 text-3xl leading-tight text-white md:text-5xl">
                New Patient Registration
                <br />
                <span className="bg-gradient-to-r from-cyan-300 to-teal-300 bg-clip-text text-transparent">
                  and Triage Workflow
                </span>
              </h1>
              <p className="mt-3 max-w-2xl text-base text-slate-200/90">
                This flow creates normalized patient and visit records, reconstructs the v1.0.2
                feature payload, and returns a backend-labeled urgency result for display.
              </p>
            </div>

            <div className="flex shrink-0 gap-3">
              <MetricCard label="Model" value="CatBoost v1.0.2" />
              <MetricCard label="Payload" value="61 Features" />
              <MetricCard label="Scope" value="Phase 1-3" />
            </div>
          </div>
        </div>
      </header>

      <section className="animate-fade-up grid gap-6 lg:grid-cols-[1.2fr_0.95fr]">
        <section className="panel-soft rounded-3xl border p-6 md:p-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">
                Intake Workflow
              </p>
              <h2 className="font-heading mt-1 text-2xl text-white">New Patient Form</h2>
            </div>
            <span className="rounded-full border border-cyan-300/30 bg-cyan-300/15 px-3 py-1 text-xs text-cyan-100">
              Patient + Visit Submission
            </span>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-5">
            <fieldset className="fieldset-wrapper">
              <legend className="fieldset-legend">Workflow Context</legend>
              <div className="mb-4 rounded-2xl border border-cyan-300/15 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-50/90">
                Site and submitting actor are stored with the visit. Missing numeric measurements can stay
                blank and will continue through reconstruction as missing values for CatBoost.
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField
                  label="Site"
                  name="site_id"
                  value={formData.site_id}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.site_id)}
                </SelectField>
                <SelectField
                  label="Submitted By"
                  name="nurse_id"
                  value={formData.nurse_id}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.nurse_id)}
                </SelectField>
              </div>
            </fieldset>

            <fieldset className="fieldset-wrapper">
              <legend className="fieldset-legend">Patient Master Data</legend>
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField
                  label="Patient Name"
                  name="name"
                  type="text"
                  placeholder="e.g. Aisha Khan"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Age"
                  name="age"
                  type="number"
                  min="0"
                  max="120"
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
                  {renderOptions(fieldOptions.sex)}
                </SelectField>
                <SelectField
                  label="Language"
                  name="language"
                  value={formData.language}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.language)}
                </SelectField>
                <SelectField
                  label="Insurance Type"
                  name="insurance_type"
                  value={formData.insurance_type}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.insurance_type)}
                </SelectField>
                <InputField
                  label="Active Medications"
                  name="num_active_medications"
                  type="number"
                  min="0"
                  max="20"
                  value={formData.num_active_medications}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Comorbidities"
                  name="num_comorbidities"
                  type="number"
                  min="0"
                  max="20"
                  value={formData.num_comorbidities}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Weight (kg)"
                  name="weight_kg"
                  type="number"
                  step="0.1"
                  min="2"
                  max="200"
                  value={formData.weight_kg}
                  onChange={handleChange}
                  required
                />
                <InputField
                  label="Height (cm)"
                  name="height_cm"
                  type="number"
                  step="0.1"
                  min="45"
                  max="250"
                  value={formData.height_cm}
                  onChange={handleChange}
                  required
                />
              </div>
            </fieldset>

            <fieldset className="fieldset-wrapper">
              <legend className="fieldset-legend">Visit Presentation</legend>
              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField
                  label="Arrival Mode"
                  name="arrival_mode"
                  value={formData.arrival_mode}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.arrival_mode)}
                </SelectField>
                <SelectField
                  label="Transport Origin"
                  name="transport_origin"
                  value={formData.transport_origin}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.transport_origin)}
                </SelectField>
                <SelectField
                  label="Pain Location"
                  name="pain_location"
                  value={formData.pain_location}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.pain_location)}
                </SelectField>
                <SelectField
                  label="Mental Status"
                  name="mental_status_triage"
                  value={formData.mental_status_triage}
                  onChange={handleChange}
                  required
                >
                  {renderOptions(fieldOptions.mental_status_triage)}
                </SelectField>
              </div>
              <div className="mt-4">
                <TextAreaField
                  label="Chief Complaint"
                  name="chief_complaint_raw"
                  value={formData.chief_complaint_raw}
                  onChange={handleChange}
                  rows={3}
                  placeholder="e.g. Severe chest pain radiating to the left arm with shortness of breath"
                  required
                />
              </div>
            </fieldset>

            <fieldset className="fieldset-wrapper">
              <legend className="fieldset-legend">Vitals and Scores</legend>
              <div className="mb-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
                Leave a field blank only when the measurement is unavailable at intake. The backend will
                calculate derived vitals when possible and otherwise preserve missing numeric values.
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <InputField
                  label="Heart Rate"
                  name="heart_rate"
                  type="number"
                  min="20"
                  max="260"
                  value={formData.heart_rate}
                  onChange={handleChange}
                />
                <InputField
                  label="Respiratory Rate"
                  name="respiratory_rate"
                  type="number"
                  min="0"
                  max="80"
                  value={formData.respiratory_rate}
                  onChange={handleChange}
                />
                <InputField
                  label="SpO₂ (%)"
                  name="spo2"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.spo2}
                  onChange={handleChange}
                />
                <InputField
                  label="Systolic BP"
                  name="systolic_bp"
                  type="number"
                  min="40"
                  max="300"
                  value={formData.systolic_bp}
                  onChange={handleChange}
                />
                <InputField
                  label="Diastolic BP"
                  name="diastolic_bp"
                  type="number"
                  min="20"
                  max="200"
                  value={formData.diastolic_bp}
                  onChange={handleChange}
                />
                <InputField
                  label="Temperature (°C)"
                  name="temperature_c"
                  type="number"
                  step="0.1"
                  min="30"
                  max="45"
                  value={formData.temperature_c}
                  onChange={handleChange}
                />
                <InputField
                  label="Pain Score"
                  name="pain_score"
                  type="number"
                  min="0"
                  max="10"
                  value={formData.pain_score}
                  onChange={handleChange}
                />
                <InputField
                  label="GCS Total"
                  name="gcs_total"
                  type="number"
                  min="3"
                  max="15"
                  value={formData.gcs_total}
                  onChange={handleChange}
                />
              </div>
            </fieldset>

            <div className="mt-1 flex flex-wrap gap-3">
              <button type="submit" disabled={loading || optionsLoading} className="btn-primary flex-1">
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Spinner /> Running v1.0.2…
                  </span>
                ) : optionsLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Spinner /> Loading Intake Options…
                  </span>
                ) : (
                  "Create Patient and Predict Triage"
                )}
              </button>
              <button type="button" onClick={handleReset} className="btn-ghost">
                Reset
              </button>
            </div>

            {error && (
              <p className="rounded-2xl border border-rose-300/40 bg-rose-400/15 px-4 py-3 text-sm text-rose-100">
                {error}
              </p>
            )}
          </form>
        </section>

        <div className="flex flex-col gap-6">
          <section className="panel-soft rounded-3xl border p-6">
            <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">
              Verification Notes
            </p>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>Creates a normalized `patients` document and a new `visits` document.</li>
              <li>Uses `patient_history` only when it already exists for that patient.</li>
              <li>Reconstructs the Phase 2 pre-PCA payload before calling CatBoost v1.0.2.</li>
              <li>Lets the backend derive `urgency_label` from the returned `triage_acuity`.</li>
            </ul>
          </section>

          {result && severity ? <SeverityCard result={result} severity={severity} /> : <EmptyState />}
        </div>
      </section>
    </>
  );
}

export default TriagePage;
