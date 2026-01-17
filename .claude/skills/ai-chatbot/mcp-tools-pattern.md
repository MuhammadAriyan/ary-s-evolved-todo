# MCP Tools Pattern Skill

## Purpose
Create stateless MCP tools using Official MCP SDK (FastMCP) with @function_tool decorator for AI agents.

## Context7 Reference
- Library: `/modelcontextprotocol/python-sdk`
- Query: "function_tool decorator patterns"

## Tool Implementation Pattern

### 1. Basic Tool Structure
```python
# backend/app/services/ai/tools/task_tools.py
from agents import function_tool
from sqlmodel import select
from app.models.task import Task
from app.core.database import get_session

@function_tool
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] = [],
    due_date: str | None = None,
) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (max 500 characters)
        description: Optional task description
        priority: Task priority (low, medium, high)
        tags: Optional list of tags
        due_date: Optional due date in ISO format

    Returns:
        dict with task_id and success status
    """
    async with get_session() as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task '{title}' created successfully"
        }
```

### 2. Query Tool Pattern
```python
@function_tool
async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
) -> dict:
    """
    List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID
        completed: Filter by completion status
        priority: Filter by priority level
        tags: Filter by tags (any match)
        limit: Maximum number of tasks to return

    Returns:
        dict with list of tasks
    """
    async with get_session() as session:
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)
        if priority:
            statement = statement.where(Task.priority == priority)
        if tags:
            statement = statement.where(Task.tags.overlap(tags))

        statement = statement.limit(limit).order_by(Task.created_at.desc())
        result = await session.exec(statement)
        tasks = result.all()

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [task.model_dump() for task in tasks]
        }
```

### 3. Update Tool Pattern
```python
@function_tool
async def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to complete

    Returns:
        dict with success status
    """
    async with get_session() as session:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id  # CRITICAL: User isolation
        )
        result = await session.exec(statement)
        task = result.first()

        if not task:
            return {
                "success": False,
                "error": "Task not found or access denied"
            }

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()

        return {
            "success": True,
            "message": f"Task '{task.title}' marked as completed"
        }
```

### 4. All 8 Required Tools
```python
# Tool registry
TASK_TOOLS = [
    add_task,        # Create task
    list_tasks,      # Query tasks
    complete_task,   # Mark completed
    delete_task,     # Remove task
    update_task,     # Modify task
    uncomplete_task, # Reopen task
    get_task_analytics,  # Statistics
    search_tasks,    # Keyword search
]
```

### 5. Registering Tools with Agent
```python
from agents import Agent
from app.services.ai.tools.task_tools import TASK_TOOLS

task_agent = Agent(
    name="Elara",
    instructions="You help users add tasks...",
    tools=TASK_TOOLS,
)
```

## Key Principles
- **Stateless**: No in-memory state, all data in database
- **User Isolation**: ALWAYS filter by user_id
- **Docstrings**: Used by AI to understand tool purpose
- **Type Hints**: Required for proper tool schema generation
- **Error Handling**: Return dict with success/error, never raise
