from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jobspy import scrape_jobs

from app.config import settings
from app.db.models import SearchProfile


def run_search_profile(profile: SearchProfile) -> pd.DataFrame:
    location = profile.location.indeed_location_string if profile.location else None
    sites = profile.sites or settings.site_list

    return scrape_jobs(
        site_name=sites,
        search_term=profile.search_term,
        location=location,
        results_wanted=profile.results_wanted or settings.default_results_wanted,
        country_indeed="India",
        hours_old=profile.hours_old or settings.default_hours_old,
        is_remote=profile.is_remote,
        verbose=1,
    )
