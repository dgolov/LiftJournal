"""add completed_at to user_cycle_runs

Revision ID: 006
Revises: 005
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_cycle_runs', sa.Column('completed_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('user_cycle_runs', 'completed_at')
