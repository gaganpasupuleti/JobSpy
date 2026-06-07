import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

export default function AdminScrapePanel({
  adminKey,
  roles,
  scrapeInProgress,
  onStarted,
}) {
  const [profiles, setProfiles] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [roleFilter, setRoleFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const loadProfiles = useCallback(async () => {
    if (!adminKey) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSearchProfiles(adminKey, roleFilter || undefined);
      setProfiles(data);
      setSelected((prev) => {
        const ids = new Set(data.map((p) => p.id));
        return new Set([...prev].filter((id) => ids.has(id)));
      });
    } catch (e) {
      setError(e.message);
      setProfiles([]);
    } finally {
      setLoading(false);
    }
  }, [adminKey, roleFilter]);

  useEffect(() => {
    if (adminKey) loadProfiles();
  }, [adminKey, loadProfiles]);

  const grouped = useMemo(() => {
    const map = new Map();
    for (const p of profiles) {
      if (!map.has(p.role_slug)) {
        map.set(p.role_slug, { name: p.role_name, items: [] });
      }
      map.get(p.role_slug).items.push(p);
    }
    return [...map.entries()].sort((a, b) => a[1].name.localeCompare(b[1].name));
  }, [profiles]);

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleRole(roleSlug) {
    const ids = profiles.filter((p) => p.role_slug === roleSlug).map((p) => p.id);
    setSelected((prev) => {
      const next = new Set(prev);
      const allOn = ids.every((id) => next.has(id));
      for (const id of ids) {
        if (allOn) next.delete(id);
        else next.add(id);
      }
      return next;
    });
  }

  function selectAll() {
    setSelected(new Set(profiles.map((p) => p.id)));
  }

  function clearAll() {
    setSelected(new Set());
  }

  async function runScrape() {
    if (selected.size === 0) {
      setError("Select at least one profile to scrape.");
      return;
    }
    setRunning(true);
    setError(null);
    setMessage(null);
    try {
      const res = await api.triggerDashboardRefresh({
        adminKey,
        profileIds: [...selected],
      });
      setMessage(res.message);
      onStarted?.(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  if (!adminKey) {
    return (
      <section className="dash-panel admin-panel">
        <h3>Select profiles to scrape</h3>
        <p className="dash-muted">
          Save your admin API key above to pick role × city × level combinations instead of a fixed count.
        </p>
      </section>
    );
  }

  return (
    <section className="dash-panel admin-panel">
      <h3>Select profiles to scrape</h3>
      <p className="dash-muted">
        Choose specific search profiles (Indeed, LinkedIn, Naukri, Foundit). Runs in the background — same as refresh above.
      </p>

      {error && (
        <div className="alert error">
          {error}
          <button type="button" className="alert-dismiss" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}

      {message && (
        <div className="alert" style={{ background: "#e8f5ee", color: "var(--success)" }}>
          {message}
        </div>
      )}

      <div className="admin-toolbar">
        <label>
          Role filter
          <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
            <option value="">All roles ({profiles.length})</option>
            {(roles || []).map((r) => (
              <option key={r.slug} value={r.slug}>
                {r.name}
              </option>
            ))}
          </select>
        </label>
        <span className="admin-selection-count">
          <strong>{selected.size}</strong> selected
        </span>
        <button type="button" className="btn ghost" onClick={selectAll} disabled={loading}>
          Select all
        </button>
        <button type="button" className="btn ghost" onClick={clearAll} disabled={loading}>
          Clear
        </button>
        <button
          type="button"
          className="btn primary"
          onClick={runScrape}
          disabled={running || scrapeInProgress || selected.size === 0}
        >
          {running
            ? "Starting…"
            : scrapeInProgress
              ? "Scrape running…"
              : `Scrape selected (${selected.size})`}
        </button>
        <button type="button" className="btn ghost" onClick={loadProfiles} disabled={loading}>
          Reload list
        </button>
      </div>

      {loading ? (
        <div className="empty-state">
          <div className="spinner" />
          <p>Loading profiles…</p>
        </div>
      ) : (
        <div className="admin-profile-groups">
          {grouped.map(([slug, group]) => {
            const ids = group.items.map((p) => p.id);
            const selCount = ids.filter((id) => selected.has(id)).length;
            const allOn = selCount === ids.length;
            return (
              <div key={slug} className="admin-role-group">
                <div className="admin-role-header">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={allOn && ids.length > 0}
                      onChange={() => toggleRole(slug)}
                    />
                    <strong>{group.name}</strong>
                    <span className="admin-role-meta">
                      {selCount}/{ids.length} profiles
                    </span>
                  </label>
                </div>
                <div className="admin-city-grid">
                  {group.items.map((p) => (
                    <label key={p.id} className="admin-city-chip checkbox-label">
                      <input
                        type="checkbox"
                        checked={selected.has(p.id)}
                        onChange={() => toggle(p.id)}
                      />
                      <span>
                        {p.city}
                        {p.experience_label ? ` · ${p.experience_label}` : ""}
                      </span>
                      {p.last_scraped_at && (
                        <span className="admin-scraped-hint" title={p.last_scraped_at}>
                          ✓
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
