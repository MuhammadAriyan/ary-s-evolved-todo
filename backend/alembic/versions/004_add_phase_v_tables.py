"""Add Phase V tables and extend tasks table

Revision ID: 004
Revises: 003
Create Date: 2026-02-01

This migration adds 8 new tables for Phase V event-driven microservices:
- audit_logs: Complete audit trail of all task operations
- scheduled_reminders: Scheduled reminders with cron expressions
- friend_connections: Friend relationships between users
- collaboration_groups: Collaboration groups for shared task management
- group_memberships: User memberships in collaboration groups
- task_assignments: Task assignments to specific users
- task_comments: Comments on tasks with @mention support
- direct_messages: Direct messages between friends

Also extends the tasks table with:
- search_vector: Full-text search support
- recurring_pattern: Recurring task patterns (cron expressions)
- parent_task_id: Link to parent task for recurring instances
- recurrence_count: Number of times task has recurred
- group_id: Link to collaboration group
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('task_id', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('operation', sa.String(length=20), nullable=False),
        sa.Column('before_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('after_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('idx_audit_event_id', 'audit_logs', ['event_id'])
    op.create_index('idx_audit_event_type', 'audit_logs', ['event_type'])
    op.create_index('idx_audit_task_id', 'audit_logs', ['task_id', 'timestamp'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id', 'timestamp'])

    # 2. Create scheduled_reminders table
    op.create_table(
        'scheduled_reminders',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('reminder_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('notification_channels', postgresql.ARRAY(sa.String()), nullable=False, server_default="ARRAY['in_app']"),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('last_triggered_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_reminder_status', 'scheduled_reminders', ['status'])
    op.create_index('idx_reminder_task_id', 'scheduled_reminders', ['task_id'])
    op.create_index('idx_reminder_time', 'scheduled_reminders', ['reminder_time'], postgresql_where=sa.text("status = 'pending'"))
    op.create_index('idx_reminder_user_id', 'scheduled_reminders', ['user_id'])

    # 3. Create friend_connections table
    op.create_table(
        'friend_connections',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id_1', sa.String(length=50), nullable=False),
        sa.Column('user_id_2', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('requested_by', sa.String(length=50), nullable=False),
        sa.Column('connected_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('user_id_1 <> user_id_2', name='check_different_users'),
        sa.CheckConstraint('user_id_1 < user_id_2', name='check_user_order'),
        sa.ForeignKeyConstraint(['requested_by'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id_1'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id_2'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id_1', 'user_id_2', name='unique_friendship')
    )
    op.create_index('idx_friend_status', 'friend_connections', ['status'])
    op.create_index('idx_friend_user1', 'friend_connections', ['user_id_1', 'status'])
    op.create_index('idx_friend_user2', 'friend_connections', ['user_id_2', 'status'])

    # 4. Create collaboration_groups table
    op.create_table(
        'collaboration_groups',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_user_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_group_name', 'collaboration_groups', ['name'])
    op.create_index('idx_group_owner', 'collaboration_groups', ['owner_user_id'])

    # 5. Create group_memberships table
    op.create_table(
        'group_memberships',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='member'),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='{"add_tasks": false, "edit_tasks": false, "delete_tasks": false, "comment": true, "assign": false}'),
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['collaboration_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'user_id', name='unique_group_membership')
    )
    op.create_index('idx_membership_group', 'group_memberships', ['group_id'])
    op.create_index('idx_membership_role', 'group_memberships', ['role'])
    op.create_index('idx_membership_user', 'group_memberships', ['user_id'])

    # 6. Create task_assignments table
    op.create_table(
        'task_assignments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.String(length=50), nullable=False),
        sa.Column('assigned_to_user_id', sa.String(length=50), nullable=False),
        sa.Column('assigned_by_user_id', sa.String(length=50), nullable=False),
        sa.Column('group_id', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('assigned_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['collaboration_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_assignment_group', 'task_assignments', ['group_id'])
    op.create_index('idx_assignment_task', 'task_assignments', ['task_id'])
    op.create_index('idx_assignment_to_user', 'task_assignments', ['assigned_to_user_id', 'status'])

    # 7. Create task_comments table
    op.create_table(
        'task_comments',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('task_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('group_id', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('mentioned_users', postgresql.ARRAY(sa.String()), nullable=True, server_default="ARRAY[]::TEXT[]"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['collaboration_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_comment_group', 'task_comments', ['group_id'])
    op.create_index('idx_comment_mentions', 'task_comments', ['mentioned_users'], postgresql_using='gin')
    op.create_index('idx_comment_task', 'task_comments', ['task_id', 'created_at'])
    op.create_index('idx_comment_user', 'task_comments', ['user_id'])

    # 8. Create direct_messages table
    op.create_table(
        'direct_messages',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('from_user_id', sa.String(length=50), nullable=False),
        sa.Column('to_user_id', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('read_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['from_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dm_conversation', 'direct_messages', ['from_user_id', 'to_user_id', 'sent_at'])
    op.create_index('idx_dm_from_user', 'direct_messages', ['from_user_id', 'sent_at'])
    op.create_index('idx_dm_to_user', 'direct_messages', ['to_user_id', 'sent_at'])
    op.create_index('idx_dm_unread', 'direct_messages', ['to_user_id'], postgresql_where=sa.text('read_at IS NULL'))

    # 9. Extend tasks table with Phase V columns
    op.add_column('task', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))
    op.add_column('task', sa.Column('recurring_pattern', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('task', sa.Column('parent_task_id', sa.String(length=50), nullable=True))
    op.add_column('task', sa.Column('recurrence_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('task', sa.Column('group_id', sa.String(length=50), nullable=True))

    op.create_foreign_key('fk_task_parent', 'task', 'task', ['parent_task_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_task_group', 'task', 'collaboration_groups', ['group_id'], ['id'], ondelete='CASCADE')

    op.create_index('idx_tasks_group', 'task', ['group_id'])
    op.create_index('idx_tasks_parent', 'task', ['parent_task_id'])
    op.create_index('idx_tasks_recurring', 'task', ['recurring_pattern'], postgresql_where=sa.text('recurring_pattern IS NOT NULL'))
    op.create_index('idx_tasks_search_vector', 'task', ['search_vector'], postgresql_using='gin')

    # 10. Create trigger function for automatic search_vector updates
    op.execute("""
        CREATE OR REPLACE FUNCTION tasks_search_vector_update()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 11. Create trigger on tasks table
    op.execute("""
        CREATE TRIGGER tasks_search_vector_trigger
        BEFORE INSERT OR UPDATE ON task
        FOR EACH ROW
        EXECUTE FUNCTION tasks_search_vector_update();
    """)


