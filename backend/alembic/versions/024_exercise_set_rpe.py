"""exercise set RPE

Revision ID: 024
Revises: 023
Create Date: 2026-09-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "024"
down_revision: Union[str, None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Optional — a set logged before this migration, or one the lifter
    # simply chose not to rate, has no RPE at all rather than a fake default.
    op.add_column("exercise_sets", sa.Column("rpe", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("exercise_sets", "rpe")
