"""GroupMembership model for user memberships in collaboration groups."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional


class GroupMembership(SQLModel, table=True):
    """Group membership model with role-based permissions."""

    __tablename__ = "group_memberships"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: str = Field(foreign_key="collaboration_groups.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    role: str = Field(max_length=20, default="member")
    permissions: dict = Field(
        default_factory=lambda: {
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
