"""add theme to users

Revision ID: 007
Revises: 006
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('theme', sa.String(10), nullable=False, server_default='light'))


def downgrade():
    op.drop_column('users', 'theme')
