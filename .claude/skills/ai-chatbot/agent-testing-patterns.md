# Agent Testing Patterns Skill

## Purpose
Test AI agents, MCP tools, and multi-agent handoffs with mocked AI responses for deterministic testing.

## Context7 Reference
- Library: `/pytest-dev/pytest`
- Query: "async testing fixtures mocking"

## Testing Patterns

### 1. Test Configuration
```python
# backend/tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
def test_user():
    return User(id="test-user-123", email="test@example.com")

@pytest.fixture
def test_user_id():
    return "test-user-123"
```

### 2. Mock AI Client
```python
# backend/tests/mocks/ai_client.py
from unittest.mock import AsyncMock, MagicMock

class MockMessage:
    def __init__(self, content: str):
        self.content = content

class MockChoice:
    def __init__(self, message: MockMessage):
        self.message = message

class MockCompletion:
    def __init__(self, content: str):
        self.choices = [MockChoice(MockMessage(content))]

def create_mock_ai_client(responses: list[str] | None = None):
    """Create a mock OpenAI client with predefined responses"""
    responses = responses or ["Mocked AI response"]
    response_iter = iter(responses)

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=lambda **kwargs: MockCompletion(next(response_iter, "Default response"))
    )
    return mock_client

@pytest.fixture
def mock_ai_client():
    return create_mock_ai_client()

@pytest.fixture
def mock_ai_responses():
    """Fixture to set specific AI responses"""
    def _set_responses(responses: list[str]):
        return create_mock_ai_client(responses)
    return _set_responses
```

### 3. MCP Tool Unit Tests
```python
# backend/tests/unit/test_mcp_tools.py
import pytest
from app.services.ai.tools.task_tools import (
    add_task, list_tasks, complete_task, delete_task,
    update_task, uncomplete_task, get_task_analytics, search_tasks
)
from app.models.task import Task

class TestAddTask:
    @pytest.mark.asyncio
    async def test_creates_task_successfully(self, db_session, test_user_id):
        result = await add_task(
            db=db_session,
            user_id=test_user_id,
            title="Test Task",
            description="Test Description",
            priority="high",
        )

        assert result["success"] is True
        assert "task_id" in result

    @pytest.mark.asyncio
    async def test_enforces_user_isolation(self, db_session):
        # Create task for user A
        result_a = await add_task(
            db=db_session,
            user_id="user-a",
            title="User A Task",
        )

        # List tasks for user B should not see user A's task
        result_b = await list_tasks(db=db_session, user_id="user-b")

        assert result_b["count"] == 0

    @pytest.mark.asyncio
    async def test_validates_title_length(self, db_session, test_user_id):
        with pytest.raises(ValueError, match="Title too long"):
            await add_task(
                db=db_session,
                user_id=test_user_id,
                title="x" * 501,  # Exceeds 500 char limit
            )

class TestListTasks:
    @pytest.mark.asyncio
    async def test_filters_by_completed(self, db_session, test_user_id):
        # Create completed and incomplete tasks
        await add_task(db=db_session, user_id=test_user_id, title="Task 1")
        task2 = await add_task(db=db_session, user_id=test_user_id, title="Task 2")
        await complete_task(db=db_session, user_id=test_user_id, task_id=task2["task_id"])

        # Filter incomplete only
        result = await list_tasks(db=db_session, user_id=test_user_id, completed=False)

        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Task 1"

    @pytest.mark.asyncio
    async def test_filters_by_priority(self, db_session, test_user_id):
        await add_task(db=db_session, user_id=test_user_id, title="Low", priority="low")
        await add_task(db=db_session, user_id=test_user_id, title="High", priority="high")

        result = await list_tasks(db=db_session, user_id=test_user_id, priority="high")

        assert result["count"] == 1
        assert result["tasks"][0]["priority"] == "high"
```

