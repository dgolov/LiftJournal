"""coach role, coach-athlete links, plan authorship

Revision ID: 025
Revises: 024
Create Date: 2026-09-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "025"
down_revision: Union[str, None] = "024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_coach", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("coach_bio", sa.Text(), nullable=False, server_default=""))
    op.add_column("users", sa.Column("coach_accepting", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "coach_athletes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("coach_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("athlete_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("initiated_by", sa.String(10), nullable=False),
        sa.Column("can_see_private", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("can_edit_plan", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("message", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("coach_id <> athlete_id", name="ck_coach_athletes_not_self"),
    )
    op.create_index("ix_coach_athletes_coach_id", "coach_athletes", ["coach_id"])
    op.create_index("ix_coach_athletes_athlete_id", "coach_athletes", ["athlete_id"])
    # At most one open (pending/active) link per pair; declined/ended ones stay
    # as history and don't block a fresh invite.
    op.create_index(
        "uq_coach_athletes_open_pair", "coach_athletes", ["coach_id", "athlete_id"],
        unique=True, postgresql_where=sa.text("status IN ('pending', 'active')"),
    )

    op.add_column("planned_workouts", sa.Column(
        "created_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    ))
    op.execute("UPDATE planned_workouts SET created_by = user_id")

    op.add_column("notifications", sa.Column(
        "coach_link_id", sa.String(36), sa.ForeignKey("coach_athletes.id", ondelete="CASCADE"), nullable=True,
    ))
    op.add_column("notifications", sa.Column(
        "planned_workout_id", sa.String, sa.ForeignKey("planned_workouts.id", ondelete="CASCADE"), nullable=True,
    ))


def downgrade() -> None:
    op.drop_column("notifications", "planned_workout_id")
    op.drop_column("notifications", "coach_link_id")
    op.drop_column("planned_workouts", "created_by")
    op.drop_index("uq_coach_athletes_open_pair", table_name="coach_athletes")
    op.drop_index("ix_coach_athletes_athlete_id", table_name="coach_athletes")
    op.drop_index("ix_coach_athletes_coach_id", table_name="coach_athletes")
    op.drop_table("coach_athletes")
    op.drop_column("users", "coach_accepting")
    op.drop_column("users", "coach_bio")
    op.drop_column("users", "is_coach")
