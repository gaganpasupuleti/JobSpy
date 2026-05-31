from __future__ import annotations

import random
import re
import time
from datetime import datetime, timedelta

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Job

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

GONE_STATUS_CODES = {404, 410}

UNAVAILABLE_PHRASES = (
    "job has expired",
    "job is expired",
    "job no longer available",
    "no longer available",
    "this job is no longer",
    "this position is no longer",
    "page not found",
    "job not found",
    "position has been filled",
    "listing has expired",
    "not available anymore",
    "job you are looking for",
    "couldn't find this job",
    "could not find this job",
    "this job posting is closed",
    "job posting has been removed",
    "role has been filled",
)

SITE_UNAVAILABLE_PHRASES: dict[str, tuple[str, ...]] = {
    "indeed": ("job expired", "this job has expired"),
    "linkedin": ("job no longer available", "no longer accepting applications"),
    "naukri": ("job expired", "this job is not available"),
    "foundit": ("job expired", "no longer exists"),
}


class LinkCheckResult:
    __slots__ = ("status", "reason")

    def __init__(self, status: str, reason: str | None = None):
        self.status = status  # active | inactive | inconclusive
        self.reason = reason


def _phrases_for_site(site: str) -> tuple[str, ...]:
    extra = SITE_UNAVAILABLE_PHRASES.get(site, ())
    return UNAVAILABLE_PHRASES + extra


def _body_indicates_unavailable(text: str, site: str) -> str | None:
    lowered = text.lower()
    for phrase in _phrases_for_site(site):
        if phrase in lowered:
            return phrase
    return None


def check_job_url(job_url: str, site: str, timeout: int = 15) -> LinkCheckResult:
    """Check whether a job posting URL still appears to be live."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(
            job_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )

        if response.status_code in GONE_STATUS_CODES:
            response.close()
            return LinkCheckResult("inactive", f"HTTP {response.status_code}")

        if response.status_code == 403:
            response.close()
            return LinkCheckResult("inconclusive", "HTTP 403 blocked")

        if response.status_code >= 500:
            response.close()
            return LinkCheckResult("inconclusive", f"HTTP {response.status_code}")

        # Read a sample of the body — enough to catch expired-job messages.
        chunks: list[bytes] = []
        size = 0
        max_bytes = 48_000
        for chunk in response.iter_content(chunk_size=4096):
            if not chunk:
                continue
            chunks.append(chunk)
            size += len(chunk)
            if size >= max_bytes:
                break
        response.close()

        body = b"".join(chunks).decode("utf-8", errors="ignore")
        phrase = _body_indicates_unavailable(body, site)
        if phrase:
            return LinkCheckResult("inactive", f"page contains '{phrase}'")

        # Some sites return soft 404 titles.
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", body, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).lower()
            if any(x in title for x in ("404", "not found", "expired", "unavailable")):
                return LinkCheckResult("inactive", f"title indicates unavailable: {title[:80]}")

        return LinkCheckResult("active")

    except requests.Timeout:
        return LinkCheckResult("inconclusive", "timeout")
    except requests.RequestException as exc:
        return LinkCheckResult("inconclusive", str(exc)[:120])


def verify_job_links(
    db: Session,
    limit: int | None = None,
    site: str | None = None,
    stale_hours: int | None = None,
) -> dict:
    """
    Check stored job URLs and deactivate listings that appear removed or expired.
    Jobs with inconclusive results (blocked/timeout) stay active and can be retried later.
    """
    batch_size = limit or settings.link_verify_batch_size
    stale_hours = stale_hours if stale_hours is not None else settings.link_verify_stale_hours
    stale_cutoff = datetime.utcnow() - timedelta(hours=stale_hours)

    query = (
        db.query(Job)
        .filter(Job.is_active.is_(True))
        .filter(
            (Job.last_verified_at.is_(None)) | (Job.last_verified_at < stale_cutoff)
        )
        .order_by(Job.last_verified_at.asc().nullsfirst())
    )
    if site:
        query = query.filter(Job.site == site.lower())

    jobs = query.limit(batch_size).all()
    now = datetime.utcnow()

    stats = {
        "processed": 0,
        "still_active": 0,
        "deactivated": 0,
        "inconclusive": 0,
        "deactivated_jobs": [],
    }

    for i, job in enumerate(jobs, start=1):
        result = check_job_url(job.job_url, job.site)
        stats["processed"] += 1

        if result.status == "inactive":
            job.is_active = False
            job.updated_at = now
            job.last_verified_at = now
            stats["deactivated"] += 1
            stats["deactivated_jobs"].append(
                {
                    "id": str(job.id),
                    "site": job.site,
                    "title": job.title,
                    "company": job.company_name,
                    "reason": result.reason,
                }
            )
        elif result.status == "active":
            job.last_verified_at = now
            stats["still_active"] += 1
        else:
            job.last_verified_at = now
            stats["inconclusive"] += 1

        if i < len(jobs):
            time.sleep(random.uniform(
                settings.link_verify_sleep_seconds * 0.5,
                settings.link_verify_sleep_seconds * 1.5,
            ))

    db.commit()
    return stats
