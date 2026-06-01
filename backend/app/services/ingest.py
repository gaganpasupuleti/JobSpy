from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import ExperienceBand, Job, JobKeyword, Keyword, RoleCategory, SearchProfile
from app.services.experience import infer_experience
from app.services.geo_india import verify_india_job
from app.services.job_tagger import TagStatus, apply_tag_status
from app.services.role_classifier import classify_role
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


def _resolve_experience_band_id(
    db: Session,
    *,
    title: str | None,
    description: str | None,
    profile: SearchProfile,
    experience_bands: dict[str, int],
) -> int | None:
    inference = infer_experience(title, description)
    if inference.slug and inference.slug in experience_bands:
        return experience_bands[inference.slug]
    if profile.experience_band_id:
        return profile.experience_band_id
    return None


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
        title = _safe_str(row.get("title"))
        description = _safe_str(row.get("description"))
        location_display = _safe_str(row.get("location"))
        city, state = _split_location(location_display)
        is_remote = _safe_bool(row.get("is_remote"))

        is_india_verified = verify_india_job(
            country="India",
            location_display=location_display,
            city=city,
            state=state,
            is_remote=is_remote,
        )

        classification = classify_role(
            db,
            title=title,
            description=description,
            profile_role_category_id=profile.role_category_id,
        )

        needs_review = False
        review_reason = None
        if classification.profile_mismatch:
            needs_review = True
            review_reason = "role_profile_mismatch"
        elif classification.role_category_id is None:
            needs_review = True
            review_reason = "low_role_confidence"

        experience_band_id = _resolve_experience_band_id(
            db,
            title=title,
            description=description,
            profile=profile,
            experience_bands=experience_bands,
        )

        key_skills = extract_key_skills(
            description=description,
            raw_skills=_safe_str(row.get("skills")),
            title=title,
        )

        existing = (
            db.query(Job)
            .filter(Job.site == site, Job.external_id == external_id)
            .first()
        )

        inference = infer_experience(title, description)

        payload = dict(
            site=site,
            external_id=external_id,
            title=title or "Untitled",
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
            is_remote=is_remote,
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
            experience_band_id=experience_band_id,
            role_category_id=classification.role_category_id,
            profile_role_category_id=profile.role_category_id,
            role_match_score=float(classification.score),
            location_id=profile.location_id,
            search_profile_id=profile.id,
            scrape_run_id=scrape_run_id,
            is_active=True,
            is_india_verified=is_india_verified,
            needs_review=needs_review,
            review_reason=review_reason,
            last_verified_at=datetime.utcnow(),
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

        apply_tag_status(job)
        if job.role_category_id:
            tag_job_keywords(db, job, job.role_category_id)
        upserted += 1

    db.commit()
    return upserted


def retag_job(db: Session, job: Job) -> None:
    """Recompute tags for an existing job (e.g. after rule changes)."""
    classification = classify_role(
        db,
        title=job.title,
        description=job.description,
        profile_role_category_id=job.profile_role_category_id or job.role_category_id,
    )
    experience_bands = {b.slug: b.id for b in db.query(ExperienceBand).all()}
    inference = infer_experience(job.title, job.description)

    job.is_india_verified = verify_india_job(
        country=job.country,
        location_display=job.location_display,
        city=job.city,
        state=job.state,
        is_remote=job.is_remote,
    )

    job.role_category_id = classification.role_category_id
    job.role_match_score = float(classification.score)
    job.needs_review = False
    job.review_reason = None

    if classification.profile_mismatch:
        job.needs_review = True
        job.review_reason = "role_profile_mismatch"
    elif classification.role_category_id is None:
        job.needs_review = True
        job.review_reason = "low_role_confidence"

    if inference.slug and inference.slug in experience_bands:
        job.experience_band_id = experience_bands[inference.slug]

    apply_tag_status(job)


def _split_location(location: str | None) -> tuple[str | None, str | None]:
    if not location:
        return None, None
    parts = [p.strip() for p in location.split(",")]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return location, None
