"""workout templates

Revision ID: 016
Revises: 015
Create Date: 2026-08-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_templates",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="Силовая"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_workout_templates_user_id", "workout_templates", ["user_id"])

    op.create_table(
        "template_exercises",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("template_id", sa.String(), sa.ForeignKey("workout_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_template_exercises_template_id", "template_exercises", ["template_id"])


def downgrade() -> None:
    op.drop_table("template_exercises")
    op.drop_table("workout_templates")
