"""Task model for todo items."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy import String, Text
from datetime import datetime, date
from typing import Optional, List


class Task(SQLModel, table=True):
    """Task model for todo items with user isolation."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False, index=True)  # Validated via JWT, no FK constraint
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(max_length=10, nullable=False)  # High, Medium, Low
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[date] = Field(default=None, index=True)
    recurring: Optional[str] = Field(default=None, max_length=20)  # daily, weekly, monthly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V: Event-Driven Microservices Extensions
    search_vector: Optional[str] = Field(default=None, sa_column=Column(TSVECTOR, nullable=True))
    recurring_pattern: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    recurrence_count: int = Field(default=0)
    group_id: Optional[str] = Field(default=None)  # FK removed temporarily until collaboration_groups table is created
