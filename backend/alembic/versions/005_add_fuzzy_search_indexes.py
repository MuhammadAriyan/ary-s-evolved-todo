"""Alembic migration: Add pg_trgm extension and trigram indexes for fuzzy search."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_fuzzy_search_indexes'
down_revision = '004_add_phase_v_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add pg_trgm extension and create trigram indexes for fuzzy search."""

    # Enable pg_trgm extension
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    # Create trigram index on title
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_title_trgm
        ON tasks USING GIN(title gin_trgm_ops);
    ''')

    # Create trigram index on description
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_description_trgm
        ON tasks USING GIN(description gin_trgm_ops);
    ''')

    print("✓ pg_trgm extension enabled")
    print("✓ Trigram index created on tasks.title")
    print("✓ Trigram index created on tasks.description")


def downgrade() -> None:
    """Remove trigram indexes and pg_trgm extension."""

    # Drop trigram indexes
    op.execute('DROP INDEX IF EXISTS idx_tasks_title_trgm;')
    op.execute('DROP INDEX IF EXISTS idx_tasks_description_trgm;')

    # Note: We don't drop the extension as other features might depend on it
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm;')

    print("✓ Trigram indexes removed")
