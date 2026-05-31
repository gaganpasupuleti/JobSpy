import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ScrapeStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class RoleCategory(Base):
    __tablename__ = "role_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    keywords: Mapped[list["Keyword"]] = relationship(back_populates="role_category")
    search_profiles: Mapped[list["SearchProfile"]] = relationship(back_populates="role_category")
    jobs: Mapped[list["Job"]] = relationship(back_populates="role_category")


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_category_id: Mapped[int] = mapped_column(ForeignKey("role_categories.id"), nullable=False)
    term: Mapped[str] = mapped_column(String(128), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    search_weight: Mapped[int] = mapped_column(Integer, default=1)

    role_category: Mapped["RoleCategory"] = relationship(back_populates="keywords")
    job_links: Mapped[list["JobKeyword"]] = relationship(back_populates="keyword")

    __table_args__ = (UniqueConstraint("role_category_id", "term", name="uq_keyword_role_term"),)


class ExperienceBand(Base):
    __tablename__ = "experience_bands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    search_profiles: Mapped[list["SearchProfile"]] = relationship(back_populates="experience_band")
    jobs: Mapped[list["Job"]] = relationship(back_populates="experience_band")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    country: Mapped[str] = mapped_column(String(64), default="India")
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    indeed_location_string: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    search_profiles: Mapped[list["SearchProfile"]] = relationship(back_populates="location")
    jobs: Mapped[list["Job"]] = relationship(back_populates="location")

    __table_args__ = (UniqueConstraint("city", "state", "country", name="uq_location_city_state"),)


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_category_id: Mapped[int] = mapped_column(ForeignKey("role_categories.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    experience_band_id: Mapped[int | None] = mapped_column(ForeignKey("experience_bands.id"))
    search_term: Mapped[str] = mapped_column(Text, nullable=False)
    sites: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    results_wanted: Mapped[int] = mapped_column(Integer, default=20)
    hours_old: Mapped[int | None] = mapped_column(Integer, default=168)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    role_category: Mapped["RoleCategory"] = relationship(back_populates="search_profiles")
    location: Mapped["Location"] = relationship(back_populates="search_profiles")
    experience_band: Mapped["ExperienceBand | None"] = relationship(back_populates="search_profiles")
    scrape_runs: Mapped[list["ScrapeRun"]] = relationship(back_populates="search_profile")
    jobs: Mapped[list["Job"]] = relationship(back_populates="search_profile")

    __table_args__ = (
        UniqueConstraint(
            "role_category_id", "location_id", "experience_band_id", name="uq_search_profile"
        ),
    )


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    search_profile_id: Mapped[int] = mapped_column(ForeignKey("search_profiles.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default=ScrapeStatus.PENDING.value)
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_upserted: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    search_profile: Mapped["SearchProfile"] = relationship(back_populates="scrape_runs")
    jobs: Mapped[list["Job"]] = relationship(back_populates="scrape_run")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    site: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(256))
    company_url: Mapped[str | None] = mapped_column(Text)
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    job_url_direct: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    key_skills: Mapped[str | None] = mapped_column(Text)
    description_format: Mapped[str | None] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(128))
    state: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64))
    location_display: Mapped[str | None] = mapped_column(String(256))
    is_remote: Mapped[bool | None] = mapped_column(Boolean)
    job_type: Mapped[str | None] = mapped_column(String(64))
    job_level: Mapped[str | None] = mapped_column(String(128))
    job_function: Mapped[str | None] = mapped_column(String(256))
    company_industry: Mapped[str | None] = mapped_column(String(256))
    salary_interval: Mapped[str | None] = mapped_column(String(32))
    min_amount: Mapped[float | None] = mapped_column(Float)
    max_amount: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(8))
    salary_source: Mapped[str | None] = mapped_column(String(32))
    date_posted: Mapped[date | None] = mapped_column(Date)
    experience_years_min: Mapped[int | None] = mapped_column(Integer)
    experience_years_max: Mapped[int | None] = mapped_column(Integer)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_category_id: Mapped[int | None] = mapped_column(ForeignKey("role_categories.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    experience_band_id: Mapped[int | None] = mapped_column(ForeignKey("experience_bands.id"))
    search_profile_id: Mapped[int | None] = mapped_column(ForeignKey("search_profiles.id"))
    scrape_run_id: Mapped[int | None] = mapped_column(ForeignKey("scrape_runs.id"))

    role_category: Mapped["RoleCategory | None"] = relationship(back_populates="jobs")
    location: Mapped["Location | None"] = relationship(back_populates="jobs")
    experience_band: Mapped["ExperienceBand | None"] = relationship(back_populates="jobs")
    search_profile: Mapped["SearchProfile | None"] = relationship(back_populates="jobs")
    scrape_run: Mapped["ScrapeRun | None"] = relationship(back_populates="jobs")
    keyword_links: Mapped[list["JobKeyword"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(back_populates="job")
    saved_by: Mapped[list["SavedJob"]] = relationship(back_populates="job")

    __table_args__ = (
        UniqueConstraint("site", "external_id", name="uq_job_site_external"),
        Index("ix_jobs_listing", "is_active", "date_posted"),
        Index("ix_jobs_filters", "role_category_id", "location_id", "experience_band_id"),
        Index("ix_jobs_title", "title"),
        Index("ix_jobs_company", "company_name"),
    )


class JobKeyword(Base):
    __tablename__ = "job_keywords"

    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)

    job: Mapped["Job"] = relationship(back_populates="keyword_links")
    keyword: Mapped["Keyword"] = relationship(back_populates="job_links")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(256), unique=True)
    name: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    applications: Mapped[list["Application"]] = relationship(back_populates="student")
    saved_jobs: Mapped[list["SavedJob"]] = relationship(back_populates="student")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("students.id"))
    session_id: Mapped[str | None] = mapped_column(String(128))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str] = mapped_column(String(32), default="web")

    student: Mapped["Student | None"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("students.id"))
    session_id: Mapped[str | None] = mapped_column(String(128))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student | None"] = relationship(back_populates="saved_jobs")
    job: Mapped["Job"] = relationship(back_populates="saved_by")

    __table_args__ = (UniqueConstraint("session_id", "job_id", name="uq_saved_session_job"),)
