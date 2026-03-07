"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("muscle_group", sa.String(100), nullable=False),
        sa.Column("secondary_muscles", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("equipment", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "workouts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "workout_id",
            sa.String(),
            sa.ForeignKey("workouts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "workout_exercise_id",
            sa.String(),
            sa.ForeignKey("workout_exercises.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, server_default=""),
        sa.Column("age", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avatar_url", sa.String(500), nullable=True),
    )

    op.create_table(
        "weight_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("kg", sa.Float(), nullable=False),
    )

    op.create_table(
        "goals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("done", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Index for workout ordering
    op.create_index("ix_workouts_created_at", "workouts", ["created_at"])
    op.create_index("ix_weight_entries_date", "weight_entries", ["date"])


def downgrade() -> None:
    op.drop_table("goals")
    op.drop_table("weight_entries")
    op.drop_table("users")
    op.drop_table("exercise_sets")
    op.drop_table("workout_exercises")
    op.drop_table("workouts")
    op.drop_table("exercises")
