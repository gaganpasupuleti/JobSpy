import { useCallback, useEffect, useState } from "react";
import { Eye, Loader2 } from "lucide-react";
import { api } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardContent } from "../components/ui/Card";
import { Dialog } from "../components/ui/Dialog";
import { Table, TBody, TD, TH, THead, TR } from "../components/ui/Table";
import { formatDate } from "../lib/utils";

function statusVariant(status) {
  if (status === "console_sent") return "success";
  if (status === "failed") return "danger";
  return "warning";
}

export default function EmailLogsPage() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setEmails(await api.getEmailNotifications());
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
        <h2 className="text-2xl font-bold text-navy">Email Logs</h2>
        <p className="text-sm text-slate-500">Generated email notifications (console mode)</p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading...
        </div>
      ) : emails.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-slate-500">
            No emails yet. Run a demo scan or send a test alert.
          </CardContent>
        </Card>
      ) : (
        <Table>
          <THead>
            <TR>
              <TH>Recipient</TH>
              <TH>Subject</TH>
              <TH>Matched Job</TH>
              <TH>Status</TH>
              <TH>Created</TH>
              <TH>Sent</TH>
              <TH></TH>
            </TR>
          </THead>
          <TBody>
            {emails.map((email) => (
              <TR key={email.id}>
                <TD>{email.to_email}</TD>
                <TD className="max-w-[200px] truncate">{email.subject}</TD>
                <TD>
                  {email.job_title
                    ? `${email.job_title} @ ${email.company}`
                    : "—"}
                </TD>
                <TD>
                  <Badge variant={statusVariant(email.status)}>{email.status}</Badge>
                </TD>
                <TD className="whitespace-nowrap text-xs">
                  {formatDate(email.created_at)}
                </TD>
                <TD className="whitespace-nowrap text-xs">
                  {formatDate(email.sent_at)}
                </TD>
                <TD>
                  <Button variant="ghost" size="sm" onClick={() => setSelected(email)}>
                    <Eye className="h-4 w-4" />
                  </Button>
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      )}

      <Dialog
        open={!!selected}
        onClose={() => setSelected(null)}
        title="Email Body"
        className="max-w-2xl"
      >
        {selected && (
          <div className="space-y-3">
            <p className="text-sm">
              <strong>To:</strong> {selected.to_email}
            </p>
            <p className="text-sm">
              <strong>Subject:</strong> {selected.subject}
            </p>
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-cream-dark p-4 text-sm">
              {selected.body}
            </pre>
          </div>
        )}
      </Dialog>
    </div>
  );
}
