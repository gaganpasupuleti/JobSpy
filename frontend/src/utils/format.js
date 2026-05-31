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

export function siteLabel(site) {
  const labels = {
    indeed: "Indeed",
    linkedin: "LinkedIn",
    naukri: "Naukri",
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
