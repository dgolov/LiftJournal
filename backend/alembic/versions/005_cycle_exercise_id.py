"""add exercise_id to cycle_exercises

Revision ID: 005
Revises: 004
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cycle_exercises', sa.Column('exercise_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_cycle_exercises_exercise_id',
        'cycle_exercises', 'exercises',
        ['exercise_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_cycle_exercises_exercise_id', 'cycle_exercises', type_='foreignkey')
    op.drop_column('cycle_exercises', 'exercise_id')
