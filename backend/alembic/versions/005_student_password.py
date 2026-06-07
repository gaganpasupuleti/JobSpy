"""add password_hash to students

Revision ID: 005_student_password
Revises: 004_job_tagging
Create Date: 2026-06-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_student_password"
down_revision: Union[str, None] = "004_job_tagging"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("students", sa.Column("password_hash", sa.String(256), nullable=True))


def downgrade() -> None:
    op.drop_column("students", "password_hash")
