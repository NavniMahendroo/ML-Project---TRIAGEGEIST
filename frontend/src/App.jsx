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

        <Route path="/admin" element={<Navigate to="/admin/patients" replace />} />
        <Route path="/admin/patients" element={<AdminPatientsPage />} />
        <Route path="/admin/stats" element={<AdminStatsPage />} />
        <Route path="/admin/doctors" element={<AdminDoctorsPage />} />
        <Route path="/admin/outcomes" element={<AdminOutcomesPage />} />
        <Route path="/admin/settings" element={<AdminSettingsPage />} />

        <Route path="/staff" element={<StaffDashboardPage />} />
        <Route path="/staff/tasks" element={<StaffTasksPage />} />
        <Route path="/staff/settings" element={<StaffSettingsPage />} />
        <Route path="/staff/logout" element={<StaffLogoutPage />} />

        <Route path="/triage" element={<Navigate to="/patient/form" replace />} />
        <Route path="/chatbot" element={<Navigate to="/patient/chatbot" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
