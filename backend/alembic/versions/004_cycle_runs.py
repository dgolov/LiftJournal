"""004_cycle_runs

Revision ID: 004
Revises: 003
Create Date: 2026-03-08
"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_cycle_runs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cycle_id', sa.String(), sa.ForeignKey('training_cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'cycle_workout_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('run_id', sa.String(), sa.ForeignKey('user_cycle_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cycle_workout_id', sa.String(), sa.ForeignKey('cycle_workouts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workout_id', sa.String(), sa.ForeignKey('workouts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('cycle_workout_logs')
    op.drop_table('user_cycle_runs')
