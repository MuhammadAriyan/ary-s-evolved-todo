"""Pydantic schemas for task operations."""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(pattern="^(High|Medium|Low)$")
    tags: List[str] = Field(default_factory=list, max_length=10)
    due_date: Optional[date] = None
    recurring: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(default=None, pattern="^(High|Medium|Low)$")
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    due_date: Optional[date] = None
    recurring: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[date]
    recurring: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
