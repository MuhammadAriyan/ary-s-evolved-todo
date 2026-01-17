# Data Model: AI Todo Chatbot

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-01-11

## Overview

This document defines the database schema for conversation persistence in the AI Todo Chatbot. All models use SQLModel with async session support for Neon PostgreSQL.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │       │   Conversation   │       │   Message   │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │──1:N──│ id (PK)          │──1:N──│ id (PK)     │
│ email       │       │ user_id (FK)     │       │ conv_id(FK) │
│ ...         │       │ title            │       │ role        │
└─────────────┘       │ created_at       │       │ content     │
                      │ updated_at       │       │ agent_name  │
                      └──────────────────┘       │ agent_icon  │
                                                 │ created_at  │
                                                 └─────────────┘

┌─────────────┐
│    Task     │  (existing, enhanced)
├─────────────┤
│ id (PK)     │
│ user_id(FK) │
│ title       │
│ description │
│ completed   │
│ priority    │
│ tags[]      │
│ due_date    │
│ created_at  │
│ updated_at  │
└─────────────┘
```

## Models

### Conversation

Represents a chat session between user and AI.

```python
# backend/app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="Owner of the conversation"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="AI-generated summary title"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last activity timestamp"
    )

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Constraints**:
- Maximum 100 conversations per user
- Title generated after first exchange (AI summary)
- Cascade delete removes all messages

**Indexes**:
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_updated_at` on `updated_at DESC`

---

### Message

Represents a single message in a conversation.

```python
# backend/app/models/message.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.conversation import Conversation

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation"
    )
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, system"
    )
    content: str = Field(
        max_length=10000,
        description="Message content (user: 1000 char limit enforced at API)"
    )
    agent_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Name of responding agent (assistant messages only)"
    )
    agent_icon: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Icon of responding agent (emoji)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When message was created"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

**Constraints**:
- User messages: 1000 character limit (enforced at API layer)
- Assistant messages: 10000 character limit (AI responses can be longer)
- Role must be one of: `user`, `assistant`, `system`

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_created_at` on `created_at`

---

### Task (Enhanced)

Existing task model with additional fields for AI chatbot features.

```python
# backend/app/models/task.py (enhanced)
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from typing import Optional
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True
    )
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="medium", max_length=20)
    tags: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String))
    )
    due_date: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes** (existing + new):
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_user_completed` on `(user_id, completed)`
- `idx_tasks_tags` GIN index on `tags`
- `idx_tasks_due_date` on `due_date` WHERE `due_date IS NOT NULL`

---

## Migration

```sql
-- Alembic migration: add_chat_tables

-- Create conversations table
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_name VARCHAR(50),
    agent_icon VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Add constraint for role values
ALTER TABLE messages ADD CONSTRAINT chk_message_role
    CHECK (role IN ('user', 'assistant', 'system'));
```

---

## Query Patterns

### Get User Conversations (with limit)
```python
async def get_user_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
```

### Get Conversation with Messages (User Isolation)
```python
async def get_conversation_with_messages(
    session: AsyncSession,
    conversation_id: str,
    user_id: str,  # CRITICAL: Always verify ownership
) -> Conversation | None:
    statement = (
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,  # User isolation
        )
    )
    result = await session.exec(statement)
    conversation = result.first()

    if conversation:
        msg_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        msg_result = await session.exec(msg_statement)
        conversation.messages = msg_result.all()

    return conversation
```

### Count User Conversations (for limit check)
```python
async def count_user_conversations(
    session: AsyncSession,
    user_id: str,
) -> int:
    statement = (
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user_id)
    )
    result = await session.exec(statement)
    return result.one()
```

---

## Data Validation Rules

| Field | Rule |
|-------|------|
| `conversation.title` | Max 200 chars, nullable |
| `message.content` (user) | Max 1000 chars (API enforced) |
| `message.content` (assistant) | Max 10000 chars |
| `message.role` | Enum: user, assistant, system |
| `message.agent_icon` | Single emoji (max 10 chars for compound) |
| Conversations per user | Max 100 |

---

## Performance Considerations

1. **Pagination**: Always use `limit` and `offset` for conversation lists
2. **Eager Loading**: Load messages only when viewing specific conversation
3. **Index Usage**: Queries should use `user_id` index for isolation
4. **Cascade Delete**: Deleting conversation removes all messages automatically
5. **Connection Pooling**: Use SQLModel async session with pool_size=5, max_overflow=10
