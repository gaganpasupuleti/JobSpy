from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_admin_key
from app.db.models import RoleCategory, ScrapeRun, SearchProfile
from app.db.session import get_db
from app.schemas.admin import ScrapeRunOut, ScrapeTriggerResponse, SearchProfileOut
from app.services.worker import run_profile_scrape

router = APIRouter(prefix="/admin/scrape", tags=["admin"], dependencies=[Depends(verify_admin_key)])


@router.get("/profiles", response_model=list[SearchProfileOut])
def list_search_profiles(
    role: str | None = Query(None, description="Filter by role category slug"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(SearchProfile)
        .options(
            joinedload(SearchProfile.role_category),
            joinedload(SearchProfile.location),
            joinedload(SearchProfile.experience_band),
        )
        .filter(SearchProfile.is_active.is_(True))
    )
    if role:
        query = query.join(RoleCategory).filter(RoleCategory.slug == role)

    profiles = query.all()
    profiles.sort(
        key=lambda p: (
            p.role_category.sort_order if p.role_category else 0,
            p.location.city if p.location else "",
            p.experience_band.sort_order if p.experience_band else 0,
        )
    )

    return [
        SearchProfileOut(
            id=p.id,
            role_slug=p.role_category.slug if p.role_category else "",
            role_name=p.role_category.name if p.role_category else "",
            city=p.location.city if p.location else "",
            location_display=p.location.display_name if p.location else "",
            experience_label=p.experience_band.label if p.experience_band else "",
            is_remote=p.is_remote,
            search_term=p.search_term,
            sites=p.sites if isinstance(p.sites, list) else [],
            last_scraped_at=p.last_scraped_at,
        )
        for p in profiles
    ]


@router.post("/run", response_model=ScrapeTriggerResponse)
def trigger_scrape(
    profile_id: int | None = Query(None, description="Single profile (legacy)"),
    profile_ids: list[int] | None = Query(None, description="Specific profiles to scrape"),
    limit: int = Query(1, ge=1, le=50, description="Used when profile_ids not set"),
    db: Session = Depends(get_db),
):
    query = db.query(SearchProfile).filter(SearchProfile.is_active.is_(True))

    if profile_ids:
        query = query.filter(SearchProfile.id.in_(profile_ids))
    elif profile_id:
        query = query.filter(SearchProfile.id == profile_id)
    else:
        query = query.order_by(
            SearchProfile.last_scraped_at.asc().nullsfirst()
        ).limit(limit)

    profiles = query.all()
    if profile_ids and len(profiles) != len(set(profile_ids)):
        found = {p.id for p in profiles}
        missing = sorted(set(profile_ids) - found)
        if missing:
            raise HTTPException(
                status_code=404,
                detail=f"Search profile(s) not found: {missing}",
            )

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
