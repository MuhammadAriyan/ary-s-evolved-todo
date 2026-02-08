# Data Model: Phase V Event-Driven Cloud Deployment

**Date**: 2026-01-31
**Feature**: Phase V Event-Driven Cloud Deployment
**Status**: Phase 1 Design Output

## Overview

This document defines the database schema extensions for Phase V, including new tables for audit logs, scheduled reminders, collaboration features (friends, groups, permissions), task assignments, comments, and direct messaging.

**Database**: Neon PostgreSQL (existing, extended)
**ORM**: SQLModel
**Migration Tool**: Alembic

---

## Existing Tables (Phase II/III - No Changes)

### users
Managed by Better Auth - no changes required.

### tasks
Extended with new columns for search and recurring patterns.

### conversations
Existing chat history table - no changes required.

### messages
Existing conversation messages table - no changes required.

---

## New Tables for Phase V

### 1. audit_logs

**Purpose**: Complete audit trail of all task operations for compliance, debugging, and conflict resolution.

**Schema**:

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    task_id VARCHAR(50),
    user_id VARCHAR(50) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    before_state JSONB,
    after_state JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_task_id ON audit_logs(task_id, timestamp DESC);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_event_id ON audit_logs(event_id);
```

**SQLModel**:

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID
from datetime import datetime
from typing import Optional
import uuid

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, nullable=False)
    event_type: str = Field(max_length=50, nullable=False)
    task_id: Optional[str] = Field(max_length=50, nullable=True)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    operation: str = Field(max_length=20, nullable=False)
    before_state: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    after_state: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    ip_address: Optional[str] = Field(default=None, sa_column=Column(INET))
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    timestamp: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_audit_user_id', 'user_id', 'timestamp'),
        Index('idx_audit_task_id', 'task_id', 'timestamp'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_event_type', 'event_type'),
    )
```

**Retention Policy**: Archive logs older than 90 days to cold storage (S3/Oracle Object Storage).

---

### 2. scheduled_reminders

**Purpose**: Store scheduled reminders for tasks with exact times and cron expressions.

**Schema**:

```sql
CREATE TABLE scheduled_reminders (
    id BIGSERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    reminder_time TIMESTAMPTZ NOT NULL,
    cron_expression VARCHAR(100),
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    notification_channels TEXT[] NOT NULL DEFAULT ARRAY['in_app'],
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_reminder_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_reminder_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_reminder_user_id ON scheduled_reminders(user_id);
CREATE INDEX idx_reminder_task_id ON scheduled_reminders(task_id);
CREATE INDEX idx_reminder_time ON scheduled_reminders(reminder_time) WHERE status = 'pending';
CREATE INDEX idx_reminder_status ON scheduled_reminders(status);
```

**SQLModel**:

```python
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

class ScheduledReminder(SQLModel, table=True):
    __tablename__ = "scheduled_reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    reminder_time: datetime = Field(nullable=False)
    cron_expression: Optional[str] = Field(max_length=100, nullable=True)
    timezone: str = Field(max_length=50, default="UTC")
    notification_channels: list[str] = Field(
        default=["in_app"],
        sa_column=Column(ARRAY(String))
    )
    status: str = Field(max_length=20, default="pending")
    last_triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_reminder_user_id', 'user_id'),
        Index('idx_reminder_task_id', 'task_id'),
        Index('idx_reminder_time', 'reminder_time'),
        Index('idx_reminder_status', 'status'),
    )
```

**Status Values**: `pending`, `triggered`, `cancelled`, `expired`

---

### 3. friend_connections

**Purpose**: Store friend relationships between users with online status tracking.

**Schema**:

```sql
CREATE TABLE friend_connections (
    id BIGSERIAL PRIMARY KEY,
    user_id_1 VARCHAR(50) NOT NULL,
    user_id_2 VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    requested_by VARCHAR(50) NOT NULL,
    connected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_friend_user1 FOREIGN KEY (user_id_1) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_friend_user2 FOREIGN KEY (user_id_2) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_friend_requester FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_friendship UNIQUE (user_id_1, user_id_2),
    CONSTRAINT check_different_users CHECK (user_id_1 <> user_id_2),
    CONSTRAINT check_user_order CHECK (user_id_1 < user_id_2)
);

CREATE INDEX idx_friend_user1 ON friend_connections(user_id_1, status);
CREATE INDEX idx_friend_user2 ON friend_connections(user_id_2, status);
CREATE INDEX idx_friend_status ON friend_connections(status);
```

