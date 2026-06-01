# JobBoard India — Test Frontend

Student job portal UI for the JobSpy backend API.

## Features

- **Browse jobs** with filters: keyword, role, city, experience, source, remote
- **Pagination** through results
- **Job detail modal** with full description, salary, company info
- **Apply** — tracks apply via API, opens original posting in new tab
- **Save jobs** — bookmarks synced to backend + localStorage
- **Saved jobs tab** — view all bookmarked roles
- **API status** indicator in header
- **Ops dashboard** at `/dashboard` — live/inactive job counts, breakdowns, last updated, manual scrape refresh

## Quick start

1. Start the backend (Postgres required):
   ```bash
   cd backend
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```

2. Install and run frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open http://localhost:5173

The Vite dev server proxies `/api` and `/health` to `localhost:8000`.

## Production / Railway

Set the API URL when building:

```bash
VITE_API_URL=https://your-api.railway.app npm run build
```

Deploy the `dist/` folder to Vercel, Netlify, or Railway static hosting.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `""` (uses proxy in dev) | Backend API base URL |
| `VITE_ADMIN_API_KEY` | (optional) | Same as backend `ADMIN_API_KEY` for dashboard refresh button |

## Ops dashboard

Open **http://localhost:5173/dashboard** (or `/dashboard` on your deployed site).

- Shows when data was last updated
- Live vs inactive job counts, breakdown by site / role / experience / job level
- **Refresh jobs now** runs a background scrape immediately (no cron needed)
- Requires admin key via `VITE_ADMIN_API_KEY` or one-time paste in the UI
