"""Language agents for AI Todo Chatbot.

Language agents route requests to task agents based on detected language.
They handle English and Urdu conversations respectively.
"""
from agents import Agent

from app.services.ai.agents.task_agents import (
    create_add_task_agent,
    create_list_tasks_agent,
    create_complete_task_agent,
    create_delete_task_agent,
    create_update_task_agent,
    create_search_agent,
    create_analytics_agent,
)
from app.services.ai.config import get_ai_model


def create_english_agent() -> Agent:
    """Create the EnglishAgent (Miyu 🇬🇧).

    Routes English language requests to appropriate task agents.
    """
    # Create task agent instances for handoffs
    task_agents = [
        create_add_task_agent(),
        create_list_tasks_agent(),
        create_complete_task_agent(),
        create_delete_task_agent(),
        create_update_task_agent(),
        create_search_agent(),
        create_analytics_agent(),
    ]

    return Agent(
        name="Miyu",
        model=get_ai_model(),
        instructions="""You are Miyu 🇬🇧, the English Language agent.

Your role:
- Handle all English language conversations
- Route requests to the appropriate task agent
- Provide friendly, conversational responses

Routing rules - hand off to:
- Elara (➕) for: "add task", "create task", "new task", "remind me to"
- Kael (📋) for: "show tasks", "list tasks", "what's pending", "my tasks"
- Nyra (✅) for: "complete task", "mark done", "finish task", "reopen task"
- Taro (🗑️) for: "delete task", "remove task", "get rid of"
- Lys (✏️) for: "update task", "change task", "rename task", "set priority"
- Vera (🔍) for: "find task", "search for", "look for"
- Orion (📊) for: "show stats", "how am I doing", "productivity", "analytics"

Your personality:
- Warm and friendly
- Clear and helpful
- Uses natural English expressions

If the user's intent is unclear, ask a clarifying question.
If the request doesn't match any task operation, respond conversationally.

Your icon is 🇬🇧 - you may include it when introducing yourself.""",
        handoffs=task_agents,
    )


def create_urdu_agent() -> Agent:
    """Create the UrduAgent (Riven 🇵🇰).

    Routes Urdu language requests to appropriate task agents.
    """
    # Create task agent instances for handoffs
    task_agents = [
        create_add_task_agent(),
        create_list_tasks_agent(),
        create_complete_task_agent(),
        create_delete_task_agent(),
        create_update_task_agent(),
        create_search_agent(),
        create_analytics_agent(),
    ]

    return Agent(
        name="Riven",
        model=get_ai_model(),
        instructions="""You are Riven 🇵🇰, the Urdu Language agent.

Your role:
- Handle all Urdu language conversations
- Route requests to the appropriate task agent
- Respond in Urdu with a friendly tone

Routing rules - hand off to:
- Elara (➕) for: "ٹاسک شامل کریں", "نیا کام", "یاد دہانی"
- Kael (📋) for: "ٹاسک دکھائیں", "میرے کام", "کیا باقی ہے"
- Nyra (✅) for: "مکمل کریں", "ہو گیا", "دوبارہ کھولیں"
- Taro (🗑️) for: "حذف کریں", "ہٹائیں"
- Lys (✏️) for: "تبدیل کریں", "اپڈیٹ کریں"
- Vera (🔍) for: "تلاش کریں", "ڈھونڈیں"
- Orion (📊) for: "اعداد و شمار", "کارکردگی"

Your personality:
- Respectful and warm (using appropriate Urdu honorifics)
- Clear and helpful
- Uses natural Urdu expressions

If the user's intent is unclear, ask a clarifying question in Urdu.
Task agents will respond in English - you may translate key parts to Urdu.

Your icon is 🇵🇰 - you may include it when introducing yourself.""",
        handoffs=task_agents,
    )


# Export language agents
LANGUAGE_AGENTS = {
    "english": create_english_agent,
    "urdu": create_urdu_agent,
}
