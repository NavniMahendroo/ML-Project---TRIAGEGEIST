import React, { useEffect, useMemo, useState } from "react";
import RoleShell from "../components/RoleShell";
import { api } from "../lib/api";

const superadminLinks = [
  { to: "/superadmin", label: "Operations Dashboard" },
  { to: "/signin", label: "Logout" },
];

function StatTile({ label, value, tone }) {
  return (
    <article className={`rounded-2xl border p-4 ${tone}`}>
      <p className="text-xs uppercase tracking-[0.2em]">{label}</p>
      <p className="font-heading mt-2 text-3xl">{value}</p>
    </article>
  );
}

function formatTimestamp(value) {
  if (!value) return "Not attended";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function SuperadminDashboardPage() {
  const [summary, setSummary] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [pendingVisitId, setPendingVisitId] = useState(null);
  const [pendingReassignId, setPendingReassignId] = useState(null);
  const [reassignTargets, setReassignTargets] = useState({});

  useEffect(() => {
    let isActive = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");
        const [summaryResponse, assignmentsResponse] = await Promise.all([
          api.getSuperadminSummary(),
          api.listSuperadminAssignments(200),
        ]);
        if (!isActive) return;

        setSummary(summaryResponse);
        const nextAssignments = assignmentsResponse.items || [];
        setAssignments(nextAssignments);
        setReassignTargets(() => {
          const initialTargets = {};
          nextAssignments.forEach((item) => {
            if (item.assigned_doctor_id) {
              initialTargets[item.visit_id] = item.assigned_doctor_id;
            }
          });
          return initialTargets;
        });
      } catch (err) {
        if (isActive) {
          setError(err.message || "Unable to load superadmin dashboard.");
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadDashboard();
    return () => {
      isActive = false;
    };
  }, []);

  const markAttended = async (visitId) => {
    try {
      setPendingVisitId(visitId);
      setActionError("");
      const updated = await api.markSuperadminAssignmentAttended(visitId);
      setAssignments((prev) => prev.map((item) => (
        item.visit_id === visitId
          ? {
              ...item,
              attended_by_doctor: updated.attended_by_doctor,
              attended_at: updated.attended_at,
              attended_by_doctor_id: updated.attended_by_doctor_id,
              assignment_status: updated.assignment_status,
            }
          : item
      )));
    } catch (err) {
      setError(err.message || "Unable to update attended status.");
    } finally {
      setPendingVisitId(null);
    }
  };

  const reassignVisit = async (visitId) => {
    const doctorId = reassignTargets[visitId];
    if (!doctorId) {
      setActionError("Select a doctor before reassigning.");
      return;
    }

    try {
      setPendingReassignId(visitId);
      setActionError("");
      const updated = await api.reassignSuperadminAssignment(visitId, doctorId);
      setAssignments((prev) => prev.map((item) => (
        item.visit_id === visitId
          ? {
              ...item,
              assigned_doctor_id: updated.assigned_doctor_id,
              assigned_doctor_name: updated.assigned_doctor_name,
              assignment_status: updated.assignment_status,
              attended_by_doctor: updated.attended_by_doctor,
              attended_at: updated.attended_at,
              attended_by_doctor_id: updated.attended_by_doctor_id,
            }
          : item
      )));
      setReassignTargets((prev) => ({ ...prev, [visitId]: updated.assigned_doctor_id }));
    } catch (err) {
      setActionError(err.message || "Unable to reassign the visit.");
    } finally {
      setPendingReassignId(null);
    }
  };

  const nursesOnDuty = summary?.nurses?.filter((nurse) => nurse.on_duty) || [];
  const doctorsOnDuty = summary?.doctors?.filter((doctor) => doctor.on_duty) || [];
  const nursesOffDuty = summary?.nurses?.filter((nurse) => !nurse.on_duty) || [];
  const doctorsOffDuty = summary?.doctors?.filter((doctor) => !doctor.on_duty) || [];

  const doctorOptions = useMemo(() => {
    const list = summary?.doctors ? [...summary.doctors] : [];
    return list.sort((a, b) => a.name.localeCompare(b.name));
  }, [summary]);

  const acuityDistribution = useMemo(() => {
    const counts = [0, 0, 0, 0, 0];
    assignments.forEach((assignment) => {
      const level = Math.max(1, Math.min(5, Number(assignment.triage_acuity || 3)));
      counts[level - 1] += 1;
    });
    return counts;
  }, [assignments]);

  const maxAcuityCount = Math.max(1, ...acuityDistribution);
  const attendanceTotal = (summary?.attended_visits || 0) + (summary?.pending_visits || 0) || 1;
  const attendedPercent = summary ? Math.round((summary.attended_visits / attendanceTotal) * 100) : 0;
  const pendingPercent = summary ? 100 - attendedPercent : 0;

  return (
    <RoleShell
      role="Superadmin Console"
      title="Operations Dashboard"
      subtitle="Track patient assignment, attendance progress, and live staffing coverage across doctors and nurses."
      links={superadminLinks}
      showGlobalHeader={false}
    >
      {loading ? <p className="text-sm text-slate-300">Loading superadmin dashboard...</p> : null}
      {error ? <p className="mb-4 text-sm text-rose-300">{error}</p> : null}
      {actionError ? <p className="mb-4 text-sm text-rose-300">{actionError}</p> : null}

      {summary ? (
        <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
          <StatTile label="Patients" value={summary.total_patients} tone="border-cyan-200/20 bg-cyan-300/10 text-cyan-50" />
          <StatTile label="Visits" value={summary.total_visits} tone="border-blue-200/20 bg-blue-300/10 text-blue-50" />
          <StatTile label="Nurses" value={summary.total_nurses} tone="border-emerald-200/20 bg-emerald-300/10 text-emerald-50" />
          <StatTile label="Doctors" value={summary.total_doctors} tone="border-violet-200/20 bg-violet-300/10 text-violet-50" />
          <StatTile label="Pending" value={summary.pending_visits} tone="border-amber-200/20 bg-amber-300/10 text-amber-50" />
          <StatTile label="Attended" value={summary.attended_visits} tone="border-rose-200/20 bg-rose-300/10 text-rose-50" />
        </section>
      ) : null}

      {summary ? (
        <section className="mt-6 grid gap-5 lg:grid-cols-3">
          <article className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Attendance Progress</p>
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span>Attended</span>
                <span>{summary.attended_visits} / {attendanceTotal}</span>
              </div>
              <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
                <div className="h-full bg-emerald-400/70" style={{ width: `${attendedPercent}%` }} />
              </div>
              <div className="mt-3 flex items-center justify-between text-xs text-slate-300">
                <span>Pending</span>
                <span>{summary.pending_visits} / {attendanceTotal}</span>
              </div>
              <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
                <div className="h-full bg-amber-400/70" style={{ width: `${pendingPercent}%` }} />
              </div>
            </div>
          </article>

          <article className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Duty Coverage</p>
            <div className="mt-4 space-y-4">
              <div>
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>Doctors on duty</span>
                  <span>{summary.doctors_on_duty} / {summary.total_doctors}</span>
                </div>
                <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full bg-violet-400/70"
                    style={{ width: `${summary.total_doctors ? Math.round((summary.doctors_on_duty / summary.total_doctors) * 100) : 0}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>Nurses on duty</span>
                  <span>{summary.nurses_on_duty} / {summary.total_nurses}</span>
                </div>
                <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full bg-emerald-400/70"
                    style={{ width: `${summary.total_nurses ? Math.round((summary.nurses_on_duty / summary.total_nurses) * 100) : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </article>

          <article className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Acuity Spread</p>
            <div className="mt-4 space-y-3">
              {acuityDistribution.map((count, index) => (
                <div key={`acuity-${index + 1}`}>
                  <div className="flex items-center justify-between text-xs text-slate-300">
                    <span>Level {index + 1}</span>
                    <span>{count}</span>
                  </div>
                  <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full bg-cyan-400/70"
                      style={{ width: `${Math.round((count / maxAcuityCount) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>
      ) : null}

      <section className="mt-6 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">On Duty</p>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <div>
              <p className="text-xs text-slate-300">Doctors ({summary?.doctors_on_duty || 0})</p>
              <div className="mt-2 space-y-2">
                {doctorsOnDuty.map((doctor) => (
                  <div key={doctor.staff_id} className="rounded-xl border border-emerald-200/20 bg-emerald-300/10 px-3 py-2 text-xs text-emerald-100">
                    {doctor.name} • {doctor.staff_id} • {doctor.specialty || "General"}
                  </div>
                ))}
                {doctorsOnDuty.length === 0 ? <p className="text-xs text-slate-400">No on-duty doctors.</p> : null}
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-300">Nurses ({summary?.nurses_on_duty || 0})</p>
              <div className="mt-2 space-y-2">
                {nursesOnDuty.map((nurse) => (
                  <div key={nurse.staff_id} className="rounded-xl border border-emerald-200/20 bg-emerald-300/10 px-3 py-2 text-xs text-emerald-100">
                    {nurse.name} • {nurse.staff_id}
                  </div>
                ))}
                {nursesOnDuty.length === 0 ? <p className="text-xs text-slate-400">No on-duty nurses.</p> : null}
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Off Duty</p>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <div>
              <p className="text-xs text-slate-300">Doctors ({summary?.doctors_off_duty || 0})</p>
              <div className="mt-2 space-y-2">
                {doctorsOffDuty.map((doctor) => (
                  <div key={doctor.staff_id} className="rounded-xl border border-amber-200/20 bg-amber-300/10 px-3 py-2 text-xs text-amber-100">
                    {doctor.name} • {doctor.staff_id} • {doctor.specialty || "General"}
                  </div>
                ))}
                {doctorsOffDuty.length === 0 ? <p className="text-xs text-slate-400">No off-duty doctors.</p> : null}
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-300">Nurses ({summary?.nurses_off_duty || 0})</p>
              <div className="mt-2 space-y-2">
                {nursesOffDuty.map((nurse) => (
                  <div key={nurse.staff_id} className="rounded-xl border border-amber-200/20 bg-amber-300/10 px-3 py-2 text-xs text-amber-100">
                    {nurse.name} • {nurse.staff_id}
                  </div>
                ))}
                {nursesOffDuty.length === 0 ? <p className="text-xs text-slate-400">No off-duty nurses.</p> : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-6 rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Patient Assignment Matrix</p>
        <div className="mt-3 space-y-3">
          {assignments.map((assignment) => (
            <article key={assignment.visit_id} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold">{assignment.patient_name}</p>
                  <p className="mt-1 text-xs text-slate-300">
                    {assignment.patient_id} • {assignment.visit_id} • Nurse {assignment.nurse_name || assignment.nurse_id}
                  </p>
                  <p className="mt-1 text-xs text-slate-300">
                    Specialty: {assignment.target_specialty || "Emergency"} • Doctor: {assignment.assigned_doctor_name || assignment.assigned_doctor_id || "Unassigned"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-cyan-200">Acuity {assignment.triage_acuity} ({assignment.urgency_label})</p>
                  <p className="mt-1 text-xs text-slate-400">{assignment.assignment_status.replaceAll("_", " ")}</p>
                  <p className={`mt-1 text-xs ${assignment.attended_by_doctor ? "text-emerald-200" : "text-amber-200"}`}>
                    {assignment.attended_by_doctor ? "Attended" : "Pending"}
                  </p>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-3">
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                  <span>Attended at: {formatTimestamp(assignment.attended_at)}</span>
                  <span className="rounded-full border border-white/10 bg-white/10 px-2 py-1 text-[11px] uppercase tracking-[0.16em]">
                    {assignment.assignment_status.replaceAll("_", " ")}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    value={reassignTargets[assignment.visit_id] || ""}
                    onChange={(event) => setReassignTargets((prev) => ({ ...prev, [assignment.visit_id]: event.target.value }))}
                    disabled={assignment.attended_by_doctor}
                    className="min-w-[180px] rounded-xl border border-white/10 bg-slate-900/60 px-3 py-2 text-xs text-slate-100"
                  >
                    <option value="" disabled>
                      Select doctor
                    </option>
                    {doctorOptions.map((doctor) => (
                      <option key={doctor.staff_id} value={doctor.staff_id}>
                        {doctor.name} ({doctor.specialty || "General"}) {doctor.on_duty ? "" : "- Off duty"}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => reassignVisit(assignment.visit_id)}
                    disabled={assignment.attended_by_doctor || pendingReassignId === assignment.visit_id}
                    className={`rounded-xl px-4 py-2 text-xs font-semibold ${assignment.attended_by_doctor ? "cursor-default bg-slate-500/20 text-slate-300" : "bg-violet-400/20 text-violet-100 hover:bg-violet-400/30"} disabled:opacity-70`}
                  >
                    {assignment.attended_by_doctor
                      ? "Locked"
                      : pendingReassignId === assignment.visit_id
                        ? "Reassigning..."
                        : "Reassign"}
                  </button>
                  <button
                    type="button"
                    onClick={() => markAttended(assignment.visit_id)}
                    disabled={assignment.attended_by_doctor || pendingVisitId === assignment.visit_id}
                    className={`rounded-xl px-4 py-2 text-xs font-semibold ${assignment.attended_by_doctor ? "cursor-default bg-emerald-400/20 text-emerald-100" : "bg-cyan-400/20 text-cyan-100 hover:bg-cyan-400/30"} disabled:opacity-70`}
                  >
                    {assignment.attended_by_doctor
                      ? "Attended"
                      : pendingVisitId === assignment.visit_id
                        ? "Updating..."
                        : "Mark Attended"}
                  </button>
                </div>
              </div>
            </article>
          ))}
          {assignments.length === 0 ? <p className="text-sm text-slate-300">No visits available for assignment monitoring.</p> : null}
        </div>
      </section>
    </RoleShell>
  );
}
