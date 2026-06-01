"""Heuristic India location verification for scraped jobs."""

from __future__ import annotations

import re

NON_INDIA_MARKERS = (
    "united states",
    "united kingdom",
    " u.s.",
    " usa",
    " us,",
    " uk,",
    " london",
    " singapore",
    " dubai",
    " uae",
    " canada",
    " australia",
    " germany",
    " ireland",
    " philippines",
    " china",
    " hong kong",
    " san francisco",
    " new york",
    " california",
    "texas,",
    "washington, dc",
)

INDIA_MARKERS = (
    "india",
    "bharat",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
    "mumbai",
    "pune",
    "delhi",
    "ncr",
    "gurgaon",
    "gurugram",
    "noida",
    "kolkata",
    "ahmedabad",
    "kochi",
    "jaipur",
    "chandigarh",
    "indore",
    "coimbatore",
    "visakhapatnam",
    "telangana",
    "karnataka",
    "tamil nadu",
    "maharashtra",
    "gujarat",
    "kerala",
    "rajasthan",
    "madhya pradesh",
    "andhra pradesh",
    "west bengal",
)


def verify_india_job(
    *,
    country: str | None,
    location_display: str | None,
    city: str | None,
    state: str | None,
    is_remote: bool | None,
) -> bool:
    """Return True when the posting plausibly targets India."""
    country_norm = (country or "").strip().lower()
    if country_norm and country_norm not in ("india", "in"):
        return False

    blob = " ".join(
        filter(None, [location_display, city, state, "remote india" if is_remote else ""])
    ).lower()

    if not blob.strip():
        return country_norm in ("india", "in")

    for marker in NON_INDIA_MARKERS:
        if marker in blob:
            return False

    for marker in INDIA_MARKERS:
        if marker in blob:
            return True

    if is_remote and "india" in blob:
        return True

    # Scrape was India-targeted; empty/ambiguous location — allow with country default
    if country_norm in ("india", "in") or not country_norm:
        return not _looks_foreign_city(blob)

    return False


def _looks_foreign_city(blob: str) -> bool:
    return bool(re.search(r"\b(usa|u\.s\.a|uk|uae)\b", blob, re.I))
