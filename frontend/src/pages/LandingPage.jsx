import React from "react";
import { Link } from "react-router-dom";
import PlatformLayout from "../components/PlatformLayout";

const highlights = [
  {
    title: "AI-Assisted Intake",
    detail: "Voice chatbot and structured intake forms work together to reduce queue pressure.",
  },
  {
    title: "Role-Based Experience",
    detail: "Separate workflows for patients, staff, and admins with focused dashboards.",
  },
  {
    title: "Real-Time Visibility",
    detail: "Track department load, triage priorities, and outcomes from one platform.",
  },
];

export default function LandingPage() {
  return (
    <PlatformLayout>
      <section className="panel-soft panel-glow rounded-3xl border px-6 py-10 md:px-10 md:py-14">
        <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="font-heading text-xs uppercase tracking-[0.26em] text-cyan-200/90">Smart Emergency Triage</p>
            <h1 className="font-heading mt-4 text-4xl leading-tight text-white md:text-6xl">
              Welcome to
              <span className="ml-3 bg-gradient-to-r from-cyan-200 via-teal-200 to-emerald-200 bg-clip-text text-transparent">
                TriageGeist
              </span>
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-200/90 md:text-lg">
              TriageGeist is a hospital intake and prioritization platform that helps classify patient urgency,
              streamline care workflows, and give decision-makers clear operational insights.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/patient/form" className="btn-primary no-underline">
                Patient Form
              </Link>
              <Link
                to="/patient/chatbot"
                className="rounded-2xl border border-white/25 bg-white/10 px-5 py-3 text-sm font-semibold text-white no-underline transition hover:bg-white/20"
              >
                Chatbot Triage
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-cyan-100/20 bg-slate-950/45 p-6">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Platform Goals</p>
            <ul className="mt-4 space-y-3 text-sm text-slate-200/90">
              <li>Faster patient routing to correct departments.</li>
              <li>Reduced registration friction in emergencies.</li>
              <li>Better accountability for staffing and outcomes.</li>
            </ul>
            <div className="mt-6 h-2 rounded-full bg-white/10">
              <div className="h-full w-4/5 rounded-full bg-gradient-to-r from-cyan-300 via-teal-300 to-emerald-300" />
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-5 md:grid-cols-3">
        {highlights.map((item) => (
          <article key={item.title} className="panel-soft rounded-2xl border p-5">
            <h2 className="font-heading text-xl text-white">{item.title}</h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-200/85">{item.detail}</p>
          </article>
        ))}
      </section>
    </PlatformLayout>
  );
}
