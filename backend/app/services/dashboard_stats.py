from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models import ExperienceBand, Job, RoleCategory, ScrapeRun, ScrapeStatus, SearchProfile
from app.schemas.admin import ScrapeRunOut
from app.services.job_tagger import TagStatus
from app.schemas.dashboard import (
    CountByLabel,
    DashboardStatsOut,
    JobsSummary,
    JobsTagSummary,
    SearchProfilesSummary,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def is_scrape_in_progress(db: Session) -> bool:
    running = (
        db.query(ScrapeRun.id)
        .filter(
            ScrapeRun.status == ScrapeStatus.RUNNING.value,
            ScrapeRun.finished_at.is_(None),
        )
        .first()
    )
    return running is not None


def get_dashboard_stats(db: Session) -> DashboardStatsOut:
    live = db.query(func.count(Job.id)).filter(Job.is_active.is_(True)).scalar() or 0
    inactive = db.query(func.count(Job.id)).filter(Job.is_active.is_(False)).scalar() or 0

    by_site_rows = (
        db.query(Job.site, func.count(Job.id))
        .filter(Job.is_active.is_(True))
        .group_by(Job.site)
        .order_by(desc(func.count(Job.id)))
        .all()
    )

    by_role_rows = (
        db.query(RoleCategory.name, RoleCategory.slug, func.count(Job.id))
        .join(Job, Job.role_category_id == RoleCategory.id)
        .filter(Job.is_active.is_(True))
        .group_by(RoleCategory.id, RoleCategory.name, RoleCategory.slug)
        .order_by(desc(func.count(Job.id)))
        .all()
    )

    by_experience_rows = (
        db.query(ExperienceBand.label, ExperienceBand.slug, func.count(Job.id))
        .join(Job, Job.experience_band_id == ExperienceBand.id)
        .filter(Job.is_active.is_(True))
        .group_by(ExperienceBand.id, ExperienceBand.label, ExperienceBand.slug)
        .order_by(desc(func.count(Job.id)))
        .all()
    )

    by_level_rows = (
        db.query(Job.job_level, func.count(Job.id))
        .filter(Job.is_active.is_(True), Job.job_level.isnot(None), Job.job_level != "")
        .group_by(Job.job_level)
        .order_by(desc(func.count(Job.id)))
        .limit(20)
        .all()
    )

    unassigned_experience = (
        db.query(func.count(Job.id))
        .filter(Job.is_active.is_(True), Job.experience_band_id.is_(None))
        .scalar()
        or 0
    )

    last_job_scraped_at = db.query(func.max(Job.scraped_at)).scalar()

    last_success = (
        db.query(ScrapeRun)
        .filter(ScrapeRun.status == ScrapeStatus.SUCCESS.value)
        .order_by(desc(ScrapeRun.finished_at))
        .first()
    )

    now = _utcnow()
    day_ago = now - timedelta(hours=24)

    active_profiles_q = db.query(SearchProfile).filter(SearchProfile.is_active.is_(True))
    total_active_profiles = active_profiles_q.count()
    never_scraped = (
        active_profiles_q.filter(SearchProfile.last_scraped_at.is_(None)).count()
    )
    scraped_last_24h = (
        active_profiles_q.filter(SearchProfile.last_scraped_at >= day_ago).count()
    )

    recent_runs = (
        db.query(ScrapeRun).order_by(desc(ScrapeRun.started_at)).limit(10).all()
    )

    unassigned_role = (
        db.query(func.count(Job.id))
        .filter(Job.is_active.is_(True), Job.role_category_id.is_(None))
        .scalar()
        or 0
    )

    by_experience = [
        CountByLabel(label=label, slug=slug, count=count)
        for label, slug, count in by_experience_rows
    ]
    if unassigned_experience:
        by_experience.append(
            CountByLabel(label="Unassigned", slug=None, count=unassigned_experience)
        )

    by_role = [
        CountByLabel(label=name, slug=slug, count=count)
        for name, slug, count in by_role_rows
    ]
    if unassigned_role:
        by_role.append(CountByLabel(label="Unassigned", slug=None, count=unassigned_role))

    def _tag_count(status: str) -> int:
        return (
            db.query(func.count(Job.id))
            .filter(Job.is_active.is_(True), Job.tag_status == status)
            .scalar()
            or 0
        )

    jobs_by_tag = JobsTagSummary(
        complete=_tag_count(TagStatus.COMPLETE),
        partial=_tag_count(TagStatus.PARTIAL),
        untagged=_tag_count(TagStatus.UNTAGGED),
        flagged=_tag_count(TagStatus.FLAGGED),
        non_india=_tag_count(TagStatus.NON_INDIA),
    )

    return DashboardStatsOut(
        last_job_scraped_at=last_job_scraped_at,
        last_successful_scrape_at=last_success.finished_at if last_success else None,
        scrape_in_progress=is_scrape_in_progress(db),
        jobs=JobsSummary(live=live, inactive=inactive, total=live + inactive),
        jobs_by_tag=jobs_by_tag,
        by_site=[CountByLabel(label=site, slug=site, count=count) for site, count in by_site_rows],
        by_role=by_role,
        by_experience=by_experience,
        by_job_level=[
            CountByLabel(label=level, slug=None, count=count)
            for level, count in by_level_rows
        ],
        search_profiles=SearchProfilesSummary(
            total_active=total_active_profiles,
            never_scraped=never_scraped,
            scraped_last_24h=scraped_last_24h,
        ),
        recent_scrape_runs=[ScrapeRunOut.model_validate(r) for r in recent_runs],
    )
