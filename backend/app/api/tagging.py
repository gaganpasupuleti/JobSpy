from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_admin_key
from app.db.models import ExperienceBand, Job, RoleCategory
from app.db.session import get_db
from app.schemas.jobs import JobDetailOut
from app.schemas.tagging import (
    ManualTagResponse,
    ManualTagUpdate,
    TaggingQueueItem,
    TaggingQueueResponse,
)
from app.services.job_tagger import TagStatus
from app.services.manual_tag import apply_manual_tags, queue_item_from_job

router = APIRouter(
    prefix="/admin/tagging",
    tags=["tagging"],
    dependencies=[Depends(verify_admin_key)],
)


@router.get("/queue", response_model=TaggingQueueResponse)
def tagging_queue(
    tag_status: str | None = Query(
        None,
        description="Filter: flagged, untagged, partial, non_india (default: all review queue)",
    ),
    q: str | None = Query(None, description="Search title or company"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Job)
        .options(
            joinedload(Job.role_category),
            joinedload(Job.profile_role_category),
            joinedload(Job.experience_band),
        )
        .filter(Job.is_active.is_(True))
    )

    if tag_status:
        if tag_status not in (
            TagStatus.FLAGGED,
            TagStatus.UNTAGGED,
            TagStatus.PARTIAL,
            TagStatus.NON_INDIA,
            TagStatus.COMPLETE,
        ):
            raise HTTPException(status_code=400, detail="Invalid tag_status filter")
        query = query.filter(Job.tag_status == tag_status)
    else:
        query = query.filter(
            Job.tag_status.in_(
                [
                    TagStatus.FLAGGED,
                    TagStatus.UNTAGGED,
                    TagStatus.PARTIAL,
                    TagStatus.NON_INDIA,
                ]
            )
        )

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            Job.title.ilike(pattern) | Job.company_name.ilike(pattern)
        )

    total = query.count()
    jobs = (
        query.order_by(desc(Job.needs_review), desc(Job.scraped_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TaggingQueueResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TaggingQueueItem(**queue_item_from_job(j)) for j in jobs],
    )


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job_for_tagging(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetailOut.model_validate(job)


@router.patch("/{job_id}", response_model=ManualTagResponse)
def update_job_tags(
    job_id: UUID,
    body: ManualTagUpdate,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not any(
        [
            body.role is not None,
            body.experience is not None,
            body.is_india_verified is not None,
            body.approve,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one tag field or approve=true",
        )

    try:
        job = apply_manual_tags(
            db,
            job,
            role_slug=body.role,
            experience_slug=body.experience,
            is_india_verified=body.is_india_verified,
            approve=body.approve,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    role = (
        db.query(RoleCategory).filter(RoleCategory.id == job.role_category_id).first()
        if job.role_category_id
        else None
    )
    band = (
        db.query(ExperienceBand).filter(ExperienceBand.id == job.experience_band_id).first()
        if job.experience_band_id
        else None
    )
    msg = "Tags updated"
    if job.tag_status == TagStatus.COMPLETE:
        msg = "Job fully tagged — now visible on Browse"
    elif body.approve:
        msg = "Saved; still incomplete (check role, level, India)"

    return ManualTagResponse(
        id=job.id,
        tag_status=job.tag_status,
        needs_review=job.needs_review,
        review_reason=job.review_reason,
        role_slug=role.slug if role else None,
        experience_slug=band.slug if band else None,
        is_india_verified=job.is_india_verified,
        message=msg,
    )
