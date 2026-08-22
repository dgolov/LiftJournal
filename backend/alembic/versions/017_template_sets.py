"""template sets (replace target_sets with real weight/reps)

Revision ID: 017
Revises: 016
Create Date: 2026-08-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "template_sets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("template_exercise_id", sa.String(), sa.ForeignKey("template_exercises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_template_sets_template_exercise_id", "template_sets", ["template_exercise_id"])
    op.drop_column("template_exercises", "target_sets")


def downgrade() -> None:
    op.add_column("template_exercises", sa.Column("target_sets", sa.Integer(), nullable=False, server_default="3"))
    op.drop_table("template_sets")
