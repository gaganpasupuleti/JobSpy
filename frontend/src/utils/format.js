export function formatSalary(job) {
  if (!job.min_amount && !job.max_amount) return null;
  const cur = job.currency || "INR";
  const fmt = (n) =>
    new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(n);
  const interval = job.salary_interval ? ` / ${job.salary_interval}` : "";
  if (job.min_amount && job.max_amount) {
    return `${cur} ${fmt(job.min_amount)} – ${fmt(job.max_amount)}${interval}`;
  }
  return `${cur} ${fmt(job.min_amount || job.max_amount)}${interval}`;
}

export function formatDate(d) {
  if (!d) return "Recently posted";
  return new Date(d).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(d) {
  if (!d) return "—";
  return new Date(d).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function siteLabel(site) {
  const labels = {
    indeed: "Indeed",
    linkedin: "LinkedIn",
    naukri: "Naukri",
    foundit: "Foundit",
    glassdoor: "Glassdoor",
  };
  return labels[site] || site;
}

export function experienceLabel(bands, bandId) {
  const band = bands.find((b) => b.id === bandId);
  return band?.label || null;
}

export function roleLabel(roles, roleId) {
  const role = roles.find((r) => r.id === roleId);
  return role?.name || null;
}

export function parseSkills(keySkills) {
  if (!keySkills) return [];
  return keySkills.split(",").map((s) => s.trim()).filter(Boolean);
}
