"""Integration tests for chat API endpoints."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json


class TestUnifiedChatEndpoint:
    """Tests for POST /api/v1/chat endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    @patch('app.api.v1.endpoints.chat.process_message')
    async def test_unified_chat_creates_conversation_when_not_provided(
        self, mock_process, mock_service_class, mock_rate_limit
    ):
        """Test that conversation is auto-created when not provided."""
        from app.api.v1.endpoints.chat import unified_chat
        from app.schemas.chat import UnifiedChatRequest

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "new-conv-123"
        mock_service.create_conversation.return_value = mock_conversation
        mock_service.get_messages.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_message.content = "Response"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        mock_process.return_value = {
            "success": True,
            "content": "Response",
            "agent_name": "Miyu",
            "agent_icon": "\U0001F1EC\U0001F1E7",
            "tool_calls": [],
        }

        request = UnifiedChatRequest(message="Hello")
        mock_session = MagicMock()

        result = await unified_chat(request, mock_session, "user-123")

        assert result.conversation_id == "new-conv-123"
        mock_service.create_conversation.assert_called_once_with("user-123")

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    @patch('app.api.v1.endpoints.chat.process_message')
    async def test_unified_chat_uses_existing_conversation(
        self, mock_process, mock_service_class, mock_rate_limit
    ):
        """Test that existing conversation is used when provided."""
        from app.api.v1.endpoints.chat import unified_chat
        from app.schemas.chat import UnifiedChatRequest

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "existing-conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_messages.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_message.content = "Response"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        mock_process.return_value = {
            "success": True,
            "content": "Response",
            "agent_name": "Aren",
            "agent_icon": "\U0001F916",
            "tool_calls": [],
        }

        request = UnifiedChatRequest(
            conversation_id="existing-conv-123",
            message="Hello"
        )
        mock_session = MagicMock()

        result = await unified_chat(request, mock_session, "user-123")

        assert result.conversation_id == "existing-conv-123"
        mock_service.create_conversation.assert_not_called()

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_unified_chat_returns_404_for_nonexistent_conversation(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that 404 is returned for nonexistent conversation."""
        from app.api.v1.endpoints.chat import unified_chat
        from app.schemas.chat import UnifiedChatRequest
        from fastapi import HTTPException

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_service.get_conversation.return_value = None
        mock_service_class.return_value = mock_service

        request = UnifiedChatRequest(
            conversation_id="nonexistent",
            message="Hello"
        )
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await unified_chat(request, mock_session, "user-123")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    async def test_unified_chat_rate_limited(self, mock_rate_limit):
        """Test that rate limiting is enforced."""
        from app.api.v1.endpoints.chat import unified_chat
        from app.schemas.chat import UnifiedChatRequest
        from fastapi import HTTPException

        mock_rate_limit.side_effect = HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

        request = UnifiedChatRequest(message="Hello")
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await unified_chat(request, mock_session, "user-123")

        assert exc_info.value.status_code == 429


class TestCreateConversationEndpoint:
    """Tests for POST /api/v1/chat/conversations endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_create_conversation_success(self, mock_service_class):
        """Test successful conversation creation."""
        from app.api.v1.endpoints.chat import create_conversation

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "new-conv-123"
        mock_conversation.title = None
        mock_service.create_conversation.return_value = mock_conversation
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await create_conversation(mock_session, "user-123")

        assert result == mock_conversation

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_create_conversation_at_limit_returns_400(
        self, mock_service_class
    ):
        """Test that 400 is returned when at conversation limit."""
        from app.api.v1.endpoints.chat import create_conversation
        from fastapi import HTTPException

        mock_service = MagicMock()
        mock_service.create_conversation.side_effect = ValueError(
            "Maximum conversations limit (100) reached"
        )
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_conversation(mock_session, "user-123")

        assert exc_info.value.status_code == 400
        assert "Maximum conversations" in str(exc_info.value.detail)


class TestListConversationsEndpoint:
    """Tests for GET /api/v1/chat/conversations endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_list_conversations_success(self, mock_service_class):
        """Test successful conversation listing."""
        from app.api.v1.endpoints.chat import list_conversations
        from datetime import datetime

        mock_service = MagicMock()
        mock_conv = MagicMock()
        mock_conv.id = "conv-123"
        mock_conv.title = None  # Must be string or None, not MagicMock
        mock_conv.created_at = datetime.now()
        mock_conv.updated_at = datetime.now()
        mock_service.get_user_conversations.return_value = [mock_conv]
        mock_service.count_user_conversations.return_value = 1
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await list_conversations(mock_session, "user-123", limit=50, offset=0)

        assert result.total == 1
        assert len(result.conversations) == 1

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_list_conversations_with_pagination(self, mock_service_class):
        """Test conversation listing with pagination."""
        from app.api.v1.endpoints.chat import list_conversations

        mock_service = MagicMock()
        mock_service.get_user_conversations.return_value = []
        mock_service.count_user_conversations.return_value = 100
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await list_conversations(
            mock_session, "user-123", limit=10, offset=20
        )

        assert result.limit == 10
        assert result.offset == 20
        mock_service.get_user_conversations.assert_called_with(
            user_id="user-123", limit=10, offset=20
        )


class TestGetConversationEndpoint:
    """Tests for GET /api/v1/chat/conversations/{id} endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_get_conversation_success(self, mock_service_class):
        """Test successful conversation retrieval."""
        from app.api.v1.endpoints.chat import get_conversation

        mock_service = MagicMock()
        mock_conv = MagicMock()
        mock_conv.id = "conv-123"
        mock_conv.messages = []
        mock_service.get_conversation_with_messages.return_value = mock_conv
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await get_conversation("conv-123", mock_session, "user-123")

        assert result == mock_conv

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_get_conversation_returns_404_for_nonexistent(
        self, mock_service_class
    ):
        """Test that 404 is returned for nonexistent conversation."""
        from app.api.v1.endpoints.chat import get_conversation
        from fastapi import HTTPException

        mock_service = MagicMock()
        mock_service.get_conversation_with_messages.return_value = None
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_conversation("nonexistent", mock_session, "user-123")

        assert exc_info.value.status_code == 404


class TestDeleteConversationEndpoint:
    """Tests for DELETE /api/v1/chat/conversations/{id} endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_delete_conversation_success(self, mock_service_class):
        """Test successful conversation deletion."""
        from app.api.v1.endpoints.chat import delete_conversation

        mock_service = MagicMock()
        mock_service.delete_conversation.return_value = True
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await delete_conversation("conv-123", mock_session, "user-123")

        assert result["success"] is True

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_delete_conversation_returns_404_for_nonexistent(
        self, mock_service_class
    ):
        """Test that 404 is returned for nonexistent conversation."""
        from app.api.v1.endpoints.chat import delete_conversation
        from fastapi import HTTPException

        mock_service = MagicMock()
        mock_service.delete_conversation.return_value = False
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await delete_conversation("nonexistent", mock_session, "user-123")

        assert exc_info.value.status_code == 404


class TestSendMessageEndpoint:
    """Tests for POST /api/v1/chat/conversations/{id}/messages endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    @patch('app.api.v1.endpoints.chat.process_message')
    async def test_send_message_success(
        self, mock_process, mock_service_class, mock_rate_limit
    ):
        """Test successful message sending."""
        from app.api.v1.endpoints.chat import send_message
        from app.schemas.chat import SendMessageRequest

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_messages.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_message.role = "assistant"
        mock_message.content = "Response"
        mock_message.agent_name = "Miyu"
        mock_message.agent_icon = "\U0001F1EC\U0001F1E7"
        mock_message.created_at = "2024-01-01T00:00:00"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        mock_process.return_value = {
            "success": True,
            "content": "Response",
            "agent_name": "Miyu",
            "agent_icon": "\U0001F1EC\U0001F1E7",
            "tool_calls": ["add_task"],
        }

        request = SendMessageRequest(content="Add a task", language="en-US")
        mock_session = MagicMock()

        result = await send_message("conv-123", request, mock_session, "user-123")

        assert result.agent_name == "Miyu"
        assert "add_task" in result.tool_calls

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_send_message_returns_404_for_nonexistent_conversation(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that 404 is returned for nonexistent conversation."""
        from app.api.v1.endpoints.chat import send_message
        from app.schemas.chat import SendMessageRequest
        from fastapi import HTTPException

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_service.get_conversation.return_value = None
        mock_service_class.return_value = mock_service

        request = SendMessageRequest(content="Hello", language="en-US")
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await send_message("nonexistent", request, mock_session, "user-123")

        assert exc_info.value.status_code == 404


class TestGenerateTitleEndpoint:
    """Tests for POST /api/v1/chat/conversations/{id}/title endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_generate_title_success(self, mock_service_class):
        """Test successful title generation."""
        from app.api.v1.endpoints.chat import generate_title

        mock_service = MagicMock()
        mock_conv = MagicMock()
        mock_conv.id = "conv-123"

        mock_msg = MagicMock()
        mock_msg.role = "user"
        mock_msg.content = "Add a task to buy groceries"
        mock_conv.messages = [mock_msg]

        mock_service.get_conversation_with_messages.return_value = mock_conv
        mock_service.update_conversation_title.return_value = mock_conv
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await generate_title("conv-123", mock_session, "user-123")

        assert result.title == "Add a task to buy groceries"

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_generate_title_truncates_long_content(self, mock_service_class):
        """Test that long content is truncated in title."""
        from app.api.v1.endpoints.chat import generate_title

        mock_service = MagicMock()
        mock_conv = MagicMock()
        mock_conv.id = "conv-123"

        mock_msg = MagicMock()
        mock_msg.role = "user"
        mock_msg.content = "x" * 100  # Long content
        mock_conv.messages = [mock_msg]

        mock_service.get_conversation_with_messages.return_value = mock_conv
        mock_service.update_conversation_title.return_value = mock_conv
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        result = await generate_title("conv-123", mock_session, "user-123")

        # Should be truncated to 50 chars + "..."
        assert len(result.title) == 53
        assert result.title.endswith("...")

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_generate_title_returns_400_for_empty_conversation(
        self, mock_service_class
    ):
        """Test that 400 is returned for conversation with no messages."""
        from app.api.v1.endpoints.chat import generate_title
        from fastapi import HTTPException

        mock_service = MagicMock()
        mock_conv = MagicMock()
        mock_conv.id = "conv-123"
        mock_conv.messages = []
        mock_service.get_conversation_with_messages.return_value = mock_conv
        mock_service_class.return_value = mock_service

        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await generate_title("conv-123", mock_session, "user-123")

        assert exc_info.value.status_code == 400


class TestStreamChatEndpoint:
    """Tests for POST /api/v1/chat/stream endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_creates_conversation_when_not_provided(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that conversation is auto-created for streaming."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from fastapi.responses import StreamingResponse

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "new-conv-123"
        mock_service.create_conversation.return_value = mock_conversation
        mock_service.get_optimized_context.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        request = ChatStreamRequest(
            message="Hello",
            conversation_id=None,
            language_hint=LanguageHint.AUTO,
            context_window=6,
        )
        mock_session = MagicMock()

        with patch('app.api.v1.endpoints.chat.process_message_streamed') as mock_stream:
            async def mock_generator():
                yield {"type": "agent_change", "agent": "Aren", "icon": "\U0001F916"}
                yield {"type": "done", "message_id": "msg-123", "content": "Done"}

            mock_stream.return_value = mock_generator()

            result = await stream_chat(request, mock_session, "user-123")

            assert isinstance(result, StreamingResponse)
            mock_service.create_conversation.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_returns_404_for_nonexistent_conversation(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that 404 is returned for nonexistent conversation."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from fastapi import HTTPException

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_service.get_conversation.return_value = None
        mock_service_class.return_value = mock_service

        request = ChatStreamRequest(
            message="Hello",
            conversation_id="nonexistent",
            language_hint=LanguageHint.AUTO,
            context_window=6,
        )
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await stream_chat(request, mock_session, "user-123")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    async def test_stream_chat_rate_limited(self, mock_rate_limit):
        """Test that rate limiting is enforced for streaming."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from fastapi import HTTPException

        mock_rate_limit.side_effect = HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

        request = ChatStreamRequest(
            message="Hello",
            language_hint=LanguageHint.AUTO,
            context_window=6,
        )
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await stream_chat(request, mock_session, "user-123")

        assert exc_info.value.status_code == 429


class TestStreamChatSSEFormat:
    """Tests for SSE event format in streaming endpoint."""

    def test_sse_event_format_token(self):
        """Test that token events are properly formatted."""
        event = {"type": "token", "content": "Hello"}
        sse_line = f"data: {json.dumps(event)}\n\n"

        assert sse_line.startswith("data: ")
        assert sse_line.endswith("\n\n")
        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "token"
        assert parsed["content"] == "Hello"

    def test_sse_event_format_agent_change(self):
        """Test that agent_change events are properly formatted."""
        event = {"type": "agent_change", "agent": "Miyu", "icon": "\U0001F1EC\U0001F1E7"}
        sse_line = f"data: {json.dumps(event)}\n\n"

        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "agent_change"
        assert parsed["agent"] == "Miyu"

    def test_sse_event_format_tool_call(self):
        """Test that tool_call events are properly formatted."""
        event = {"type": "tool_call", "tool": "add_task", "args": {"title": "Test"}}
        sse_line = f"data: {json.dumps(event)}\n\n"

        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "tool_call"
        assert parsed["tool"] == "add_task"

    def test_sse_event_format_done(self):
        """Test that done events are properly formatted."""
        event = {"type": "done", "message_id": "msg-123"}
        sse_line = f"data: {json.dumps(event)}\n\n"

        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "done"
        assert parsed["message_id"] == "msg-123"

    def test_sse_event_format_error(self):
        """Test that error events are properly formatted."""
        event = {"type": "error", "message": "Something went wrong"}
        sse_line = f"data: {json.dumps(event)}\n\n"

        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "error"
        assert parsed["message"] == "Something went wrong"

    def test_sse_event_format_conversation_created(self):
        """Test that conversation_created events are properly formatted."""
        event = {"type": "conversation_created", "conversation_id": "conv-123"}
        sse_line = f"data: {json.dumps(event)}\n\n"

        parsed = json.loads(sse_line[6:-2])
        assert parsed["type"] == "conversation_created"
        assert parsed["conversation_id"] == "conv-123"


class TestStreamChatContextWindow:
    """Tests for context window behavior in streaming endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_uses_context_window(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that context_window parameter is passed to get_optimized_context."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_optimized_context.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        request = ChatStreamRequest(
            message="Hello",
            conversation_id="conv-123",
            language_hint=LanguageHint.AUTO,
            context_window=10,  # Custom context window
        )
        mock_session = MagicMock()

        with patch('app.api.v1.endpoints.chat.process_message_streamed') as mock_stream:
            async def mock_generator():
                yield {"type": "done", "message_id": "msg-123", "content": "Done"}

            mock_stream.return_value = mock_generator()

            await stream_chat(request, mock_session, "user-123")

            # Verify get_optimized_context was called with context_window=10
            mock_service.get_optimized_context.assert_called_once()
            call_kwargs = mock_service.get_optimized_context.call_args
            assert call_kwargs[1]["context_window"] == 10

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_default_context_window(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that default context_window is 6."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_optimized_context.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        # Don't specify context_window - should use default
        request = ChatStreamRequest(
            message="Hello",
            conversation_id="conv-123",
            language_hint=LanguageHint.AUTO,
        )
        mock_session = MagicMock()

        with patch('app.api.v1.endpoints.chat.process_message_streamed') as mock_stream:
            async def mock_generator():
                yield {"type": "done", "message_id": "msg-123", "content": "Done"}

            mock_stream.return_value = mock_generator()

            await stream_chat(request, mock_session, "user-123")

            # Verify default context_window=6 was used
            call_kwargs = mock_service.get_optimized_context.call_args
            assert call_kwargs[1]["context_window"] == 6


class TestStreamChatLanguageHint:
    """Tests for language hint behavior in streaming endpoint."""

    def test_language_hint_enum_has_english(self):
        """Test that LanguageHint enum has English value."""
        from app.schemas.chat import LanguageHint
        assert LanguageHint.ENGLISH.value == "en"

    def test_language_hint_enum_has_urdu(self):
        """Test that LanguageHint enum has Urdu value."""
        from app.schemas.chat import LanguageHint
        assert LanguageHint.URDU.value == "ur"

    def test_language_hint_enum_has_auto(self):
        """Test that LanguageHint enum has Auto value."""
        from app.schemas.chat import LanguageHint
        assert LanguageHint.AUTO.value == "auto"

    def test_chat_stream_request_accepts_english_hint(self):
        """Test that ChatStreamRequest accepts English language hint."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        request = ChatStreamRequest(
            message="Hello",
            language_hint=LanguageHint.ENGLISH,
            context_window=6,
        )

        assert request.language_hint == LanguageHint.ENGLISH
        assert request.language_hint.value == "en"

    def test_chat_stream_request_accepts_urdu_hint(self):
        """Test that ChatStreamRequest accepts Urdu language hint."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        request = ChatStreamRequest(
            message="Hello",
            language_hint=LanguageHint.URDU,
            context_window=6,
        )

        assert request.language_hint == LanguageHint.URDU
        assert request.language_hint.value == "ur"

    def test_chat_stream_request_defaults_to_auto(self):
        """Test that ChatStreamRequest defaults to AUTO language hint."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        request = ChatStreamRequest(
            message="Hello",
            context_window=6,
        )

        assert request.language_hint == LanguageHint.AUTO

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    @patch('app.api.v1.endpoints.chat.process_message_streamed')
    async def test_stream_chat_returns_streaming_response(
        self, mock_stream, mock_service_class, mock_rate_limit
    ):
        """Test that stream_chat returns a StreamingResponse."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from fastapi.responses import StreamingResponse

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_optimized_context.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        async def mock_generator():
            yield {"type": "done", "message_id": "msg-123", "content": "Done"}

        mock_stream.return_value = mock_generator()

        request = ChatStreamRequest(
            message="Hello",
            conversation_id="conv-123",
            language_hint=LanguageHint.ENGLISH,
            context_window=6,
        )
        mock_session = MagicMock()

        result = await stream_chat(request, mock_session, "user-123")

        # Verify it returns a StreamingResponse with correct media type
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/event-stream"


class TestStreamChatMessageSaving:
    """Tests for message saving behavior in streaming endpoint."""

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_saves_user_message(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that user message is saved before streaming."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.get_optimized_context.return_value = []

        mock_message = MagicMock()
        mock_message.id = "msg-123"
        mock_service.add_message.return_value = mock_message

        mock_service_class.return_value = mock_service

        request = ChatStreamRequest(
            message="Test user message",
            conversation_id="conv-123",
            language_hint=LanguageHint.AUTO,
            context_window=6,
        )
        mock_session = MagicMock()

        with patch('app.api.v1.endpoints.chat.process_message_streamed') as mock_stream:
            async def mock_generator():
                yield {"type": "done", "message_id": "msg-123", "content": "Done"}

            mock_stream.return_value = mock_generator()

            await stream_chat(request, mock_session, "user-123")

            # Verify user message was saved
            add_message_calls = mock_service.add_message.call_args_list
            assert len(add_message_calls) >= 1
            first_call = add_message_calls[0]
            assert first_call[1]["role"] == "user"
            assert first_call[1]["content"] == "Test user message"

    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.chat.check_rate_limit')
    @patch('app.api.v1.endpoints.chat.ConversationService')
    async def test_stream_chat_fails_if_user_message_not_saved(
        self, mock_service_class, mock_rate_limit
    ):
        """Test that 500 is returned if user message fails to save."""
        from app.api.v1.endpoints.chat import stream_chat
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from fastapi import HTTPException

        mock_rate_limit.return_value = None

        mock_service = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.id = "conv-123"
        mock_service.get_conversation.return_value = mock_conversation
        mock_service.add_message.return_value = None  # Simulate failure

        mock_service_class.return_value = mock_service

        request = ChatStreamRequest(
            message="Test",
            conversation_id="conv-123",
            language_hint=LanguageHint.AUTO,
            context_window=6,
        )
        mock_session = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await stream_chat(request, mock_session, "user-123")

        assert exc_info.value.status_code == 500


class TestChatSchemaValidation:
    """Tests for chat schema validation."""

    def test_chat_stream_request_validates_message_length(self):
        """Test that ChatStreamRequest validates message length."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from pydantic import ValidationError

        # Empty message should fail
        with pytest.raises(ValidationError):
            ChatStreamRequest(
                message="",
                language_hint=LanguageHint.AUTO,
                context_window=6,
            )

    def test_chat_stream_request_validates_context_window_min(self):
        """Test that context_window minimum is 1."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChatStreamRequest(
                message="Hello",
                language_hint=LanguageHint.AUTO,
                context_window=0,
            )

    def test_chat_stream_request_validates_context_window_max(self):
        """Test that context_window maximum is 20."""
        from app.schemas.chat import ChatStreamRequest, LanguageHint
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChatStreamRequest(
                message="Hello",
                language_hint=LanguageHint.AUTO,
                context_window=21,
            )

    def test_language_hint_enum_values(self):
        """Test that LanguageHint has correct values."""
        from app.schemas.chat import LanguageHint

        assert LanguageHint.ENGLISH.value == "en"
        assert LanguageHint.URDU.value == "ur"
        assert LanguageHint.AUTO.value == "auto"

    def test_unified_chat_request_validates_message_length(self):
        """Test that UnifiedChatRequest validates message length."""
        from app.schemas.chat import UnifiedChatRequest
        from pydantic import ValidationError

        # Empty message should fail
        with pytest.raises(ValidationError):
            UnifiedChatRequest(message="")

        # Message over 1000 chars should fail
        with pytest.raises(ValidationError):
            UnifiedChatRequest(message="x" * 1001)
