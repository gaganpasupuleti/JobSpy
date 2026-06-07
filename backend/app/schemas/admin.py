from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScrapeRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_profile_id: int
    started_at: datetime
    finished_at: datetime | None
    status: str
    jobs_found: int
    jobs_upserted: int
    error_message: str | None


class ScrapeTriggerResponse(BaseModel):
    message: str
    profiles_queued: int
    runs: list[ScrapeRunOut]


class SearchProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_slug: str
    role_name: str
    city: str
    location_display: str
    experience_label: str
    is_remote: bool
    search_term: str
    sites: list[str]
    last_scraped_at: datetime | None
