from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.admin import ScrapeRunOut


class CountByLabel(BaseModel):
    label: str
    slug: str | None = None
    count: int


class JobsSummary(BaseModel):
    live: int
    inactive: int
    total: int


class SearchProfilesSummary(BaseModel):
    total_active: int
    never_scraped: int
    scraped_last_24h: int


class DashboardStatsOut(BaseModel):
    last_job_scraped_at: datetime | None
    last_successful_scrape_at: datetime | None
    scrape_in_progress: bool
    jobs: JobsSummary
    by_site: list[CountByLabel]
    by_role: list[CountByLabel]
    by_experience: list[CountByLabel]
    by_job_level: list[CountByLabel]
    search_profiles: SearchProfilesSummary
    recent_scrape_runs: list[ScrapeRunOut]


class DashboardRefreshOut(BaseModel):
    message: str
    profiles_queued: int


class DashboardRefreshStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scrape_in_progress: bool
    current_run: ScrapeRunOut | None
    recent_scrape_runs: list[ScrapeRunOut]