def downgrade() -> None:
    # Drop trigger and function
    op.execute('DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON task')
    op.execute('DROP FUNCTION IF EXISTS tasks_search_vector_update()')

    # Drop indexes on tasks table
    op.drop_index('idx_tasks_search_vector', table_name='task')
    op.drop_index('idx_tasks_recurring', table_name='task')
    op.drop_index('idx_tasks_parent', table_name='task')
    op.drop_index('idx_tasks_group', table_name='task')

    # Drop foreign keys on tasks table
    op.drop_constraint('fk_task_group', 'task', type_='foreignkey')
    op.drop_constraint('fk_task_parent', 'task', type_='foreignkey')

    # Drop columns from tasks table
    op.drop_column('task', 'group_id')
    op.drop_column('task', 'recurrence_count')
    op.drop_column('task', 'parent_task_id')
    op.drop_column('task', 'recurring_pattern')
    op.drop_column('task', 'search_vector')

    # Drop all new tables (in reverse order of creation)
    op.drop_index('idx_dm_unread', table_name='direct_messages')
    op.drop_index('idx_dm_to_user', table_name='direct_messages')
    op.drop_index('idx_dm_from_user', table_name='direct_messages')
    op.drop_index('idx_dm_conversation', table_name='direct_messages')
    op.drop_table('direct_messages')

    op.drop_index('idx_comment_user', table_name='task_comments')
    op.drop_index('idx_comment_task', table_name='task_comments')
    op.drop_index('idx_comment_mentions', table_name='task_comments')
    op.drop_index('idx_comment_group', table_name='task_comments')
    op.drop_table('task_comments')

    op.drop_index('idx_assignment_to_user', table_name='task_assignments')
    op.drop_index('idx_assignment_task', table_name='task_assignments')
    op.drop_index('idx_assignment_group', table_name='task_assignments')
    op.drop_table('task_assignments')

    op.drop_index('idx_membership_user', table_name='group_memberships')
    op.drop_index('idx_membership_role', table_name='group_memberships')
    op.drop_index('idx_membership_group', table_name='group_memberships')
    op.drop_table('group_memberships')

    op.drop_index('idx_group_owner', table_name='collaboration_groups')
    op.drop_index('idx_group_name', table_name='collaboration_groups')
    op.drop_table('collaboration_groups')

    op.drop_index('idx_friend_user2', table_name='friend_connections')
    op.drop_index('idx_friend_user1', table_name='friend_connections')
    op.drop_index('idx_friend_status', table_name='friend_connections')
    op.drop_table('friend_connections')

    op.drop_index('idx_reminder_user_id', table_name='scheduled_reminders')
    op.drop_index('idx_reminder_time', table_name='scheduled_reminders')
    op.drop_index('idx_reminder_task_id', table_name='scheduled_reminders')
    op.drop_index('idx_reminder_status', table_name='scheduled_reminders')
    op.drop_table('scheduled_reminders')

    op.drop_index('idx_audit_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_task_id', table_name='audit_logs')
    op.drop_index('idx_audit_event_type', table_name='audit_logs')
    op.drop_index('idx_audit_event_id', table_name='audit_logs')
    op.drop_table('audit_logs')
