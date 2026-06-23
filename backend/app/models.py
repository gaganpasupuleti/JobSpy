from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class JobPost(Base):
    __tablename__ = "job_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="demo")
    job_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class JobAlertRule(Base):
    __tablename__ = "job_alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, default="")
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EmailNotification(Base):
    __tablename__ = "email_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("job_alert_rules.id"), nullable=True
    )
    job_post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("job_posts.id"), nullable=True
    )
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    alert_rule: Mapped["JobAlertRule | None"] = relationship("JobAlertRule")
    job_post: Mapped["JobPost | None"] = relationship("JobPost")


class JobScanRun(Base):
    __tablename__ = "job_scan_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="demo")
    search_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="started")
    jobs_found_count: Mapped[int] = mapped_column(Integer, default=0)
    new_jobs_count: Mapped[int] = mapped_column(Integer, default=0)
    matched_alerts_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
