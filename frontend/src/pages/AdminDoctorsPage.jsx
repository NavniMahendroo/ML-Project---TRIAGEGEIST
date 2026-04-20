import React, { useEffect, useState } from "react";
import RoleShell from "../components/RoleShell";
import { api } from "../lib/api";

const adminLinks = [
  { to: "/admin/patients", label: "Assigned Patients" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Doctor Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

export default function AdminDoctorsPage() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    async function loadDoctors() {
      try {
        setLoading(true);
        const response = await api.listDoctors();
        if (!isActive) return;
        setDoctors(response.items || []);
      } catch (err) {
        if (isActive) {
          setError(err.message || "Unable to load doctors.");
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadDoctors();
    return () => {
      isActive = false;
    };
  }, []);

  return (
    <RoleShell
      role="Admin Console"
      title="Doctor Management"
      subtitle="Track doctor specialties, on-duty coverage, and routing readiness across departments."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
        {loading ? <p className="text-sm text-slate-300">Loading doctors...</p> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
        {!loading && !error ? (
          <div className="grid gap-3 md:grid-cols-2">
            {doctors.map((doctor) => (
              <article key={doctor.doctor_id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-white">{doctor.name}</p>
                    <p className="mt-1 text-xs text-slate-300">{doctor.doctor_id} • {doctor.specialty}</p>
                  </div>
                  <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-[11px] text-cyan-100">
                    {doctor.role}
                  </span>
                </div>
                <p className={`mt-3 inline-flex rounded-full px-3 py-1 text-xs ${doctor.on_duty ? "bg-emerald-400/20 text-emerald-100" : "bg-amber-400/20 text-amber-100"}`}>
                  {doctor.on_duty ? "On Duty" : "Off Duty"}
                </p>
              </article>
            ))}
            {doctors.length === 0 ? <p className="text-sm text-slate-300">No doctors found.</p> : null}
          </div>
        ) : null}
      </section>
    </RoleShell>
  );
}
