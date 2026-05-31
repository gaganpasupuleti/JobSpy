from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import verify_admin_key
from app.db.models import ScrapeRun, ScrapeStatus, SearchProfile
from app.db.session import get_db
from app.schemas.admin import ScrapeRunOut, ScrapeTriggerResponse
from app.services.worker import run_profile_scrape

router = APIRouter(prefix="/admin/scrape", tags=["admin"], dependencies=[Depends(verify_admin_key)])


@router.post("/run", response_model=ScrapeTriggerResponse)
def trigger_scrape(
    profile_id: int | None = Query(None),
    limit: int = Query(1, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(SearchProfile).filter(SearchProfile.is_active.is_(True))
    if profile_id:
        query = query.filter(SearchProfile.id == profile_id)
    else:
        query = query.order_by(
            SearchProfile.last_scraped_at.asc().nullsfirst()
        ).limit(limit)

    profiles = query.all()
    runs: list[ScrapeRun] = []

    for profile in profiles:
        run = run_profile_scrape(db, profile)
        runs.append(run)

    return ScrapeTriggerResponse(
        message=f"Completed scrape for {len(profiles)} profile(s)",
        profiles_queued=len(profiles),
        runs=[ScrapeRunOut.model_validate(r) for r in runs],
    )


@router.get("/runs", response_model=list[ScrapeRunOut])
def list_scrape_runs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    runs = (
        db.query(ScrapeRun)
        .order_by(ScrapeRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return [ScrapeRunOut.model_validate(r) for r in runs]
