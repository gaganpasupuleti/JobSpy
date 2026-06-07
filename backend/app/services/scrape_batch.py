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
        _scrape_profiles(db, profiles)
    finally:
        db.close()


def run_scrape_by_ids(profile_ids: list[int]) -> dict:
    """Scrape specific search profiles by ID."""
    db = SessionLocal()
    try:
        profiles = (
            db.query(SearchProfile)
            .filter(
                SearchProfile.is_active.is_(True),
                SearchProfile.id.in_(profile_ids),
            )
            .all()
        )
        order = {pid: i for i, pid in enumerate(profile_ids)}
        profiles.sort(key=lambda p: order.get(p.id, len(profile_ids)))
        return _scrape_profiles(db, profiles)
    finally:
        db.close()


def run_full_scrape() -> dict:
    """Scrape all active profiles (12 roles × 15 cities × 6 levels = 1080)."""
    db = SessionLocal()
    try:
        profiles = (
            db.query(SearchProfile)
            .filter(SearchProfile.is_active.is_(True))
            .order_by(SearchProfile.last_scraped_at.asc().nullsfirst())
            .all()
        )
        return _scrape_profiles(db, profiles)
    finally:
        db.close()


def _scrape_profiles(db: Session, profiles: list[SearchProfile]) -> dict:
    success = 0
    failed = 0
    for i, profile in enumerate(profiles):
        run = run_profile_scrape(db, profile)
        if run.status == "success":
            success += 1
        else:
            failed += 1
        if i < len(profiles) - 1:
            time.sleep(settings.scrape_sleep_seconds)
    return {
        "profiles_total": len(profiles),
        "profiles_success": success,
        "profiles_failed": failed,
    }
