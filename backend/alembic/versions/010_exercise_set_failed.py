"""add failed column to exercise_sets

Revision ID: 010
Revises: 009
Create Date: 2026-04-19
"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "exercise_sets",
        sa.Column("failed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("exercise_sets", "failed")
