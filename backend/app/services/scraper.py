from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jobspy import scrape_jobs

from app.config import settings
from app.db.models import SearchProfile

log = logging.getLogger(__name__)


def _search_term_for_site(site: str, profile: SearchProfile) -> str:
    term = profile.search_term
    if site == "foundit":
        match = re.search(r'"([^"]+)"', term)
        if match:
            return match.group(1)
        if " OR " in term:
            return term.split(" OR ")[0].strip().strip('"')
    return term


def run_search_profile(profile: SearchProfile) -> pd.DataFrame:
    location = profile.location.indeed_location_string if profile.location else None
    sites = settings.site_list
    frames: list[pd.DataFrame] = []

    for site in sites:
        try:
            df = scrape_jobs(
                site_name=[site],
                search_term=_search_term_for_site(site, profile),
                location=location,
                results_wanted=profile.results_wanted or settings.default_results_wanted,
                country_indeed="India",
                hours_old=profile.hours_old or settings.default_hours_old,
                is_remote=profile.is_remote,
                verbose=1,
            )
        except Exception as exc:
            log.warning("Scrape failed for site=%s profile=%s: %s", site, profile.id, exc)
            continue

        if df is not None and not df.empty:
            frames.append(df)
            log.info("Scraped %s jobs from %s", len(df), site)
        else:
            log.info("No jobs from %s — skipping (not stored)", site)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
