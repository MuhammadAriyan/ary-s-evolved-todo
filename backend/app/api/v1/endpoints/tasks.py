"""Task API endpoints."""
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy import cast, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from typing import List, Optional
from datetime import datetime
import logging

from app.api.deps import SessionDep, CurrentUser
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.event_publisher import get_event_publisher

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    tag: Optional[str] = Query(None, description="Filter by tag"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    sort: Optional[str] = Query(None, description="Sort by: priority, due_date, title"),
):
    """List all tasks for the authenticated user with optional filters."""
    query = select(Task).where(Task.user_id == current_user)

    # Apply filters
    if tag:
        # Cast the array to TEXT[] to match the column type
        query = query.where(Task.tags.contains(cast([tag], ARRAY(TEXT))))
    if priority:
        query = query.where(Task.priority == priority)
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Apply sorting
    if sort == "priority":
        query = query.order_by(Task.priority.desc())
    elif sort == "due_date":
        query = query.order_by(Task.due_date.asc())
    elif sort == "title":
        query = query.order_by(Task.title.asc())
    else:
        query = query.order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Create a new task for the authenticated user."""
    task = Task(
        user_id=current_user,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        recurring=task_data.recurring,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # T031: Publish task.created event
    try:
        event_publisher = get_event_publisher()
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurring": task.recurring,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        await event_publisher.publish_task_event(
            event_type="task.created",
            task_id=str(task.id),
            user_id=current_user,
            task_data=task_dict,
            after_state=task_dict
        )
        logger.info(f"Published task.created event for task {task.id}")
    except Exception as e:
        logger.error(f"Failed to publish task.created event: {str(e)}")
        # Don't fail the request if event publishing fails

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get a specific task by ID with user isolation."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Update a task with user isolation."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T031: Capture before state for event
    before_state = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurring": task.recurring,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # T031: Publish task.updated event
    try:
        event_publisher = get_event_publisher()
        after_state = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurring": task.recurring,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        await event_publisher.publish_task_event(
            event_type="task.updated",
            task_id=str(task.id),
            user_id=current_user,
            task_data=after_state,
            before_state=before_state,
            after_state=after_state
        )
        logger.info(f"Published task.updated event for task {task.id}")
    except Exception as e:
        logger.error(f"Failed to publish task.updated event: {str(e)}")

    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    task_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Toggle task completion status."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T031: Capture before state
    before_completed = task.completed

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # T031: Publish task.completed event
    try:
        event_publisher = get_event_publisher()
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurring": task.recurring,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        event_type = "task.completed" if task.completed else "task.uncompleted"
        await event_publisher.publish_task_event(
            event_type=event_type,
            task_id=str(task.id),
            user_id=current_user,
            task_data=task_dict,
            after_state=task_dict
        )
        logger.info(f"Published {event_type} event for task {task.id}")
    except Exception as e:
        logger.error(f"Failed to publish task completion event: {str(e)}")

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Delete a task with user isolation."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T031: Capture task data before deletion
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurring": task.recurring,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }

    session.delete(task)
    session.commit()

    # T031: Publish task.deleted event
    try:
        event_publisher = get_event_publisher()
        await event_publisher.publish_task_event(
            event_type="task.deleted",
            task_id=str(task_id),
            user_id=current_user,
            task_data=task_dict,
            before_state=task_dict
        )
        logger.info(f"Published task.deleted event for task {task_id}")
    except Exception as e:
        logger.error(f"Failed to publish task.deleted event: {str(e)}")

    return None
