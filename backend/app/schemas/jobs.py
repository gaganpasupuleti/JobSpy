from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    site: str
    title: str
    company_name: str | None
    location_display: str | None
    city: str | None
    state: str | None
    is_remote: bool | None
    job_type: str | None
    min_amount: float | None
    max_amount: float | None
    currency: str | None
    salary_interval: str | None
    date_posted: date | None
    job_url: str
    key_skills: str | None = None
    role_category_id: int | None
    location_id: int | None
    experience_band_id: int | None
    tag_status: str | None = None
    needs_review: bool = False
    scraped_at: datetime


class JobDetailOut(JobListOut):
    description: str | None
    job_url_direct: str | None
    company_url: str | None
    job_level: str | None
    job_function: str | None
    company_industry: str | None
    experience_years_min: int | None
    experience_years_max: int | None
    salary_source: str | None


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[JobListOut]


class ApplyRequest(BaseModel):
    session_id: str | None = None
    student_id: UUID | None = None


class ApplyResponse(BaseModel):
    redirect_url: str
    application_id: UUID


class SaveJobRequest(BaseModel):
    session_id: str = Field(..., min_length=1)


class SaveJobResponse(BaseModel):
    saved: bool
    saved_job_id: UUID
