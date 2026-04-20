import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import PlatformLayout from "../components/PlatformLayout";

const roleRoutes = {
  staff: "/staff",
  admin: "/admin/patients",
};

export default function SignInPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "", role: "staff" });

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = (event) => {
    event.preventDefault();
    navigate(roleRoutes[form.role] || "/");
  };

  return (
    <PlatformLayout>
      <section className="mx-auto w-full max-w-xl panel-soft panel-glow rounded-3xl border p-7 md:p-9">
        <p className="font-heading text-xs uppercase tracking-[0.24em] text-cyan-200">Secure Access</p>
        <h1 className="font-heading mt-3 text-3xl text-white md:text-4xl">Sign In</h1>
        <p className="mt-2 text-sm text-slate-200/85">For staff and administrators. Patients can continue without login from the patient area.</p>

        <form onSubmit={onSubmit} className="mt-7 space-y-4">
          <label className="field-block">
            <span className="field-label">Username</span>
            <input
              className="field-input"
              name="username"
              value={form.username}
              onChange={onChange}
              placeholder="staff.id"
              required
            />
          </label>

          <label className="field-block">
            <span className="field-label">Password</span>
            <input
              className="field-input"
              type="password"
              name="password"
              value={form.password}
              onChange={onChange}
              placeholder="••••••••"
              required
            />
          </label>

          <label className="field-block">
            <span className="field-label">Role</span>
            <select className="field-input" name="role" value={form.role} onChange={onChange}>
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </select>
          </label>

          <button className="btn-primary w-full" type="submit">Continue</button>
        </form>
      </section>
    </PlatformLayout>
  );
}
