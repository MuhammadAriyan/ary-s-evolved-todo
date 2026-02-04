"""TaskComment model for comments on tasks with @mention support."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text
from datetime import datetime
from typing import Optional, List


class TaskComment(SQLModel, table=True):
    """Task comment model with @mention support."""

    __tablename__ = "task_comments"

    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    group_id: Optional[str] = Field(foreign_key="collaboration_groups.id", nullable=True)
    content: str = Field(sa_column=Column(Text), nullable=False)
    mentioned_users: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
