import React from "react";
import RoleShell from "../components/RoleShell";
import { staffTasks } from "../constants/mockData";

const staffLinks = [
  { to: "/staff", label: "Dashboard" },
  { to: "/staff/tasks", label: "Tasks" },
  { to: "/staff/settings", label: "Settings" },
  { to: "/staff/logout", label: "Logout" },
];

export default function StaffTasksPage() {
  return (
    <RoleShell
      role="Staff Workspace"
      title="Task Notifications"
      subtitle="Track upcoming and completed tasks in separate sections."
      links={staffLinks}
      showGlobalHeader={false}
    >
      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Upcoming Tasks</p>
          <div className="mt-3 space-y-2">
            {staffTasks.upcoming.map((task) => (
              <div key={task.id} className="rounded-xl border border-amber-200/20 bg-amber-300/10 px-3 py-2 text-sm text-amber-50">
                <p className="font-medium">{task.title}</p>
                <p className="text-xs text-amber-100/80">{task.id} • Due {task.due}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-cyan-100/20 bg-slate-950/45 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Completed Tasks</p>
          <div className="mt-3 space-y-2">
            {staffTasks.completed.map((task) => (
              <div key={task.id} className="rounded-xl border border-emerald-200/20 bg-emerald-300/10 px-3 py-2 text-sm text-emerald-50">
                <p className="font-medium">{task.title}</p>
                <p className="text-xs text-emerald-100/80">{task.id} • Completed {task.doneAt}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </RoleShell>
  );
}
