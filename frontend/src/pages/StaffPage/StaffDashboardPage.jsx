import React from "react";
import RoleShell from "../../components/RoleShell";
import { staffPatients, staffTasks } from "../../constants/mockData";

const staffLinks = [
  { to: "/staff", label: "Dashboard" },
  { to: "/staff/tasks", label: "Tasks" },
  { to: "/staff/settings", label: "Settings" },
  { to: "/staff/logout", label: "Logout" },
];

function StatTile({ label, value }) {
  return (
    <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/90">{label}</p>
      <p className="font-heading mt-2 text-3xl text-white">{value}</p>
    </div>
  );
}

export default function StaffDashboardPage() {
  const taskTypeCounts = staffTasks.completed.reduce((acc, task) => {
    const key = task.type || "Other";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const taskTypeEntries = Object.entries(taskTypeCounts).map(([type, count], index) => ({
    type,
    count,
    color: ["#22d3ee", "#34d399", "#f59e0b", "#a78bfa", "#f87171"][index % 5],
  }));
  const totalCompleted = taskTypeEntries.reduce((sum, entry) => sum + entry.count, 0) || 1;

  let offset = 0;
  const pieGradient = `conic-gradient(${taskTypeEntries
    .map((entry) => {
      const start = (offset / totalCompleted) * 100;
      offset += entry.count;
      const end = (offset / totalCompleted) * 100;
      return `${entry.color} ${start}% ${end}%`;
    })
    .join(", ")})`;

  return (
    <RoleShell
      role="Staff Workspace"
      title="Department Overview"
      subtitle="Patients, outcomes, and task completion insights for your shift."
      links={staffLinks}
      showGlobalHeader={false}
    >
      <section>

        <div className="mt-7 grid gap-4 md:grid-cols-3">
          <StatTile label="Patients In Dept" value={staffPatients.length} />
          <StatTile label="Survived" value={342} />
          <StatTile label="Admitted" value={198} />
        </div>

        <section className="mt-7 grid gap-5 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Completed Task Types</p>
            <div className="mt-4 grid items-center gap-5 md:grid-cols-[0.8fr_1.2fr]">
              <div className="mx-auto h-48 w-48 rounded-full ring-8 ring-white/10" style={{ background: pieGradient }} />

              <div className="space-y-2">
                {taskTypeEntries.map((entry) => {
                  const percent = ((entry.count / totalCompleted) * 100).toFixed(1);
                  return (
                    <div key={entry.type} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="h-2.5 w-2.5 rounded-full" style={{ background: entry.color }} />
                          <span>{entry.type}</span>
                        </div>
                        <span>{entry.count} ({percent}%)</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Patients Under Your Department</p>
            <div className="mt-4 space-y-2">
              {staffPatients.map((patient) => (
                <article key={patient.id} className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{patient.name}</span>
                    <span className="text-cyan-200">Acuity {patient.acuity}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-300">{patient.id} • Bed {patient.bed} • {patient.state}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </section>
    </RoleShell>
  );
}
