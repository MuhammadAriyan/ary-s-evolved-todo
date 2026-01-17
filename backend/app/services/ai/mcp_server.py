"""MCP Server for task operations using Official MCP SDK.

This module creates an MCP server that exposes task operations as tools.
The server is used by OpenAI Agents via mcp_servers parameter.

Architecture:
- MCP server runs as subprocess or in-process
- Agents connect via MCPServerStdio or MCPServerSse
- Tools are async and run database operations in thread pool (anyio)
"""
from datetime import datetime, date
from typing import Optional
from sqlmodel import create_engine, Session, select, func
from sqlalchemy import cast, or_
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from mcp.server.fastmcp import FastMCP
import os
import anyio

from app.models.task import Task


# Create MCP server instance
mcp = FastMCP("Todo Task Server")


def _get_db_session() -> Session:
    """Get a fresh database session for MCP tools."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")

    engine = create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )
    return Session(engine)


# ============================================================================
# Synchronous database operations (run in thread pool)
# ============================================================================

def _add_task_sync(
    user_id: str,
    title: str,
    description: str,
    priority: str,
    tags: list[str] | None,
    parsed_due_date: date | None,
) -> dict:
    """Sync implementation of add_task."""
    with _get_db_session() as session:
        task = Task(
            user_id=user_id,
            title=title[:200],
            description=description or None,
            priority=priority,
            tags=tags or [],
            due_date=parsed_due_date,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }


def _list_tasks_sync(
    user_id: str,
    completed: bool | None,
    priority: str | None,
    tags: list[str] | None,
    limit: int,
) -> list[dict]:
    """Sync implementation of list_tasks."""
    with _get_db_session() as session:
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        if priority:
            query = query.where(Task.priority == priority)

        if tags:
            for tag in tags:
                query = query.where(Task.tags.contains(cast([tag], ARRAY(TEXT))))

        query = query.order_by(Task.created_at.desc()).limit(limit)
        tasks = session.exec(query).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            }
            for task in tasks
        ]


def _complete_task_sync(user_id: str, task_id: int) -> dict:
    """Sync implementation of complete_task."""
    with _get_db_session() as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"error": "Task not found or access denied"}

        if task.completed:
            return {"task_id": task_id, "status": "already_completed", "title": task.title}

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        return {"task_id": task_id, "status": "completed", "title": task.title}


def _uncomplete_task_sync(user_id: str, task_id: int) -> dict:
    """Sync implementation of uncomplete_task."""
    with _get_db_session() as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"error": "Task not found or access denied"}

        if not task.completed:
            return {"task_id": task_id, "status": "already_open", "title": task.title}

        task.completed = False
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        return {"task_id": task_id, "status": "reopened", "title": task.title}


def _delete_task_sync(user_id: str, task_id: int) -> dict:
    """Sync implementation of delete_task."""
    with _get_db_session() as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"error": "Task not found or access denied"}

        title = task.title
        session.delete(task)
        session.commit()
        return {"task_id": task_id, "status": "deleted", "title": title}


def _update_task_sync(
    user_id: str,
    task_id: int,
    title: str | None,
    description: str | None,
    priority: str | None,
    tags: list[str] | None,
    due_date: str | None,
) -> dict:
    """Sync implementation of update_task."""
    with _get_db_session() as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"error": "Task not found or access denied"}

        updated_fields = []

        if title is not None:
            if len(title) > 200:
                return {"error": "Title must be 200 characters or less"}
            task.title = title
            updated_fields.append("title")

        if description is not None:
            task.description = description or None
            updated_fields.append("description")

        if priority is not None:
            valid_priorities = ["High", "Medium", "Low"]
            if priority not in valid_priorities:
                return {"error": f"Invalid priority. Use: {', '.join(valid_priorities)}"}
            task.priority = priority
            updated_fields.append("priority")

        if tags is not None:
            task.tags = tags
            updated_fields.append("tags")

        if due_date is not None:
            try:
                task.due_date = date.fromisoformat(due_date) if due_date else None
                updated_fields.append("due_date")
            except ValueError:
                return {"error": "Invalid due date format. Use YYYY-MM-DD"}

        if not updated_fields:
            return {"task_id": task_id, "status": "no_changes", "title": task.title}

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        return {"task_id": task_id, "status": "updated", "title": task.title}


def _search_tasks_sync(user_id: str, query: str, limit: int) -> list[dict]:
    """Sync implementation of search_tasks."""
    search_term = f"%{query.lower()}%"

    with _get_db_session() as session:
        statement = (
            select(Task)
            .where(
                Task.user_id == user_id,
                or_(
                    func.lower(Task.title).like(search_term),
                    func.lower(Task.description).like(search_term),
                )
            )
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        tasks = session.exec(statement).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }
            for task in tasks
        ]


def _get_task_analytics_sync(user_id: str) -> dict:
    """Sync implementation of get_task_analytics."""
    with _get_db_session() as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.completed)
        pending_tasks = total_tasks - completed_tasks

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        by_priority = {"High": 0, "Medium": 0, "Low": 0}
        for task in tasks:
            if task.priority in by_priority:
                by_priority[task.priority] += 1

        today = date.today()
        overdue_tasks = sum(
            1 for t in tasks
            if t.due_date and t.due_date < today and not t.completed
        )
        tasks_due_today = sum(
            1 for t in tasks
            if t.due_date and t.due_date == today and not t.completed
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 1),
            "by_priority": by_priority,
            "overdue_tasks": overdue_tasks,
            "tasks_due_today": tasks_due_today,
        }


# ============================================================================
# Async MCP Tools (run sync operations in thread pool)
# ============================================================================

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "Medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
) -> dict:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (max 200 characters)
        description: Optional task description
        priority: Task priority (High, Medium, Low)
        tags: Optional list of tags
        due_date: Optional due date in ISO format (YYYY-MM-DD)

    Returns:
        dict with task_id and success status
    """
    if not title:
        return {"error": "Title is required"}

    if len(title) > 200:
        return {"error": "Title must be 200 characters or less"}

    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        priority = "Medium"

    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            return {"error": "Invalid due date format. Use YYYY-MM-DD"}

    try:
        return await anyio.to_thread.run_sync(
            lambda: _add_task_sync(user_id, title, description, priority, tags, parsed_due_date)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
) -> list[dict] | dict:
    """List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID
        completed: Filter by completion status (true/false)
        priority: Filter by priority level (High/Medium/Low)
        tags: Filter by tags (returns tasks with any matching tag)
        limit: Maximum number of tasks to return (default 50, max 100)

    Returns:
        list of task objects or error dict
    """
    limit = min(limit, 100)

    try:
        return await anyio.to_thread.run_sync(
            lambda: _list_tasks_sync(user_id, completed, priority, tags, limit)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to complete

    Returns:
        dict with success status and confirmation message
    """
    try:
        return await anyio.to_thread.run_sync(
            lambda: _complete_task_sync(user_id, task_id)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def uncomplete_task(user_id: str, task_id: int) -> dict:
    """Reopen a completed task.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to reopen

    Returns:
        dict with success status and confirmation message
    """
    try:
        return await anyio.to_thread.run_sync(
            lambda: _uncomplete_task_sync(user_id, task_id)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to delete

    Returns:
        dict with success status and confirmation message
    """
    try:
        return await anyio.to_thread.run_sync(
            lambda: _delete_task_sync(user_id, task_id)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
) -> dict:
    """Update task properties.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to update
        title: New task title (optional)
        description: New description (optional)
        priority: New priority level (optional)
        tags: New tags list - replaces existing (optional)
        due_date: New due date in ISO format (optional)

    Returns:
        dict with success status and list of updated fields
    """
    try:
        return await anyio.to_thread.run_sync(
            lambda: _update_task_sync(user_id, task_id, title, description, priority, tags, due_date)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def search_tasks(
    user_id: str,
    query: str,
    limit: int = 20,
) -> list[dict] | dict:
    """Search tasks by keyword.

    Args:
        user_id: The authenticated user's ID
        query: Search keyword to match in title or description
        limit: Maximum number of results (default 20)

    Returns:
        dict with matching tasks and count
    """
    if not query or len(query.strip()) == 0:
        return {"error": "Search query is required"}

    limit = min(limit, 100)

    try:
        return await anyio.to_thread.run_sync(
            lambda: _search_tasks_sync(user_id, query, limit)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def get_task_analytics(user_id: str) -> dict:
    """Get task statistics for the user.

    Args:
        user_id: The authenticated user's ID

    Returns:
        dict with analytics including counts, completion rate, and breakdowns
    """
    try:
        return await anyio.to_thread.run_sync(
            lambda: _get_task_analytics_sync(user_id)
        )
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# Export the MCP server instance
def get_mcp_server() -> FastMCP:
    """Get the MCP server instance."""
    return mcp
