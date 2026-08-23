"""exercise is_private

Revision ID: 020
Revises: 019
Create Date: 2026-08-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("exercises", sa.Column("is_private", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("exercises", "is_private")
