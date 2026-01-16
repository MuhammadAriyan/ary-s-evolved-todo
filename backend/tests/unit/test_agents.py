"""Unit tests for AI agents - orchestrator and language agents."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
import asyncio


class TestGetAgentIcon:
    """Tests for get_agent_icon function."""

    def test_returns_robot_for_aren(self):
        """Test that Aren gets robot icon."""
        from app.services.ai.agents.orchestrator import get_agent_icon
        assert get_agent_icon("Aren") == "\U0001F916"

    def test_returns_gb_flag_for_miyu(self):
        """Test that Miyu gets GB flag icon."""
        from app.services.ai.agents.orchestrator import get_agent_icon
        assert get_agent_icon("Miyu") == "\U0001F1EC\U0001F1E7"

    def test_returns_pk_flag_for_riven(self):
        """Test that Riven gets PK flag icon."""
        from app.services.ai.agents.orchestrator import get_agent_icon
        assert get_agent_icon("Riven") == "\U0001F1F5\U0001F1F0"

    def test_returns_robot_for_unknown_agent(self):
        """Test that unknown agents get default robot icon."""
        from app.services.ai.agents.orchestrator import get_agent_icon
        assert get_agent_icon("Unknown") == "\U0001F916"
        assert get_agent_icon("") == "\U0001F916"


class TestCreateOrchestrator:
    """Tests for create_orchestrator function."""

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.orchestrator.create_english_agent')
    @patch('app.services.ai.agents.orchestrator.create_urdu_agent')
    def test_creates_orchestrator_with_handoffs(
        self, mock_urdu, mock_english, mock_model
    ):
        """Test that orchestrator is created with language agent handoffs."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_model.return_value = "gpt-4"
        mock_english.return_value = MagicMock(name="Miyu")
        mock_urdu.return_value = MagicMock(name="Riven")

        orchestrator = create_orchestrator(mcp_server=None)

        assert orchestrator.name == "Aren"
        assert len(orchestrator.handoffs) == 2
        mock_english.assert_called_once_with(None)
        mock_urdu.assert_called_once_with(None)

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.orchestrator.create_english_agent')
    @patch('app.services.ai.agents.orchestrator.create_urdu_agent')
    def test_passes_mcp_server_to_language_agents(
        self, mock_urdu, mock_english, mock_model
    ):
        """Test that MCP server is passed to language agents."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_model.return_value = "gpt-4"
        mock_mcp = MagicMock()

        create_orchestrator(mcp_server=mock_mcp)

        mock_english.assert_called_once_with(mock_mcp)
        mock_urdu.assert_called_once_with(mock_mcp)


class TestCreateEnglishAgent:
    """Tests for create_english_agent function."""

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_creates_english_agent_with_correct_name(self, mock_model):
        """Test that English agent has correct name."""
        from app.services.ai.agents.language_agents import create_english_agent

        mock_model.return_value = "gpt-4"
        agent = create_english_agent(mcp_server=None)

        assert agent.name == "Miyu"

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_creates_english_agent_with_mcp_server(self, mock_model):
        """Test that English agent receives MCP server."""
        from app.services.ai.agents.language_agents import create_english_agent

        mock_model.return_value = "gpt-4"
        mock_mcp = MagicMock()

        agent = create_english_agent(mcp_server=mock_mcp)

        assert mock_mcp in agent.mcp_servers

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_creates_english_agent_without_mcp_server(self, mock_model):
        """Test that English agent works without MCP server."""
        from app.services.ai.agents.language_agents import create_english_agent

        mock_model.return_value = "gpt-4"
        agent = create_english_agent(mcp_server=None)

        assert agent.mcp_servers == []


class TestCreateUrduAgent:
    """Tests for create_urdu_agent function."""

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_creates_urdu_agent_with_correct_name(self, mock_model):
        """Test that Urdu agent has correct name."""
        from app.services.ai.agents.language_agents import create_urdu_agent

        mock_model.return_value = "gpt-4"
        agent = create_urdu_agent(mcp_server=None)

        assert agent.name == "Riven"

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_creates_urdu_agent_with_mcp_server(self, mock_model):
        """Test that Urdu agent receives MCP server."""
        from app.services.ai.agents.language_agents import create_urdu_agent

        mock_model.return_value = "gpt-4"
        mock_mcp = MagicMock()

        agent = create_urdu_agent(mcp_server=mock_mcp)

        assert mock_mcp in agent.mcp_servers


class TestProcessMessage:
    """Tests for process_message function."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_success(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test successful message processing."""
        from app.services.ai.agents.orchestrator import process_message

        # Setup mocks
        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Miyu"
        mock_create_orch.return_value = mock_agent

        mock_result = MagicMock()
        mock_result.final_output = "Task added!"
        mock_result.last_agent = mock_agent
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Add a task",
            conversation_history=None,
        )

        assert result["success"] is True
        assert result["content"] == "Task added!"
        assert result["agent_name"] == "Miyu"

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_with_conversation_history(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test message processing with conversation history."""
        from app.services.ai.agents.orchestrator import process_message

        # Setup mocks
        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Aren"
        mock_create_orch.return_value = mock_agent

        mock_result = MagicMock()
        mock_result.final_output = "Response"
        mock_result.last_agent = mock_agent
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = await process_message(
            user_id="user-123",
            message="Add a task",
            conversation_history=history,
        )

        assert result["success"] is True
        # Verify Runner.run was called with messages including history
        call_args = mock_runner.run.call_args
        messages = call_args[0][1]  # Second positional arg
        # Should have: system message + 2 history + 1 current
        assert len(messages) == 4

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_connection_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test handling of connection errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock()
        mock_runner.run = AsyncMock(side_effect=ConnectionError("Network error"))

        result = await process_message(
            user_id="user-123",
            message="Add a task",
        )

        assert result["success"] is False
        assert result["error"] == "Connection error"
        assert "trouble connecting" in result["content"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_timeout_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test handling of timeout errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock()
        mock_runner.run = AsyncMock(side_effect=TimeoutError("Request timed out"))

        result = await process_message(
            user_id="user-123",
            message="Add a task",
        )

        assert result["success"] is False
        assert result["error"] == "Timeout"
        assert "took too long" in result["content"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_value_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test handling of value errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock()
        mock_runner.run = AsyncMock(side_effect=ValueError("Invalid input"))

        result = await process_message(
            user_id="user-123",
            message="Add a task",
        )

        assert result["success"] is False
        assert "couldn't understand" in result["content"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_process_message_generic_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test handling of generic errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock()
        mock_runner.run = AsyncMock(side_effect=RuntimeError("Unknown error"))

        result = await process_message(
            user_id="user-123",
            message="Add a task",
        )

        assert result["success"] is False
        assert "unexpected error" in result["content"]


class TestProcessMessageStreamed:
    """Tests for process_message_streamed function."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_yields_initial_agent_change(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that streaming yields initial agent_change event."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        # Setup mocks
        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Aren"
        mock_create_orch.return_value = mock_agent

        # Mock streaming result
        mock_stream_result = MagicMock()

        async def empty_stream():
            return
            yield  # Make it an async generator

        mock_stream_result.stream_events = empty_stream
        mock_stream_result.final_output = "Done"  # Property, not callable
        mock_stream_result.last_agent = mock_agent
        mock_runner.run_streamed = MagicMock(return_value=mock_stream_result)

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
        ):
            events.append(event)

        # First event should be agent_change for Aren
        assert len(events) >= 1
        assert events[0]["type"] == "agent_change"
        assert events[0]["agent"] == "Aren"

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    async def test_yields_error_on_connection_error(self, mock_mcp_class):
        """Test that streaming yields error event on connection error."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(side_effect=ConnectionError("Network error"))
        mock_mcp_class.return_value = mock_mcp

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
        ):
            events.append(event)

        assert len(events) == 1
        assert events[0]["type"] == "error"
        assert "Connection" in events[0]["message"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    async def test_yields_error_on_timeout(self, mock_mcp_class):
        """Test that streaming yields error event on timeout."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(side_effect=TimeoutError("Timeout"))
        mock_mcp_class.return_value = mock_mcp

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
        ):
            events.append(event)

        assert len(events) == 1
        assert events[0]["type"] == "error"
        assert "timed out" in events[0]["message"]


