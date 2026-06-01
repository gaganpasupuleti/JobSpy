import { siteLabel, parseSkills } from "../utils/format";

export default function JobCard({ job, roles, bands, saved, onSelect, onSave, onUnsave }) {
  const salary = job.min_amount || job.max_amount
    ? `${job.currency || ""} ${job.min_amount || ""}${job.max_amount ? `–${job.max_amount}` : ""}`
    : null;

  const skills = parseSkills(job.key_skills).slice(0, 4);

  return (
    <article className="job-card" onClick={() => onSelect(job.id)}>
      <div className="job-card-top">
        <span className={`site-badge site-${job.site}`}>{siteLabel(job.site)}</span>
        {job.is_remote && <span className="remote-badge">Remote</span>}
        {job.tag_status && job.tag_status !== "complete" && (
          <span className={`tag-badge tag-${job.tag_status}`}>
            {job.needs_review ? "Review" : job.tag_status}
          </span>
        )}
        <button
          className={`save-btn ${saved ? "saved" : ""}`}
          title={saved ? "Remove from saved" : "Save job"}
          onClick={(e) => {
            e.stopPropagation();
            saved ? onUnsave(job.id) : onSave(job.id);
          }}
        >
          {saved ? "★ Saved" : "☆ Save"}
        </button>
      </div>
      <h3 className="job-title">{job.title}</h3>
      <p className="job-company">{job.company_name || "Company not listed"}</p>
      <p className="job-location">
        {job.location_display || [job.city, job.state].filter(Boolean).join(", ") || "India"}
      </p>
      {skills.length > 0 && (
        <div className="skill-chips compact">
          {skills.map((skill) => (
            <span key={skill} className="skill-chip">{skill}</span>
          ))}
          {parseSkills(job.key_skills).length > 4 && (
            <span className="skill-chip more">+{parseSkills(job.key_skills).length - 4}</span>
          )}
        </div>
      )}
      <div className="job-meta">
        {salary && <span className="meta-chip salary">{salary}</span>}
        {job.job_type && <span className="meta-chip">{job.job_type}</span>}
        {job.date_posted && (
          <span className="meta-chip muted">{new Date(job.date_posted).toLocaleDateString("en-IN")}</span>
        )}
      </div>
    </article>
  );
}
