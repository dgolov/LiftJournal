"""exercise moderation: is_approved + created_by

Revision ID: 019
Revises: 018
Create Date: 2026-08-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default true so every existing exercise (built-in and any custom
    # ones already in use) stays visible — only newly submitted custom
    # exercises going forward start out pending.
    op.add_column("exercises", sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("exercises", sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))


def downgrade() -> None:
    op.drop_column("exercises", "created_by")
    op.drop_column("exercises", "is_approved")
