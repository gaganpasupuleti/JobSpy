from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ScrapeRun, ScrapeStatus, SearchProfile
from app.services.ingest import upsert_jobs_from_dataframe
from app.services.scraper import run_search_profile


def run_profile_scrape(db: Session, profile: SearchProfile) -> ScrapeRun:
    run = ScrapeRun(
        search_profile_id=profile.id,
        status=ScrapeStatus.RUNNING.value,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        df = run_search_profile(profile)
        jobs_found = len(df)
        jobs_upserted = upsert_jobs_from_dataframe(db, df, profile, run.id)

        run.status = ScrapeStatus.SUCCESS.value
        run.jobs_found = jobs_found
        run.jobs_upserted = jobs_upserted
        run.finished_at = datetime.utcnow()
        profile.last_scraped_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run
    except Exception as exc:
        run.status = ScrapeStatus.FAILED.value
        run.error_message = str(exc)[:2000]
        run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run
