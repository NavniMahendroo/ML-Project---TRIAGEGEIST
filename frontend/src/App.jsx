import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import TriagePage from "./pages/TriagePage";
import ChatbotPage from "./pages/ChatbotPage/index";
import { Backdrop } from "./components/UI";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/chatbot" replace />} />
        <Route path="/triage" element={
          <main className="app-shell min-h-screen overflow-hidden">
            <Backdrop />
            <div className="relative z-10 mx-auto w-full max-w-7xl px-4 py-8 md:px-10 md:py-12">
              <TriagePage />
            </div>
          </main>
        } />
        <Route path="/chatbot" element={<ChatbotPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
