import { useCallback, useEffect, useState } from "react";
import { Loader2, Play } from "lucide-react";
import { api } from "../api/client";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { formatDate } from "../lib/utils";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    jobs: 0,
    activeAlerts: 0,
    emails: 0,
    lastScan: null,
  });
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [jobs, alerts, emails, scans] = await Promise.all([
        api.getJobs(),
        api.getAlerts(),
        api.getEmailNotifications(),
        api.getScanRuns(),
      ]);
      setStats({
        jobs: jobs.length,
        activeAlerts: alerts.filter((a) => a.is_active).length,
        emails: emails.length,
        lastScan: scans[0] || null,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleRunScan() {
    setScanning(true);
    setMessage("");
    try {
      const result = await api.runDemoScan();
      setMessage(
        `Scan complete: ${result.scan_run.new_jobs_count} new jobs, ${result.emails_generated} emails generated.`
      );
      await load();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setScanning(false);
    }
  }

  const statusVariant =
    stats.lastScan?.status === "completed"
      ? "success"
      : stats.lastScan?.status === "failed"
        ? "danger"
        : "default";

  return (
    <div className="space-y-6 pb-16 md:pb-0">
      <div>
        <h2 className="text-2xl font-bold text-navy">Dashboard</h2>
        <p className="text-sm text-slate-500">Overview of jobs, alerts, and scans</p>
      </div>

      <Alert variant="info">
        Console email mode enabled. No real emails will be sent.
      </Alert>

      {message && <Alert variant="success">{message}</Alert>}

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading...
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Jobs" value={stats.jobs} />
          <StatCard title="Active Alerts" value={stats.activeAlerts} />
          <StatCard title="Emails Generated" value={stats.emails} />
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">
                Last Scan
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats.lastScan ? (
                <div className="space-y-1">
                  <Badge variant={statusVariant}>{stats.lastScan.status}</Badge>
                  <p className="text-xs text-slate-500">
                    {formatDate(stats.lastScan.created_at)}
                  </p>
                </div>
              ) : (
                <p className="text-2xl font-bold text-navy">—</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Run Demo Scan</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-600">
            Imports demo jobs (if missing), matches active alert rules, and generates
            console email notifications.
          </p>
          <Button onClick={handleRunScan} disabled={scanning}>
            {scanning ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Play className="mr-2 h-4 w-4" />
            )}
            Run Demo Scan
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ title, value }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold text-navy">{value}</p>
      </CardContent>
    </Card>
  );
}
