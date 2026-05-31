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
