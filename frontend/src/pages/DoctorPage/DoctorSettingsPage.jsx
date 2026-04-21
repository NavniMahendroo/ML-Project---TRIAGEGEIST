import React, { useState } from "react";
import RoleShell from "../../components/RoleShell";

const adminLinks = [
  { to: "/admin/patients", label: "Patients by Department" },
  { to: "/admin/stats", label: "Overall Graphs" },
  { to: "/admin/doctors", label: "Staff Management" },
  { to: "/admin/outcomes", label: "Survived vs Admitted" },
  { to: "/admin/settings", label: "Settings" },
  { to: "/signin", label: "Logout" },
];

export default function DoctorSettingsPage() {
  const [notifyCritical, setNotifyCritical] = useState(true);
  const [autoArchive, setAutoArchive] = useState(false);

  return (
    <RoleShell
      role="Admin Console"
      title="Settings"
      subtitle="Manage alerting and reporting defaults for the hospital dashboard."
      links={adminLinks}
      showGlobalHeader={false}
    >
      <section className="grid gap-4">
        <label className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 px-5 py-4 text-sm text-slate-100">
          <input
            className="mr-3"
            type="checkbox"
            checked={notifyCritical}
            onChange={(event) => setNotifyCritical(event.target.checked)}
          />
          Enable critical triage alert notifications
        </label>

        <label className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 px-5 py-4 text-sm text-slate-100">
          <input
            className="mr-3"
            type="checkbox"
            checked={autoArchive}
            onChange={(event) => setAutoArchive(event.target.checked)}
          />
          Auto-archive completed daily reports
        </label>
      </section>
    </RoleShell>
  );
}
