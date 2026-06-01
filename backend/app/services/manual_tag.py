from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.db.models import ExperienceBand, Job, RoleCategory
from app.services.ingest import tag_job_keywords
from app.services.job_tagger import apply_tag_status


def apply_manual_tags(
    db: Session,
    job: Job,
    *,
    role_slug: str | None = None,
    experience_slug: str | None = None,
    is_india_verified: bool | None = None,
    approve: bool = False,
) -> Job:
    if role_slug is not None:
        role = db.query(RoleCategory).filter(RoleCategory.slug == role_slug).first()
        if not role:
            raise ValueError(f"Unknown role slug: {role_slug}")
        job.role_category_id = role.id
        tag_job_keywords(db, job, role.id)

    if experience_slug is not None:
        band = db.query(ExperienceBand).filter(ExperienceBand.slug == experience_slug).first()
        if not band:
            raise ValueError(f"Unknown experience slug: {experience_slug}")
        job.experience_band_id = band.id

    if is_india_verified is not None:
        job.is_india_verified = is_india_verified

    if approve:
        job.needs_review = False
        job.review_reason = None

    apply_tag_status(job)
    db.commit()
    db.refresh(job)
    return job


def queue_item_from_job(job: Job) -> dict:
    role = job.role_category
    profile_role = job.profile_role_category
    band = job.experience_band
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "site": job.site,
        "location_display": job.location_display,
        "tag_status": job.tag_status,
        "needs_review": job.needs_review,
        "review_reason": job.review_reason,
        "is_india_verified": job.is_india_verified,
        "role_category_id": job.role_category_id,
        "role_name": role.name if role else None,
        "role_slug": role.slug if role else None,
        "profile_role_name": profile_role.name if profile_role else None,
        "experience_band_id": job.experience_band_id,
        "experience_label": band.label if band else None,
        "experience_slug": band.slug if band else None,
        "role_match_score": job.role_match_score,
        "date_posted": job.date_posted,
        "scraped_at": job.scraped_at,
    }
