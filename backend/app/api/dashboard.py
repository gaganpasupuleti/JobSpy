from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import verify_admin_key
from app.db.models import ScrapeRun, ScrapeStatus
from app.db.session import get_db
from app.schemas.admin import ScrapeRunOut
from app.schemas.dashboard import (
    DashboardRefreshOut,
    DashboardRefreshStatusOut,
    DashboardStatsOut,
)
from app.services.dashboard_stats import get_dashboard_stats, is_scrape_in_progress
from app.services.scrape_batch import run_full_scrape, run_scrape_batch, run_scrape_by_ids

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
def dashboard_stats(db: Session = Depends(get_db)):
    """Public job-board health metrics for the ops dashboard."""
    return get_dashboard_stats(db)


@router.get("/refresh/status", response_model=DashboardRefreshStatusOut)
def refresh_status(db: Session = Depends(get_db)):
    in_progress = is_scrape_in_progress(db)
    current = None
    if in_progress:
        current = (
            db.query(ScrapeRun)
            .filter(
                ScrapeRun.status == ScrapeStatus.RUNNING.value,
                ScrapeRun.finished_at.is_(None),
            )
            .order_by(desc(ScrapeRun.started_at))
            .first()
        )
    recent = db.query(ScrapeRun).order_by(desc(ScrapeRun.started_at)).limit(10).all()
    return DashboardRefreshStatusOut(
        scrape_in_progress=in_progress,
        current_run=ScrapeRunOut.model_validate(current) if current else None,
        recent_scrape_runs=[ScrapeRunOut.model_validate(r) for r in recent],
    )


@router.post(
    "/refresh",
    response_model=DashboardRefreshOut,
    dependencies=[Depends(verify_admin_key)],
)
def trigger_refresh(
    background_tasks: BackgroundTasks,
    limit: int = Query(5, ge=1, le=50),
    full: bool = Query(False, description="Scrape all active profiles (~1080)"),
    profile_ids: list[int] | None = Query(
        None, description="Specific search profile IDs to scrape in background"
    ),
    db: Session = Depends(get_db),
):
    """Start a background scrape pass (requires X-Admin-Key)."""
    if is_scrape_in_progress(db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scrape is already in progress. Wait for it to finish.",
        )

    if profile_ids:
        if len(profile_ids) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Select at most 200 profiles per background run.",
            )
        background_tasks.add_task(run_scrape_by_ids, profile_ids)
        return DashboardRefreshOut(
            message=f"Scrape started for {len(profile_ids)} selected profile(s)",
            profiles_queued=len(profile_ids),
        )

    if full:
        background_tasks.add_task(run_full_scrape)
        return DashboardRefreshOut(
            message="Full India scrape started (all roles × cities × levels)",
            profiles_queued=1080,
        )

    background_tasks.add_task(run_scrape_batch, limit)
    return DashboardRefreshOut(
        message="Scrape started in background",
        profiles_queued=limit,
    )
