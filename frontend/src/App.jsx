import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import TriagePage from "./pages/TriagePage";
import ChatbotPage from "./pages/ChatbotPage/index";
import LandingPage from "./pages/LandingPage";
import PrivacyPage from "./pages/PrivacyPage";
import PatientHubPage from "./pages/PatientHubPage";
import SignInPage from "./pages/SignInPage";
import AdminPatientsPage from "./pages/AdminPatientsPage";
import AdminStatsPage from "./pages/AdminStatsPage";
import AdminDoctorsPage from "./pages/AdminDoctorsPage";
import AdminOutcomesPage from "./pages/AdminOutcomesPage";
import AdminSettingsPage from "./pages/AdminSettingsPage";
import StaffDashboardPage from "./pages/StaffDashboardPage";
import StaffTasksPage from "./pages/StaffTasksPage";
import StaffSettingsPage from "./pages/StaffSettingsPage";
import StaffLogoutPage from "./pages/StaffLogoutPage";
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
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/patient" element={<PatientHubPage />} />
        <Route path="/patient/form" element={<PlatformLayout><TriagePage /></PlatformLayout>} />
        <Route path="/patient/chatbot" element={<ChatbotPage />} />

        <Route path="/admin" element={<AdminProtectedRoute><Navigate to="/admin/patients" replace /></AdminProtectedRoute>} />
        <Route path="/admin/patients" element={<AdminProtectedRoute><AdminPatientsPage /></AdminProtectedRoute>} />
        <Route path="/admin/stats" element={<AdminProtectedRoute><AdminStatsPage /></AdminProtectedRoute>} />
        <Route path="/admin/doctors" element={<AdminProtectedRoute><AdminDoctorsPage /></AdminProtectedRoute>} />
        <Route path="/admin/outcomes" element={<AdminProtectedRoute><AdminOutcomesPage /></AdminProtectedRoute>} />
        <Route path="/admin/settings" element={<AdminProtectedRoute><AdminSettingsPage /></AdminProtectedRoute>} />

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
