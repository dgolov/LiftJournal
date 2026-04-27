"""add user_follows table

Revision ID: 013
Revises: 012
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_follows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('follower_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('following_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint('follower_id', 'following_id'),
    )


def downgrade() -> None:
    op.drop_table('user_follows')
