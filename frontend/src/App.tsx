import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import EmailAnalyzer from "./pages/EmailAnalyzer";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/email-analyzer" element={<EmailAnalyzer />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;