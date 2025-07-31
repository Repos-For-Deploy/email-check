import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/Login"; // or "pages/Login" if using absolute imports
import Dashboards from "./pages/DashboardPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboards/>} />
      </Routes>
    </Router>
    
  );
}

export default App;
