export default function JobFilters({ filters, meta, onChange, onSearch, loading }) {
  return (
    <section className="filters-panel">
      <h2>Find your next role</h2>
      <p className="filters-sub">Search jobs across India — filter by role, city, and experience.</p>

      <div className="filters-grid">
        <label>
          Keyword
          <input
            type="text"
            placeholder="e.g. data analyst, Python, fresher"
            value={filters.keyword}
            onChange={(e) => onChange("keyword", e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
          />
        </label>

        <label>
          Role category
          <select value={filters.role} onChange={(e) => onChange("role", e.target.value)}>
            <option value="">All roles</option>
            {meta.roles.map((r) => (
              <option key={r.slug} value={r.slug}>
                {r.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          City
          <select value={filters.location} onChange={(e) => onChange("location", e.target.value)}>
            <option value="">All cities</option>
            {meta.locations.map((l) => (
              <option key={l.id} value={l.city}>
                {l.display_name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Experience
          <select value={filters.experience} onChange={(e) => onChange("experience", e.target.value)}>
            <option value="">All levels</option>
            {meta.bands.map((b) => (
              <option key={b.slug} value={b.slug}>
                {b.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Source
          <select value={filters.site} onChange={(e) => onChange("site", e.target.value)}>
            <option value="">All sources</option>
            <option value="indeed">Indeed</option>
            <option value="linkedin">LinkedIn</option>
            <option value="naukri">Naukri</option>
          </select>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.is_remote === "true"}
            onChange={(e) => onChange("is_remote", e.target.checked ? "true" : "")}
          />
          Remote only
        </label>
      </div>

      <div className="filters-actions">
        <button className="btn primary" onClick={onSearch} disabled={loading}>
          {loading ? "Searching…" : "Search jobs"}
        </button>
        <button
          className="btn ghost"
          onClick={() => {
            onChange("reset");
          }}
        >
          Clear filters
        </button>
      </div>
    </section>
  );
}
