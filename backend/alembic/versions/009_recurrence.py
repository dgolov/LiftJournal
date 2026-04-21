"""add recurrence to planned workouts

Revision ID: 009
Revises: 008
Create Date: 2026-04-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("planned_workouts", sa.Column("recurrence_group_id", sa.String(), nullable=True))
    op.create_index("ix_planned_workouts_recurrence_group", "planned_workouts", ["recurrence_group_id"])


def downgrade() -> None:
    op.drop_index("ix_planned_workouts_recurrence_group", "planned_workouts")
    op.drop_column("planned_workouts", "recurrence_group_id")
