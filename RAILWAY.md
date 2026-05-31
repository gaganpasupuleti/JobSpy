# Railway deployment guide

Deploy **one combined service** (API + student frontend) or split services if you prefer.

## Single service (recommended)

One Railway service serves everything at one URL:

| Path | What |
|------|------|
| `/` | Student job board (React UI) |
| `/health` | API health check |
| `/docs` | Swagger API docs |
| `/api/v1/*` | REST API |

### Setup

1. **PostgreSQL** plugin → `DATABASE_URL` auto-injected
2. **JobSpy service** from GitHub (`gaganpasupuleti/JobSpy`, branch `main`)
   - Uses root `railway.toml` → `backend/Dockerfile`
   - Dockerfile builds frontend + API in one image
3. **Variables:**
   - `DATABASE_URL` → reference Postgres
   - `ADMIN_API_KEY` → your secret
   - `CORS_ORIGINS` → `*` (optional for same-origin)
4. **Generate Domain** → one URL for students and API

No `VITE_API_URL` needed — frontend calls the API on the same domain.

### Worker (optional, separate service)

Same `backend/Dockerfile`, start command:
```
python /app/run_worker.py --once --limit 10
```

## Split services (alternative)

If you prefer separate URLs, deploy a second service with `frontend/Dockerfile` and set `VITE_API_URL` to your API domain. See `frontend/README.md`.

## Trigger first scrape

```powershell
curl -X POST "https://YOUR-URL/api/v1/admin/scrape/run?limit=3" -H "X-Admin-Key: YOUR_KEY"
```
