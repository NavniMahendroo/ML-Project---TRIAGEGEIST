import React from "react";
import { Link, NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/privacy", label: "Privacy" },
  { to: "/patient", label: "Patient" },
  { to: "/signin", label: "Sign In" },
];

export default function PlatformLayout({ children, showHeader = true }) {
  return (
    <main className="app-shell min-h-screen overflow-hidden">
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />
      <div className="orb orb-three" aria-hidden="true" />
      <div className="scan-grid" aria-hidden="true" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-10 pt-6 md:px-8">
        {showHeader ? (
          <header className="panel-soft panel-glow mb-8 rounded-2xl border px-4 py-4 md:px-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <Link to="/" className="flex items-center gap-3 no-underline">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/20 text-cyan-100 ring-1 ring-cyan-200/25">
                  <span className="text-xl">+</span>
                </div>
                <div>
                  <p className="font-heading text-lg font-semibold tracking-wide text-white">TriageGeist</p>
                  <p className="text-xs uppercase tracking-[0.24em] text-cyan-200/90">Hospital Triage Platform</p>
                </div>
              </Link>

              <nav className="flex flex-wrap items-center gap-2">
                {links.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `rounded-xl px-4 py-2 text-sm font-medium transition ${
                        isActive
                          ? "bg-cyan-300/20 text-cyan-100 ring-1 ring-cyan-200/30"
                          : "text-slate-200 hover:bg-white/10 hover:text-white"
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </div>
          </header>
        ) : null}

        {children}
      </div>
    </main>
  );
}
