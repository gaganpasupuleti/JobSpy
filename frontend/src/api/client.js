const BASE = import.meta.env.VITE_API_URL || "";
const ADMIN_KEY_STORAGE = "jobboard_admin_key";

export function getAdminKey() {
  return import.meta.env.VITE_ADMIN_API_KEY || sessionStorage.getItem(ADMIN_KEY_STORAGE) || "";
}

export function setAdminKey(key) {
  if (key) sessionStorage.setItem(ADMIN_KEY_STORAGE, key);
  else sessionStorage.removeItem(ADMIN_KEY_STORAGE);
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
          : detail
            ? JSON.stringify(detail)
            : `Request failed: ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  getRoles: () => request("/api/v1/meta/roles"),
  getLocations: () => request("/api/v1/meta/locations"),
  getExperienceBands: () => request("/api/v1/meta/experience-bands"),
  getKeywords: (role) =>
    request(`/api/v1/meta/keywords${role ? `?role=${role}` : ""}`),
  getJobs: (params) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== "" && v !== null && v !== undefined) qs.set(k, v);
    });
    return request(`/api/v1/jobs?${qs}`);
  },
  getJob: (id) => request(`/api/v1/jobs/${id}`),
  applyToJob: (id, sessionId) =>
    request(`/api/v1/jobs/${id}/apply`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
  saveJob: (id, sessionId) =>
    request(`/api/v1/jobs/${id}/save`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
  getDashboardStats: () => request("/api/v1/dashboard/stats"),
  getDashboardRefreshStatus: () => request("/api/v1/dashboard/refresh/status"),
  triggerDashboardRefresh: (limit, adminKey) =>
    request(`/api/v1/dashboard/refresh?limit=${limit}`, {
      method: "POST",
      headers: { "X-Admin-Key": adminKey },
    }),
};
