from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    sort_order: int


class ExperienceBandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    label: str
    sort_order: int


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city: str
    state: str
    country: str
    display_name: str
    is_active: bool


class KeywordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    term: str
    is_primary: bool
    role_category_id: int


class ConfigOut(BaseModel):
    default_sites: list[str]
    default_results_wanted: int
    default_hours_old: int


class SiteOut(BaseModel):
    slug: str
    label: str
    active_count: int