class TestLanguageAgentsExport:
    """Tests for LANGUAGE_AGENTS export."""

    def test_language_agents_dict_has_english(self):
        """Test that LANGUAGE_AGENTS contains english."""
        from app.services.ai.agents.language_agents import LANGUAGE_AGENTS
        assert "english" in LANGUAGE_AGENTS

    def test_language_agents_dict_has_urdu(self):
        """Test that LANGUAGE_AGENTS contains urdu."""
        from app.services.ai.agents.language_agents import LANGUAGE_AGENTS
        assert "urdu" in LANGUAGE_AGENTS

    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_language_agents_factories_work(self, mock_model):
        """Test that language agent factories create agents."""
        from app.services.ai.agents.language_agents import LANGUAGE_AGENTS

        mock_model.return_value = "gpt-4"

        english_agent = LANGUAGE_AGENTS["english"](None)
        urdu_agent = LANGUAGE_AGENTS["urdu"](None)

        assert english_agent.name == "Miyu"
        assert urdu_agent.name == "Riven"


class TestProcessMessageStreamedAdvanced:
    """Advanced tests for process_message_streamed function."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_yields_done_event_with_final_content(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that streaming yields done event with accumulated content."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Miyu"
        mock_create_orch.return_value = mock_agent

        mock_stream_result = MagicMock()

        async def empty_stream():
            return
            yield

        mock_stream_result.stream_events = empty_stream
        mock_stream_result.final_output = "Final response content"  # Property, not callable
        mock_stream_result.last_agent = mock_agent
        mock_runner.run_streamed = MagicMock(return_value=mock_stream_result)

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
        ):
            events.append(event)

        # Should have done event with content
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) == 1
        assert done_events[0].get("content") == "Final response content"

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_language_hint_passed_to_function(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that language_hint parameter is accepted."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Aren"
        mock_create_orch.return_value = mock_agent

        mock_stream_result = MagicMock()

        async def empty_stream():
            return
            yield

        mock_stream_result.stream_events = empty_stream
        mock_stream_result.final_output = "Done"  # Property, not callable
        mock_stream_result.last_agent = mock_agent
        mock_runner.run_streamed = MagicMock(return_value=mock_stream_result)

        # Should not raise with language_hint parameter
        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
            language_hint="en",
        ):
            events.append(event)

        assert len(events) >= 1

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    async def test_yields_error_on_generic_exception(self, mock_mcp_class):
        """Test that streaming yields error event on generic exception."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(side_effect=RuntimeError("Unexpected error"))
        mock_mcp_class.return_value = mock_mcp

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Hello",
        ):
            events.append(event)

        assert len(events) == 1
        assert events[0]["type"] == "error"
        assert "unexpected error" in events[0]["message"].lower()

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_detects_agent_change_at_end(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that agent change is detected when last_agent differs."""
        from app.services.ai.agents.orchestrator import process_message_streamed

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        # Orchestrator starts as Aren
        orchestrator = MagicMock()
        orchestrator.name = "Aren"
        mock_create_orch.return_value = orchestrator

        # But final agent is Miyu (handoff occurred)
        final_agent = MagicMock()
        final_agent.name = "Miyu"

        mock_stream_result = MagicMock()

        async def empty_stream():
            return
            yield

        mock_stream_result.stream_events = empty_stream
        mock_stream_result.final_output = "Done"  # Property, not callable
        mock_stream_result.last_agent = final_agent
        mock_runner.run_streamed = MagicMock(return_value=mock_stream_result)

        events = []
        async for event in process_message_streamed(
            user_id="user-123",
            message="Add a task",
        ):
            events.append(event)

        # Should have agent_change events
        agent_changes = [e for e in events if e.get("type") == "agent_change"]
        assert len(agent_changes) >= 1
        # Last agent change should be Miyu
        assert agent_changes[-1]["agent"] == "Miyu"


class TestProcessMessageWithHistory:
    """Tests for process_message with various conversation history scenarios."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_empty_conversation_history(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test message processing with empty conversation history."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Aren"
        mock_create_orch.return_value = mock_agent

        mock_result = MagicMock()
        mock_result.final_output = "Response"
        mock_result.last_agent = mock_agent
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Hello",
            conversation_history=[],
        )

        assert result["success"] is True
        # Should have: system message + current message = 2 messages
        call_args = mock_runner.run.call_args
        messages = call_args[0][1]
        assert len(messages) == 2

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_long_conversation_history(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test message processing with long conversation history."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_agent = MagicMock()
        mock_agent.name = "Aren"
        mock_create_orch.return_value = mock_agent

        mock_result = MagicMock()
        mock_result.final_output = "Response"
        mock_result.last_agent = mock_agent
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        # Create long history
        history = []
        for i in range(20):
            history.append({"role": "user", "content": f"Message {i}"})
            history.append({"role": "assistant", "content": f"Response {i}"})

        result = await process_message(
            user_id="user-123",
            message="Final message",
            conversation_history=history,
        )

        assert result["success"] is True
        # Should have: system + 40 history + 1 current = 42 messages
        call_args = mock_runner.run.call_args
        messages = call_args[0][1]
        assert len(messages) == 42


class TestAgentIconMapping:
    """Tests for agent icon mapping edge cases."""

    def test_icon_mapping_case_sensitivity(self):
        """Test that icon mapping is case-sensitive."""
        from app.services.ai.agents.orchestrator import get_agent_icon

        # Exact case should work
        assert get_agent_icon("Aren") == "\U0001F916"
        assert get_agent_icon("Miyu") == "\U0001F1EC\U0001F1E7"
        assert get_agent_icon("Riven") == "\U0001F1F5\U0001F1F0"

        # Wrong case should return default
        assert get_agent_icon("aren") == "\U0001F916"
        assert get_agent_icon("MIYU") == "\U0001F916"
        assert get_agent_icon("riven") == "\U0001F916"

    def test_icon_mapping_none_input(self):
        """Test that None input returns default icon."""
        from app.services.ai.agents.orchestrator import get_agent_icon

        # None should return default (robot)
        assert get_agent_icon(None) == "\U0001F916"