**SQLModel**:

```python
class FriendConnection(SQLModel, table=True):
    __tablename__ = "friend_connections"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id_1: str = Field(foreign_key="users.id", nullable=False)
    user_id_2: str = Field(foreign_key="users.id", nullable=False)
    status: str = Field(max_length=20, default="pending")
    requested_by: str = Field(foreign_key="users.id", nullable=False)
    connected_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_friend_user1', 'user_id_1', 'status'),
        Index('idx_friend_user2', 'user_id_2', 'status'),
        Index('idx_friend_status', 'status'),
    )
```

**Status Values**: `pending`, `accepted`, `blocked`, `rejected`

**Note**: Always store user IDs in sorted order (user_id_1 < user_id_2) to prevent duplicate friendships.

---

### 4. collaboration_groups

**Purpose**: Store collaboration groups for shared task management.

**Schema**:

```sql
CREATE TABLE collaboration_groups (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_user_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_group_owner FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_group_owner ON collaboration_groups(owner_user_id);
CREATE INDEX idx_group_name ON collaboration_groups(name);
```

**SQLModel**:

```python
class CollaborationGroup(SQLModel, table=True):
    __tablename__ = "collaboration_groups"

    id: str = Field(primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    owner_user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_group_owner', 'owner_user_id'),
        Index('idx_group_name', 'name'),
    )
```

---

### 5. group_memberships

**Purpose**: Store user memberships in collaboration groups with role-based permissions.

**Schema**:

```sql
CREATE TABLE group_memberships (
    id BIGSERIAL PRIMARY KEY,
    group_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    permissions JSONB NOT NULL DEFAULT '{"add_tasks": false, "edit_tasks": false, "delete_tasks": false, "comment": true, "assign": false}',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_membership_group FOREIGN KEY (group_id) REFERENCES collaboration_groups(id) ON DELETE CASCADE,
    CONSTRAINT fk_membership_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_group_membership UNIQUE (group_id, user_id)
);

CREATE INDEX idx_membership_group ON group_memberships(group_id);
CREATE INDEX idx_membership_user ON group_memberships(user_id);
CREATE INDEX idx_membership_role ON group_memberships(role);
```

**SQLModel**:

```python
class GroupMembership(SQLModel, table=True):
    __tablename__ = "group_memberships"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: str = Field(foreign_key="collaboration_groups.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    role: str = Field(max_length=20, default="member")
    permissions: dict = Field(
        default={
            "add_tasks": False,
            "edit_tasks": False,
            "delete_tasks": False,
            "comment": True,
            "assign": False
        },
        sa_column=Column(JSONB)
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_membership_group', 'group_id'),
        Index('idx_membership_user', 'user_id'),
        Index('idx_membership_role', 'role'),
    )
```

**Role Values**: `owner`, `admin`, `member`

**Permission Keys**: `add_tasks`, `edit_tasks`, `delete_tasks`, `comment`, `assign`

---

### 6. task_assignments

**Purpose**: Store task assignments to specific users within groups.

**Schema**:

```sql
CREATE TABLE task_assignments (
    id BIGSERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    assigned_to_user_id VARCHAR(50) NOT NULL,
    assigned_by_user_id VARCHAR(50) NOT NULL,
    group_id VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT fk_assignment_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignment_to_user FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignment_by_user FOREIGN KEY (assigned_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignment_group FOREIGN KEY (group_id) REFERENCES collaboration_groups(id) ON DELETE CASCADE
);

CREATE INDEX idx_assignment_task ON task_assignments(task_id);
CREATE INDEX idx_assignment_to_user ON task_assignments(assigned_to_user_id, status);
CREATE INDEX idx_assignment_group ON task_assignments(group_id);
```

