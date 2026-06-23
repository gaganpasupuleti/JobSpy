from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class JobPostCreate(BaseModel):
    title: str
    company: str
    location: str
    source: str = "manual"
    job_url: str | None = None
    description: str | None = None
    experience_level: str | None = None
    employment_type: str | None = None
    posted_date: datetime | None = None


class JobPostOut(JobPostCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AlertRuleCreate(BaseModel):
    alert_name: str
    recipient_name: str
    recipient_email: EmailStr
    keywords: str
    location: str = ""
    experience_level: str | None = None
    employment_type: str | None = None
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    alert_name: str | None = None
    recipient_name: str | None = None
    recipient_email: EmailStr | None = None
    keywords: str | None = None
    location: str | None = None
    experience_level: str | None = None
    employment_type: str | None = None
    is_active: bool | None = None


class AlertRuleOut(AlertRuleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmailNotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_rule_id: int | None
    job_post_id: int | None
    to_email: str
    subject: str
    body: str
    status: str
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None
    job_title: str | None = None
    company: str | None = None


class ScanRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    search_keyword: str | None
    location: str | None
    status: str
    jobs_found_count: int
    new_jobs_count: int
    matched_alerts_count: int
    created_at: datetime
    completed_at: datetime | None


class HealthOut(BaseModel):
    status: str = "ok"
    service: str = "JobSpy Alerts Lab API"
    email_mode: str = "console"


class ScanResultOut(BaseModel):
    scan_run: ScanRunOut
    emails_generated: int = Field(description="Number of email notifications created")
