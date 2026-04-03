import React from "react";

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

export { MiniStat, MetricCard, Spinner, InputField, SelectField, TextAreaField, Backdrop };
