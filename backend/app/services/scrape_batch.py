import time

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import SearchProfile
from app.db.session import SessionLocal
from app.services.worker import run_profile_scrape


def run_scrape_batch(limit: int) -> None:
    """Run up to `limit` search profiles (oldest last_scraped_at first)."""
    db = SessionLocal()
    try:
        profiles = (
            db.query(SearchProfile)
            .filter(SearchProfile.is_active.is_(True))
            .order_by(SearchProfile.last_scraped_at.asc().nullsfirst())
            .limit(limit)
            .all()
        )
        for i, profile in enumerate(profiles):
            run_profile_scrape(db, profile)
            if i < len(profiles) - 1:
                time.sleep(settings.scrape_sleep_seconds)
    finally:
        db.close()


def queue_profiles_for_batch(db: Session, limit: int) -> list[SearchProfile]:
    return (
        db.query(SearchProfile)
        .filter(SearchProfile.is_active.is_(True))
        .order_by(SearchProfile.last_scraped_at.asc().nullsfirst())
        .limit(limit)
        .all()
    )