**SQLModel**:

```python
class TaskAssignment(SQLModel, table=True):
    __tablename__ = "task_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    assigned_to_user_id: str = Field(foreign_key="users.id", nullable=False)
    assigned_by_user_id: str = Field(foreign_key="users.id", nullable=False)
    group_id: Optional[str] = Field(foreign_key="collaboration_groups.id", nullable=True)
    status: str = Field(max_length=20, default="pending")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    __table_args__ = (
        Index('idx_assignment_task', 'task_id'),
        Index('idx_assignment_to_user', 'assigned_to_user_id', 'status'),
        Index('idx_assignment_group', 'group_id'),
    )
```

**Status Values**: `pending`, `in_progress`, `completed`, `cancelled`

---

### 7. task_comments

**Purpose**: Store comments on tasks with @mention support.

**Schema**:

```sql
CREATE TABLE task_comments (
    id VARCHAR(50) PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    group_id VARCHAR(50),
    content TEXT NOT NULL,
    mentioned_users TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_comment_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_group FOREIGN KEY (group_id) REFERENCES collaboration_groups(id) ON DELETE CASCADE
);

CREATE INDEX idx_comment_task ON task_comments(task_id, created_at DESC);
CREATE INDEX idx_comment_user ON task_comments(user_id);
CREATE INDEX idx_comment_group ON task_comments(group_id);
CREATE INDEX idx_comment_mentions ON task_comments USING GIN(mentioned_users);
```

**SQLModel**:

```python
class TaskComment(SQLModel, table=True):
    __tablename__ = "task_comments"

    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    group_id: Optional[str] = Field(foreign_key="collaboration_groups.id", nullable=True)
    content: str = Field(sa_column=Column(Text), nullable=False)
    mentioned_users: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String))
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_comment_task', 'task_id', 'created_at'),
        Index('idx_comment_user', 'user_id'),
        Index('idx_comment_group', 'group_id'),
    )
```

---

### 8. direct_messages

**Purpose**: Store direct messages between friends.

**Schema**:

```sql
CREATE TABLE direct_messages (
    id VARCHAR(50) PRIMARY KEY,
    from_user_id VARCHAR(50) NOT NULL,
    to_user_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ,

    CONSTRAINT fk_dm_from_user FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_dm_to_user FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_dm_from_user ON direct_messages(from_user_id, sent_at DESC);
CREATE INDEX idx_dm_to_user ON direct_messages(to_user_id, sent_at DESC);
CREATE INDEX idx_dm_conversation ON direct_messages(from_user_id, to_user_id, sent_at DESC);
CREATE INDEX idx_dm_unread ON direct_messages(to_user_id) WHERE read_at IS NULL;
```

**SQLModel**:

```python
class DirectMessage(SQLModel, table=True):
    __tablename__ = "direct_messages"

    id: str = Field(primary_key=True)
    from_user_id: str = Field(foreign_key="users.id", nullable=False)
    to_user_id: str = Field(foreign_key="users.id", nullable=False)
    content: str = Field(sa_column=Column(Text), nullable=False)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    __table_args__ = (
        Index('idx_dm_from_user', 'from_user_id', 'sent_at'),
        Index('idx_dm_to_user', 'to_user_id', 'sent_at'),
        Index('idx_dm_conversation', 'from_user_id', 'to_user_id', 'sent_at'),
    )
```

---

## Extended Existing Tables

### tasks (Extended)

**New Columns**:

```sql
ALTER TABLE tasks
ADD COLUMN search_vector tsvector,
ADD COLUMN recurring_pattern JSONB,
ADD COLUMN parent_task_id VARCHAR(50),
ADD COLUMN recurrence_count INTEGER DEFAULT 0,
ADD COLUMN group_id VARCHAR(50),
ADD CONSTRAINT fk_task_parent FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_task_group FOREIGN KEY (group_id) REFERENCES collaboration_groups(id) ON DELETE CASCADE;

-- Full-text search index
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN(search_vector);

-- Trigger for automatic search_vector update
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

CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_search_vector_update();

-- Indexes for new columns
CREATE INDEX idx_tasks_group ON tasks(group_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_recurring ON tasks(recurring_pattern) WHERE recurring_pattern IS NOT NULL;
```

