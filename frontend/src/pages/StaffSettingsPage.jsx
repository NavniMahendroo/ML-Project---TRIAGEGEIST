import React, { useState } from "react";
import RoleShell from "../components/RoleShell";

const staffLinks = [
  { to: "/staff", label: "Dashboard" },
  { to: "/staff/tasks", label: "Tasks" },
  { to: "/staff/settings", label: "Settings" },
  { to: "/staff/logout", label: "Logout" },
];

export default function StaffSettingsPage() {
  const [soundAlerts, setSoundAlerts] = useState(true);
  const [showCompleted, setShowCompleted] = useState(true);

  return (
    <RoleShell
      role="Staff Workspace"
      title="Settings"
      subtitle="Configure your shift notification preferences."
      links={staffLinks}
      showGlobalHeader={false}
    >
      <section className="grid gap-4">
        <label className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 px-5 py-4 text-sm text-slate-100">
          <input
            className="mr-3"
            type="checkbox"
            checked={soundAlerts}
            onChange={(event) => setSoundAlerts(event.target.checked)}
          />
          Enable alert sound for new critical tasks
        </label>

        <label className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 px-5 py-4 text-sm text-slate-100">
          <input
            className="mr-3"
            type="checkbox"
            checked={showCompleted}
            onChange={(event) => setShowCompleted(event.target.checked)}
          />
          Keep completed tasks visible in task panel
        </label>
      </section>
    </RoleShell>
  );
}
