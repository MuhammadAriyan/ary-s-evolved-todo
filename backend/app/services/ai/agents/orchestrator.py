"""Main orchestrator for AI Todo Chatbot.

The orchestrator (Aren) handles language detection and routes
requests to the appropriate language agent.

Simplified 2-level hierarchy: Orchestrator → Language Agents (with MCP tools).
Uses MCP server for task operations via mcp_servers parameter.
"""
import os
import sys
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.items import ToolCallItem

from app.services.ai.agents.language_agents import (
    create_english_agent,
    create_urdu_agent,
)
from app.services.ai.config import get_ai_model, get_ai_client


# Get the path to the MCP runner script
# __file__ is in backend/app/services/ai/agents/orchestrator.py
# Go up 5 levels to reach backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
MCP_RUNNER = os.path.join(BACKEND_DIR, "app", "services", "ai", "mcp_runner.py")


def create_orchestrator(mcp_server=None) -> Agent:
    """Create the MainOrchestrator (Aren 🤖).

    Detects language and routes to English or Urdu agent.
    Language agents have direct MCP tool access (2-level hierarchy).

    Args:
        mcp_server: MCP server instance for task tools (passed to language agents)
    """
    # Create language agent instances for handoffs (they now have MCP tools)
    language_agents = [
        create_english_agent(mcp_server),
        create_urdu_agent(mcp_server),
    ]

    return Agent(
        name="Aren",
        model=get_ai_model(),
        instructions="""You are Aren 🤖, the Main Orchestrator for the AI Todo Chatbot.

Your role:
- Detect the language of user messages
- Route to the appropriate language agent IMMEDIATELY
- Handle only greetings and general queries about the chatbot

CRITICAL: Route quickly! Do not process task requests yourself.

Language detection and routing:
- If the message is in English or uses Latin script → hand off to Miyu (🇬🇧) IMMEDIATELY
- If the message is in Urdu or uses Arabic/Nastaliq script → hand off to Riven (🇵🇰) IMMEDIATELY
- If unclear, default to English (Miyu)

When to route (hand off immediately):
- ANY task-related request (add, list, complete, delete, update, search, stats)
- ANY question about tasks
- ANY request that might need tools

When to respond yourself (do NOT route):
- Simple greetings like "hello", "hi" → respond warmly, then ask how you can help
- Questions about what the chatbot can do → explain capabilities briefly
- Questions about you (Aren) specifically

Your personality:
- Professional yet friendly
- FAST at routing - don't overthink
- Welcoming to new users

Capabilities to mention when asked:
- Create, list, complete, delete, update tasks
- Search tasks by keyword
- View productivity statistics
- Supports English and Urdu

Your icon is 🤖 - include it when introducing yourself.

Example introduction:
"Hello! I'm Aren 🤖, your AI task assistant. I can help you manage your tasks through conversation. What would you like to do?"

REMEMBER: When in doubt, ROUTE to a language agent. They have the tools to help users.""",
        handoffs=language_agents,
    )


