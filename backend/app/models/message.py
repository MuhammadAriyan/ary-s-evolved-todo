"""Message model for conversation messages."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(SQLModel, table=True):
    """Message model for individual messages in a conversation."""

    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation"
    )
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, system"
    )
    content: str = Field(
        description="Message content (user: 1000 char limit enforced at API)"
    )
    agent_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Name of responding agent (assistant messages only)"
    )
    agent_icon: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Icon of responding agent (emoji)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When message was created"
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