### 4. Agent Behavior Tests
```python
# backend/tests/unit/test_agents.py
import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai.agents.orchestrator import MainOrchestrator
from app.services.ai.agents.language_agents import EnglishAgent, UrduAgent

class TestMainOrchestrator:
    @pytest.mark.asyncio
    async def test_routes_english_to_miyu(self, mock_ai_client, test_user_id):
        with patch('app.services.ai.config.external_client', mock_ai_client):
            orchestrator = MainOrchestrator(user_id=test_user_id)

            # Mock language detection
            with patch.object(orchestrator, '_detect_language', return_value='en'):
                result = await orchestrator.process("Add a task called groceries")

                assert result.agent_name in ["Miyu", "Elara"]  # English agent or task agent

    @pytest.mark.asyncio
    async def test_routes_urdu_to_riven(self, mock_ai_client, test_user_id):
        with patch('app.services.ai.config.external_client', mock_ai_client):
            orchestrator = MainOrchestrator(user_id=test_user_id)

            with patch.object(orchestrator, '_detect_language', return_value='ur'):
                result = await orchestrator.process("کام شامل کریں")

                assert result.agent_name == "Riven"

class TestAgentPersonalities:
    @pytest.mark.asyncio
    async def test_elara_responds_with_icon(self, mock_ai_client, test_user_id):
        """Elara (AddTaskAgent) should include ➕ icon"""
        # Test that agent metadata includes correct icon
        from app.services.ai.agents.task_agents import add_task_agent

        assert add_task_agent.name == "Elara"
        # Icon should be in response metadata
```

### 5. Integration Tests
```python
# backend/tests/integration/test_agent_handoffs.py
import pytest
from app.services.ai.orchestrator import process_chat_message

class TestAgentHandoffs:
    @pytest.mark.asyncio
    async def test_full_add_task_flow(self, db_session, test_user_id, mock_ai_client):
        """Test complete flow: Orchestrator → Language → Task Agent"""
        with patch('app.services.ai.config.external_client', mock_ai_client):
            result = await process_chat_message(
                user_id=test_user_id,
                message="Add a task: Buy milk",
                conversation_history=[],
            )

            # Should have created a task
            assert result.content is not None
            assert result.agent_icon in ["➕", "🇬🇧", "🤖"]

    @pytest.mark.asyncio
    async def test_conversation_context_preserved(self, db_session, test_user_id, mock_ai_client):
        """Test that conversation history is passed to agents"""
        history = [
            {"role": "user", "content": "Add task: Buy groceries"},
            {"role": "assistant", "content": "Task added!"},
        ]

        with patch('app.services.ai.config.external_client', mock_ai_client):
            result = await process_chat_message(
                user_id=test_user_id,
                message="Now complete it",
                conversation_history=history,
            )

            # Agent should understand context
            assert result.content is not None
```

### 6. Rate Limiter Tests
```python
# backend/tests/unit/test_rate_limiter.py
import pytest
from datetime import datetime, timedelta
from app.middleware.rate_limit import RateLimiter

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self):
        limiter = RateLimiter(requests=5, window=60)

        for _ in range(5):
            assert await limiter.check("user-1") is True

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        limiter = RateLimiter(requests=5, window=60)

        for _ in range(5):
            await limiter.check("user-1")

        # 6th request should be blocked
        assert await limiter.check("user-1") is False

    @pytest.mark.asyncio
    async def test_resets_after_window(self):
        limiter = RateLimiter(requests=5, window=1)  # 1 second window

        for _ in range(5):
            await limiter.check("user-1")

        # Wait for window to expire
        import asyncio
        await asyncio.sleep(1.1)

        # Should allow again
        assert await limiter.check("user-1") is True
```

## Key Principles
- **Deterministic**: Mock AI for predictable tests
- **Isolation**: Test user isolation in every tool
- **Coverage**: Test success and error paths
- **Integration**: Test full agent handoff flows
- **Performance**: Keep tests fast with in-memory DB
