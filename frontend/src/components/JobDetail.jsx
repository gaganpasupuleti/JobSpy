import { formatDate, formatSalary, siteLabel, experienceLabel, roleLabel, parseSkills } from "../utils/format";

export default function JobDetail({
  job,
  roles,
  bands,
  saved,
  applying,
  onClose,
  onApply,
  onSave,
  onUnsave,
}) {
  if (!job) return null;

  const salary = formatSalary(job);
  const exp = experienceLabel(bands, job.experience_band_id);
  const role = roleLabel(roles, job.role_category_id);
  const skills = parseSkills(job.key_skills);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal job-detail" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="detail-header">
          <span className={`site-badge site-${job.site}`}>{siteLabel(job.site)}</span>
          {job.is_remote && <span className="remote-badge">Remote</span>}
          {role && <span className="meta-chip">{role}</span>}
          {exp && <span className="meta-chip">{exp}</span>}
        </div>

        <h2>{job.title}</h2>
        <p className="detail-company">{job.company_name}</p>
        <p className="detail-location">
          {job.location_display || [job.city, job.state, job.country].filter(Boolean).join(", ")}
        </p>

        <div className="detail-facts">
          {salary && <div><strong>Salary</strong> {salary}</div>}
          {job.job_type && <div><strong>Type</strong> {job.job_type}</div>}
          {job.date_posted && <div><strong>Posted</strong> {formatDate(job.date_posted)}</div>}
          {job.company_industry && <div><strong>Industry</strong> {job.company_industry}</div>}
          {job.job_level && <div><strong>Level</strong> {job.job_level}</div>}
          {(job.experience_years_min != null || job.experience_years_max != null) && (
            <div>
              <strong>Experience</strong>{" "}
              {job.experience_years_min ?? 0}–{job.experience_years_max ?? "+"} years
            </div>
          )}
        </div>

        {skills.length > 0 && (
          <div className="detail-skills">
            <h3>Key skills</h3>
            <div className="skill-chips">
              {skills.map((skill) => (
                <span key={skill} className="skill-chip">{skill}</span>
              ))}
            </div>
          </div>
        )}

        {job.description && (
          <div className="detail-description">
            <h3>Job description</h3>
            <div className="description-body">{job.description}</div>
          </div>
        )}

        {!job.description && !skills.length && (
          <p className="detail-empty-note">
            Full description not available from {siteLabel(job.site)}. Click Apply to view on the original posting.
          </p>
        )}

        <div className="detail-actions">
          <button className="btn primary lg" onClick={onApply} disabled={applying}>
            {applying ? "Opening…" : "Apply on " + siteLabel(job.site)}
          </button>
          <button
            className={`btn ${saved ? "saved" : "ghost"}`}
            onClick={() => (saved ? onUnsave() : onSave())}
          >
            {saved ? "★ Saved" : "☆ Save for later"}
          </button>
          {job.company_url && (
            <a className="btn ghost" href={job.company_url} target="_blank" rel="noreferrer">
              View company
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
