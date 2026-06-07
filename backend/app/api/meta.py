from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.constants.sites import SITE_ORDER, site_label
from app.db.models import ExperienceBand, Job, Keyword, Location, RoleCategory
from app.db.session import get_db
from app.config import settings
from app.schemas.meta import (
    ConfigOut,
    ExperienceBandOut,
    KeywordOut,
    LocationOut,
    RoleCategoryOut,
    SiteOut,
)

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/config", response_model=ConfigOut)
def get_config():
    return ConfigOut(
        default_sites=settings.site_list,
        default_results_wanted=settings.default_results_wanted,
        default_hours_old=settings.default_hours_old,
    )


@router.get("/sites", response_model=list[SiteOut])
def list_sites(db: Session = Depends(get_db)):
    """Sources that have at least one active job in the DB (hide empty sites)."""
    rows = (
        db.query(Job.site, func.count(Job.id))
        .filter(Job.is_active.is_(True))
        .group_by(Job.site)
        .all()
    )
    counts = {site: count for site, count in rows if count > 0}

    ordered_slugs = [s for s in SITE_ORDER if s in counts]
    extra = sorted(set(counts) - set(ordered_slugs))
    ordered_slugs.extend(extra)

    return [
        SiteOut(slug=slug, label=site_label(slug), active_count=counts[slug])
        for slug in ordered_slugs
    ]


@router.get("/roles", response_model=list[RoleCategoryOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(RoleCategory).order_by(RoleCategory.sort_order).all()


@router.get("/locations", response_model=list[LocationOut])
def list_locations(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Location)
    if active_only:
        query = query.filter(Location.is_active.is_(True))
    return query.order_by(Location.display_name).all()


@router.get("/experience-bands", response_model=list[ExperienceBandOut])
def list_experience_bands(db: Session = Depends(get_db)):
    return db.query(ExperienceBand).order_by(ExperienceBand.sort_order).all()


@router.get("/keywords", response_model=list[KeywordOut])
def list_keywords(role: str | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Keyword)
    if role:
        category = db.query(RoleCategory).filter(RoleCategory.slug == role).first()
        if not category:
            raise HTTPException(status_code=404, detail="Role category not found")
        query = query.filter(Keyword.role_category_id == category.id)
    return query.order_by(Keyword.term).all()
