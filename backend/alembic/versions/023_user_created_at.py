"""user created_at

Revision ID: 023
Revises: 022
Create Date: 2026-08-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "023"
down_revision: Union[str, None] = "022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default now() backfills existing users with the migration
    # timestamp — their real signup date isn't recoverable, and the admin
    # dashboard only uses this for a rough "new users" trend.
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("users", "created_at")
