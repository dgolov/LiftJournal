"""exercise moderation: replace is_approved/is_private with a single status

Revision ID: 022
Revises: 021
Create Date: 2026-08-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022"
down_revision: Union[str, None] = "021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("exercises", sa.Column("status", sa.String(20), nullable=True))
    op.execute("""
        UPDATE exercises SET status = CASE
            WHEN is_private = true THEN 'private'
            WHEN is_approved = true THEN 'approved'
            ELSE 'pending'
        END
    """)
    op.alter_column("exercises", "status", nullable=False, server_default="approved")
    op.drop_column("exercises", "is_approved")
    op.drop_column("exercises", "is_private")


def downgrade() -> None:
    op.add_column("exercises", sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("exercises", sa.Column("is_private", sa.Boolean(), nullable=False, server_default="false"))
    op.execute("UPDATE exercises SET is_approved = (status = 'approved'), is_private = (status = 'private')")
    op.drop_column("exercises", "status")
