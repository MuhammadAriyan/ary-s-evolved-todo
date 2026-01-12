"""MCP tools for task operations.

These tools are exposed to AI agents for task management.
All tools filter by user_id for isolation.
"""
from datetime import datetime, date
from typing import Optional
from sqlmodel import Session, select, func
from sqlalchemy import cast, or_
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

from app.models.task import Task
from app.database import get_session


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
        return {"success": False, "error": "Title is required"}

    if len(title) > 200:
        return {"success": False, "error": "Title must be 200 characters or less"}

    # Validate priority
    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        priority = "Medium"

    # Parse due date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            return {"success": False, "error": "Invalid due date format. Use YYYY-MM-DD"}

    try:
        session = next(get_session())
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
            "success": True,
            "task_id": task.id,
            "message": f"Task '{title}' created successfully"
        }
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
) -> dict:
    """List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID
        completed: Filter by completion status (true/false)
        priority: Filter by priority level (High/Medium/Low)
        tags: Filter by tags (returns tasks with any matching tag)
        limit: Maximum number of tasks to return (default 50, max 100)

    Returns:
        dict with list of tasks and count
    """
    limit = min(limit, 100)

    try:
        session = next(get_session())
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        if priority:
            query = query.where(Task.priority == priority)

        if tags:
            # Filter tasks that have any of the specified tags
            for tag in tags:
                query = query.where(Task.tags.contains(cast([tag], ARRAY(TEXT))))

        query = query.order_by(Task.created_at.desc()).limit(limit)
        tasks = session.exec(query).all()

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [
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
        }
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to complete

    Returns:
        dict with success status and confirmation message
    """
    try:
        session = next(get_session())
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or access denied"}

        if task.completed:
            return {"success": True, "message": f"Task '{task.title}' is already completed"}

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {"success": True, "message": f"Task '{task.title}' marked as completed"}
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def uncomplete_task(user_id: str, task_id: int) -> dict:
    """Reopen a completed task.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to reopen

    Returns:
        dict with success status and confirmation message
    """
    try:
        session = next(get_session())
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or access denied"}

        if not task.completed:
            return {"success": True, "message": f"Task '{task.title}' is already open"}

        task.completed = False
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {"success": True, "message": f"Task '{task.title}' reopened"}
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to delete

    Returns:
        dict with success status and confirmation message
    """
    try:
        session = next(get_session())
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or access denied"}

        title = task.title
        session.delete(task)
        session.commit()

        return {"success": True, "message": f"Task '{title}' deleted"}
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


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
        session = next(get_session())
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or access denied"}

        updated_fields = []

        if title is not None:
            if len(title) > 200:
                return {"success": False, "error": "Title must be 200 characters or less"}
            task.title = title
            updated_fields.append("title")

        if description is not None:
            task.description = description or None
            updated_fields.append("description")

        if priority is not None:
            valid_priorities = ["High", "Medium", "Low"]
            if priority not in valid_priorities:
                return {"success": False, "error": f"Invalid priority. Use: {', '.join(valid_priorities)}"}
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
                return {"success": False, "error": "Invalid due date format. Use YYYY-MM-DD"}

        if not updated_fields:
            return {"success": True, "message": "No changes made", "updated_fields": []}

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {
            "success": True,
            "message": "Task updated successfully",
            "updated_fields": updated_fields
        }
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def search_tasks(
    user_id: str,
    query: str,
    limit: int = 20,
) -> dict:
    """Search tasks by keyword.

    Args:
        user_id: The authenticated user's ID
        query: Search keyword to match in title or description
        limit: Maximum number of results (default 20)

    Returns:
        dict with matching tasks and count
    """
    if not query or len(query.strip()) == 0:
        return {"success": False, "error": "Search query is required"}

    limit = min(limit, 100)
    search_term = f"%{query.lower()}%"

    try:
        session = next(get_session())
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

        return {
            "success": True,
            "count": len(tasks),
            "query": query,
            "tasks": [
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
        }
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


async def get_task_analytics(user_id: str) -> dict:
    """Get task statistics for the user.

    Args:
        user_id: The authenticated user's ID

    Returns:
        dict with analytics including counts, completion rate, and breakdowns
    """
    try:
        session = next(get_session())

        # Get all tasks for the user
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.completed)
        pending_tasks = total_tasks - completed_tasks

        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Count by priority
        by_priority = {"High": 0, "Medium": 0, "Low": 0}
        for task in tasks:
            if task.priority in by_priority:
                by_priority[task.priority] += 1

        # Count overdue and due today
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
            "success": True,
            "analytics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": round(completion_rate, 1),
                "by_priority": by_priority,
                "overdue_tasks": overdue_tasks,
                "tasks_due_today": tasks_due_today,
            }
        }
    except Exception as e:
        return {"success": False, "error": "Database error occurred"}


# Export all tools
TASK_TOOLS = [
    add_task,
    list_tasks,
    complete_task,
    uncomplete_task,
    delete_task,
    update_task,
    search_tasks,
    get_task_analytics,
]
