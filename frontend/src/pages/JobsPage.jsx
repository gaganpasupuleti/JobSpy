import { useCallback, useEffect, useState } from "react";
import { ExternalLink, Loader2, Plus } from "lucide-react";
import { api } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Dialog } from "../components/ui/Dialog";
import { Input, Label, Select, Textarea } from "../components/ui/Input";
import { Table, TBody, TD, TH, THead, TR } from "../components/ui/Table";

const emptyJob = {
  title: "",
  company: "",
  location: "",
  source: "manual",
  job_url: "",
  description: "",
  experience_level: "",
  employment_type: "Full-time",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    keyword: "",
    location: "",
    source: "",
    experience_level: "",
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyJob);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getJobs(filters);
      setJobs(data);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  async function handleCreate(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createJob({
        ...form,
        job_url: form.job_url || null,
        description: form.description || null,
        experience_level: form.experience_level || null,
        employment_type: form.employment_type || null,
      });
      setDialogOpen(false);
      setForm(emptyJob);
      await load();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6 pb-16 md:pb-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-navy">Jobs</h2>
          <p className="text-sm text-slate-500">Search and manage job posts</p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Job
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Input
              placeholder="Keyword"
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
            />
            <Input
              placeholder="Location"
              value={filters.location}
              onChange={(e) => setFilters({ ...filters, location: e.target.value })}
            />
            <Input
              placeholder="Source"
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
            />
            <Input
              placeholder="Experience level"
              value={filters.experience_level}
              onChange={(e) =>
                setFilters({ ...filters, experience_level: e.target.value })
              }
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading jobs...
        </div>
      ) : jobs.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-slate-500">
            No jobs found. Run a demo scan from the dashboard or add a job manually.
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="hidden md:block">
            <Table>
              <THead>
                <TR>
                  <TH>Title</TH>
                  <TH>Company</TH>
                  <TH>Location</TH>
                  <TH>Experience</TH>
                  <TH>Source</TH>
                  <TH>Link</TH>
                </TR>
              </THead>
              <TBody>
                {jobs.map((job) => (
                  <TR key={job.id}>
                    <TD className="font-medium">{job.title}</TD>
                    <TD>{job.company}</TD>
                    <TD>{job.location}</TD>
                    <TD>{job.experience_level || "—"}</TD>
                    <TD>
                      <Badge variant="navy">{job.source}</Badge>
                    </TD>
                    <TD>
                      {job.job_url ? (
                        <a
                          href={job.job_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-navy hover:underline"
                        >
                          Open <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        "—"
                      )}
                    </TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          </div>
          <div className="grid gap-3 md:hidden">
            {jobs.map((job) => (
              <Card key={job.id}>
                <CardContent className="space-y-2 pt-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold text-navy">{job.title}</p>
                    <Badge variant="navy">{job.source}</Badge>
                  </div>
                  <p className="text-sm text-slate-600">
                    {job.company} · {job.location}
                  </p>
                  <p className="text-xs text-slate-500">
                    {job.experience_level || "Any experience"}
                  </p>
                  {job.job_url && (
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm text-navy hover:underline"
                    >
                      View job
                    </a>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} title="Add Manual Job">
        <form onSubmit={handleCreate} className="space-y-3">
          <div>
            <Label>Title</Label>
            <Input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label>Company</Label>
              <Input required value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
            </div>
            <div>
              <Label>Location</Label>
              <Input required value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label>Experience Level</Label>
              <Input value={form.experience_level} onChange={(e) => setForm({ ...form, experience_level: e.target.value })} />
            </div>
            <div>
              <Label>Employment Type</Label>
              <Select value={form.employment_type} onChange={(e) => setForm({ ...form, employment_type: e.target.value })}>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </Select>
            </div>
          </div>
          <div>
            <Label>Job URL</Label>
            <Input value={form.job_url} onChange={(e) => setForm({ ...form, job_url: e.target.value })} />
          </div>
          <div>
            <Label>Description</Label>
            <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save Job"}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
