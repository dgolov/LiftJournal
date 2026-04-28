"""workout likes and comments

Revision ID: 014
Revises: 013
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'workout_likes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('workout_id', sa.String, sa.ForeignKey('workouts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint('user_id', 'workout_id', name='uq_workout_likes_user_workout'),
    )

    op.create_table(
        'workout_comments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workout_id', sa.String, sa.ForeignKey('workouts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('workout_comments')
    op.drop_table('workout_likes')
