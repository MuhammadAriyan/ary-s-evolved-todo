"""FriendConnection model for friend relationships between users."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class FriendConnection(SQLModel, table=True):
    """Friend connection model for user relationships."""

    __tablename__ = "friend_connections"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id_1: str = Field(foreign_key="users.id", nullable=False)
    user_id_2: str = Field(foreign_key="users.id", nullable=False)
    status: str = Field(max_length=20, default="pending")
    requested_by: str = Field(foreign_key="users.id", nullable=False)
    connected_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
