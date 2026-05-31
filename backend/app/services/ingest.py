from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import ExperienceBand, Job, JobKeyword, Keyword, RoleCategory, SearchProfile
from app.services.experience import infer_experience
from app.services.skills import extract_key_skills


def extract_external_id(site: str, job_url: str, row_id: str | None) -> str:
    if site == "indeed":
        parsed = urlparse(job_url)
        jk = parse_qs(parsed.query).get("jk", [None])[0]
        if jk:
            return jk
    if site == "linkedin":
        match = re.search(r"/jobs/view/(\d+)", job_url)
        if match:
            return match.group(1)
    if site == "naukri":
        match = re.search(r"/(\d+)(?:\?|$)", job_url)
        if match:
            return match.group(1)
    if site == "foundit":
        if row_id:
            cleaned = str(row_id).split("-", 1)[-1] if "-" in str(row_id) else str(row_id)
            return cleaned
        match = re.search(r"/job/(\d+)", job_url)
        if match:
            return match.group(1)
    if row_id:
        cleaned = str(row_id).split("-", 1)[-1] if "-" in str(row_id) else str(row_id)
        return cleaned
    return str(uuid.uuid4())


def _parse_date(value) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def _safe_str(value) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return str(value)


def _safe_float(value) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value) -> bool | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return bool(value)


def tag_job_keywords(db: Session, job: Job, role_category_id: int) -> None:
    keywords = db.query(Keyword).filter(Keyword.role_category_id == role_category_id).all()
    haystack = f"{job.title} {job.description or ''}".lower()
    for kw in keywords:
        if kw.term.lower() in haystack:
            exists = (
                db.query(JobKeyword)
                .filter(JobKeyword.job_id == job.id, JobKeyword.keyword_id == kw.id)
                .first()
            )
            if not exists:
                db.add(JobKeyword(job_id=job.id, keyword_id=kw.id))


def upsert_jobs_from_dataframe(
    db: Session,
    df: pd.DataFrame,
    profile: SearchProfile,
    scrape_run_id: int,
) -> int:
    if df.empty:
        return 0

    experience_bands = {b.slug: b.id for b in db.query(ExperienceBand).all()}
    upserted = 0

    for _, row in df.iterrows():
        site = _safe_str(row.get("site")) or "unknown"
        job_url = _safe_str(row.get("job_url"))
        if not job_url:
            continue

        external_id = extract_external_id(site, job_url, _safe_str(row.get("id")))
        inference = infer_experience(
            _safe_str(row.get("title")),
            _safe_str(row.get("description")),
        )

        location_display = _safe_str(row.get("location"))
        city, state = _split_location(location_display)
        description = _safe_str(row.get("description"))
        key_skills = extract_key_skills(
            description=description,
            raw_skills=_safe_str(row.get("skills")),
            title=_safe_str(row.get("title")),
        )

        existing = (
            db.query(Job)
            .filter(Job.site == site, Job.external_id == external_id)
            .first()
        )

        payload = dict(
            site=site,
            external_id=external_id,
            title=_safe_str(row.get("title")) or "Untitled",
            company_name=_safe_str(row.get("company")),
            company_url=_safe_str(row.get("company_url")),
            job_url=job_url,
            job_url_direct=_safe_str(row.get("job_url_direct")),
            description=description,
            key_skills=key_skills,
            description_format="markdown",
            city=city,
            state=state,
            country="India",
            location_display=location_display,
            is_remote=_safe_bool(row.get("is_remote")),
            job_type=_safe_str(row.get("job_type")),
            job_level=_safe_str(row.get("job_level")),
            job_function=_safe_str(row.get("job_function")),
            company_industry=_safe_str(row.get("company_industry")),
            salary_interval=_safe_str(row.get("interval")),
            min_amount=_safe_float(row.get("min_amount")),
            max_amount=_safe_float(row.get("max_amount")),
            currency=_safe_str(row.get("currency")),
            salary_source=_safe_str(row.get("salary_source")),
            date_posted=_parse_date(row.get("date_posted")),
            experience_years_min=inference.years_min,
            experience_years_max=inference.years_max,
            experience_band_id=experience_bands.get(inference.slug) if inference.slug else None,
            role_category_id=profile.role_category_id,
            location_id=profile.location_id,
            search_profile_id=profile.id,
            scrape_run_id=scrape_run_id,
            is_active=True,
            updated_at=datetime.utcnow(),
        )

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            job = existing
        else:
            job = Job(**payload)
            db.add(job)
            db.flush()

        tag_job_keywords(db, job, profile.role_category_id)
        upserted += 1

    db.commit()
    return upserted


def _split_location(location: str | None) -> tuple[str | None, str | None]:
    if not location:
        return None, None
    parts = [p.strip() for p in location.split(",")]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return location, None
