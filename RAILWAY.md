# Railway deployment guide

Deploy **3 services** from this repo on [Railway](https://railway.app):

## 1. PostgreSQL
- Add **PostgreSQL** plugin to your project
- Railway auto-injects `DATABASE_URL`

## 2. API service
- **Root directory:** repo root
- **Config file:** `railway.toml`
- **Dockerfile:** `backend/Dockerfile`
- **Variables:**
  - `DATABASE_URL` → reference from Postgres service
  - `ADMIN_API_KEY` → generate a secret
  - `CORS_ORIGINS` → `*` or your frontend URL
- **Health check:** `/health`
- Generate domain → note URL e.g. `https://jobboard-api-production.up.railway.app`

## 3. Frontend service
- **Root directory:** repo root
- **Config file:** `frontend/railway.toml`
- **Dockerfile:** `frontend/Dockerfile`
- **Build variable:**
  - `VITE_API_URL` = `https://YOUR-API-URL.railway.app` (no trailing slash)
- Generate domain → public student portal

## 4. Worker service (optional)
- Same image as API (`backend/Dockerfile`)
- **Start command:** `python /app/run_worker.py --once --limit 10`
- Link same `DATABASE_URL`
- Use Railway Cron every 6 hours

## CLI deploy (after `railway login`)

```powershell
cd JobSpy
railway init
railway add --database postgres
railway variables set ADMIN_API_KEY=your-secret-key
railway up
railway domain
```

## Trigger first scrape

```powershell
curl -X POST "https://YOUR-API/api/v1/admin/scrape/run?limit=1" -H "X-Admin-Key: your-secret-key"
```
