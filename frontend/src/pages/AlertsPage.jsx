import { useCallback, useEffect, useState } from "react";
import { Loader2, Mail, Trash2 } from "lucide-react";
import { api } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Checkbox, Input, Label } from "../components/ui/Input";

const emptyAlert = {
  alert_name: "",
  recipient_name: "",
  recipient_email: "",
  keywords: "",
  location: "",
  experience_level: "",
  is_active: true,
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(emptyAlert);
  const [saving, setSaving] = useState(false);
  const [testingId, setTestingId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setAlerts(await api.getAlerts());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleCreate(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createAlert({
        ...form,
        location: form.location || "",
        experience_level: form.experience_level || null,
      });
      setForm(emptyAlert);
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive(alert) {
    await api.updateAlert(alert.id, { is_active: !alert.is_active });
    await load();
  }

  async function handleDelete(id) {
    if (!confirm("Delete this alert rule?")) return;
    await api.deleteAlert(id);
    await load();
  }

  async function handleTest(id) {
    setTestingId(id);
    try {
      await api.sendTestAlert(id);
      alert("Test email generated — check backend console and Email Logs page.");
    } catch (err) {
      alert(err.message);
    } finally {
      setTestingId(null);
    }
  }

  return (
    <div className="space-y-6 pb-16 md:pb-0">
      <div>
        <h2 className="text-2xl font-bold text-navy">Alert Rules</h2>
        <p className="text-sm text-slate-500">Create and manage job alert rules</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Create Alert Rule</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label>Alert Name</Label>
              <Input required value={form.alert_name} onChange={(e) => setForm({ ...form, alert_name: e.target.value })} />
            </div>
            <div>
              <Label>Keywords</Label>
              <Input required value={form.keywords} onChange={(e) => setForm({ ...form, keywords: e.target.value })} placeholder="e.g. Python" />
            </div>
            <div>
              <Label>Recipient Name</Label>
              <Input required value={form.recipient_name} onChange={(e) => setForm({ ...form, recipient_name: e.target.value })} />
            </div>
            <div>
              <Label>Recipient Email</Label>
              <Input required type="email" value={form.recipient_email} onChange={(e) => setForm({ ...form, recipient_email: e.target.value })} />
            </div>
            <div>
              <Label>Location (optional)</Label>
              <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="Leave empty for any" />
            </div>
            <div>
              <Label>Experience Level (optional)</Label>
              <Input value={form.experience_level} onChange={(e) => setForm({ ...form, experience_level: e.target.value })} />
            </div>
            <div className="flex items-center gap-2 sm:col-span-2">
              <Checkbox
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                id="is_active"
              />
              <Label htmlFor="is_active">Active</Label>
            </div>
            <div className="sm:col-span-2">
              <Button type="submit" disabled={saving}>
                {saving ? "Creating..." : "Create Alert"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading alerts...
        </div>
      ) : (
        <div className="grid gap-4">
          {alerts.map((alert) => (
            <Card key={alert.id}>
              <CardContent className="flex flex-wrap items-start justify-between gap-4 pt-6">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-navy">{alert.alert_name}</h3>
                    <Badge variant={alert.is_active ? "success" : "default"}>
                      {alert.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-600">
                    Keywords: <strong>{alert.keywords}</strong>
                    {alert.location && ` · Location: ${alert.location}`}
                    {alert.experience_level && ` · Exp: ${alert.experience_level}`}
                  </p>
                  <p className="text-sm text-slate-500">
                    {alert.recipient_name} &lt;{alert.recipient_email}&gt;
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm" onClick={() => toggleActive(alert)}>
                    {alert.is_active ? "Deactivate" : "Activate"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTest(alert.id)}
                    disabled={testingId === alert.id}
                  >
                    <Mail className="mr-1 h-3 w-3" />
                    {testingId === alert.id ? "Sending..." : "Send Test"}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(alert.id)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
