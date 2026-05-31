"""add last_verified_at to jobs

Revision ID: 003_last_verified
Revises: 002_key_skills
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_last_verified"
down_revision: Union[str, None] = "002_key_skills"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_last_verified_at", "jobs", ["last_verified_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_last_verified_at", table_name="jobs")
    op.drop_column("jobs", "last_verified_at")
