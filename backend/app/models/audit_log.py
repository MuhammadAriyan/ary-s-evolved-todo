"""AuditLog model for complete audit trail of task operations."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID
from sqlalchemy import Text
from datetime import datetime
from typing import Optional
import uuid


class AuditLog(SQLModel, table=True):
    """Audit log model for tracking all task operations."""

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
    request_id: Optional[str] = Field(default=None, max_length=100)
    timestamp: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
