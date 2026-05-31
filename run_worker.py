#!/usr/bin/env python3
"""Scraper worker CLI — run all active search profiles or a single scrape pass."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.db.models import SearchProfile
from app.db.session import SessionLocal
from app.seed.seed import seed_database
from app.services.worker import run_profile_scrape


def main() -> int:
    parser = argparse.ArgumentParser(description="JobSpy scraper worker")
    parser.add_argument("--once", action="store_true", help="Run one pass and exit")
    parser.add_argument("--profile-id", type=int, help="Scrape a single search profile")
    parser.add_argument("--limit", type=int, default=0, help="Max profiles per pass (0 = all)")
    parser.add_argument(
        "--verify-links",
        action="store_true",
        help="Check stored job URLs and deactivate expired/removed listings",
    )
    parser.add_argument(
        "--verify-limit",
        type=int,
        default=0,
        help="Max jobs to verify when using --verify-links (0 = config default)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_database(db)

        if args.verify_links:
            from app.services.link_verify import verify_job_links

            limit = args.verify_limit or None
            stats = verify_job_links(db, limit=limit)
            print(
                f"Link verify: processed={stats['processed']} "
                f"still_active={stats['still_active']} "
                f"deactivated={stats['deactivated']} "
                f"inconclusive={stats['inconclusive']}"
            )
            for item in stats.get("deactivated_jobs", [])[:10]:
                print(f"  - [{item['site']}] {item['title']} ({item['reason']})")
            return 0

        while True:
            query = db.query(SearchProfile).filter(SearchProfile.is_active.is_(True))
            if args.profile_id:
                query = query.filter(SearchProfile.id == args.profile_id)
            else:
                query = query.order_by(SearchProfile.last_scraped_at.asc().nullsfirst())
                if args.limit > 0:
                    query = query.limit(args.limit)

            profiles = query.all()
            if not profiles:
                print("No active search profiles found.")
                break

            print(f"Scraping {len(profiles)} profile(s)...")
            for i, profile in enumerate(profiles, start=1):
                role = profile.role_category.name if profile.role_category else "?"
                city = profile.location.display_name if profile.location else "?"
                print(f"[{i}/{len(profiles)}] {role} @ {city}")
                run = run_profile_scrape(db, profile)
                print(
                    f"  -> {run.status}: found={run.jobs_found}, upserted={run.jobs_upserted}"
                )
                if run.error_message:
                    print(f"  -> error: {run.error_message[:200]}")

                if i < len(profiles):
                    time.sleep(settings.scrape_sleep_seconds)

            if args.once or args.profile_id:
                break

            print(f"Sleeping {settings.scrape_sleep_seconds}s before next cycle...")
            time.sleep(settings.scrape_sleep_seconds)
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
