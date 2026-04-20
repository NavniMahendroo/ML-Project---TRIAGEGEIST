import React from "react";
import RoleShell from "../components/RoleShell";

const adminLinks = [
  { to: "/admin/patients", label: "Patients by Department" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Doctor Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

function StatCard({ label, value, tone }) {
  return (
    <div className={`rounded-2xl border p-6 ${tone}`}>
      <p className="text-xs uppercase tracking-[0.2em]">{label}</p>
      <p className="font-heading mt-3 text-5xl">{value}</p>
    </div>
  );
}

export default function AdminOutcomesPage() {
  return (
    <RoleShell
      role="Admin Console"
      title="Outcome Stats"
      subtitle="Hospital-level patient outcomes from triage flow decisions."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="grid gap-5 md:grid-cols-2">
        <StatCard label="Survived" value={1142} tone="border-emerald-200/20 bg-emerald-300/10 text-emerald-100" />
        <StatCard label="Admitted" value={706} tone="border-amber-200/20 bg-amber-300/10 text-amber-100" />
      </section>
    </RoleShell>
  );
}
