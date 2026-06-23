import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import EmailNotification, JobAlertRule, JobPost
from app.services.matching import job_matches_alert

logger = logging.getLogger(__name__)

EMAIL_MODE = "console"


def render_email_subject(job: JobPost) -> str:
    return f"New job match: {job.title} at {job.company}"


def render_email_body(alert: JobAlertRule, job: JobPost) -> str:
    return f"""Hi {alert.recipient_name},

We found a new job that matches your alert: {alert.alert_name}

Job Title: {job.title}
Company: {job.company}
Location: {job.location}
Experience: {job.experience_level or 'N/A'}
Source: {job.source}

Job Link:
{job.job_url or 'N/A'}

Short Description:
{job.description or 'N/A'}

Thanks,
JobSpy Alerts Lab"""


def print_email_to_console(notification: EmailNotification) -> None:
    border = "=" * 60
    logger.info(
        "\n%s\n[CONSOLE EMAIL] To: %s\nSubject: %s\n%s\n%s\n%s",
        border,
        notification.to_email,
        notification.subject,
        border,
        notification.body,
        border,
    )


def create_and_send_console_email(
    db: Session,
    alert: JobAlertRule,
    job: JobPost,
) -> EmailNotification:
    now = datetime.now(timezone.utc)
    notification = EmailNotification(
        alert_rule_id=alert.id,
        job_post_id=job.id,
        to_email=alert.recipient_email,
        subject=render_email_subject(job),
        body=render_email_body(alert, job),
        status="console_sent",
        sent_at=now,
    )
    db.add(notification)
    db.flush()
    print_email_to_console(notification)
    return notification


def generate_emails_for_matches(
    db: Session,
    jobs: list[JobPost],
    alerts: list[JobAlertRule] | None = None,
) -> list[EmailNotification]:
    if alerts is None:
        alerts = db.query(JobAlertRule).filter(JobAlertRule.is_active.is_(True)).all()

    created: list[EmailNotification] = []
    for job in jobs:
        for alert in alerts:
            if not job_matches_alert(job, alert):
                continue
            existing = (
                db.query(EmailNotification)
                .filter(
                    EmailNotification.alert_rule_id == alert.id,
                    EmailNotification.job_post_id == job.id,
                )
                .first()
            )
            if existing:
                continue
            created.append(create_and_send_console_email(db, alert, job))
    return created


def send_test_email(db: Session, alert: JobAlertRule) -> EmailNotification:
    job = (
        db.query(JobPost)
        .filter(
            (JobPost.title.ilike(f"%{alert.keywords}%"))
            | (JobPost.description.ilike(f"%{alert.keywords}%"))
        )
        .first()
    )
    if not job:
        job = JobPost(
            title=f"Sample {alert.keywords} Role",
            company="JobSpy Demo Corp",
            location=alert.location or "Remote",
            source="demo",
            job_url="https://demo.jobspy.local/jobs/sample-test",
            description=f"This is a test email for alert '{alert.alert_name}'.",
            experience_level=alert.experience_level or "Fresher",
            employment_type="Full-time",
        )
        db.add(job)
        db.flush()

    return create_and_send_console_email(db, alert, job)
