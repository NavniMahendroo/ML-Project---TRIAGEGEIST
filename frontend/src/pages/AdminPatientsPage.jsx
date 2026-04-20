import React, { useState } from "react";
import RoleShell from "../components/RoleShell";
import { adminPatientsByDepartment } from "../constants/mockData";

const adminLinks = [
  { to: "/admin/patients", label: "Patients by Department" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Doctor Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

function DashboardStat({ label, value, tone }) {
  return (
    <article className={`rounded-2xl border p-4 ${tone}`}>
      <p className="text-xs uppercase tracking-[0.2em]">{label}</p>
      <p className="font-heading mt-2 text-3xl">{value}</p>
    </article>
  );
}

export default function AdminPatientsPage() {
  const [selectedDepartment, setSelectedDepartment] = useState("Emergency");
  const selectedPatients = adminPatientsByDepartment[selectedDepartment] || [];
  const admittedCount = selectedPatients.filter((patient) => patient.status === "Admitted").length;
  const observationCount = selectedPatients.filter((patient) => patient.status === "Observation").length;
  const criticalCount = selectedPatients.filter((patient) => patient.acuity <= 2).length;

  return (
    <RoleShell
      role="Admin Console"
      title="Patients by Department"
      subtitle="Monitor patient load, urgency distribution, and admission pressure by hospital unit."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="mb-5 grid gap-4 md:grid-cols-4">
        <DashboardStat label="Department" value={selectedDepartment} tone="border-cyan-200/20 bg-cyan-300/10 text-cyan-50" />
        <DashboardStat label="Total Patients" value={selectedPatients.length} tone="border-blue-200/20 bg-blue-300/10 text-blue-50" />
        <DashboardStat label="Critical (Acuity 1-2)" value={criticalCount} tone="border-rose-200/20 bg-rose-300/10 text-rose-50" />
        <DashboardStat label="Admitted" value={admittedCount} tone="border-emerald-200/20 bg-emerald-300/10 text-emerald-50" />
      </section>

      <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Departments</p>
          <div className="mt-3 space-y-2">
            {Object.keys(adminPatientsByDepartment).map((dept) => (
              <button
                key={dept}
                onClick={() => setSelectedDepartment(dept)}
                className={`w-full rounded-xl px-3 py-2 text-left text-sm ${selectedDepartment === dept ? "bg-cyan-300/20 text-cyan-50" : "bg-white/5 text-slate-200"}`}
              >
                {dept}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">{selectedDepartment} Patients</p>
            <span className="rounded-full border border-amber-200/25 bg-amber-300/10 px-3 py-1 text-xs text-amber-100">
              Observation: {observationCount}
            </span>
          </div>
          <div className="mt-3 space-y-2">
            {selectedPatients.map((patient) => (
              <div key={patient.id} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100">
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{patient.name}</span>
                  <span className={`${patient.acuity <= 2 ? "text-rose-200" : "text-cyan-200"}`}>Acuity {patient.acuity}</span>
                </div>
                <div className="mt-1 text-xs text-slate-300">{patient.id} • {patient.status}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </RoleShell>
  );
}
