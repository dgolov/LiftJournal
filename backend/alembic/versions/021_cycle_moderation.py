"""training cycle moderation: is_approved

Revision ID: 021
Revises: 020
Create Date: 2026-08-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "021"
down_revision: Union[str, None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default true so every already-public cycle stays visible —
    # only a fresh transition to public goes to moderation from here on.
    op.add_column("training_cycles", sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"))


def downgrade() -> None:
    op.drop_column("training_cycles", "is_approved")
