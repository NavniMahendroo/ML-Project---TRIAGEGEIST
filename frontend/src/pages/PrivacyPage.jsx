import React from "react";
import PlatformLayout from "../components/PlatformLayout";

const points = [
  "Patient information is collected only for triage, treatment, and operational care workflows.",
  "Role-based access controls ensure staff members only see department-relevant data.",
  "Clinical records are encrypted in transit and protected in storage by hospital security policies.",
  "Voice-chat transcripts are used for triage review and quality improvement under medical supervision.",
  "Administrative dashboards display aggregate trends and are not intended for unauthorized data export.",
];

export default function PrivacyPage() {
  return (
    <PlatformLayout>
      <section className="panel-soft panel-glow rounded-3xl border p-7 md:p-10">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">Privacy & Data Use</p>
        <h1 className="font-heading mt-4 text-4xl text-white md:text-5xl">Your Information Matters</h1>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-slate-200/90 md:text-base">
          TriageGeist is designed for clinical triage support. We apply strict handling of patient data and make
          sure access is limited to authorized hospital personnel.
        </p>

        <div className="mt-8 space-y-4">
          {points.map((point) => (
            <div key={point} className="rounded-2xl border border-cyan-100/15 bg-slate-950/30 px-4 py-3 text-sm text-slate-100/90">
              {point}
            </div>
          ))}
        </div>
      </section>
    </PlatformLayout>
  );
}
