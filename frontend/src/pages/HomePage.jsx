import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import Header from "../components/Header";
import JobFilters from "../components/JobFilters";
import JobCard from "../components/JobCard";
import JobDetail from "../components/JobDetail";
import {
  useSession,
  getSavedJobIds,
  addSavedJobId,
  removeSavedJobId,
} from "../hooks/useSession";

const DEFAULT_FILTERS = {
  keyword: "",
  company: "",
  role: "",
  location: "",
  experience: "",
  site: "",
  is_remote: "",
  page: 1,
  page_size: 12,
};

export default function HomePage() {
  const { sessionId } = useSession();
  const [tab, setTab] = useState("browse");
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [meta, setMeta] = useState({ roles: [], locations: [], bands: [] });
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("loading");
  const [selectedJob, setSelectedJob] = useState(null);
  const [applying, setApplying] = useState(false);
  const [savedIds, setSavedIds] = useState(getSavedJobIds());
  const [savedJobs, setSavedJobs] = useState([]);
  const [savedLoading, setSavedLoading] = useState(false);

  useEffect(() => {
    async function loadMeta() {
      try {
        await api.health();
        const [roles, locations, bands] = await Promise.all([
          api.getRoles(),
          api.getLocations(),
          api.getExperienceBands(),
        ]);
        setMeta({ roles, locations, bands });
        setApiStatus("ok");
      } catch {
        setApiStatus("error");
      }
    }
    loadMeta();
  }, []);

  const fetchJobs = useCallback(async (f = filters, jobBucket = "tagged") => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getJobs({ ...f, bucket: jobBucket });
      setJobs(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e.message);
      setJobs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    if (apiStatus !== "ok" || (tab !== "browse" && tab !== "others")) return;
    fetchJobs(filters, tab === "others" ? "others" : "tagged");
  }, [apiStatus, tab, fetchJobs, filters]);

  const loadSavedJobs = useCallback(async () => {
    const ids = getSavedJobIds();
    setSavedIds(ids);
    if (ids.length === 0) {
      setSavedJobs([]);
      return;
    }
    setSavedLoading(true);
    try {
      const results = await Promise.allSettled(ids.map((id) => api.getJob(id)));
      setSavedJobs(
        results
          .filter((r) => r.status === "fulfilled")
          .map((r) => r.value)
      );
    } finally {
      setSavedLoading(false);
    }
  }, []);

  useEffect(() => {
    if (tab === "saved" && apiStatus === "ok") loadSavedJobs();
  }, [tab, apiStatus, loadSavedJobs, savedIds.length]);

  function handleFilterChange(key, value) {
    if (key === "reset") {
      setFilters(DEFAULT_FILTERS);
      fetchJobs(DEFAULT_FILTERS, tab === "others" ? "others" : "tagged");
      return;
    }
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  }

  function handleSearch() {
    fetchJobs({ ...filters, page: 1 }, tab === "others" ? "others" : "tagged");
  }

  function jobBucketForTab() {
    return tab === "others" ? "others" : "tagged";
  }

  async function openJob(id) {
    try {
      const job = await api.getJob(id);
      setSelectedJob(job);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleApply(jobId) {
    setApplying(true);
    try {
      const { redirect_url } = await api.applyToJob(jobId, sessionId);
      window.open(redirect_url, "_blank", "noopener,noreferrer");
    } catch (e) {
      setError(e.message);
    } finally {
      setApplying(false);
    }
  }

  async function handleSave(jobId) {
    try {
      await api.saveJob(jobId, sessionId);
      addSavedJobId(jobId);
      setSavedIds(getSavedJobIds());
    } catch (e) {
      setError(e.message);
    }
  }

  function handleUnsave(jobId) {
    removeSavedJobId(jobId);
    setSavedIds(getSavedJobIds());
    setSavedJobs((prev) => prev.filter((j) => j.id !== jobId));
  }

  const totalPages = Math.ceil(total / filters.page_size) || 1;
  const displayJobs = tab === "saved" ? savedJobs : jobs;

  return (
    <div className="app">
      <Header
        tab={tab}
        onTabChange={setTab}
        savedCount={savedIds.length}
        apiStatus={apiStatus}
      />

      <main className="main">
        {apiStatus === "error" && (
          <div className="alert error">
            <strong>Backend not reachable.</strong> Start the API with{" "}
            <code>uvicorn app.main:app --reload --port 8000</code> in the{" "}
            <code>backend/</code> folder, then refresh.
          </div>
        )}

        {error && (
          <div className="alert error">
            {error}
            <button className="alert-dismiss" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {tab === "others" && (
          <section className="saved-header">
            <h2>Others</h2>
            <p>
              Jobs that need review: missing tags, uncertain role, or flagged mismatch.
              Fully tagged India jobs are under Browse.
            </p>
          </section>
        )}

        {(tab === "browse" || tab === "others") && (
          <>
            <JobFilters
              filters={filters}
              meta={meta}
              onChange={handleFilterChange}
              onSearch={handleSearch}
              loading={loading}
            />

            <section className="results-header">
              <p>
                {loading ? "Loading…" : (
                  <>
                    <strong>{total.toLocaleString("en-IN")}</strong> jobs found
                    {filters.role && meta.roles.find((r) => r.slug === filters.role) && (
                      <> in {meta.roles.find((r) => r.slug === filters.role).name}</>
                    )}
                  </>
                )}
              </p>
              {tab === "browse" && (
                <p className="dash-muted" style={{ margin: "0.35rem 0 0" }}>
                  Fully tagged: India + role + experience level
                </p>
              )}
            </section>
          </>
        )}

        {tab === "saved" && (
          <section className="saved-header">
            <h2>Saved jobs</h2>
            <p>Jobs you bookmarked on this device ({savedIds.length})</p>
          </section>
        )}

        {(tab === "browse" || tab === "others" ? loading : savedLoading) && displayJobs.length === 0 ? (
          <div className="empty-state">
            <div className="spinner" />
            <p>Loading jobs…</p>
          </div>
        ) : displayJobs.length === 0 ? (
          <div className="empty-state">
            <h3>
              {tab === "saved"
                ? "No saved jobs yet"
                : tab === "others"
                  ? "No jobs in Others"
                  : "No jobs found"}
            </h3>
            <p>
              {tab === "saved"
                ? "Click ☆ Save on any job to bookmark it here."
                : tab === "others"
                  ? "All scraped jobs are fully tagged, or run a scrape from the ops dashboard."
                  : "Try different filters or run a scrape on the ops dashboard."}
            </p>
          </div>
        ) : (
          <div className="job-grid">
            {displayJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                roles={meta.roles}
                bands={meta.bands}
                saved={savedIds.includes(job.id)}
                onSelect={openJob}
                onSave={handleSave}
                onUnsave={handleUnsave}
              />
            ))}
          </div>
        )}

        {(tab === "browse" || tab === "others") && totalPages > 1 && (
          <div className="pagination">
            <button
              className="btn ghost"
              disabled={filters.page <= 1 || loading}
              onClick={() => {
                const next = { ...filters, page: filters.page - 1 };
                setFilters(next);
                fetchJobs(next, jobBucketForTab());
              }}
            >
              ← Previous
            </button>
            <span>
              Page {filters.page} of {totalPages}
            </span>
            <button
              className="btn ghost"
              disabled={filters.page >= totalPages || loading}
              onClick={() => {
                const next = { ...filters, page: filters.page + 1 };
                setFilters(next);
                fetchJobs(next, jobBucketForTab());
              }}
            >
              Next →
            </button>
          </div>
        )}
      </main>

      {selectedJob && (
        <JobDetail
          job={selectedJob}
          roles={meta.roles}
          bands={meta.bands}
          saved={savedIds.includes(selectedJob.id)}
          applying={applying}
          onClose={() => setSelectedJob(null)}
          onApply={() => handleApply(selectedJob.id)}
          onSave={() => handleSave(selectedJob.id)}
          onUnsave={() => handleUnsave(selectedJob.id)}
        />
      )}

      <footer className="footer">
        <p>JobBoard India · Powered by JobSpy · Apply redirects to original job posting</p>
      </footer>
    </div>
  );
}
