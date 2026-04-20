import React from "react";
import { MiniStat } from "./UI";

function SeverityCard({ result, severity }) {
  const level = result.triage_acuity;
  const clamped = Math.max(1, Math.min(5, Number(level)));
  const widthPercent = `${((6 - clamped) / 5) * 100}%`;
  const engineLabel = result.engine === "ml_pipeline" ? "CatBoost v1.0.2" : result.engine;

  return (
    <section
      className={`animate-fade-up rounded-3xl border border-white/20 bg-slate-900/60 p-6 shadow-2xl backdrop-blur-xl md:p-8 ${severity.glow}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-heading text-sm uppercase tracking-[0.2em] text-cyan-200">
            Triage Result
          </p>
          <h3 className="font-heading mt-2 flex items-center gap-3 text-3xl text-white">
            <span className="text-4xl">{severity.icon}</span>
            Level {level}
          </h3>
        </div>
        <span className={`rounded-full px-4 py-1.5 text-sm font-bold ${severity.chip}`}>
          {severity.label}
        </span>
      </div>

      <div className={`mt-5 rounded-2xl border p-5 ${severity.card}`}>
        <p className="text-lg font-semibold">{result.urgency_label}</p>
        <p className="mt-1 text-sm opacity-80">{severity.sublabel}</p>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <span className="text-xs uppercase tracking-[0.16em] text-slate-400">Patient ID</span>
          <div className="font-heading mt-1 text-lg font-semibold text-white">{result.patient_id}</div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <span className="text-xs uppercase tracking-[0.16em] text-slate-400">Visit ID</span>
          <div className="font-heading mt-1 text-lg font-semibold text-white">{result.visit_id}</div>
        </div>
      </div>

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

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className={`rounded-2xl border border-cyan-300/20 bg-cyan-400/10 p-4 ${result.chief_complaint_system ? "" : "opacity-80"}`}>
          <p className="text-xs uppercase tracking-[0.16em] text-cyan-100/70">Chief Complaint System</p>
          <p className="mt-1 text-sm text-cyan-50">
            {result.chief_complaint_system || "Pending future classifier"}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Routed Specialty</p>
          <p className="mt-1 text-sm text-white">{result.target_specialty || "Emergency"}</p>
          <p className="mt-2 text-xs text-slate-400">
            Assigned Doctor: {result.assigned_doctor_id || "Awaiting doctor allocation"}
          </p>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3">
        <MiniStat label="Acuity" value={level} />
        <MiniStat label="Label" value={result.urgency_label} />
        <MiniStat label="Engine" value={engineLabel} />
      </div>
    </section>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-slate-900/30 p-8 text-center backdrop-blur-lg">
      <div className="text-6xl opacity-40">🩺</div>
      <p className="font-heading mt-4 text-xl text-white/60">Awaiting New Patient Intake</p>
      <p className="mt-2 max-w-xs text-sm text-slate-400">
        Submit the registration and visit form to create the patient record,
        store the visit, and receive a v1.0.2 triage prediction.
      </p>
    </div>
  );
}

export { SeverityCard, EmptyState };
