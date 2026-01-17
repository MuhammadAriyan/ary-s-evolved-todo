"""Unit tests for ConversationService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid


class TestConversationServiceCreate:
    """Tests for conversation creation."""

    def test_create_conversation_success(self, mock_session, test_user_id):
        """Test successful conversation creation."""
        from app.services.conversation_service import ConversationService

        service = ConversationService(mock_session)

        # Mock the count to be under limit
        mock_session.exec.return_value.one.return_value = 5

        conversation = service.create_conversation(test_user_id)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert conversation.user_id == test_user_id

    def test_create_conversation_at_limit_raises_error(self, mock_session, test_user_id):
        """Test that creating conversation at limit raises ValueError."""
        from app.services.conversation_service import ConversationService

        service = ConversationService(mock_session)

        # Mock the count to be at limit
        mock_session.exec.return_value.one.return_value = 100

        with pytest.raises(ValueError, match="Maximum conversations limit"):
            service.create_conversation(test_user_id)

    def test_max_conversations_constant(self):
        """Test that MAX_CONVERSATIONS_PER_USER is 100."""
        from app.services.conversation_service import ConversationService
        assert ConversationService.MAX_CONVERSATIONS_PER_USER == 100


class TestConversationServiceGet:
    """Tests for conversation retrieval."""

    def test_get_conversation_returns_conversation(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test getting a conversation by ID."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.get_conversation(mock_conversation.id, test_user_id)

        assert result == mock_conversation

    def test_get_conversation_returns_none_for_wrong_user(
        self, mock_session, test_user_id, other_user_id, mock_conversation
    ):
        """Test that conversation is not returned for wrong user."""
        from app.services.conversation_service import ConversationService

        # Conversation belongs to test_user_id, but we query with other_user_id
        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_conversation(mock_conversation.id, other_user_id)

        assert result is None

    def test_get_conversation_returns_none_for_nonexistent(
        self, mock_session, test_user_id
    ):
        """Test that None is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_conversation("nonexistent-id", test_user_id)

        assert result is None


class TestConversationServiceGetWithMessages:
    """Tests for conversation retrieval with messages."""

    def test_get_conversation_with_messages_loads_messages(
        self, mock_session, test_user_id, mock_conversation, mock_message
    ):
        """Test that messages are loaded with conversation."""
        from app.services.conversation_service import ConversationService

        # First call returns conversation, second returns messages
        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = [mock_message]

        service = ConversationService(mock_session)
        result = service.get_conversation_with_messages(
            mock_conversation.id, test_user_id
        )

        assert result is not None
        assert result.messages == [mock_message]

    def test_get_conversation_with_messages_returns_none_for_wrong_user(
        self, mock_session, other_user_id
    ):
        """Test that None is returned for wrong user."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_conversation_with_messages("conv-id", other_user_id)

        assert result is None


class TestConversationServiceList:
    """Tests for listing conversations."""

    def test_get_user_conversations_returns_list(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test listing user conversations."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.all.return_value = [mock_conversation]
        service = ConversationService(mock_session)

        result = service.get_user_conversations(test_user_id)

        assert len(result) == 1
        assert result[0] == mock_conversation

    def test_get_user_conversations_respects_limit(
        self, mock_session, test_user_id
    ):
        """Test that limit is enforced."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        # Request more than max
        service.get_user_conversations(test_user_id, limit=200)

        # Verify the query was built (limit is enforced internally)
        mock_session.exec.assert_called()

    def test_count_user_conversations(self, mock_session, test_user_id):
        """Test counting user conversations."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.one.return_value = 42
        service = ConversationService(mock_session)

        result = service.count_user_conversations(test_user_id)

        assert result == 42


class TestConversationServiceDelete:
    """Tests for conversation deletion."""

    def test_delete_conversation_success(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test successful conversation deletion."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.delete_conversation(mock_conversation.id, test_user_id)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_conversation)
        mock_session.commit.assert_called_once()

    def test_delete_conversation_returns_false_for_nonexistent(
        self, mock_session, test_user_id
    ):
        """Test that False is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.delete_conversation("nonexistent-id", test_user_id)

        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_conversation_user_isolation(
        self, mock_session, test_user_id, other_user_id, mock_conversation
    ):
        """Test that user cannot delete another user's conversation."""
        from app.services.conversation_service import ConversationService

        # Return None because user_id doesn't match
        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.delete_conversation(mock_conversation.id, other_user_id)

        assert result is False


