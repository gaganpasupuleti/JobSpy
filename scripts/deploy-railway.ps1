# Railway deployment script (run from repo root in an interactive terminal)
#
# Prerequisites:
#   1. Railway account: https://railway.app
#   2. Railway CLI installed: npm install -g @railway/cli
#
# Usage:
#   .\scripts\deploy-railway.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== JobSpy Job Board - Railway Deploy ===" -ForegroundColor Cyan

# Step 1: Login (opens browser)
Write-Host "`n[1/6] Login to Railway..." -ForegroundColor Yellow
railway whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    railway login
}

# Step 2: Create or link project
Write-Host "`n[2/6] Initialize Railway project..." -ForegroundColor Yellow
if (-not (Test-Path ".railway")) {
    railway init
}

# Step 3: Add PostgreSQL (skip if already added)
Write-Host "`n[3/6] Add PostgreSQL database..." -ForegroundColor Yellow
Write-Host "If prompted, select 'PostgreSQL'. Skip if DB already exists in project."
railway add --database postgres 2>$null

# Step 4: Set environment variables
Write-Host "`n[4/6] Set environment variables..." -ForegroundColor Yellow
$adminKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
Write-Host "Generated ADMIN_API_KEY: $adminKey"
Write-Host "Save this key — you need it to trigger scrapes."

railway variables set ADMIN_API_KEY=$adminKey
railway variables set CORS_ORIGINS="*"
railway variables set DEFAULT_SITES="indeed,linkedin,naukri"
railway variables set DEFAULT_RESULTS_WANTED=20
railway variables set DEFAULT_HOURS_OLD=168
railway variables set SCRAPE_SLEEP_SECONDS=45

# Step 5: Deploy API service
Write-Host "`n[5/6] Deploying API service (this may take a few minutes)..." -ForegroundColor Yellow
railway up --detach

Write-Host "`n[6/6] Generate public domain..." -ForegroundColor Yellow
railway domain

Write-Host @"

=== Deploy complete (API) ===

Next steps:
1. Open your API URL and check: https://YOUR-DOMAIN/health
2. Open API docs: https://YOUR-DOMAIN/docs
3. Trigger first scrape:
   curl -X POST "https://YOUR-DOMAIN/api/v1/admin/scrape/run?limit=1" -H "X-Admin-Key: $adminKey"

4. Add WORKER service in Railway dashboard:
   - New Service -> same GitHub repo OR duplicate from API
   - Start command: python /app/run_worker.py --once --limit 10
   - Use railway.worker.toml config OR set start command manually
   - Link same DATABASE_URL variable from Postgres

"@ -ForegroundColor Green
