import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import AlertsPage from "./pages/AlertsPage";
import DashboardPage from "./pages/DashboardPage";
import EmailLogsPage from "./pages/EmailLogsPage";
import JobsPage from "./pages/JobsPage";
import ScanRunsPage from "./pages/ScanRunsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/email-logs" element={<EmailLogsPage />} />
          <Route path="/scan-runs" element={<ScanRunsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
