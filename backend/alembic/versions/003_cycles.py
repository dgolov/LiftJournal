"""add training cycles and user maxes

Revision ID: 003
Revises: 002
Create Date: 2026-03-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "training_cycles",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("author_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_training_cycles_created_by", "training_cycles", ["created_by"])
    op.create_index("ix_training_cycles_is_public", "training_cycles", ["is_public"])

    op.create_table(
        "cycle_workouts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cycle_id", sa.String(), sa.ForeignKey("training_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("workout_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_cycle_workouts_cycle_id", "cycle_workouts", ["cycle_id"])

    op.create_table(
        "cycle_exercises",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cycle_workout_id", sa.String(), sa.ForeignKey("cycle_workouts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "cycle_sets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cycle_exercise_id", sa.String(), sa.ForeignKey("cycle_exercises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("percent_1rm", sa.Float(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "user_maxes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.Date(), nullable=False),
        sa.UniqueConstraint("user_id", "exercise_name", name="uq_user_maxes"),
    )
    op.create_index("ix_user_maxes_user_id", "user_maxes", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_maxes")
    op.drop_table("cycle_sets")
    op.drop_table("cycle_exercises")
    op.drop_table("cycle_workouts")
    op.drop_table("training_cycles")
