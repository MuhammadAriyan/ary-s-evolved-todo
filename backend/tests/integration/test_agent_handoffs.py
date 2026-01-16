"""Integration tests for agent handoffs and multi-agent flows."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestAgentHandoffRouting:
    """Tests for language detection and agent routing."""

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_orchestrator_has_english_agent_handoff(
        self, mock_lang_model, mock_orch_model
    ):
        """Test that orchestrator can hand off to English agent."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_orch_model.return_value = "gpt-4"
        mock_lang_model.return_value = "gpt-4"

        orchestrator = create_orchestrator(mcp_server=None)

        agent_names = [agent.name for agent in orchestrator.handoffs]
        assert "Miyu" in agent_names

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_orchestrator_has_urdu_agent_handoff(
        self, mock_lang_model, mock_orch_model
    ):
        """Test that orchestrator can hand off to Urdu agent."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_orch_model.return_value = "gpt-4"
        mock_lang_model.return_value = "gpt-4"

        orchestrator = create_orchestrator(mcp_server=None)

        agent_names = [agent.name for agent in orchestrator.handoffs]
        assert "Riven" in agent_names

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_two_level_hierarchy_structure(
        self, mock_lang_model, mock_orch_model
    ):
        """Test that we have exactly 2-level hierarchy (orchestrator -> language agents)."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_orch_model.return_value = "gpt-4"
        mock_lang_model.return_value = "gpt-4"

        orchestrator = create_orchestrator(mcp_server=None)

        # Orchestrator should have exactly 2 handoffs (English and Urdu)
        assert len(orchestrator.handoffs) == 2

        # Language agents should not have further handoffs (they have tools instead)
        for agent in orchestrator.handoffs:
            # Language agents don't have handoffs, they have MCP tools
            assert not hasattr(agent, 'handoffs') or len(agent.handoffs) == 0


class TestAgentHandoffWithMCP:
    """Tests for agent handoffs with MCP server integration."""

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_mcp_server_passed_to_language_agents(
        self, mock_lang_model, mock_orch_model
    ):
        """Test that MCP server is passed to language agents for tool access."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_orch_model.return_value = "gpt-4"
        mock_lang_model.return_value = "gpt-4"
        mock_mcp = MagicMock()

        orchestrator = create_orchestrator(mcp_server=mock_mcp)

        # Both language agents should have the MCP server
        for agent in orchestrator.handoffs:
            assert mock_mcp in agent.mcp_servers

    @patch('app.services.ai.agents.orchestrator.get_ai_model')
    @patch('app.services.ai.agents.language_agents.get_ai_model')
    def test_orchestrator_has_no_mcp_servers(
        self, mock_lang_model, mock_orch_model
    ):
        """Test that orchestrator itself doesn't have MCP servers (only routes)."""
        from app.services.ai.agents.orchestrator import create_orchestrator

        mock_orch_model.return_value = "gpt-4"
        mock_lang_model.return_value = "gpt-4"
        mock_mcp = MagicMock()

        orchestrator = create_orchestrator(mcp_server=mock_mcp)

        # Orchestrator should not have MCP servers directly
        assert not hasattr(orchestrator, 'mcp_servers') or len(orchestrator.mcp_servers) == 0


class TestAgentHandoffTracking:
    """Tests for tracking which agent handled a request."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_tracks_final_agent_after_handoff(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that the final agent is tracked after handoff."""
        from app.services.ai.agents.orchestrator import process_message

        # Setup mocks
        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        orchestrator = MagicMock()
        orchestrator.name = "Aren"
        mock_create_orch.return_value = orchestrator

        # Simulate handoff to Miyu
        final_agent = MagicMock()
        final_agent.name = "Miyu"

        mock_result = MagicMock()
        mock_result.final_output = "Task added!"
        mock_result.last_agent = final_agent  # Handoff occurred
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Add a task to buy groceries",
        )

        # Should report Miyu as the agent, not Aren
        assert result["agent_name"] == "Miyu"

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_tracks_orchestrator_when_no_handoff(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that orchestrator is tracked when no handoff occurs."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        orchestrator = MagicMock()
        orchestrator.name = "Aren"
        mock_create_orch.return_value = orchestrator

        mock_result = MagicMock()
        mock_result.final_output = "Hello! How can I help?"
        mock_result.last_agent = orchestrator  # No handoff
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Hello",
        )

        assert result["agent_name"] == "Aren"


