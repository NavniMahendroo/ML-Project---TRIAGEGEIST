import React, { useMemo } from "react";
import RoleShell from "../../components/RoleShell";
import { departmentStats } from "../../constants/mockData";

const adminLinks = [
  { to: "/admin/patients", label: "Patients by Department" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Staff Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

export default function DoctorStatsPage() {
  const totalPatients = useMemo(() => departmentStats.reduce((sum, item) => sum + item.patients, 0), []);

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
    <RoleShell
      role="Admin Console"
      title="Overall Stats Graph"
      subtitle="Real-time visual distribution of current patient traffic."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
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
    </RoleShell>
  );
}
