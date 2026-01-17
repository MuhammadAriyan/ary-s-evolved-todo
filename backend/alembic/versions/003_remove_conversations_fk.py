"""Remove foreign key constraint on conversations.user_id

Better Auth manages users externally, so we can't enforce FK to local users table.

Revision ID: 003
Revises: 002
Create Date: 2026-01-12

"""
from alembic import op

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the foreign key constraint since Better Auth manages users externally
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')


def downgrade() -> None:
    # Re-add the foreign key constraint (only if users table exists and has matching data)
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
