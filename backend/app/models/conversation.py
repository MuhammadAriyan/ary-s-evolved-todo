"""Conversation model for AI chat sessions."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    """Conversation model for AI chat sessions with user isolation."""

    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        nullable=False,
        index=True,
        description="Owner of the conversation"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="AI-generated summary title"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last activity timestamp"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
