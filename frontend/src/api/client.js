const BASE = import.meta.env.VITE_API_URL || "";

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
    throw new Error(err.detail || `Request failed: ${res.status}`);
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
};
