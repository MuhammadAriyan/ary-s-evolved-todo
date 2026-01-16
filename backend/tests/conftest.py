"""Shared pytest fixtures for backend tests."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from typing import Generator, AsyncGenerator
import uuid

from sqlmodel import Session


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    session.exec = MagicMock(return_value=MagicMock(
        all=MagicMock(return_value=[]),
        first=MagicMock(return_value=None),
        one=MagicMock(return_value=0),
    ))
    session.get = MagicMock(return_value=None)
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_user_id() -> str:
    """Test user ID for isolation tests."""
    return "test-user-123"


@pytest.fixture
def other_user_id() -> str:
    """Another user ID for cross-user access tests."""
    return "other-user-456"


# ============================================================================
# Conversation Fixtures
# ============================================================================

@pytest.fixture
def test_conversation_id() -> str:
    """Test conversation ID."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_conversation(test_user_id: str, test_conversation_id: str) -> MagicMock:
    """Create a mock conversation."""
    conversation = MagicMock()
    conversation.id = test_conversation_id
    conversation.user_id = test_user_id
    conversation.title = None
    conversation.created_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()
    conversation.messages = []
    return conversation


@pytest.fixture
def mock_message(test_conversation_id: str) -> MagicMock:
    """Create a mock message."""
    message = MagicMock()
    message.id = str(uuid.uuid4())
    message.conversation_id = test_conversation_id
    message.role = "user"
    message.content = "Test message"
    message.agent_name = None
    message.agent_icon = None
    message.created_at = datetime.utcnow()
    return message


@pytest.fixture
def mock_assistant_message(test_conversation_id: str) -> MagicMock:
    """Create a mock assistant message."""
    message = MagicMock()
    message.id = str(uuid.uuid4())
    message.conversation_id = test_conversation_id
    message.role = "assistant"
    message.content = "I can help you with that!"
    message.agent_name = "Miyu"
    message.agent_icon = "\U0001F1EC\U0001F1E7"  # GB flag
    message.created_at = datetime.utcnow()
    return message


# ============================================================================
# AI/Agent Fixtures
# ============================================================================

@pytest.fixture
def mock_ai_response() -> dict:
    """Mock AI response from orchestrator."""
    return {
        "success": True,
        "content": "I've added that task for you!",
        "agent_name": "Miyu",
        "agent_icon": "\U0001F1EC\U0001F1E7",
        "tool_calls": ["add_task"],
    }


@pytest.fixture
def mock_ai_error_response() -> dict:
    """Mock AI error response."""
    return {
        "success": False,
        "error": "Connection error",
        "content": "I'm having trouble connecting to the AI service.",
        "agent_name": "Aren",
        "agent_icon": "\U0001F916",
        "tool_calls": [],
    }


@pytest.fixture
def mock_mcp_server() -> MagicMock:
    """Create a mock MCP server."""
    server = MagicMock()
    server.__aenter__ = AsyncMock(return_value=server)
    server.__aexit__ = AsyncMock(return_value=None)
    return server


@pytest.fixture
def mock_agent() -> MagicMock:
    """Create a mock Agent."""
    agent = MagicMock()
    agent.name = "Miyu"
    return agent


@pytest.fixture
def mock_runner_result(mock_agent: MagicMock) -> MagicMock:
    """Create a mock Runner result."""
    result = MagicMock()
    result.final_output = "Task added successfully!"
    result.last_agent = mock_agent
    result.new_items = []
    return result


# ============================================================================
# Streaming Fixtures
# ============================================================================

@pytest.fixture
def mock_stream_events() -> list[dict]:
    """Mock SSE stream events."""
    return [
        {"type": "agent_change", "agent": "Aren", "icon": "\U0001F916"},
        {"type": "token", "content": "I'll "},
        {"type": "token", "content": "help "},
        {"type": "token", "content": "you!"},
        {"type": "agent_change", "agent": "Miyu", "icon": "\U0001F1EC\U0001F1E7"},
        {"type": "tool_call", "tool": "add_task", "args": {"title": "Test"}},
        {"type": "done", "message_id": "msg-123", "content": "I'll help you!"},
    ]


@pytest.fixture
def mock_stream_error_event() -> dict:
    """Mock SSE error event."""
    return {"type": "error", "message": "Connection error occurred"}


# ============================================================================
# Rate Limiter Fixtures
# ============================================================================

@pytest.fixture
def fresh_rate_limiter():
    """Create a fresh rate limiter for testing."""
    from app.middleware.rate_limit import RateLimiter
    return RateLimiter(max_requests=5, window_seconds=60)


# ============================================================================
# HTTP Client Fixtures (for integration tests)
# ============================================================================

@pytest.fixture
def auth_headers(test_user_id: str) -> dict:
    """Create mock auth headers."""
    return {"Authorization": f"Bearer mock-token-{test_user_id}"}


# ============================================================================
# Async Test Configuration
# ============================================================================

@pytest.fixture
def event_loop_policy():
    """Configure event loop for async tests."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
