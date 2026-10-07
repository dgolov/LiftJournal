"""cycle main exercises, plans linked to a cycle layout

Revision ID: 026
Revises: 025
Create Date: 2026-09-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "026"
down_revision: Union[str, None] = "025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("training_cycles", sa.Column("main_exercises", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("planned_workouts", sa.Column(
        "cycle_id", sa.String, sa.ForeignKey("training_cycles.id", ondelete="SET NULL"), nullable=True,
    ))
    op.add_column("planned_workouts", sa.Column("cycle_schedule_id", sa.String(36), nullable=True))
    op.create_index("ix_planned_workouts_cycle_schedule_id", "planned_workouts", ["cycle_schedule_id"])


def downgrade() -> None:
    op.drop_index("ix_planned_workouts_cycle_schedule_id", table_name="planned_workouts")
    op.drop_column("planned_workouts", "cycle_schedule_id")
    op.drop_column("planned_workouts", "cycle_id")
    op.drop_column("training_cycles", "main_exercises")
