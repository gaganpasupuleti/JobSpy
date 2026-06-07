# Job Board Backend (Railway)

FastAPI + PostgreSQL job board backend that scrapes India job listings via JobSpy and exposes REST APIs for a student frontend.

## Local setup

1. Copy env file:
   ```bash
   cp .env.example .env
   ```

2. Start Postgres (Docker):
   ```bash
   cd backend
   docker compose up -d db
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   pip install -e .
   ```

4. Run migrations and seed:
   ```bash
   cd backend
   alembic upgrade head
   ```

5. Start API:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

6. Run scraper worker (one profile):
   ```bash
   python run_worker.py --once --limit 1
   ```

API docs: http://localhost:8000/docs

### Test student logins

| Email | Password |
|-------|----------|
| `student@jobboard.test` | `Student123!` |
| `demo@jobboard.test` | `Demo123!` |
| `priya@jobboard.test` | `Priya123!` |

Sign in at `/login`. Accounts are seeded on API startup. Set `AUTH_SECRET` in production.

## Railway deployment

Create a new Railway project with three components:

1. **PostgreSQL** — add the plugin; Railway injects `DATABASE_URL`.
2. **API service** — connect this repo, use `backend/Dockerfile` with repo root as build context.
   - Env vars: `DATABASE_URL`, `ADMIN_API_KEY`, `CORS_ORIGINS`
   - Health check: `/health`
3. **Worker service** — same Docker image, override start command:
   ```
   python /app/run_worker.py --once --limit 10
   ```
   Or use Railway Cron every 6 hours with the same command.

### Manual scrape trigger

```bash
curl -X POST "https://YOUR-API.railway.app/api/v1/admin/scrape/run?limit=1" \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY"
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/jobs` | List jobs (filters: role, location, experience, keyword, site) |
| GET | `/api/v1/jobs/{id}` | Job detail |
| POST | `/api/v1/jobs/{id}/apply` | Track apply + get redirect URL |
| POST | `/api/v1/jobs/{id}/save` | Bookmark job |
| GET | `/api/v1/meta/roles` | Role categories |
| GET | `/api/v1/meta/locations` | Cities |
| GET | `/api/v1/meta/experience-bands` | Experience levels |
| GET | `/api/v1/meta/keywords?role=` | Keywords by role |
| POST | `/api/v1/admin/scrape/run` | Trigger scrape (requires `X-Admin-Key`) |
| GET | `/api/v1/admin/scrape/runs` | Scrape history |
| GET | `/api/v1/dashboard/stats` | Job health metrics (ops UI) |
| POST | `/api/v1/dashboard/refresh` | Background scrape (requires `X-Admin-Key`) |
| GET | `/api/v1/dashboard/refresh/status` | Scrape in-progress status |
| GET | `/api/v1/jobs?bucket=tagged\|others` | Student browse: fully tagged vs review queue |
| POST | `/api/v1/admin/jobs/retag` | Recompute tags on existing jobs |
| GET | `/api/v1/admin/tagging/queue` | Jobs needing manual tags (admin key) |
| PATCH | `/api/v1/admin/tagging/{id}` | Set role, level, India, approve |

After deploy, run migration `alembic upgrade head`, then `POST /api/v1/admin/jobs/retag` once to tag existing rows.

## Seed data

On startup the API seeds:
- 12 role categories with keywords
- 15 India locations
- 1080 search profiles (12 roles × 15 cities × 6 experience levels)
