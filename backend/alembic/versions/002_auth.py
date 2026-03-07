"""add auth fields to users and user_id to workouts

Revision ID: 002
Revises: 001
Create Date: 2026-03-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add auth fields to users
    op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("hashed_password", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])

    # Add user_id FK to workouts
    op.add_column("workouts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_workouts_user_id",
        "workouts", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_workouts_user_id", "workouts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_workouts_user_id", "workouts")
    op.drop_constraint("fk_workouts_user_id", "workouts", type_="foreignkey")
    op.drop_column("workouts", "user_id")

    op.drop_index("ix_users_email", "users")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "email")