**SQLModel Extension**:

```python
from sqlalchemy.dialects.postgresql import TSVECTOR

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # ... existing fields ...

    # New fields for Phase V
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR, nullable=True)
    )
    recurring_pattern: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)
    )
    parent_task_id: Optional[str] = Field(
        foreign_key="tasks.id",
        nullable=True
    )
    recurrence_count: int = Field(default=0)
    group_id: Optional[str] = Field(
        foreign_key="collaboration_groups.id",
        nullable=True
    )
```

**Recurring Pattern Schema**:

```json
{
  "type": "cron",
  "expression": "0 9 * * 1-5",
  "timezone": "America/New_York",
  "end_date": "2026-12-31T23:59:59Z"
}
```

---

## Database Migration Strategy

### Phase 1: Add New Tables

```bash
# Create Alembic migration
alembic revision --autogenerate -m "Add Phase V tables"

# Review migration file
# Edit if needed to ensure proper order

# Apply migration
alembic upgrade head
```

### Phase 2: Extend Existing Tables

```bash
# Create migration for tasks table extensions
alembic revision -m "Extend tasks table for Phase V"

# Apply migration
alembic upgrade head
```

### Phase 3: Backfill Data

```python
# Backfill search_vector for existing tasks
from sqlmodel import Session, select
from models import Task

def backfill_search_vectors(session: Session):
    tasks = session.exec(select(Task)).all()
    for task in tasks:
        # Trigger will automatically update search_vector
        task.updated_at = datetime.utcnow()
        session.add(task)
    session.commit()
```

---

## Performance Considerations

### Indexing Strategy

- **Primary Keys**: All tables use appropriate primary keys (BIGSERIAL or VARCHAR)
- **Foreign Keys**: All foreign keys indexed for join performance
- **Composite Indexes**: Used for common query patterns (user_id + timestamp)
- **Partial Indexes**: Used for filtered queries (e.g., pending reminders)
- **GIN Indexes**: Used for array columns (tags, mentioned_users) and tsvector

### Query Optimization

- **Pagination**: Use cursor-based pagination for large result sets
- **Covering Indexes**: Include frequently accessed columns in indexes
- **Partitioning**: Consider partitioning audit_logs by month if >1M rows
- **Connection Pooling**: Configure SQLAlchemy pool (size=20, max_overflow=10)

### Data Retention

- **Audit Logs**: Archive after 90 days to cold storage
- **Direct Messages**: Consider retention policy (e.g., 1 year)
- **Scheduled Reminders**: Clean up triggered/expired reminders after 30 days

---

## Summary

### New Tables Count: 8

1. audit_logs
2. scheduled_reminders
3. friend_connections
4. collaboration_groups
5. group_memberships
6. task_assignments
7. task_comments
8. direct_messages

### Extended Tables: 1

1. tasks (added search_vector, recurring_pattern, parent_task_id, recurrence_count, group_id)

### Total Indexes: 35+

- Primary key indexes: 9
- Foreign key indexes: 20+
- Composite indexes: 10+
- GIN indexes: 3 (search_vector, mentioned_users, tags)
- Partial indexes: 2 (pending reminders, unread messages)

### Estimated Storage (10,000 users, 100,000 tasks)

- audit_logs: ~500MB (with 90-day retention)
- scheduled_reminders: ~10MB
- friend_connections: ~5MB
- collaboration_groups: ~2MB
- group_memberships: ~5MB
- task_assignments: ~20MB
- task_comments: ~50MB
- direct_messages: ~100MB
- tasks (extended): +50MB for search_vector

**Total Additional Storage**: ~750MB

---

## Next Steps

1. Create Alembic migrations for all new tables
2. Create SQLModel model files in `backend/src/models/`
3. Write database seeding scripts for development
4. Create API contracts in `contracts/api.yaml`
5. Create event schemas in `contracts/events.yaml`
6. Document Dapr component configurations in `contracts/dapr/`
