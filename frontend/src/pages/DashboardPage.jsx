import { useCallback, useEffect, useState } from "react";
import { api, getAdminKey, setAdminKey } from "../api/client";
import Header from "../components/Header";
import { formatDateTime, siteLabel } from "../utils/format";

const POLL_MS = 5000;

function BreakdownTable({ title, rows, emptyLabel = "No data" }) {
  const max = rows.length ? Math.max(...rows.map((r) => r.count)) : 1;
  return (
    <section className="dash-panel">
      <h3>{title}</h3>
      {rows.length === 0 ? (
        <p className="dash-muted">{emptyLabel}</p>
      ) : (
        <ul className="dash-breakdown">
          {rows.map((row) => (
            <li key={`${row.label}-${row.slug || ""}`}>
              <span className="dash-breakdown-label">{row.label}</span>
              <div className="dash-bar-track">
                <div
                  className="dash-bar-fill"
                  style={{ width: `${Math.max(4, (row.count / max) * 100)}%` }}
                />
              </div>
              <span className="dash-breakdown-count">{row.count.toLocaleString("en-IN")}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function statusClass(status) {
  if (status === "success") return "status-success";
  if (status === "failed") return "status-failed";
  if (status === "running") return "status-running";
  return "";
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("loading");
  const [refreshLimit, setRefreshLimit] = useState(5);
  const [fullScrape, setFullScrape] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState(null);
  const [adminKeyInput, setAdminKeyInput] = useState(
    () => getAdminKey() || ""
  );
  const [showKeyForm, setShowKeyForm] = useState(!getAdminKey());

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
      setApiStatus("ok");
      setError(null);
      return data;
    } catch (e) {
      setError(e.message);
      setApiStatus("error");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    async function init() {
      try {
        await api.health();
        await loadStats();
      } catch {
        setApiStatus("error");
        setLoading(false);
      }
    }
    init();
  }, [loadStats]);

  useEffect(() => {
    if (!stats?.scrape_in_progress) return undefined;
    const id = setInterval(loadStats, POLL_MS);
    return () => clearInterval(id);
  }, [stats?.scrape_in_progress, loadStats]);

  function saveAdminKey(e) {
    e.preventDefault();
    setAdminKey(adminKeyInput.trim());
    setShowKeyForm(false);
    setRefreshMessage("Admin key saved for this browser session.");
  }

  async function handleRefresh() {
    const key = getAdminKey();
    if (!key) {
      setShowKeyForm(true);
      setError("Set your admin API key before triggering a refresh.");
      return;
    }
    setRefreshing(true);
    setRefreshMessage(null);
    setError(null);
    try {
      const res = await api.triggerDashboardRefresh(refreshLimit, key, fullScrape);
      setRefreshMessage(res.message);
      await loadStats();
    } catch (e) {
      setError(e.message);
    } finally {
      setRefreshing(false);
    }
  }

  const lastUpdated = stats?.last_successful_scrape_at || stats?.last_job_scraped_at;

  return (
    <div className="app">
      <Header apiStatus={apiStatus} variant="dashboard" />

      <main className="main dashboard-main">
        <div className="dash-hero">
          <div>
            <h2 className="dash-title">Job board health</h2>
            <p className="dash-subtitle">
              Live metrics and manual scrape control — no cron required.
            </p>
          </div>
          <div className="dash-last-updated">
            <span className="dash-last-label">Data last updated</span>
            <strong>
              {loading ? "Loading…" : lastUpdated ? formatDateTime(lastUpdated) : "Never"}
            </strong>
            {stats?.last_job_scraped_at &&
              stats.last_successful_scrape_at &&
              stats.last_job_scraped_at !== stats.last_successful_scrape_at && (
                <span className="dash-muted dash-last-extra">
                  Latest job ingest: {formatDateTime(stats.last_job_scraped_at)}
                </span>
              )}
          </div>
        </div>

        {apiStatus === "error" && (
          <div className="alert error">
            <strong>Backend not reachable.</strong> Start the API, then reload this page.
          </div>
        )}

        {error && (
          <div className="alert error">
            {error}
            <button className="alert-dismiss" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {refreshMessage && (
          <div className="alert" style={{ background: "#e8f5ee", color: "var(--success)" }}>
            {refreshMessage}
          </div>
        )}

        {stats?.scrape_in_progress && (
          <div className="alert dash-scrape-banner">
            <div className="spinner spinner-sm" />
            Scrape in progress… this page refreshes every few seconds.
          </div>
        )}

        <section className="dash-cards">
          <article className="dash-card dash-card-live">
            <span className="dash-card-label">Fully tagged</span>
            <strong className="dash-card-value">
              {(stats?.jobs_by_tag?.complete ?? 0).toLocaleString("en-IN")}
            </strong>
            <span className="dash-card-hint">Browse tab (India + role + level)</span>
          </article>
          <article className="dash-card">
            <span className="dash-card-label">Others queue</span>
            <strong className="dash-card-value">
              {(
                (stats?.jobs_by_tag?.partial ?? 0) +
                (stats?.jobs_by_tag?.untagged ?? 0) +
                (stats?.jobs_by_tag?.flagged ?? 0)
              ).toLocaleString("en-IN")}
            </strong>
            <span className="dash-card-hint">
              Partial {stats?.jobs_by_tag?.partial ?? 0} · Flagged{" "}
              {stats?.jobs_by_tag?.flagged ?? 0}
            </span>
          </article>
          <article className="dash-card dash-card-live">
            <span className="dash-card-label">Live jobs</span>
            <strong className="dash-card-value">
              {(stats?.jobs.live ?? 0).toLocaleString("en-IN")}
            </strong>
            <span className="dash-card-hint">All active in database</span>
          </article>
          <article className="dash-card">
            <span className="dash-card-label">Inactive</span>
            <strong className="dash-card-value">
              {(stats?.jobs.inactive ?? 0).toLocaleString("en-IN")}
            </strong>
            <span className="dash-card-hint">Expired or removed</span>
          </article>
          <article className="dash-card">
            <span className="dash-card-label">Total in database</span>
            <strong className="dash-card-value">
              {(stats?.jobs.total ?? 0).toLocaleString("en-IN")}
            </strong>
          </article>
          <article className="dash-card">
            <span className="dash-card-label">Search profiles</span>
            <strong className="dash-card-value">
              {stats?.search_profiles.total_active ?? "—"}
            </strong>
            <span className="dash-card-hint">
              {stats?.search_profiles.never_scraped ?? 0} never scraped ·{" "}
              {stats?.search_profiles.scraped_last_24h ?? 0} in last 24h
            </span>
          </article>
        </section>

        <section className="dash-panel dash-refresh-panel">
          <h3>Refresh jobs now</h3>
          <p className="dash-muted">
            Runs a scrape pass immediately in the background (oldest profiles first).
            Requires the same key as <code>ADMIN_API_KEY</code> on the API.
          </p>

          {showKeyForm && (
            <form className="dash-key-form" onSubmit={saveAdminKey}>
              <label>
                Admin API key
                <input
                  type="password"
                  value={adminKeyInput}
                  onChange={(e) => setAdminKeyInput(e.target.value)}
                  placeholder="Paste ADMIN_API_KEY"
                  autoComplete="off"
                />
              </label>
              <button type="submit" className="btn ghost">
                Save key
              </button>
            </form>
          )}

          {!showKeyForm && (
            <button
              type="button"
              className="btn ghost dash-key-change"
              onClick={() => setShowKeyForm(true)}
            >
              Change admin key
            </button>
          )}

          <div className="dash-refresh-actions">
            <label className="checkbox-label dash-full-scrape">
              <input
                type="checkbox"
                checked={fullScrape}
                onChange={(e) => setFullScrape(e.target.checked)}
                disabled={refreshing || stats?.scrape_in_progress}
              />
              Full India sync (~1080 profiles: all roles × cities × levels)
            </label>
            {!fullScrape && (
              <label>
                Profiles per run
                <select
                  value={refreshLimit}
                  onChange={(e) => setRefreshLimit(Number(e.target.value))}
                  disabled={refreshing || stats?.scrape_in_progress}
                >
                  {[1, 3, 5, 10, 15, 20].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <button
              type="button"
              className="btn primary"
              onClick={handleRefresh}
              disabled={refreshing || stats?.scrape_in_progress}
            >
              {refreshing
                ? "Starting…"
                : stats?.scrape_in_progress
                  ? "Scrape running…"
                  : fullScrape
                    ? "Start full sync"
                    : "Refresh jobs now"}
            </button>
            <button type="button" className="btn ghost" onClick={loadStats} disabled={loading}>
              Reload stats
            </button>
          </div>
        </section>

        <div className="dash-grid">
          <BreakdownTable
            title="By job board"
            rows={(stats?.by_site || []).map((r) => ({
              ...r,
              label: siteLabel(r.label),
            }))}
          />
          <BreakdownTable title="By role category" rows={stats?.by_role || []} />
          <BreakdownTable title="By experience band" rows={stats?.by_experience || []} />
          <BreakdownTable
            title="By job level"
            rows={stats?.by_job_level || []}
            emptyLabel="No job level data yet (mainly LinkedIn listings)"
          />
        </div>

        <section className="dash-panel">
          <h3>Recent scrape runs</h3>
          {!stats?.recent_scrape_runs?.length ? (
            <p className="dash-muted">No scrape runs yet. Trigger a refresh above.</p>
          ) : (
            <div className="dash-table-wrap">
              <table className="dash-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Profile</th>
                    <th>Status</th>
                    <th>Found</th>
                    <th>Upserted</th>
                    <th>Started</th>
                    <th>Finished</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_scrape_runs.map((run) => (
                    <tr key={run.id}>
                      <td>{run.id}</td>
                      <td>#{run.search_profile_id}</td>
                      <td>
                        <span className={`dash-status ${statusClass(run.status)}`}>
                          {run.status}
                        </span>
                      </td>
                      <td>{run.jobs_found}</td>
                      <td>{run.jobs_upserted}</td>
                      <td>{formatDateTime(run.started_at)}</td>
                      <td>{run.finished_at ? formatDateTime(run.finished_at) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>JobBoard India · Ops dashboard · Manual refresh uses JobSpy scrapers</p>
      </footer>
    </div>
  );
}
