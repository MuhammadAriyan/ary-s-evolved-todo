# Agent Hierarchy Design Skill

## Purpose
Design and implement multi-agent handoff patterns for the AI Todo Chatbot with orchestrator, language agents, and task agents.

## Context7 Reference
- Library: `/openai/openai-agents-python`
- Query: "agent handoff patterns multi-agent"

## Hierarchy Structure

```
Main Orchestrator (Aren 🤖)
├── English Agent (Miyu 🇬🇧)
│   └── Task Agents (7 specialized)
└── Urdu Agent (Riven 🇵🇰)
    └── Task Agents (shared)

Task Agents:
├── AddTaskAgent (Elara ➕)
├── ListTasksAgent (Kael 📋)
├── CompleteTaskAgent (Nyra ✅)
├── DeleteTaskAgent (Taro 🗑️)
├── UpdateTaskAgent (Lys ✏️)
├── AnalyticsAgent (Orion 📊)
└── SearchAgent (Vera 🔍)
```

## Implementation Patterns

### 1. Main Orchestrator
```python
# backend/app/services/ai/agents/orchestrator.py
from agents import Agent, handoff
from app.services.ai.agents.language_agents import english_agent, urdu_agent

ORCHESTRATOR_INSTRUCTIONS = """
You are Aren, the main orchestrator. You are quiet, calculating, and outcome-driven.
Your role is to detect the user's language and route to the appropriate language agent.

Rules:
1. If the message is in Urdu (اردو), hand off to Riven (Urdu Agent)
2. If the message is in English, hand off to Miyu (English Agent)
3. Never respond directly - always delegate to a language agent
4. Include your icon 🤖 in metadata
"""

main_orchestrator = Agent(
    name="Aren",
    instructions=ORCHESTRATOR_INSTRUCTIONS,
    handoffs=[
        handoff(english_agent, "Route English messages to Miyu"),
        handoff(urdu_agent, "Route Urdu messages to Riven"),
    ],
)
```

### 2. Language Agents
```python
# backend/app/services/ai/agents/language_agents.py
from agents import Agent, handoff
from app.services.ai.agents.task_agents import (
    add_task_agent, list_tasks_agent, complete_task_agent,
    delete_task_agent, update_task_agent, analytics_agent, search_agent
)

ENGLISH_AGENT_INSTRUCTIONS = """
You are Miyu, the English language agent. You are calm, precise, and emotionally reserved.
Your role is to understand the user's intent and delegate to the appropriate task agent.

Personality:
- Speak in clear, concise English
- Maintain a professional but warm tone
- Include your icon 🇬🇧 in responses

Intent Routing:
- "add", "create", "new task" → Elara (AddTaskAgent)
- "list", "show", "what tasks" → Kael (ListTasksAgent)
- "complete", "done", "finish" → Nyra (CompleteTaskAgent)
- "delete", "remove" → Taro (DeleteTaskAgent)
- "update", "change", "edit" → Lys (UpdateTaskAgent)
- "analytics", "stats", "how many" → Orion (AnalyticsAgent)
- "search", "find" → Vera (SearchAgent)
"""

english_agent = Agent(
    name="Miyu",
    instructions=ENGLISH_AGENT_INSTRUCTIONS,
    handoffs=[
        handoff(add_task_agent, "Add new tasks"),
        handoff(list_tasks_agent, "List tasks"),
        handoff(complete_task_agent, "Complete tasks"),
        handoff(delete_task_agent, "Delete tasks"),
        handoff(update_task_agent, "Update tasks"),
        handoff(analytics_agent, "Task analytics"),
        handoff(search_agent, "Search tasks"),
    ],
)

URDU_AGENT_INSTRUCTIONS = """
You are Riven, the Urdu language agent. You are direct, intense, and impatient.
Your role is to understand Urdu commands and delegate to task agents.

Personality:
- Respond in Urdu (اردو)
- Be direct and to the point
- Include your icon 🇵🇰 in responses

Intent Routing (Urdu keywords):
- "شامل کریں", "نیا کام" → Elara (AddTaskAgent)
- "دکھائیں", "فہرست" → Kael (ListTasksAgent)
- "مکمل", "ہو گیا" → Nyra (CompleteTaskAgent)
- "حذف کریں", "ہٹائیں" → Taro (DeleteTaskAgent)
- "تبدیل کریں", "اپڈیٹ" → Lys (UpdateTaskAgent)
- "اعداد و شمار" → Orion (AnalyticsAgent)
- "تلاش کریں" → Vera (SearchAgent)
"""

urdu_agent = Agent(
    name="Riven",
    instructions=URDU_AGENT_INSTRUCTIONS,
    handoffs=[
        handoff(add_task_agent, "کام شامل کریں"),
        handoff(list_tasks_agent, "کام دکھائیں"),
        handoff(complete_task_agent, "کام مکمل کریں"),
        handoff(delete_task_agent, "کام حذف کریں"),
        handoff(update_task_agent, "کام اپڈیٹ کریں"),
        handoff(analytics_agent, "اعداد و شمار"),
        handoff(search_agent, "تلاش کریں"),
    ],
)
```

### 3. Task Agents
```python
# backend/app/services/ai/agents/task_agents.py
from agents import Agent
from app.services.ai.tools.task_tools import (
    add_task, list_tasks, complete_task, delete_task,
    update_task, uncomplete_task, get_task_analytics, search_tasks
)

add_task_agent = Agent(
    name="Elara",
    instructions="""
    You are Elara, the task creation specialist. You are composed and structured.
    Use the add_task tool to create tasks. Always confirm what was created.
    Include your icon ➕ in responses.
    """,
    tools=[add_task],
)

list_tasks_agent = Agent(
    name="Kael",
    instructions="""
    You are Kael, the task listing specialist. You are minimalist and detached.
    Use the list_tasks tool to show tasks. Present results clearly and concisely.
    Include your icon 📋 in responses.
    """,
    tools=[list_tasks],
)

# ... similar for other task agents
```

### 4. Running the Hierarchy
```python
from agents import Runner

async def process_chat_message(
    user_id: str,
    message: str,
    conversation_history: list[dict]
) -> AgentResponse:
    """Process a chat message through the agent hierarchy"""

    # Inject user_id into tool context
    context = {"user_id": user_id}

    runner = Runner(
        agent=main_orchestrator,
        context=context,
    )

    result = await runner.run(
        messages=conversation_history + [{"role": "user", "content": message}]
    )

    # Extract responding agent info
    return AgentResponse(
        content=result.content,
        agent_name=result.agent.name,
        agent_icon=AGENT_ICONS[result.agent.name],
    )

AGENT_ICONS = {
    "Aren": "🤖",
    "Miyu": "🇬🇧",
    "Riven": "🇵🇰",
    "Elara": "➕",
    "Kael": "📋",
    "Nyra": "✅",
    "Taro": "🗑️",
    "Lys": "✏️",
    "Orion": "📊",
    "Vera": "🔍",
}
```

## Key Principles
- **Single Responsibility**: Each agent has one job
- **Clear Handoffs**: Explicit routing rules
- **Personality Consistency**: Each agent maintains character
- **User Context**: user_id passed through context
- **Icon Tracking**: Every response includes agent icon