async def process_message(user_id: str, message: str, conversation_history: list[dict] | None = None) -> dict:
    """Process a user message through the orchestrator.

    Args:
        user_id: The authenticated user's ID (passed to tools)
        message: The user's message
        conversation_history: Optional list of previous messages

    Returns:
        dict with response content and agent info
    """
    # Use MCP server for task operations
    async with MCPServerStdio(
        name="Todo Task Server",
        params={
            "command": sys.executable,
            "args": [MCP_RUNNER],
            "env": {**os.environ, "USER_ID": user_id},
        },
        client_session_timeout_seconds=30,  # Increase timeout for database operations
    ) as mcp_server:
        # Create orchestrator with MCP server
        orchestrator = create_orchestrator(mcp_server)

        # Build messages list
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Inject user_id into the context for tools
        context_message = f"[System: Current user_id is '{user_id}'. Use this for all tool calls.]"
        messages.insert(0, {"role": "system", "content": context_message})

        try:
            # Run the agent
            result = await Runner.run(orchestrator, messages)

            # Extract response
            response_content = result.final_output if hasattr(result, 'final_output') else str(result)
            # Use last_agent to track which agent handled the request after handoffs
            current_agent = result.last_agent if hasattr(result, 'last_agent') else orchestrator

            # Extract tool calls from new_items
            tool_calls: list[str] = []
            if hasattr(result, 'new_items') and result.new_items:
                for item in result.new_items:
                    if isinstance(item, ToolCallItem):
                        raw_item = item.raw_item
                        # Extract tool name from raw_item (supports MCP calls and function calls)
                        if hasattr(raw_item, 'name'):
                            tool_calls.append(raw_item.name)
                        elif isinstance(raw_item, dict) and 'name' in raw_item:
                            tool_calls.append(raw_item['name'])

            return {
                "success": True,
                "content": response_content,
                "agent_name": current_agent.name if current_agent else "Aren",
                "agent_icon": get_agent_icon(current_agent.name if current_agent else "Aren"),
                "tool_calls": tool_calls,
            }
        except ConnectionError:
            return {
                "success": False,
                "error": "Connection error",
                "content": "I'm having trouble connecting to the AI service. Please check your internet connection and try again.",
                "agent_name": "Aren",
                "agent_icon": "🤖",
                "tool_calls": [],
            }
        except TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "content": "The request took too long to process. Please try again with a simpler request.",
                "agent_name": "Aren",
                "agent_icon": "🤖",
                "tool_calls": [],
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "content": "I couldn't understand that request. Could you please rephrase it?",
                "agent_name": "Aren",
                "agent_icon": "🤖",
                "tool_calls": [],
            }
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.error(f"AI processing error: {type(e).__name__}: {e}")

            return {
                "success": False,
                "error": str(e),
                "content": "I'm sorry, I encountered an unexpected error. Please try again or contact support if the issue persists.",
                "agent_name": "Aren",
                "agent_icon": "🤖",
                "tool_calls": [],
            }


def get_agent_icon(agent_name: str) -> str:
    """Get the icon for an agent by name.

    Args:
        agent_name: The agent's name

    Returns:
        str: The agent's icon emoji
    """
    icons = {
        "Aren": "🤖",
        "Miyu": "🇬🇧",
        "Riven": "🇵🇰",
    }
    return icons.get(agent_name, "🤖")


