"""User model for authentication."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    name: Optional[str] = Field(default=None)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
