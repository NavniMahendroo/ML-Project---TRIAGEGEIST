import React from "react";
import { NavLink } from "react-router-dom";
import PlatformLayout from "./PlatformLayout";

export default function RoleShell({ role, title, subtitle, links, children, showGlobalHeader = true }) {
  return (
    <PlatformLayout showHeader={showGlobalHeader}>
      <section className="panel-soft panel-glow rounded-3xl border p-6 md:p-8">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">{role}</p>
        <h1 className="font-heading mt-3 text-4xl text-white md:text-5xl">{title}</h1>
        {subtitle ? <p className="mt-3 max-w-3xl text-sm text-slate-200/90 md:text-base">{subtitle}</p> : null}

        <nav className="mt-6 flex flex-wrap gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-xl px-4 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-cyan-300/20 text-cyan-100 ring-1 ring-cyan-200/30"
                    : "bg-white/5 text-slate-200 hover:bg-white/10"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-6">{children}</div>
      </section>
    </PlatformLayout>
  );
}
