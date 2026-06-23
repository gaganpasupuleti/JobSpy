import { useCallback, useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { api } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Card, CardContent } from "../components/ui/Card";
import { Table, TBody, TD, TH, THead, TR } from "../components/ui/Table";
import { formatDate } from "../lib/utils";

function statusVariant(status) {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  return "info";
}

export default function ScanRunsPage() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setRuns(await api.getScanRuns());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6 pb-16 md:pb-0">
      <div>
        <h2 className="text-2xl font-bold text-navy">Scan Runs</h2>
        <p className="text-sm text-slate-500">History of demo job scans</p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading...
        </div>
      ) : runs.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-slate-500">
            No scan runs yet. Run a demo scan from the dashboard.
          </CardContent>
        </Card>
      ) : (
        <Table>
          <THead>
            <TR>
              <TH>ID</TH>
              <TH>Source</TH>
              <TH>Status</TH>
              <TH>Jobs Found</TH>
              <TH>New Jobs</TH>
              <TH>Matched Alerts</TH>
              <TH>Started</TH>
              <TH>Completed</TH>
            </TR>
          </THead>
          <TBody>
            {runs.map((run) => (
              <TR key={run.id}>
                <TD>#{run.id}</TD>
                <TD>
                  <Badge variant="navy">{run.source}</Badge>
                </TD>
                <TD>
                  <Badge variant={statusVariant(run.status)}>{run.status}</Badge>
                </TD>
                <TD>{run.jobs_found_count}</TD>
                <TD>{run.new_jobs_count}</TD>
                <TD>{run.matched_alerts_count}</TD>
                <TD className="whitespace-nowrap text-xs">
                  {formatDate(run.created_at)}
                </TD>
                <TD className="whitespace-nowrap text-xs">
                  {formatDate(run.completed_at)}
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      )}
    </div>
  );
}
