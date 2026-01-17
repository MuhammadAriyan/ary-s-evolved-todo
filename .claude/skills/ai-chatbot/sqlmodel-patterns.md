# SQLModel Patterns Skill

## Purpose
Implement database models and queries using SQLModel for the AI Todo Chatbot with Neon PostgreSQL.

## Context7 Reference
- Library: `/tiangolo/sqlmodel`
- Query: "async session patterns relationships"

## Model Patterns

### 1. Base Model Configuration
```python
# backend/app/models/base.py
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class BaseModel(SQLModel):
    """Base model with common fields"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Conversation Model
```python
# backend/app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### 3. Message Model
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
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        index=True,
    )
    role: str = Field(max_length=20)  # user, assistant, system
    content: str = Field(max_length=10000)
    agent_name: Optional[str] = Field(default=None, max_length=50)
    agent_icon: Optional[str] = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

### 4. Enhanced Task Model
```python
# backend/app/models/task.py
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from typing import Optional
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="medium", max_length=20)
    tags: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String)),
    )
    due_date: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5. Async Session Pattern
```python
# backend/app/core/database.py
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from app.core.config import settings

# Create async engine for Neon PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_session():
    """Async context manager for database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# FastAPI dependency
async def get_db():
    async with async_session_maker() as session:
        yield session
```

### 6. Query Patterns
```python
# backend/app/repositories/conversation_repository.py
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.conversation import Conversation
from app.models.message import Message

async def get_user_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[Conversation]:
    """Get conversations for a user, ordered by most recent"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()

async def count_user_conversations(
    session: AsyncSession,
    user_id: str,
) -> int:
    """Count total conversations for a user"""
    statement = (
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user_id)
    )
    result = await session.exec(statement)
    return result.one()

async def get_conversation_with_messages(
    session: AsyncSession,
    conversation_id: str,
    user_id: str,
) -> Conversation | None:
    """Get conversation with all messages (user isolation enforced)"""
    statement = (
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,  # CRITICAL: User isolation
        )
    )
    result = await session.exec(statement)
    conversation = result.first()

    if conversation:
        # Load messages
        msg_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        msg_result = await session.exec(msg_statement)
        conversation.messages = msg_result.all()

    return conversation
```

## Key Principles
- **User Isolation**: ALWAYS filter by user_id
- **Async Sessions**: Use async context managers
- **Type Safety**: Full type hints with SQLModel
- **Relationships**: Use Relationship for joins
- **Indexes**: Add indexes for query performance
