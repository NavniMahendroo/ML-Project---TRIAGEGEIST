import React from "react";
import { Link } from "react-router-dom";
import PlatformLayout from "../components/PlatformLayout";

const cards = [
  {
    title: "Voice Chatbot Triage",
    detail: "Use the speech-to-text chatbot for guided intake and urgency prediction.",
    to: "/patient/chatbot",
    cta: "Open Chatbot",
  },
  {
    title: "Manual Patient Form",
    detail: "Fill the complete form manually if voice mode is unavailable or preferred.",
    to: "/patient/form",
    cta: "Open Patient Form",
  },
];

export default function PatientHubPage() {
  return (
    <PlatformLayout>
      <section className="panel-soft panel-glow rounded-3xl border p-7 md:p-10">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">Patient Portal</p>
        <h1 className="font-heading mt-3 text-4xl text-white md:text-5xl">Choose Your Intake Method</h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-200/90 md:text-base">
          Start your triage journey with either the chatbot or the manual registration form.
        </p>

        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {cards.map((card) => (
            <article key={card.title} className="rounded-2xl border border-cyan-100/20 bg-slate-950/40 p-6">
              <h2 className="font-heading text-2xl text-white">{card.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-slate-200/85">{card.detail}</p>
              <Link to={card.to} className="btn-primary mt-5 inline-flex no-underline">
                {card.cta}
              </Link>
            </article>
          ))}
        </div>
      </section>
    </PlatformLayout>
  );
}
