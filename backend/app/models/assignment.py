"""TaskAssignment model for task assignments to specific users."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TaskAssignment(SQLModel, table=True):
    """Task assignment model for delegating tasks to users."""

    __tablename__ = "task_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    assigned_to_user_id: str = Field(foreign_key="users.id", nullable=False)
    assigned_by_user_id: str = Field(foreign_key="users.id", nullable=False)
    group_id: Optional[str] = Field(foreign_key="collaboration_groups.id", nullable=True)
    status: str = Field(max_length=20, default="pending")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
