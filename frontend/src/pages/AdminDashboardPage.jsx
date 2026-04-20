import React, { useMemo, useState } from "react";
import PlatformLayout from "../components/PlatformLayout";
import { adminPatientsByDepartment, departmentStats, doctors } from "../constants/mockData";

function StatTile({ label, value }) {
  return (
    <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/90">{label}</p>
      <p className="font-heading mt-2 text-3xl text-white">{value}</p>
    </div>
  );
}

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState("patients");
  const [selectedDepartment, setSelectedDepartment] = useState("Emergency");

  const totalPatients = useMemo(
    () => departmentStats.reduce((sum, item) => sum + item.patients, 0),
    []
  );

  const survived = 1142;
  const admitted = 706;

  const pieGradient = useMemo(() => {
    const total = totalPatients || 1;
    let offset = 0;
    const slices = departmentStats
      .map((item) => {
        const start = (offset / total) * 100;
        offset += item.patients;
        const end = (offset / total) * 100;
        return `${item.color} ${start}% ${end}%`;
      })
      .join(", ");
    return `conic-gradient(${slices})`;
  }, [totalPatients]);

  return (
    <PlatformLayout>
      <section className="panel-soft panel-glow rounded-3xl border p-6 md:p-8">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">Admin Console</p>
        <h1 className="font-heading mt-3 text-4xl text-white md:text-5xl">Hospital Operations Dashboard</h1>

        <div className="mt-7 grid gap-4 md:grid-cols-4">
          <StatTile label="Total Patients Today" value={totalPatients} />
          <StatTile label="Departments" value={departmentStats.length} />
          <StatTile label="Survived" value={survived} />
          <StatTile label="Admitted" value={admitted} />
        </div>

        <div className="mt-7 flex flex-wrap gap-2">
          <button onClick={() => setActiveTab("patients")} className={`rounded-xl px-4 py-2 text-sm ${activeTab === "patients" ? "bg-cyan-300/20 text-cyan-100 ring-1 ring-cyan-200/30" : "bg-white/5 text-slate-200"}`}>
            Patients by Department
          </button>
          <button onClick={() => setActiveTab("stats")} className={`rounded-xl px-4 py-2 text-sm ${activeTab === "stats" ? "bg-cyan-300/20 text-cyan-100 ring-1 ring-cyan-200/30" : "bg-white/5 text-slate-200"}`}>
            Overall Stats
          </button>
          <button onClick={() => setActiveTab("doctors")} className={`rounded-xl px-4 py-2 text-sm ${activeTab === "doctors" ? "bg-cyan-300/20 text-cyan-100 ring-1 ring-cyan-200/30" : "bg-white/5 text-slate-200"}`}>
            Doctor Management
          </button>
        </div>

        {activeTab === "patients" && (
          <section className="mt-6 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
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
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">{selectedDepartment} Patients</p>
              <div className="mt-3 space-y-2">
                {(adminPatientsByDepartment[selectedDepartment] || []).map((patient) => (
                  <div key={patient.id} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{patient.name}</span>
                      <span className="text-cyan-200">Acuity {patient.acuity}</span>
                    </div>
                    <div className="mt-1 text-xs text-slate-300">{patient.id} • {patient.status}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {activeTab === "stats" && (
          <section className="mt-6 grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
            <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Patients by Department</p>
              <div className="mx-auto mt-6 h-52 w-52 rounded-full ring-8 ring-white/10" style={{ background: pieGradient }} />
            </div>

            <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Department Distribution</p>
              <div className="mt-4 space-y-3">
                {departmentStats.map((item) => {
                  const percent = ((item.patients / totalPatients) * 100).toFixed(1);
                  return (
                    <div key={item.name}>
                      <div className="mb-1 flex items-center justify-between text-sm text-slate-100">
                        <span>{item.name}</span>
                        <span>{item.patients} ({percent}%)</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <div className="h-full rounded-full" style={{ width: `${percent}%`, background: item.color }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {activeTab === "doctors" && (
          <section className="mt-6 rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Doctor Management</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
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
        )}
      </section>
    </PlatformLayout>
  );
}
