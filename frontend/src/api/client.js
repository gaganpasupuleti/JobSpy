const API_BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/health"),
  getJobs: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v)
    ).toString();
    return request(`/jobs${qs ? `?${qs}` : ""}`);
  },
  createJob: (data) =>
    request("/jobs", { method: "POST", body: JSON.stringify(data) }),
  importDemoJobs: () => request("/jobs/import-demo", { method: "POST" }),
  getAlerts: () => request("/alerts"),
  createAlert: (data) =>
    request("/alerts", { method: "POST", body: JSON.stringify(data) }),
  updateAlert: (id, data) =>
    request(`/alerts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteAlert: (id) => request(`/alerts/${id}`, { method: "DELETE" }),
  sendTestAlert: (id) =>
    request(`/alerts/${id}/send-test`, { method: "POST" }),
  runDemoScan: () => request("/scans/run-demo", { method: "POST" }),
  getEmailNotifications: () => request("/email-notifications"),
  getScanRuns: () => request("/scan-runs"),
};
