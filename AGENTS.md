# AGENTS.md

## Cursor Cloud specific instructions

### Products in this repo

1. **JobSpy (`python-jobspy`)** — Python library for scraping job boards. Entry: `jobspy/__init__.py` (`scrape_jobs()`).
2. **Job Board India** — Full-stack app: FastAPI backend + React (Vite) frontend + PostgreSQL.

### PostgreSQL (local dev)

Docker Compose is defined in `backend/docker-compose.yml`, but Cloud Agent VMs may not have Docker. Use the system PostgreSQL service instead:

```bash
sudo pg_ctlcluster 16 main start   # if not already running
pg_isready -h localhost -p 5432
```

Database credentials match `.env.example`: `postgresql://postgres:postgres@localhost:5432/jobboard`. Create the DB once if missing:

```bash
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "CREATE DATABASE jobboard;"
```

### PATH

Python CLI tools (`uvicorn`, `alembic`, etc.) install to `~/.local/bin`. Prepend to PATH before running backend commands:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Starting services (split dev — recommended)

Run from repo root after copying `.env.example` → `.env`:

```bash
# 1. DB migrations (once per schema change)
cd backend && alembic upgrade head

# 2. API (tmux session recommended)
cd backend && uvicorn app.main:app --reload --port 8000

# 3. Frontend dev server (proxies /api and /health to :8000)
cd frontend && npm run dev
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Scraper worker (optional)

Populates the jobs table via JobSpy. Requires outbound internet:

```bash
python3 run_worker.py --once --limit 1
```

Or trigger via admin API: `POST /api/v1/admin/scrape/run?limit=1` with header `X-Admin-Key` (value from `.env`).

### Lint / tests

- **Lint**: `black --check jobspy backend` (pre-commit config in `.pre-commit-config.yaml` runs Black only).
- **Tests**: No automated test suite in this repo.
- **Frontend build**: `cd frontend && npm run build`

### Gotchas

- Use `python3`, not `python` — only `python3` is on PATH by default.
- The UI works with an empty jobs table (filters/meta load from seed data), but scraping is needed to demo job listings.
- Naukri may return HTTP 406 (recaptcha) during scrapes; Indeed/LinkedIn/Foundit can still succeed.
- Re-running `alembic upgrade head` is safe and idempotent.
