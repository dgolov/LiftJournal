"""replace age with birth_date on users

Revision ID: 012
Revises: 011
Create Date: 2026-04-24
"""
from alembic import op
import sqlalchemy as sa

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True))
    op.drop_column('users', 'age')


def downgrade() -> None:
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=False, server_default='0'))
    op.drop_column('users', 'birth_date')
