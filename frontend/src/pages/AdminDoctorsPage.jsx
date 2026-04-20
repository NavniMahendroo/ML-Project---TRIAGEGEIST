import React from "react";
import RoleShell from "../components/RoleShell";
import { doctors } from "../constants/mockData";

const adminLinks = [
  { to: "/admin/patients", label: "Patients by Department" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Doctor Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

export default function AdminDoctorsPage() {
  return (
    <RoleShell
      role="Admin Console"
      title="Doctor Management"
      subtitle="Track doctor assignment and duty status across departments."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
        <div className="grid gap-3 md:grid-cols-2">
          {doctors.map((doctor) => (
            <article key={doctor.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm font-semibold text-white">{doctor.name}</p>
              <p className="mt-1 text-xs text-slate-300">{doctor.id} • {doctor.department}</p>
              <p className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs ${doctor.onDuty ? "bg-emerald-400/20 text-emerald-100" : "bg-amber-400/20 text-amber-100"}`}>
                {doctor.onDuty ? "On Duty" : "Off Duty"}
              </p>
            </article>
          ))}
        </div>
      </section>
    </RoleShell>
  );
}
