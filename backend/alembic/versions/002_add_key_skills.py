"""add key_skills column to jobs

Revision ID: 002_key_skills
Revises: 001_initial
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_key_skills"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("key_skills", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "key_skills")