class TestAgentHandoffToolCalls:
    """Tests for tool call tracking during handoffs."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_tracks_tool_calls_from_language_agent(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that tool calls from language agent are tracked."""
        from app.services.ai.agents.orchestrator import process_message
        from agents.items import ToolCallItem

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")

        # Create mock tool call item
        mock_tool_item = MagicMock(spec=ToolCallItem)
        mock_raw_item = MagicMock()
        mock_raw_item.name = "add_task"
        mock_tool_item.raw_item = mock_raw_item

        mock_result = MagicMock()
        mock_result.final_output = "Task added!"
        mock_result.last_agent = MagicMock(name="Miyu")
        mock_result.new_items = [mock_tool_item]
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Add a task",
        )

        assert "add_task" in result["tool_calls"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_tracks_multiple_tool_calls(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that multiple tool calls are tracked."""
        from app.services.ai.agents.orchestrator import process_message
        from agents.items import ToolCallItem

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")

        # Create multiple mock tool call items
        tool_items = []
        for tool_name in ["list_tasks", "get_task_analytics"]:
            mock_tool_item = MagicMock(spec=ToolCallItem)
            mock_raw_item = MagicMock()
            mock_raw_item.name = tool_name
            mock_tool_item.raw_item = mock_raw_item
            tool_items.append(mock_tool_item)

        mock_result = MagicMock()
        mock_result.final_output = "Here are your tasks and stats!"
        mock_result.last_agent = MagicMock(name="Miyu")
        mock_result.new_items = tool_items
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await process_message(
            user_id="user-123",
            message="Show my tasks and stats",
        )

        assert "list_tasks" in result["tool_calls"]
        assert "get_task_analytics" in result["tool_calls"]


class TestAgentHandoffUserIsolation:
    """Tests for user isolation during agent handoffs."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_user_id_injected_into_context(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that user_id is injected into message context."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")

        mock_result = MagicMock()
        mock_result.final_output = "Done"
        mock_result.last_agent = MagicMock(name="Aren")
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        await process_message(
            user_id="user-123",
            message="Hello",
        )

        # Verify Runner.run was called with messages containing user_id
        call_args = mock_runner.run.call_args
        messages = call_args[0][1]

        # First message should be system message with user_id
        system_msg = messages[0]
        assert system_msg["role"] == "system"
        assert "user-123" in system_msg["content"]

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    async def test_user_id_passed_to_mcp_server_env(self, mock_mcp_class):
        """Test that user_id is passed to MCP server environment."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        with patch('app.services.ai.agents.orchestrator.Runner') as mock_runner:
            with patch('app.services.ai.agents.orchestrator.create_orchestrator'):
                mock_result = MagicMock()
                mock_result.final_output = "Done"
                mock_result.last_agent = MagicMock(name="Aren")
                mock_result.new_items = []
                mock_runner.run = AsyncMock(return_value=mock_result)

                await process_message(
                    user_id="user-123",
                    message="Hello",
                )

        # Verify MCPServerStdio was called with USER_ID in env
        call_kwargs = mock_mcp_class.call_args[1]
        assert "USER_ID" in call_kwargs["params"]["env"]
        assert call_kwargs["params"]["env"]["USER_ID"] == "user-123"


class TestAgentHandoffConversationContext:
    """Tests for conversation context during handoffs."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_conversation_history_passed_to_agent(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that conversation history is passed to agent."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")

        mock_result = MagicMock()
        mock_result.final_output = "Done"
        mock_result.last_agent = MagicMock(name="Aren")
        mock_result.new_items = []
        mock_runner.run = AsyncMock(return_value=mock_result)

        history = [
            {"role": "user", "content": "Add a task"},
            {"role": "assistant", "content": "Task added!"},
        ]

        await process_message(
            user_id="user-123",
            message="Now complete it",
            conversation_history=history,
        )

        # Verify history was included in messages
        call_args = mock_runner.run.call_args
        messages = call_args[0][1]

        # Should have: system + 2 history + 1 current = 4 messages
        assert len(messages) == 4

        # History messages should be in order
        assert messages[1]["content"] == "Add a task"
        assert messages[2]["content"] == "Task added!"
        assert messages[3]["content"] == "Now complete it"


class TestAgentHandoffErrorRecovery:
    """Tests for error handling during agent handoffs."""

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_returns_aren_on_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that Aren is returned as agent on errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")
        mock_runner.run = AsyncMock(side_effect=RuntimeError("Agent error"))

        result = await process_message(
            user_id="user-123",
            message="Hello",
        )

        assert result["success"] is False
        assert result["agent_name"] == "Aren"
        assert result["agent_icon"] == "\U0001F916"

    @pytest.mark.asyncio
    @patch('app.services.ai.agents.orchestrator.MCPServerStdio')
    @patch('app.services.ai.agents.orchestrator.Runner')
    @patch('app.services.ai.agents.orchestrator.create_orchestrator')
    async def test_empty_tool_calls_on_error(
        self, mock_create_orch, mock_runner, mock_mcp_class
    ):
        """Test that tool_calls is empty on errors."""
        from app.services.ai.agents.orchestrator import process_message

        mock_mcp = MagicMock()
        mock_mcp.__aenter__ = AsyncMock(return_value=mock_mcp)
        mock_mcp.__aexit__ = AsyncMock(return_value=None)
        mock_mcp_class.return_value = mock_mcp

        mock_create_orch.return_value = MagicMock(name="Aren")
        mock_runner.run = AsyncMock(side_effect=ConnectionError("Network error"))

        result = await process_message(
            user_id="user-123",
            message="Hello",
        )

        assert result["tool_calls"] == []
