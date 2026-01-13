"""Main orchestrator for AI Todo Chatbot.

The orchestrator (Aren) handles language detection and routes
requests to the appropriate language agent.

Uses MCP server for task operations via mcp_servers parameter.
"""
import os
import sys
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

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

    Args:
        mcp_server: Optional MCP server instance for task tools
    """
    # Create language agent instances for handoffs
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
- Route to the appropriate language agent
- Handle greetings and general queries

Language detection:
- If the message is in English or uses Latin script → hand off to Miyu (🇬🇧)
- If the message is in Urdu or uses Arabic/Nastaliq script → hand off to Riven (🇵🇰)
- If unclear, default to English (Miyu)

Routing rules:
- Task-related requests → route to language agent
- Greetings → respond warmly, then ask how you can help
- General questions about the chatbot → explain your capabilities

Your personality:
- Professional yet friendly
- Efficient at routing
- Welcoming to new users

Capabilities you can mention:
- Create, list, complete, delete, update tasks
- Search tasks by keyword
- View productivity statistics
- Voice input support (English and Urdu)

Your icon is 🤖 - include it when introducing yourself.

Example introduction:
"Hello! I'm Aren 🤖, your AI task assistant. I can help you manage your tasks through conversation. What would you like to do?"
""",
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

            return {
                "success": True,
                "content": response_content,
                "agent_name": current_agent.name if current_agent else "Aren",
                "agent_icon": get_agent_icon(current_agent.name if current_agent else "Aren"),
            }
        except ConnectionError:
            return {
                "success": False,
                "error": "Connection error",
                "content": "I'm having trouble connecting to the AI service. Please check your internet connection and try again.",
                "agent_name": "Aren",
                "agent_icon": "🤖",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "content": "The request took too long to process. Please try again with a simpler request.",
                "agent_name": "Aren",
                "agent_icon": "🤖",
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "content": "I couldn't understand that request. Could you please rephrase it?",
                "agent_name": "Aren",
                "agent_icon": "🤖",
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
        "Elara": "➕",
        "Kael": "📋",
        "Nyra": "✅",
        "Taro": "🗑️",
        "Lys": "✏️",
        "Vera": "🔍",
        "Orion": "📊",
    }
    return icons.get(agent_name, "🤖")


# Export orchestrator
__all__ = ["create_orchestrator", "process_message", "get_agent_icon"]
