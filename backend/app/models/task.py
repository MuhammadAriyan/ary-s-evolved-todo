"""Task model for todo items."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
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
