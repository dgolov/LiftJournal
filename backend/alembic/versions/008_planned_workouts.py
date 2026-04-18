"""add planned workouts

Revision ID: 008
Revises: 007
Create Date: 2026-04-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "planned_workouts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="Силовая"),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("completed_workout_id", sa.String(), sa.ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_planned_workouts_user_id", "planned_workouts", ["user_id"])
    op.create_index("ix_planned_workouts_scheduled_date", "planned_workouts", ["scheduled_date"])

    op.create_table(
        "planned_exercises",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("planned_workout_id", sa.String(), sa.ForeignKey("planned_workouts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_planned_exercises_workout_id", "planned_exercises", ["planned_workout_id"])

    op.create_table(
        "planned_sets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("planned_exercise_id", sa.String(), sa.ForeignKey("planned_exercises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("planned_sets")
    op.drop_table("planned_exercises")
    op.drop_table("planned_workouts")
