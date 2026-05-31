from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import verify_admin_key
from app.db.models import Job
from app.db.session import get_db
from app.services.skills import extract_key_skills

router = APIRouter(
    prefix="/admin/jobs",
    tags=["admin"],
    dependencies=[Depends(verify_admin_key)],
)


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
