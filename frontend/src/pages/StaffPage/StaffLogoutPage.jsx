import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import PlatformLayout from "../../components/PlatformLayout";

export default function StaffLogoutPage() {
  useEffect(() => {
    localStorage.removeItem("staffAuth");
  }, []);

  return (
    <PlatformLayout showHeader={false}>
      <section className="mx-auto w-full max-w-xl panel-soft panel-glow rounded-3xl border p-8 text-center">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">Staff Workspace</p>
        <h1 className="font-heading mt-3 text-3xl text-white">Logged Out</h1>
        <p className="mt-3 text-sm text-slate-200/90">Your session has ended safely.</p>

        <div className="mt-6 flex justify-center gap-3">
          <Link className="btn-primary no-underline" to="/signin">Sign In Again</Link>
          <Link className="btn-ghost no-underline" to="/">Go Home</Link>
        </div>
      </section>
    </PlatformLayout>
  );
}
