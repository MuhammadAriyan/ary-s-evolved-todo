"""Reminder API endpoints.

T067: Add reminder endpoints in backend API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/api/v1", tags=["reminders"])

# Initialize ReminderService
reminder_service = ReminderService()
reminder_service.initialize()


# Request/Response Models
class ReminderCreate(BaseModel):
    """Request model for creating a reminder."""
    task_id: str = Field(..., description="Task ID")
    reminder_time: datetime = Field(..., description="When to send the reminder")
    timezone: str = Field(default="UTC", description="User's timezone")
    notification_channels: List[str] = Field(
        default=["in_app"],
        description="Notification channels (email, in_app, push)"
    )
    cron_expression: Optional[str] = Field(None, description="Optional cron expression for recurring reminders")


class ReminderUpdate(BaseModel):
    """Request model for updating a reminder."""
    reminder_time: Optional[datetime] = None
    timezone: Optional[str] = None
    notification_channels: Optional[List[str]] = None
    status: Optional[str] = None


class ReminderResponse(BaseModel):
    """Response model for a reminder."""
    id: int
    task_id: str
    user_id: str
    reminder_time: datetime
    timezone: str
    notification_channels: List[str]
    cron_expression: Optional[str]
    status: str
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@router.post("/tasks/{task_id}/reminders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    task_id: str,
    reminder_data: ReminderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new reminder for a task.

    T067: POST /tasks/{id}/reminders endpoint
    """
    user_id = current_user.get("id")

    # Validate task_id matches
    if reminder_data.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID in URL does not match task ID in request body"
        )

    # Create reminder
    reminder_id = reminder_service.create_reminder(
        task_id=task_id,
        user_id=user_id,
        reminder_time=reminder_data.reminder_time,
        timezone=reminder_data.timezone,
        notification_channels=reminder_data.notification_channels,
        cron_expression=reminder_data.cron_expression
    )

    if not reminder_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )

    return {
        "id": reminder_id,
        "task_id": task_id,
        "message": "Reminder created successfully"
    }


@router.get("/tasks/{task_id}/reminders", response_model=List[ReminderResponse])
async def get_task_reminders(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all reminders for a specific task.

    T067: GET /tasks/{id}/reminders endpoint
    """
    user_id = current_user.get("id")

    reminders = reminder_service.get_reminders_for_task(task_id, user_id)

    return reminders


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific reminder by ID.

    T067: GET /reminders/{id} endpoint
    """
    user_id = current_user.get("id")

    reminder = reminder_service.get_reminder(reminder_id, user_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    return reminder


@router.patch("/reminders/{reminder_id}", response_model=dict)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a reminder.

    T067: PATCH /reminders/{id} endpoint
    """
    user_id = current_user.get("id")

    success = reminder_service.update_reminder(
        reminder_id=reminder_id,
        user_id=user_id,
        reminder_time=reminder_data.reminder_time,
        timezone=reminder_data.timezone,
        notification_channels=reminder_data.notification_channels,
        status=reminder_data.status
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found or update failed"
        )

    return {"message": "Reminder updated successfully"}


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a reminder.

    T067: DELETE /reminders/{id} endpoint
    """
    user_id = current_user.get("id")

    success = reminder_service.delete_reminder(reminder_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    return None
