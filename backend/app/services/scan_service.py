from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import JobAlertRule, JobPost, JobScanRun
from app.seed_data import DEMO_ALERT_RULES, DEMO_JOBS
from app.services.email_service import generate_emails_for_matches
from app.services.jobs import insert_job_if_new


def seed_alert_rules_if_empty(db: Session) -> None:
    count = db.query(JobAlertRule).count()
    if count > 0:
        return
    for rule_data in DEMO_ALERT_RULES:
        db.add(JobAlertRule(**rule_data))
    db.commit()


def run_demo_scan(db: Session) -> JobScanRun:
    scan = JobScanRun(
        source="demo",
        search_keyword="demo-import",
        location="India",
        status="started",
    )
    db.add(scan)
    db.flush()

    try:
        seed_alert_rules_if_empty(db)

        new_jobs: list[JobPost] = []
        for job_data in DEMO_JOBS:
            job = insert_job_if_new(db, job_data)
            if job:
                new_jobs.append(job)

        all_jobs = db.query(JobPost).all()
        notifications = generate_emails_for_matches(db, all_jobs)

        scan.jobs_found_count = len(all_jobs)
        scan.new_jobs_count = len(new_jobs)
        scan.matched_alerts_count = len(notifications)
        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        return scan
    except Exception:
        scan.status = "failed"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise
