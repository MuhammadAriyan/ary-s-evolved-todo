"""CollaborationGroup model for shared task management."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from datetime import datetime
from typing import Optional


class CollaborationGroup(SQLModel, table=True):
    """Collaboration group model for shared task management."""

    __tablename__ = "collaboration_groups"

    id: str = Field(primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    owner_user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
