import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import TriagePage from "./pages/TriagePage";
import ChatbotPage from "./pages/ChatbotPage/index";
import LandingPage from "./pages/LandingPage";
import SignInPage from "./pages/SignInPage";
import DoctorPatientsPage from "./pages/DoctorPage/DoctorPatientsPage";
import DoctorStatsPage from "./pages/DoctorPage/DoctorStatsPage";
import DoctorStaffPage from "./pages/DoctorPage/DoctorStaffPage";
import DoctorOutcomesPage from "./pages/DoctorPage/DoctorOutcomesPage";
import DoctorSettingsPage from "./pages/DoctorPage/DoctorSettingsPage";
import StaffDashboardPage from "./pages/StaffPage/StaffDashboardPage";
import StaffTasksPage from "./pages/StaffPage/StaffTasksPage";
import StaffSettingsPage from "./pages/StaffPage/StaffSettingsPage";
import StaffLogoutPage from "./pages/StaffPage/StaffLogoutPage";
import PlatformLayout from "./components/PlatformLayout";

function isStaffAuthenticated() {
  try {
    const raw = localStorage.getItem("staffAuth");
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    return Boolean(parsed?.nurse_id);
  } catch {
    return false;
  }
}

function isAdminAuthenticated() {
  try {
    const raw = localStorage.getItem("adminAuth");
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    return Boolean(parsed?.doctor_id);
  } catch {
    return false;
  }
}

function StaffProtectedRoute({ children }) {
  if (!isStaffAuthenticated()) {
    return <Navigate to="/signin" replace />;
  }
  return children;
}

function AdminProtectedRoute({ children }) {
  if (!isAdminAuthenticated()) {
    return <Navigate to="/signin" replace />;
  }
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/patient" element={<Navigate to="/patient/form" replace />} />
        <Route path="/patient/form" element={<PlatformLayout><TriagePage /></PlatformLayout>} />
        <Route path="/patient/chatbot" element={<ChatbotPage />} />

        <Route path="/admin" element={<AdminProtectedRoute><Navigate to="/admin/patients" replace /></AdminProtectedRoute>} />
        <Route path="/admin/patients" element={<AdminProtectedRoute><DoctorPatientsPage /></AdminProtectedRoute>} />
        <Route path="/admin/stats" element={<AdminProtectedRoute><DoctorStatsPage /></AdminProtectedRoute>} />
        <Route path="/admin/doctors" element={<AdminProtectedRoute><DoctorStaffPage /></AdminProtectedRoute>} />
        <Route path="/admin/outcomes" element={<AdminProtectedRoute><DoctorOutcomesPage /></AdminProtectedRoute>} />
        <Route path="/admin/settings" element={<AdminProtectedRoute><DoctorSettingsPage /></AdminProtectedRoute>} />

        <Route path="/staff" element={<StaffProtectedRoute><StaffDashboardPage /></StaffProtectedRoute>} />
        <Route path="/staff/tasks" element={<StaffProtectedRoute><StaffTasksPage /></StaffProtectedRoute>} />
        <Route path="/staff/settings" element={<StaffProtectedRoute><StaffSettingsPage /></StaffProtectedRoute>} />
        <Route path="/staff/logout" element={<StaffProtectedRoute><StaffLogoutPage /></StaffProtectedRoute>} />

        <Route path="/triage" element={<Navigate to="/patient/form" replace />} />
        <Route path="/chatbot" element={<Navigate to="/patient/chatbot" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
