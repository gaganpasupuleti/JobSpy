from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import verify_admin_key
from app.db.models import Job
from app.db.session import get_db
from app.services.ingest import retag_job
from app.services.skills import extract_key_skills
from app.services.link_verify import verify_job_links

router = APIRouter(
    prefix="/admin/jobs",
    tags=["admin"],
    dependencies=[Depends(verify_admin_key)],
)


def _backfill_naukri_job(job: Job, naukri) -> bool:
    job_payload = {}
    if job.key_skills:
        job_payload["tagsAndSkills"] = job.key_skills
    description = naukri._resolve_description(job_payload, job.external_id)
    if not description:
        return False
    job.description = description
    job.key_skills = extract_key_skills(
        description=description,
        raw_skills=job.key_skills or job_payload.get("tagsAndSkills"),
        title=job.title,
    )
    job.updated_at = datetime.utcnow()
    return True


@router.post("/backfill-naukri-descriptions")
def backfill_naukri_descriptions(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Fetch missing Naukri descriptions via detail API for jobs already in the DB."""
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from jobspy.model import DescriptionFormat, ScraperInput, Site
    from jobspy.naukri import Naukri

    jobs = (
        db.query(Job)
        .filter(Job.site == "naukri", Job.is_active.is_(True))
        .filter(or_(Job.description.is_(None), Job.description == ""))
        .limit(limit)
        .all()
    )

    naukri = Naukri()
    naukri.scraper_input = ScraperInput(
        site_type=[Site.NAUKRI],
        description_format=DescriptionFormat.MARKDOWN,
    )

    updated = 0
    for job in jobs:
        if _backfill_naukri_job(job, naukri):
            updated += 1

    db.commit()
    return {"processed": len(jobs), "updated": updated}


@router.post("/backfill-skills")
def backfill_skills(
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Extract key_skills from existing job descriptions (for jobs scraped before this feature)."""
    jobs = (
        db.query(Job)
        .filter(Job.is_active.is_(True))
        .filter((Job.key_skills.is_(None)) | (Job.key_skills == ""))
        .limit(limit)
        .all()
    )
    updated = 0
    for job in jobs:
        skills = extract_key_skills(
            description=job.description,
            raw_skills=None,
            title=job.title,
        )
        if skills:
            job.key_skills = skills
            updated += 1
    db.commit()
    return {"processed": len(jobs), "updated": updated}


@router.post("/retag")
def retag_jobs(
    limit: int = Query(2000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    """Recompute India / role / level tags for existing jobs."""
    jobs = db.query(Job).filter(Job.is_active.is_(True)).limit(limit).all()
    for job in jobs:
        retag_job(db, job)
    db.commit()
    return {"processed": len(jobs)}


@router.post("/verify-links")
def verify_links(
    limit: int = Query(100, ge=1, le=1000),
    site: str | None = Query(None, description="Only verify jobs from this site"),
    stale_hours: int | None = Query(None, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Check whether stored job URLs still work. Jobs that return 404/410 or show
    an expired/removed message are marked inactive and hidden from the board.
    """
    stats = verify_job_links(db, limit=limit, site=site, stale_hours=stale_hours)
    deactivated_sample = stats.pop("deactivated_jobs", [])[:25]
    return {
        **stats,
        "deactivated_sample": deactivated_sample,
    }