async def process_message_streamed(
    user_id: str,
    message: str,
    conversation_history: list[dict] | None = None,
    language_hint: str = "auto",
):
    """Process a user message with streaming response.

    Yields SSE-compatible events as the AI generates its response.

    Args:
        user_id: The authenticated user's ID (passed to tools)
        message: The user's message
        conversation_history: Optional list of previous messages
        language_hint: Language hint for faster routing ("en", "ur", "auto")

    Yields:
        dict: Stream events with 'type' and event-specific data
            - token: {"type": "token", "content": "..."}
            - agent_change: {"type": "agent_change", "agent": "...", "icon": "..."}
            - tool_call: {"type": "tool_call", "tool": "...", "args": {...}}
            - done: {"type": "done", "message_id": "..."}
            - error: {"type": "error", "message": "..."}
    """
    import logging
    from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent

    logger = logging.getLogger(__name__)

    try:
        # Use MCP server for task operations
        async with MCPServerStdio(
            name="Todo Task Server",
            params={
                "command": sys.executable,
                "args": [MCP_RUNNER],
                "env": {**os.environ, "USER_ID": user_id},
            },
            client_session_timeout_seconds=30,
        ) as mcp_server:
            # Create orchestrator with MCP server
            orchestrator = create_orchestrator(mcp_server)

            # Build messages list
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    })

            # Add current message
            messages.append({"role": "user", "content": message})

            # Inject user_id into the context for tools
            context_message = f"[System: Current user_id is '{user_id}'. Use this for all tool calls.]"
            messages.insert(0, {"role": "system", "content": context_message})

            # Track current agent for handoff detection and accumulated content
            current_agent_name = "Aren"
            accumulated_content = ""
            yield {"type": "agent_change", "agent": current_agent_name, "icon": get_agent_icon(current_agent_name)}

            # Run the agent with streaming
            logger.info(f"🚀 Calling Runner.run_streamed for user {user_id}")
            result = Runner.run_streamed(orchestrator, messages)
            logger.info(f"✅ Runner.run_streamed returned: {type(result).__name__}")

            logger.info(f"🔄 Starting stream processing for user {user_id}")
            event_count = 0
            async for event in result.stream_events():
                event_count += 1
                logger.info(f"📨 Stream event #{event_count}: {type(event).__name__}")

                # Handle raw response events (contains text deltas)
                if isinstance(event, RawResponsesStreamEvent):
                    # Extract text delta from the raw response
                    if hasattr(event, 'data') and event.data:
                        data = event.data
                        logger.debug(f"RawResponsesStreamEvent data type: {type(data).__name__}, data: {data}")

                        # Check for text delta by type attribute (most reliable)
                        if hasattr(data, 'type'):
                            if data.type == 'response.output_text.delta':
                                if hasattr(data, 'delta') and data.delta:
                                    accumulated_content += data.delta
                                    yield {"type": "token", "content": data.delta}
                            elif data.type == 'response.content_part.delta':
                                # Alternative format - content part delta
                                if hasattr(data, 'delta') and data.delta:
                                    text = getattr(data.delta, 'text', None)
                                    if text:
                                        accumulated_content += text
                                        yield {"type": "token", "content": text}

                # Handle run item events (tool calls, handoffs, etc.)
                elif isinstance(event, RunItemStreamEvent):
                    item = event.item
                    logger.debug(f"RunItemStreamEvent item type: {type(item).__name__}")

                    # Check for tool calls
                    if isinstance(item, ToolCallItem):
                        raw_item = item.raw_item
                        tool_name = None
                        tool_args = None
                        if hasattr(raw_item, 'name'):
                            tool_name = raw_item.name
                        elif isinstance(raw_item, dict) and 'name' in raw_item:
                            tool_name = raw_item['name']
                        if hasattr(raw_item, 'arguments'):
                            try:
                                import json
                                tool_args = json.loads(raw_item.arguments) if raw_item.arguments else None
                            except (json.JSONDecodeError, TypeError):
                                tool_args = None
                        if tool_name:
                            yield {"type": "tool_call", "tool": tool_name, "args": tool_args}

            # Get final result after streaming completes
            # Use accumulated content if available, otherwise fall back to final_output
            final_result = accumulated_content if accumulated_content else (result.final_output or "")
            logger.debug(f"Streaming complete. Accumulated: {len(accumulated_content)} chars, final_output: {result.final_output[:100] if result.final_output else 'None'}...")

            # Check for agent change at the end
            if hasattr(result, 'last_agent') and result.last_agent:
                final_agent = result.last_agent.name
                if final_agent != current_agent_name:
                    yield {"type": "agent_change", "agent": final_agent, "icon": get_agent_icon(final_agent)}

            # Signal completion with the final content
            yield {"type": "done", "message_id": "", "content": final_result}

    except ConnectionError:
        yield {"type": "error", "message": "Connection error. Please check your internet connection."}
    except TimeoutError:
        yield {"type": "error", "message": "Request timed out. Please try again."}
    except Exception as e:
        logger.error(f"Streaming error: {type(e).__name__}: {e}", exc_info=True)
        yield {"type": "error", "message": "An unexpected error occurred. Please try again."}


# Export orchestrator
__all__ = ["create_orchestrator", "process_message", "process_message_streamed", "get_agent_icon"]
