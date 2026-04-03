import React from "react";
import TriagePage from "./pages/TriagePage";
import { Backdrop } from "./components/UI";

function App() {
  return (
    <main className="app-shell min-h-screen overflow-hidden px-4 py-8 md:px-10 md:py-12">
      <Backdrop />
      <div className="relative z-10 mx-auto w-full max-w-7xl">
        <TriagePage />
      </div>
    </main>
  );
}

export default App;
