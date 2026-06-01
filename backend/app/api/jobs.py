from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import Application, ExperienceBand, Job, Location, RoleCategory, SavedJob
from app.services.job_tagger import TagStatus
from app.db.session import get_db
from app.schemas.jobs import (
    ApplyRequest,
    ApplyResponse,
    JobDetailOut,
    JobListOut,
    JobListResponse,
    SaveJobRequest,
    SaveJobResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def list_jobs(
    role: str | None = Query(None),
    location: str | None = Query(None),
    experience: str | None = Query(None),
    keyword: str | None = Query(None),
    company: str | None = Query(None, description="Filter by company name"),
    site: str | None = Query(None),
    is_remote: bool | None = Query(None),
    bucket: str = Query(
        "tagged",
        description="tagged = India+role+level complete; others = partial/untagged/flagged",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active.is_(True))

    if bucket == "tagged":
        query = query.filter(Job.tag_status == TagStatus.COMPLETE)
    elif bucket == "others":
        query = query.filter(
            Job.tag_status.in_(
                [TagStatus.PARTIAL, TagStatus.UNTAGGED, TagStatus.FLAGGED]
            )
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="bucket must be 'tagged' or 'others'",
        )

    if role:
        category = db.query(RoleCategory).filter(RoleCategory.slug == role).first()
        if category:
            query = query.filter(Job.role_category_id == category.id)

    if location:
        loc = (
            db.query(Location)
            .filter(
                (Location.city.ilike(f"%{location}%"))
                | (Location.display_name.ilike(f"%{location}%"))
            )
            .first()
        )
        if loc:
            query = query.filter(Job.location_id == loc.id)

    if experience:
        band = db.query(ExperienceBand).filter(ExperienceBand.slug == experience).first()
        if band:
            query = query.filter(Job.experience_band_id == band.id)

    if keyword:
        pattern = f"%{keyword.lower()}%"
        query = query.filter(
            Job.title.ilike(pattern)
            | Job.description.ilike(pattern)
            | Job.key_skills.ilike(pattern)
        )

    if company:
        query = query.filter(Job.company_name.ilike(f"%{company.strip()}%"))

    if site:
        query = query.filter(Job.site == site.lower())

    if is_remote is not None:
        query = query.filter(Job.is_remote == is_remote)

    total = query.count()
    items = (
        query.order_by(desc(Job.date_posted), desc(Job.scraped_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[JobListOut.model_validate(j) for j in items],
    )


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetailOut.model_validate(job)


@router.post("/{job_id}/apply", response_model=ApplyResponse)
def apply_to_job(job_id: UUID, body: ApplyRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    application = Application(
        job_id=job.id,
        student_id=body.student_id,
        session_id=body.session_id,
        source="web",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    redirect_url = job.job_url_direct or job.job_url
    return ApplyResponse(redirect_url=redirect_url, application_id=application.id)


@router.post("/{job_id}/save", response_model=SaveJobResponse)
def save_job(job_id: UUID, body: SaveJobRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(SavedJob)
        .filter(SavedJob.session_id == body.session_id, SavedJob.job_id == job.id)
        .first()
    )
    if existing:
        return SaveJobResponse(saved=True, saved_job_id=existing.id)

    saved = SavedJob(session_id=body.session_id, job_id=job.id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return SaveJobResponse(saved=True, saved_job_id=saved.id)
