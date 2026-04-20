import React, { useEffect, useMemo, useState } from "react";
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

function DashboardStat({ label, value, tone }) {
  return (
    <article className={`rounded-2xl border p-4 ${tone}`}>
      <p className="text-xs uppercase tracking-[0.2em]">{label}</p>
      <p className="font-heading mt-2 text-3xl">{value}</p>
    </article>
  );
}

function formatTimestamp(value) {
  if (!value) return "Not yet attended";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function AdminPatientsPage() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [pendingVisitId, setPendingVisitId] = useState(null);
  const [dutyUpdating, setDutyUpdating] = useState(false);

  const auth = useMemo(() => {
    try {
      const raw = localStorage.getItem("adminAuth");
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }, []);

  const doctorId = auth?.doctor_id || null;
  const doctorName = auth?.name || "Doctor";
  const [onDuty, setOnDuty] = useState(Boolean(auth?.on_duty ?? true));

  useEffect(() => {
    let isActive = true;

    async function loadAssignedPatients() {
      if (!doctorId) {
        setLoading(false);
        setError("Doctor session not found.");
        return;
      }

      try {
        setLoading(true);
        const response = await api.listDoctorPatients(doctorId);
        if (!isActive) return;
        setPatients(response.items || []);
      } catch (err) {
        if (isActive) {
          setError(err.message || "Unable to load assigned patients.");
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadAssignedPatients();
    return () => {
      isActive = false;
    };
  }, [doctorId]);

  const attendedCount = patients.filter((patient) => patient.attended_by_doctor).length;
  const unattendedCount = patients.length - attendedCount;
  const criticalCount = patients.filter((patient) => patient.triage_acuity <= 2).length;

  const markAttended = async (visitId) => {
    if (!doctorId) return;

    try {
      setPendingVisitId(visitId);
      setActionError("");
      const updated = await api.markDoctorPatientAttended(doctorId, visitId);
      setPatients((prev) => prev.map((patient) => (
        patient.visit_id === visitId
          ? {
              ...patient,
              attended_by_doctor: updated.attended_by_doctor,
              attended_at: updated.attended_at,
              attended_by_doctor_id: updated.attended_by_doctor_id,
            }
          : patient
      )));
    } catch (err) {
      setActionError(err.message || "Unable to mark patient as attended.");
    } finally {
      setPendingVisitId(null);
    }
  };

  const toggleDuty = async () => {
    if (!doctorId) return;

    try {
      setDutyUpdating(true);
      setActionError("");
      const updated = await api.updateDoctorDuty(doctorId, !onDuty);
      setOnDuty(updated.on_duty);
      localStorage.setItem(
        "adminAuth",
        JSON.stringify({
          ...(auth || {}),
          doctor_id: updated.doctor_id,
          name: updated.name,
          role: updated.role,
          specialty: updated.specialty,
          on_duty: updated.on_duty,
          logged_in_at: auth?.logged_in_at || new Date().toISOString(),
        }),
      );
    } catch (err) {
      setActionError(err.message || "Unable to update duty status.");
    } finally {
      setDutyUpdating(false);
    }
  };

  return (
    <RoleShell
      role="Admin Console"
      title="Assigned Patients"
      subtitle="Review your routed patients, track urgency, and mark when you have attended them."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="mb-5 grid gap-4 md:grid-cols-4">
        <DashboardStat label="Assigned" value={patients.length} tone="border-cyan-200/20 bg-cyan-300/10 text-cyan-50" />
        <DashboardStat label="Awaiting Attendance" value={unattendedCount} tone="border-amber-200/20 bg-amber-300/10 text-amber-50" />
        <DashboardStat label="Attended" value={attendedCount} tone="border-emerald-200/20 bg-emerald-300/10 text-emerald-50" />
        <DashboardStat label="Critical" value={criticalCount} tone="border-rose-200/20 bg-rose-300/10 text-rose-50" />
      </section>

      <section className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Doctor Queue</p>
          <div className="flex flex-wrap items-center gap-2">
            {doctorId ? <span className="rounded-full border border-cyan-300/25 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-100">{doctorId}</span> : null}
            <span className={`rounded-full border px-3 py-1 text-xs ${onDuty ? "border-emerald-300/30 bg-emerald-400/10 text-emerald-100" : "border-amber-300/30 bg-amber-400/10 text-amber-100"}`}>
              {onDuty ? "On Duty" : "Off Duty"}
            </span>
            <button
              type="button"
              onClick={toggleDuty}
              disabled={dutyUpdating || !doctorId}
              className={`rounded-xl px-4 py-2 text-xs font-semibold transition ${onDuty ? "bg-amber-400/20 text-amber-100 hover:bg-amber-400/30" : "bg-emerald-400/20 text-emerald-100 hover:bg-emerald-400/30"} disabled:opacity-70`}
              title={`${doctorName}: set ${onDuty ? "off duty" : "on duty"}`}
            >
              {dutyUpdating ? "Updating..." : onDuty ? "Set Off Duty" : "Set On Duty"}
            </button>
          </div>
        </div>

        {loading ? <p className="text-sm text-slate-300">Loading assigned patients...</p> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
        {actionError ? <p className="mb-3 text-sm text-rose-300">{actionError}</p> : null}

        {!loading && !error ? (
          <div className="mt-3 space-y-3">
            {patients.map((patient) => (
              <div key={patient.visit_id} className="rounded-xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-slate-100">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold">{patient.patient_name}</span>
                      <span className={`rounded-full px-2.5 py-1 text-[11px] ${patient.triage_acuity <= 2 ? "bg-rose-400/20 text-rose-100" : "bg-cyan-300/15 text-cyan-100"}`}>
                        Acuity {patient.triage_acuity}
                      </span>
                      <span className="rounded-full bg-white/10 px-2.5 py-1 text-[11px] text-slate-200">
                        {patient.target_specialty || "Emergency"}
                      </span>
                    </div>
                    <div className="mt-1 text-xs text-slate-300">
                      {patient.patient_id} • {patient.visit_id} • {patient.assignment_status.replace(/_/g, " ")}
                    </div>
                    <div className="mt-2 text-xs text-slate-400">
                      Complaint System: {patient.chief_complaint_system || "Not captured"}
                    </div>
                  </div>

                  <div className="text-right">
                    <p className={`text-xs ${patient.attended_by_doctor ? "text-emerald-200" : "text-amber-200"}`}>
                      {patient.attended_by_doctor ? "Attended" : "Awaiting attendance"}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">{formatTimestamp(patient.attended_at)}</p>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-3">
                  <p className="text-xs text-slate-400">
                    Assigned on {formatTimestamp(patient.created_at)}
                  </p>
                  <button
                    type="button"
                    onClick={() => markAttended(patient.visit_id)}
                    disabled={patient.attended_by_doctor || pendingVisitId === patient.visit_id}
                    className={`rounded-xl px-4 py-2 text-xs font-semibold ${patient.attended_by_doctor ? "cursor-default bg-emerald-400/20 text-emerald-100" : "bg-cyan-400/20 text-cyan-100 hover:bg-cyan-400/30"} disabled:opacity-70`}
                  >
                    {patient.attended_by_doctor
                      ? "Attended"
                      : pendingVisitId === patient.visit_id
                        ? "Updating..."
                        : "Mark Attended"}
                  </button>
                </div>
              </div>
            ))}
            {patients.length === 0 ? <p className="text-sm text-slate-300">No patients are currently assigned to you.</p> : null}
          </div>
        ) : null}
      </section>
    </RoleShell>
  );
}
