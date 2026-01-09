"""Task API endpoints."""
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy import cast, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from typing import List, Optional
from datetime import datetime

from app.api.deps import SessionDep, CurrentUser
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


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

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

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

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

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

    session.delete(task)
    session.commit()

    return None
