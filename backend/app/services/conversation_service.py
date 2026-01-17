"""Conversation service for chat persistence operations."""
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select, func

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationService:
    """Service for managing conversations and messages."""

    MAX_CONVERSATIONS_PER_USER = 100

    def __init__(self, session: Session):
        """Initialize service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for a user.

        Args:
            user_id: The authenticated user's ID

        Returns:
            Conversation: The created conversation

        Raises:
            ValueError: If user has reached max conversations limit
        """
        # Check conversation limit
        count = self.count_user_conversations(user_id)
        if count >= self.MAX_CONVERSATIONS_PER_USER:
            raise ValueError(
                f"Maximum conversations limit ({self.MAX_CONVERSATIONS_PER_USER}) reached"
            )

        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(
        self, conversation_id: str, user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation by ID with user isolation.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)

        Returns:
            Conversation or None if not found/not owned by user
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def get_conversation_with_messages(
        self, conversation_id: str, user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation with all its messages.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)

        Returns:
            Conversation with messages loaded, or None
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if conversation:
            # Load messages ordered by creation time
            msg_statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            conversation.messages = list(self.session.exec(msg_statement).all())
        return conversation

    def get_user_conversations(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        """Get all conversations for a user with pagination.

        Args:
            user_id: The authenticated user's ID
            limit: Maximum number of conversations (default 50, max 100)
            offset: Number of conversations to skip

        Returns:
            List of conversations ordered by updated_at descending
        """
        # Enforce max limit
        limit = min(limit, self.MAX_CONVERSATIONS_PER_USER)

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_user_conversations(self, user_id: str) -> int:
        """Count total conversations for a user.

        Args:
            user_id: The authenticated user's ID

        Returns:
            int: Number of conversations
        """
        statement = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        result = self.session.exec(statement).one()
        return result or 0

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)

        Returns:
            bool: True if deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        self.session.delete(conversation)
        self.session.commit()
        return True

    def update_conversation_title(
        self, conversation_id: str, user_id: str, title: str
    ) -> Optional[Conversation]:
        """Update conversation title.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)
            title: New title (max 200 chars)

        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title[:200] if title else None
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        agent_icon: Optional[str] = None,
    ) -> Optional[Message]:
        """Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)
            role: Message role (user, assistant, system)
            content: Message content
            agent_name: Name of responding agent (assistant only)
            agent_icon: Icon of responding agent (assistant only)

        Returns:
            Created message or None if conversation not found
        """
        # Verify conversation ownership
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        # Validate role
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {role}")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name if role == "assistant" else None,
            agent_icon=agent_icon if role == "assistant" else None,
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(
        self, conversation_id: str, user_id: str
    ) -> list[Message]:
        """Get all messages for a conversation.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)

        Returns:
            List of messages ordered by creation time
        """
        # Verify conversation ownership first
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(self.session.exec(statement).all())

    def get_optimized_context(
        self, conversation_id: str, user_id: str, context_window: int = 6
    ) -> list[dict]:
        """Get optimized conversation context for AI processing.

        Returns the last N messages formatted for the AI agent,
        using a sliding window approach for efficient context management.

        Args:
            conversation_id: The conversation ID
            user_id: The authenticated user's ID (for isolation)
            context_window: Number of recent messages to include (default 6, max 20)

        Returns:
            List of message dicts with 'role' and 'content' keys,
            ordered chronologically (oldest first within window)
        """
        # Enforce context window limits
        context_window = max(1, min(context_window, 20))

        # Verify conversation ownership first
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        # Get the last N messages ordered by creation time descending
        # then reverse to get chronological order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(context_window)
        )
        messages = list(self.session.exec(statement).all())

        # Reverse to chronological order and format for AI
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
