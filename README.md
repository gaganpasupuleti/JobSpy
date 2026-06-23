# JobSpy Alerts Lab

Standalone **Jobs + Email Alerts** lab prototype for searching/importing jobs, saving alert rules, running demo scans, and generating console-only email notifications.

> **Email mode:** Console/log only — no real emails are sent. Every generated email is stored in the database and printed in the backend console.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + Tailwind CSS (shadcn-style components) — `http://localhost:3002` |
| Backend | FastAPI + SQLite + SQLAlchemy + Pydantic — `http://localhost:8002` |

## Setup

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3002](http://localhost:3002).

## Features

- **Jobs** — View, filter, and manually add job posts; import demo seed data
- **Alert rules** — Keyword/location/experience matching with active/inactive toggle
- **Demo scan** — Simulates a job scan: imports demo jobs (deduped), matches alerts, generates emails
- **Email logs** — View all generated notifications (console_sent status)
- **Scan history** — Track scan runs and match counts

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | API health check |
| GET | `/api/jobs` | List jobs (filter: keyword, location, source, experience_level) |
| POST | `/api/jobs` | Create manual job |
| POST | `/api/jobs/import-demo` | Insert demo jobs |
| GET | `/api/alerts` | List alert rules |
| POST | `/api/alerts` | Create alert rule |
| PATCH | `/api/alerts/{id}` | Update alert rule |
| DELETE | `/api/alerts/{id}` | Delete alert rule |
| POST | `/api/scans/run-demo` | Run demo scan |
| POST | `/api/alerts/{id}/send-test` | Send test email for alert |
| GET | `/api/email-notifications` | List email logs |
| GET | `/api/scan-runs` | List scan history |

## Manual Test Checklist

1. Start backend on port **8002**.
2. Start frontend on port **3002**.
3. Open the dashboard.
4. Click **Run Demo Scan**.
5. Verify jobs appear on the Jobs page.
6. Verify active alert rules match jobs (3 emails expected for seed alerts).
7. Verify email logs are created on the Email Logs page.
8. Verify backend console prints email content.
9. Create a new alert rule.
10. Run scan again.
11. Confirm no duplicate jobs are inserted.
12. Confirm emails are generated only for matching jobs (no duplicates for same alert+job).

## Out of Scope (this phase)

- No production SMTP / Gmail
- No login/auth
- No paid APIs
- No aggressive scraping
- No CodeQuest integration yet

## License

See [LICENSE](LICENSE) for the original JobSpy library license.
