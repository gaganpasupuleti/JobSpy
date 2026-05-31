from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import ExperienceBand, Job, Keyword, Location, RoleCategory
from app.db.session import get_db
from app.schemas.meta import ExperienceBandOut, KeywordOut, LocationOut, RoleCategoryOut

router = APIRouter(prefix="/meta", tags=["meta"])


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
