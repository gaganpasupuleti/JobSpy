from __future__ import annotations

from app.db.models import Job


class TagStatus:
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNTAGGED = "untagged"
    FLAGGED = "flagged"
    NON_INDIA = "non_india"


def compute_tag_status(
    *,
    is_india_verified: bool,
    role_category_id: int | None,
    experience_band_id: int | None,
    needs_review: bool,
) -> str:
    if not is_india_verified:
        return TagStatus.NON_INDIA
    if needs_review:
        return TagStatus.FLAGGED
    if not role_category_id:
        return TagStatus.UNTAGGED
    if not experience_band_id:
        return TagStatus.PARTIAL
    return TagStatus.COMPLETE


def apply_tag_status(job: Job) -> None:
    job.tag_status = compute_tag_status(
        is_india_verified=bool(job.is_india_verified),
        role_category_id=job.role_category_id,
        experience_band_id=job.experience_band_id,
        needs_review=bool(job.needs_review),
    )
