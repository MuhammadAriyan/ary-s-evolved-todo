"""DirectMessage model for direct messages between friends."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from datetime import datetime
from typing import Optional


class DirectMessage(SQLModel, table=True):
    """Direct message model for friend messaging."""

    __tablename__ = "direct_messages"

    id: str = Field(primary_key=True)
    from_user_id: str = Field(foreign_key="users.id", nullable=False)
    to_user_id: str = Field(foreign_key="users.id", nullable=False)
    content: str = Field(sa_column=Column(Text), nullable=False)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
