import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, getAdminKey, setAdminKey } from "../api/client";
import Header from "../components/Header";
import { formatDateTime, siteLabel } from "../utils/format";

const STATUS_FILTERS = [
  { value: "", label: "All review queue" },
  { value: "flagged", label: "Flagged" },
  { value: "untagged", label: "Untagged" },
  { value: "partial", label: "Partial" },
  { value: "non_india", label: "Non-India" },
];

export default function TaggingPage() {
  const [apiStatus, setApiStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [adminKeyInput, setAdminKeyInput] = useState(() => getAdminKey() || "");
  const [showKeyForm, setShowKeyForm] = useState(!getAdminKey());

  const [roles, setRoles] = useState([]);
  const [bands, setBands] = useState([]);
  const [page, setPage] = useState(1);
  const pageSize = 25;
  const [queue, setQueue] = useState({ items: [], total: 0 });
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    role: "",
    experience: "",
    is_india_verified: true,
    approve: true,
  });

  const adminKey = getAdminKey();

  const loadQueue = useCallback(async () => {
    if (!adminKey) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getTaggingQueue(
        {
          tag_status: statusFilter || undefined,
          q: search || undefined,
          page,
          page_size: pageSize,
        },
        adminKey
      );
      setQueue({ items: data.items, total: data.total });
      setApiStatus("ok");
    } catch (e) {
      setError(e.message);
      setApiStatus("error");
    } finally {
      setLoading(false);
    }
  }, [adminKey, statusFilter, search, page, pageSize]);

  useEffect(() => {
    async function init() {
      try {
        await api.health();
        const [r, b] = await Promise.all([api.getRoles(), api.getExperienceBands()]);
        setRoles(r);
        setBands(b);
        setApiStatus("ok");
      } catch {
        setApiStatus("error");
      }
    }
    init();
  }, []);

  useEffect(() => {
    if (adminKey) loadQueue();
  }, [adminKey, loadQueue]);

  async function loadDetail(id) {
    if (!adminKey) return;
    setSelectedId(id);
    setMessage(null);
    try {
      const job = await api.getTaggingJob(id, adminKey);
      setDetail(job);
      const roleSlug = roles.find((r) => r.id === job.role_category_id)?.slug || "";
      const bandSlug = bands.find((b) => b.id === job.experience_band_id)?.slug || "";
      setForm({
        role: roleSlug,
        experience: bandSlug,
        is_india_verified: job.is_india_verified ?? true,
        approve: true,
      });
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSave() {
    if (!adminKey || !selectedId) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const res = await api.updateJobTags(
        selectedId,
        {
          role: form.role || undefined,
          experience: form.experience || undefined,
          is_india_verified: form.is_india_verified,
          approve: form.approve,
        },
        adminKey
      );
      setMessage(res.message);
      await loadQueue();
      const item = queue.items.find((j) => j.id === selectedId);
      if (item) {
        setDetail((d) => (d ? { ...d, tag_status: res.tag_status } : d));
      }
      if (res.tag_status === "complete") {
        const idx = queue.items.findIndex((j) => j.id === selectedId);
        const next = queue.items[idx + 1];
        if (next) loadDetail(next.id);
        else setSelectedId(null);
        setDetail(null);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  function saveAdminKey(e) {
    e.preventDefault();
    setAdminKey(adminKeyInput.trim());
    setShowKeyForm(false);
  }

  const selectedItem = queue.items.find((j) => j.id === selectedId);

  return (
    <div className="app">
      <Header apiStatus={apiStatus} variant="dashboard" />

      <main className="main tagging-main">
        <div className="tagging-header">
          <div>
            <h2 className="dash-title">Internal tagging tool</h2>
            <p className="dash-subtitle">
              Manually set role, experience level, and India verification. Approve to move jobs to Browse.
            </p>
          </div>
          <div className="tagging-nav-links">
            <Link to="/dashboard" className="header-link tagging-back">
              ← Ops dashboard
            </Link>
            <Link to="/" className="header-link tagging-back">
              Student site
            </Link>
          </div>
        </div>

        {showKeyForm && (
          <section className="dash-panel">
            <h3>Admin API key required</h3>
            <form className="dash-key-form" onSubmit={saveAdminKey}>
              <label>
                Admin API key
                <input
                  type="password"
                  value={adminKeyInput}
                  onChange={(e) => setAdminKeyInput(e.target.value)}
                  placeholder="Same as ADMIN_API_KEY on Railway"
                />
              </label>
              <button type="submit" className="btn primary">
                Unlock tool
              </button>
            </form>
          </section>
        )}

        {!showKeyForm && !adminKey && (
          <div className="alert error">Set admin key to use this tool.</div>
        )}

        {error && (
          <div className="alert error">
            {error}
            <button className="alert-dismiss" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {message && (
          <div className="alert" style={{ background: "#e8f5ee", color: "var(--success)" }}>
            {message}
          </div>
        )}

        {adminKey && (
          <div className="tagging-layout">
            <aside className="tagging-queue dash-panel">
              <div className="tagging-queue-toolbar">
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                >
                  {STATUS_FILTERS.map((f) => (
                    <option key={f.value} value={f.value}>
                      {f.label}
                    </option>
                  ))}
                </select>
                <input
                  type="search"
                  placeholder="Search title or company"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && loadQueue()}
                />
                <button type="button" className="btn ghost" onClick={loadQueue} disabled={loading}>
                  Search
                </button>
              </div>

              <p className="dash-muted">
                <strong>{queue.total}</strong> jobs in queue
              </p>

              <ul className="tagging-queue-list">
                {queue.items.map((job) => (
                  <li key={job.id}>
                    <button
                      type="button"
                      className={`tagging-queue-item ${selectedId === job.id ? "active" : ""}`}
                      onClick={() => loadDetail(job.id)}
                    >
                      <span className={`tag-badge tag-${job.tag_status}`}>{job.tag_status}</span>
                      <strong>{job.title}</strong>
                      <span className="tagging-queue-meta">
                        {job.company_name || "—"} · {siteLabel(job.site)}
                      </span>
                      {job.review_reason && (
                        <span className="tagging-queue-flag">{job.review_reason}</span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>

              {queue.total > pageSize && (
                <div className="tagging-pager">
                  <button
                    type="button"
                    className="btn ghost"
                    disabled={page <= 1 || loading}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    ←
                  </button>
                  <span>
                    {page} / {Math.ceil(queue.total / pageSize)}
                  </span>
                  <button
                    type="button"
                    className="btn ghost"
                    disabled={page * pageSize >= queue.total || loading}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    →
                  </button>
                </div>
              )}
            </aside>

            <section className="tagging-editor dash-panel">
              {!selectedItem ? (
                <p className="dash-muted">Select a job from the queue to tag it.</p>
              ) : (
                <>
                  <div className="tagging-editor-head">
                    <h3>{selectedItem.title}</h3>
                    <p>
                      {selectedItem.company_name} · {siteLabel(selectedItem.site)} ·{" "}
                      {selectedItem.location_display || "India"}
                    </p>
                    {selectedItem.profile_role_name && (
                      <p className="tagging-hint">
                        Found via scrape profile: <strong>{selectedItem.profile_role_name}</strong>
                        {selectedItem.role_name && selectedItem.profile_role_name !== selectedItem.role_name && (
                          <> → classifier suggests <strong>{selectedItem.role_name}</strong></>
                        )}
                      </p>
                    )}
                    <a
                      href={detail?.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn ghost"
                    >
                      Open posting ↗
                    </a>
                  </div>

                  <form
                    className="tagging-form"
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleSave();
                    }}
                  >
                    <label>
                      Role category
                      <select
                        value={form.role}
                        onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                        required
                      >
                        <option value="">— Select role —</option>
                        {roles.map((r) => (
                          <option key={r.slug} value={r.slug}>
                            {r.name}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Experience level
                      <select
                        value={form.experience}
                        onChange={(e) => setForm((f) => ({ ...f, experience: e.target.value }))}
                        required
                      >
                        <option value="">— Select level —</option>
                        {bands.map((b) => (
                          <option key={b.slug} value={b.slug}>
                            {b.label}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={form.is_india_verified}
                        onChange={(e) =>
                          setForm((f) => ({ ...f, is_india_verified: e.target.checked }))
                        }
                      />
                      Verified India job
                    </label>

                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={form.approve}
                        onChange={(e) => setForm((f) => ({ ...f, approve: e.target.checked }))}
                      />
                      Clear review flag (approve for publishing)
                    </label>

                    <div className="tagging-form-actions">
                      <button type="submit" className="btn primary" disabled={saving}>
                        {saving ? "Saving…" : "Save & approve"}
                      </button>
                    </div>
                  </form>

                  {detail?.description && (
                    <div className="tagging-description">
                      <h4>Description</h4>
                      <div className="description-body">{detail.description.slice(0, 2000)}</div>
                    </div>
                  )}

                  <dl className="tagging-facts">
                    <div>
                      <dt>Status</dt>
                      <dd>{selectedItem.tag_status}</dd>
                    </div>
                    <div>
                      <dt>Scraped</dt>
                      <dd>{formatDateTime(selectedItem.scraped_at)}</dd>
                    </div>
                    <div>
                      <dt>Match score</dt>
                      <dd>{selectedItem.role_match_score ?? "—"}</dd>
                    </div>
                  </dl>
                </>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
