"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "role_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "experience_bands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(32), nullable=False, unique=True),
        sa.Column("label", sa.String(64), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("city", sa.String(128), nullable=False),
        sa.Column("state", sa.String(128), nullable=False),
        sa.Column("country", sa.String(64), server_default="India"),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("indeed_location_string", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.UniqueConstraint("city", "state", "country", name="uq_location_city_state"),
    )
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(256), unique=True),
        sa.Column("name", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_category_id", sa.Integer(), sa.ForeignKey("role_categories.id"), nullable=False),
        sa.Column("term", sa.String(128), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false"),
        sa.Column("search_weight", sa.Integer(), server_default="1"),
        sa.UniqueConstraint("role_category_id", "term", name="uq_keyword_role_term"),
    )
    op.create_table(
        "search_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_category_id", sa.Integer(), sa.ForeignKey("role_categories.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("experience_band_id", sa.Integer(), sa.ForeignKey("experience_bands.id")),
        sa.Column("search_term", sa.Text(), nullable=False),
        sa.Column("sites", postgresql.JSON(), nullable=False),
        sa.Column("results_wanted", sa.Integer(), server_default="20"),
        sa.Column("hours_old", sa.Integer(), server_default="168"),
        sa.Column("is_remote", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint(
            "role_category_id", "location_id", "experience_band_id", name="uq_search_profile"
        ),
    )
    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("search_profile_id", sa.Integer(), sa.ForeignKey("search_profiles.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("jobs_found", sa.Integer(), server_default="0"),
        sa.Column("jobs_upserted", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column("site", sa.String(32), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("company_name", sa.String(256)),
        sa.Column("company_url", sa.Text()),
        sa.Column("job_url", sa.Text(), nullable=False),
        sa.Column("job_url_direct", sa.Text()),
        sa.Column("description", sa.Text()),
        sa.Column("description_format", sa.String(32)),
        sa.Column("city", sa.String(128)),
        sa.Column("state", sa.String(128)),
        sa.Column("country", sa.String(64)),
        sa.Column("location_display", sa.String(256)),
        sa.Column("is_remote", sa.Boolean()),
        sa.Column("job_type", sa.String(64)),
        sa.Column("job_level", sa.String(128)),
        sa.Column("job_function", sa.String(256)),
        sa.Column("company_industry", sa.String(256)),
        sa.Column("salary_interval", sa.String(32)),
        sa.Column("min_amount", sa.Float()),
        sa.Column("max_amount", sa.Float()),
        sa.Column("currency", sa.String(8)),
        sa.Column("salary_source", sa.String(32)),
        sa.Column("date_posted", sa.Date()),
        sa.Column("experience_years_min", sa.Integer()),
        sa.Column("experience_years_max", sa.Integer()),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("role_category_id", sa.Integer(), sa.ForeignKey("role_categories.id")),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id")),
        sa.Column("experience_band_id", sa.Integer(), sa.ForeignKey("experience_bands.id")),
        sa.Column("search_profile_id", sa.Integer(), sa.ForeignKey("search_profiles.id")),
        sa.Column("scrape_run_id", sa.Integer(), sa.ForeignKey("scrape_runs.id")),
        sa.UniqueConstraint("site", "external_id", name="uq_job_site_external"),
    )
    op.create_index("ix_jobs_listing", "jobs", ["is_active", "date_posted"])
    op.create_index("ix_jobs_filters", "jobs", ["role_category_id", "location_id", "experience_band_id"])
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_company", "jobs", ["company_name"])
    op.create_table(
        "job_keywords",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("keyword_id", sa.Integer(), sa.ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id")),
        sa.Column("session_id", sa.String(128)),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("source", sa.String(32), server_default="web"),
    )
    op.create_table(
        "saved_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id")),
        sa.Column("session_id", sa.String(128)),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("session_id", "job_id", name="uq_saved_session_job"),
    )


def downgrade() -> None:
    op.drop_table("saved_jobs")
    op.drop_table("applications")
    op.drop_table("job_keywords")
    op.drop_index("ix_jobs_company", "jobs")
    op.drop_index("ix_jobs_title", "jobs")
    op.drop_index("ix_jobs_filters", "jobs")
    op.drop_index("ix_jobs_listing", "jobs")
    op.drop_table("jobs")
    op.drop_table("scrape_runs")
    op.drop_table("search_profiles")
    op.drop_table("keywords")
    op.drop_table("students")
    op.drop_table("locations")
    op.drop_table("experience_bands")
    op.drop_table("role_categories")
