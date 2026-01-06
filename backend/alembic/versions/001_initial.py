"""Initial migration: users and tasks tables

Revision ID: 001
Revises:
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create index on email
    op.create_index('ix_users_email', 'users', ['email'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('recurring', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("priority IN ('High', 'Medium', 'Low')", name='check_priority'),
        sa.CheckConstraint("recurring IS NULL OR recurring IN ('daily', 'weekly', 'monthly')", name='check_recurring')
    )

    # Create indexes for tasks
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('idx_tasks_tags', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_completed', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
