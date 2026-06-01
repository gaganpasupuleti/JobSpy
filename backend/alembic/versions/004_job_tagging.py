"""job tagging: india verification, tag_status, review flags

Revision ID: 004_job_tagging
Revises: 003_last_verified
Create Date: 2026-06-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_job_tagging"
down_revision: Union[str, None] = "003_last_verified"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("is_india_verified", sa.Boolean(), server_default="false"))
    op.add_column("jobs", sa.Column("tag_status", sa.String(32), server_default="untagged"))
    op.add_column("jobs", sa.Column("needs_review", sa.Boolean(), server_default="false"))
    op.add_column("jobs", sa.Column("review_reason", sa.String(256), nullable=True))
    op.add_column("jobs", sa.Column("role_match_score", sa.Float(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("profile_role_category_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_jobs_tag_status", "jobs", ["tag_status", "is_active"])
    op.create_foreign_key(
        "fk_jobs_profile_role_category",
        "jobs",
        "role_categories",
        ["profile_role_category_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_jobs_profile_role_category", "jobs", type_="foreignkey")
    op.drop_index("ix_jobs_tag_status", table_name="jobs")
    op.drop_column("jobs", "profile_role_category_id")
    op.drop_column("jobs", "role_match_score")
    op.drop_column("jobs", "review_reason")
    op.drop_column("jobs", "needs_review")
    op.drop_column("jobs", "tag_status")
    op.drop_column("jobs", "is_india_verified")
