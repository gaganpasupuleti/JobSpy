import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import JobPost

logger = logging.getLogger(__name__)


def job_exists(db: Session, job_data: dict) -> bool:
    job_url = job_data.get("job_url")
    if job_url:
        existing = db.query(JobPost).filter(JobPost.job_url == job_url).first()
        if existing:
            return True

    title = job_data["title"]
    company = job_data["company"]
    location = job_data["location"]
    existing = (
        db.query(JobPost)
        .filter(
            JobPost.title == title,
            JobPost.company == company,
            JobPost.location == location,
        )
        .first()
    )
    return existing is not None


def insert_job_if_new(db: Session, job_data: dict) -> JobPost | None:
    if job_exists(db, job_data):
        return None
    job = JobPost(**job_data)
    db.add(job)
    db.flush()
    return job


def import_demo_jobs(db: Session) -> tuple[int, int]:
    from app.seed_data import DEMO_JOBS

    inserted = 0
    skipped = 0
    for job_data in DEMO_JOBS:
        if job_exists(db, job_data):
            skipped += 1
            continue
        db.add(JobPost(**job_data))
        inserted += 1
    db.commit()
    logger.info("Demo import: %s inserted, %s skipped (duplicates)", inserted, skipped)
    return inserted, skipped
