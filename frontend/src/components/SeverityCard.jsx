import React from "react";
import { MiniStat } from "./UI";

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

export { SeverityCard, EmptyState };
