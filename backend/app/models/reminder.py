"""ScheduledReminder model for task reminders with cron expressions."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from datetime import datetime
from typing import Optional, List


class ScheduledReminder(SQLModel, table=True):
    """Scheduled reminder model for task notifications."""

    __tablename__ = "scheduled_reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    reminder_time: datetime = Field(nullable=False)
    cron_expression: Optional[str] = Field(max_length=100, nullable=True)
    timezone: str = Field(max_length=50, default="UTC")
    notification_channels: List[str] = Field(
        default_factory=lambda: ["in_app"],
        sa_column=Column(ARRAY(String))
    )
    status: str = Field(max_length=20, default="pending")
    last_triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
