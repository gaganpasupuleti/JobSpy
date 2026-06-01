from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaggingQueueItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company_name: str | None
    site: str
    location_display: str | None
    tag_status: str
    needs_review: bool
    review_reason: str | None
    is_india_verified: bool
    role_category_id: int | None
    role_name: str | None
    role_slug: str | None
    profile_role_name: str | None
    experience_band_id: int | None
    experience_label: str | None
    experience_slug: str | None
    role_match_score: float | None
    date_posted: date | None
    scraped_at: datetime


class TaggingQueueResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TaggingQueueItem]


class ManualTagUpdate(BaseModel):
    role: str | None = Field(None, description="Role category slug")
    experience: str | None = Field(None, description="Experience band slug")
    is_india_verified: bool | None = None
    approve: bool = Field(
        False,
        description="Clear review flag after applying tags (publish if complete)",
    )


class ManualTagResponse(BaseModel):
    id: UUID
    tag_status: str
    needs_review: bool
    review_reason: str | None
    role_slug: str | None
    experience_slug: str | None
    is_india_verified: bool
    message: str
