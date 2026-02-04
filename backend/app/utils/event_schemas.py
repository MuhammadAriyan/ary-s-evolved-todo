"""Event schema validation utilities."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class EventMetadata(BaseModel):
    """Metadata for events."""
    original_event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    source_service: Optional[str] = None


class BaseEvent(BaseModel):
    """Base event schema."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    metadata: EventMetadata = Field(default_factory=EventMetadata)

    @validator('event_id')
    def validate_event_id(cls, v):
        """Validate event_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError(f"Invalid event_id: {v}")
        return v


class TaskEventData(BaseModel):
    """Data schema for task events."""
    task_id: str
    task: Dict[str, Any]
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


class TaskEvent(BaseEvent):
    """Task event schema."""
    event_type: str = Field(..., regex=r"^task\.(created|updated|deleted|completed)$")
    data: TaskEventData

    @validator('event_type')
    def validate_event_type(cls, v):
        """Validate event_type for task events."""
        valid_types = ["task.created", "task.updated", "task.deleted", "task.completed"]
        if v not in valid_types:
            raise ValueError(f"Invalid task event type: {v}")
        return v


class ReminderEventData(BaseModel):
    """Data schema for reminder events."""
    reminder_id: int
    task_id: str
    reminder: Dict[str, Any]


class ReminderEvent(BaseEvent):
    """Reminder event schema."""
    event_type: str = Field(..., regex=r"^reminder\.(scheduled|triggered|cancelled)$")
    data: ReminderEventData


class AuditEventData(BaseModel):
    """Data schema for audit events."""
    operation: str
    resource_type: str
    resource_id: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditEvent(BaseEvent):
    """Audit event schema."""
    data: AuditEventData


def validate_event(event_data: Dict[str, Any], event_class: type[BaseEvent] = BaseEvent) -> BaseEvent:
    """
    Validate an event against a schema.

    Args:
        event_data: Event data dictionary
        event_class: Event class to validate against (default: BaseEvent)

    Returns:
        Validated event instance

    Raises:
        ValidationError: If validation fails
    """
    return event_class(**event_data)


def validate_task_event(event_data: Dict[str, Any]) -> TaskEvent:
    """
    Validate a task event.

    Args:
        event_data: Event data dictionary

    Returns:
        Validated TaskEvent instance
    """
    return validate_event(event_data, TaskEvent)


def validate_reminder_event(event_data: Dict[str, Any]) -> ReminderEvent:
    """
    Validate a reminder event.

    Args:
        event_data: Event data dictionary

    Returns:
        Validated ReminderEvent instance
    """
    return validate_event(event_data, ReminderEvent)


def validate_audit_event(event_data: Dict[str, Any]) -> AuditEvent:
    """
    Validate an audit event.

    Args:
        event_data: Event data dictionary

    Returns:
        Validated AuditEvent instance
    """
    return validate_event(event_data, AuditEvent)