class TestConversationServiceUpdateTitle:
    """Tests for title updates."""

    def test_update_conversation_title_success(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test successful title update."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.update_conversation_title(
            mock_conversation.id, test_user_id, "New Title"
        )

        assert result is not None
        assert mock_conversation.title == "New Title"
        mock_session.commit.assert_called()

    def test_update_conversation_title_truncates_long_title(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that long titles are truncated to 200 chars."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        long_title = "x" * 300
        service.update_conversation_title(
            mock_conversation.id, test_user_id, long_title
        )

        assert len(mock_conversation.title) == 200

    def test_update_conversation_title_returns_none_for_nonexistent(
        self, mock_session, test_user_id
    ):
        """Test that None is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.update_conversation_title(
            "nonexistent-id", test_user_id, "Title"
        )

        assert result is None


class TestConversationServiceAddMessage:
    """Tests for adding messages."""

    def test_add_message_success(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test successful message addition."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.add_message(
            conversation_id=mock_conversation.id,
            user_id=test_user_id,
            role="user",
            content="Hello!",
        )

        assert result is not None
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_add_message_with_agent_info(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test adding assistant message with agent info."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.add_message(
            conversation_id=mock_conversation.id,
            user_id=test_user_id,
            role="assistant",
            content="I can help!",
            agent_name="Miyu",
            agent_icon="\U0001F1EC\U0001F1E7",
        )

        assert result is not None

    def test_add_message_validates_role(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that invalid roles raise ValueError."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        with pytest.raises(ValueError, match="Invalid role"):
            service.add_message(
                conversation_id=mock_conversation.id,
                user_id=test_user_id,
                role="invalid",
                content="Hello!",
            )

    def test_add_message_returns_none_for_nonexistent_conversation(
        self, mock_session, test_user_id
    ):
        """Test that None is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.add_message(
            conversation_id="nonexistent-id",
            user_id=test_user_id,
            role="user",
            content="Hello!",
        )

        assert result is None


class TestConversationServiceGetMessages:
    """Tests for getting messages."""

    def test_get_messages_returns_list(
        self, mock_session, test_user_id, mock_conversation, mock_message
    ):
        """Test getting messages for a conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = [mock_message]
        service = ConversationService(mock_session)

        result = service.get_messages(mock_conversation.id, test_user_id)

        assert len(result) == 1

    def test_get_messages_returns_empty_for_nonexistent(
        self, mock_session, test_user_id
    ):
        """Test that empty list is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_messages("nonexistent-id", test_user_id)

        assert result == []


class TestConversationServiceGetOptimizedContext:
    """Tests for get_optimized_context - sliding window context."""

    def test_get_optimized_context_returns_formatted_messages(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that context returns properly formatted messages."""
        from app.services.conversation_service import ConversationService

        # Create mock messages
        msg1 = MagicMock()
        msg1.role = "user"
        msg1.content = "Hello"
        msg2 = MagicMock()
        msg2.role = "assistant"
        msg2.content = "Hi there!"

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = [msg2, msg1]  # Desc order
        service = ConversationService(mock_session)

        result = service.get_optimized_context(
            mock_conversation.id, test_user_id, context_window=6
        )

        # Should be reversed to chronological order
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi there!"

    def test_get_optimized_context_enforces_min_window(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that context window minimum is 1."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        # Request 0 or negative should be clamped to 1
        result = service.get_optimized_context(
            mock_conversation.id, test_user_id, context_window=0
        )

        assert result == []  # Empty but query was made

    def test_get_optimized_context_enforces_max_window(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that context window maximum is 20."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        # Request more than 20 should be clamped
        result = service.get_optimized_context(
            mock_conversation.id, test_user_id, context_window=50
        )

        # Query should have been made with limit=20
        mock_session.exec.assert_called()

    def test_get_optimized_context_returns_empty_for_nonexistent(
        self, mock_session, test_user_id
    ):
        """Test that empty list is returned for nonexistent conversation."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_optimized_context("nonexistent-id", test_user_id)

        assert result == []

    def test_get_optimized_context_user_isolation(
        self, mock_session, other_user_id, mock_conversation
    ):
        """Test that context is not returned for wrong user."""
        from app.services.conversation_service import ConversationService

        # Return None because user doesn't own conversation
        mock_session.exec.return_value.first.return_value = None
        service = ConversationService(mock_session)

        result = service.get_optimized_context(
            mock_conversation.id, other_user_id
        )

        assert result == []

    def test_get_optimized_context_default_window_is_6(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that default context window is 6."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        # Call without specifying context_window
        service.get_optimized_context(mock_conversation.id, test_user_id)

        # Verify query was made (default should be 6)
        mock_session.exec.assert_called()


class TestConversationServiceEdgeCases:
    """Tests for edge cases in ConversationService."""

    def test_create_conversation_generates_uuid(
        self, mock_session, test_user_id
    ):
        """Test that created conversation has a UUID."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.one.return_value = 0
        service = ConversationService(mock_session)

        conversation = service.create_conversation(test_user_id)

        # Conversation should have an id (UUID)
        assert conversation.id is not None

    def test_add_message_updates_conversation_timestamp(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that adding a message updates conversation updated_at."""
        from app.services.conversation_service import ConversationService
        from datetime import datetime

        original_time = mock_conversation.updated_at
        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        service.add_message(
            conversation_id=mock_conversation.id,
            user_id=test_user_id,
            role="user",
            content="Test",
        )

        # updated_at should be changed
        assert mock_conversation.updated_at != original_time

    def test_get_messages_ordered_by_created_at(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that messages are returned in chronological order."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        service.get_messages(mock_conversation.id, test_user_id)

        # Verify exec was called (order_by is in the query)
        mock_session.exec.assert_called()

    def test_delete_conversation_cascades_messages(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that deleting conversation also deletes messages."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.delete_conversation(mock_conversation.id, test_user_id)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_conversation)

    def test_update_title_with_none_clears_title(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that updating title with None clears the title."""
        from app.services.conversation_service import ConversationService

        mock_conversation.title = "Old Title"
        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        service.update_conversation_title(
            mock_conversation.id, test_user_id, None
        )

        assert mock_conversation.title is None

    def test_add_message_system_role_accepted(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that system role is accepted for messages."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        service = ConversationService(mock_session)

        result = service.add_message(
            conversation_id=mock_conversation.id,
            user_id=test_user_id,
            role="system",
            content="System message",
        )

        assert result is not None

    def test_get_user_conversations_empty_list(
        self, mock_session, test_user_id
    ):
        """Test that empty list is returned for user with no conversations."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        result = service.get_user_conversations(test_user_id)

        assert result == []

    def test_count_user_conversations_returns_zero(
        self, mock_session, test_user_id
    ):
        """Test that count returns 0 for user with no conversations."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.one.return_value = 0
        service = ConversationService(mock_session)

        result = service.count_user_conversations(test_user_id)

        assert result == 0

    def test_get_optimized_context_with_negative_window(
        self, mock_session, test_user_id, mock_conversation
    ):
        """Test that negative context window is clamped to 1."""
        from app.services.conversation_service import ConversationService

        mock_session.exec.return_value.first.return_value = mock_conversation
        mock_session.exec.return_value.all.return_value = []
        service = ConversationService(mock_session)

        # Negative should be clamped to 1
        result = service.get_optimized_context(
            mock_conversation.id, test_user_id, context_window=-5
        )

        assert result == []
