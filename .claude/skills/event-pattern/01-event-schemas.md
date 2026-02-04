# Event Schema Design

## CloudEvents Standard

Use CloudEvents specification for consistent event structure:

```json
{
  "specversion": "1.0",
  "id": "evt_a1b2c3d4",
  "source": "task-service",
  "type": "com.evolvedtodo.task.created",
  "datacontenttype": "application/json",
  "time": "2026-02-01T10:30:00Z",
  "data": {
    "task_id": "task_123",
    "title": "Complete Phase 8",
    "status": "pending",
    "user_id": "user_456"
  },
  "metadata": {
    "correlation_id": "req_xyz789",
    "causation_id": "evt_previous",
    "user_id": "user_456",
    "tenant_id": "tenant_001"
  }
}
```

## Event Type Naming

### Convention
`<domain>.<entity>.<action>`

### Examples
- `task.created` - Task was created
- `task.updated` - Task was modified
- `task.completed` - Task was marked complete
- `task.deleted` - Task was deleted
- `reminder.scheduled` - Reminder was scheduled
- `reminder.delivered` - Reminder was sent
- `user.registered` - User signed up
- `user.verified` - User verified email

## Event Schema Template

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class EventMetadata(BaseModel):
    """Metadata for event tracing and correlation"""
    correlation_id: str = Field(description="Request correlation ID")
    causation_id: Optional[str] = Field(None, description="ID of event that caused this")
    user_id: Optional[str] = Field(None, description="User who triggered event")
    tenant_id: Optional[str] = Field(None, description="Tenant/organization ID")
    ip_address: Optional[str] = Field(None, description="Client IP address")

class BaseEvent(BaseModel):
    """Base event schema following CloudEvents spec"""
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    source: str = Field(description="Service that published event")
    type: str = Field(description="Event type (domain.entity.action)")
    time: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(description="Event payload")
    metadata: EventMetadata = Field(description="Event metadata")

class TaskCreatedEvent(BaseEvent):
    """Event published when a task is created"""
    type: str = "task.created"
    source: str = "task-service"

    class Data(BaseModel):
        task_id: str
        title: str
        description: Optional[str]
        status: str
        priority: Optional[str]
        due_date: Optional[datetime]
        user_id: str
        created_at: datetime

    data: Data

class TaskUpdatedEvent(BaseEvent):
    """Event published when a task is updated"""
    type: str = "task.updated"
    source: str = "task-service"

    class Data(BaseModel):
        task_id: str
        changes: Dict[str, Any]  # Before/after values
        updated_fields: list[str]
        user_id: str
        updated_at: datetime

    data: Data
```

## Schema Versioning

### Version in Event Type
```json
{
  "type": "task.created.v2",
  "data": {
    "task_id": "123",
    "title": "New field in v2"
  }
}
```

### Version in Data
```json
{
  "type": "task.created",
  "data": {
    "schema_version": "2.0",
    "task_id": "123"
  }
}
```

### Backward Compatibility Rules
1. **Never remove fields** - Mark as deprecated instead
2. **Add optional fields only** - Don't require new fields
3. **Don't change field types** - Create new field instead
4. **Support multiple versions** - Consumers handle old and new

## Event Validation

```python
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

async def validate_event(event_data: dict, event_class: type[BaseEvent]):
    """
    Validate event against schema

    Args:
        event_data: Raw event dictionary
        event_class: Pydantic model class

    Returns:
        Validated event or None if invalid
    """
    try:
        event = event_class(**event_data)
        return event
    except ValidationError as e:
        logger.error(f"Event validation failed: {e}")
        return None

# Usage
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    if event.get("type") == "task.created":
        validated = await validate_event(event, TaskCreatedEvent)
        if validated:
            await process_task_created(validated)
```

## Event Enrichment

Add context to events before publishing:

```python
async def publish_task_event(
    event_type: str,
    task_data: dict,
    user_id: str,
    correlation_id: str
):
    """Publish enriched task event"""

    # Enrich with metadata
    event = {
        "id": f"evt_{uuid.uuid4().hex[:12]}",
        "source": "task-service",
        "type": event_type,
        "time": datetime.utcnow().isoformat(),
        "data": task_data,
        "metadata": {
            "correlation_id": correlation_id,
            "user_id": user_id,
            "tenant_id": await get_tenant_id(user_id),
            "ip_address": request.client.host
        }
    }

    await dapr_client.publish_event(
        pubsub_name="redpanda",
        topic_name="task-events",
        data=event
    )
```

## Schema Registry

Store and version event schemas:

```python
# backend/app/utils/event_schemas.py
from typing import Dict, Type
from pydantic import BaseModel

class EventSchemaRegistry:
    """Registry for event schemas"""

    _schemas: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def register(cls, event_type: str, schema: Type[BaseModel]):
        """Register event schema"""
        cls._schemas[event_type] = schema

    @classmethod
    def get_schema(cls, event_type: str) -> Type[BaseModel]:
        """Get schema for event type"""
        return cls._schemas.get(event_type)

    @classmethod
    def validate(cls, event: dict) -> BaseModel:
        """Validate event against registered schema"""
        event_type = event.get("type")
        schema = cls.get_schema(event_type)

        if not schema:
            raise ValueError(f"No schema registered for {event_type}")

        return schema(**event)

# Register schemas
EventSchemaRegistry.register("task.created", TaskCreatedEvent)
EventSchemaRegistry.register("task.updated", TaskUpdatedEvent)
EventSchemaRegistry.register("task.completed", TaskCompletedEvent)
```

## Best Practices

### 1. Include Full State
Don't force consumers to make API calls:
```json
{
  "type": "task.completed",
  "data": {
    "task_id": "123",
    "title": "Complete Phase 8",
    "completed_at": "2026-02-01T10:30:00Z",
    "completed_by": "user_456",
    "final_status": "completed"
  }
}
```

### 2. Use Correlation IDs
Track request flow across services:
```python
correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
event["metadata"]["correlation_id"] = correlation_id
```

### 3. Include Timestamps
Always include when event occurred:
```json
{
  "time": "2026-02-01T10:30:00Z",
  "data": {
    "created_at": "2026-02-01T10:30:00Z"
  }
}
```

### 4. Make Events Immutable
Never modify published events - publish new events instead

### 5. Document Schemas
Maintain schema documentation with examples:
```yaml
# specs/011-event-driven-microservices/contracts/events.yaml
task.created:
  description: Published when a new task is created
  source: task-service
  schema:
    task_id: string (required)
    title: string (required)
    user_id: string (required)
  example:
    type: task.created
    data:
      task_id: "task_123"
      title: "Complete Phase 8"
```

## Testing Schemas

```python
import pytest
from app.utils.event_schemas import TaskCreatedEvent

def test_task_created_event_valid():
    """Test valid task created event"""
    event_data = {
        "id": "evt_123",
        "source": "task-service",
        "type": "task.created",
        "time": "2026-02-01T10:30:00Z",
        "data": {
            "task_id": "task_456",
            "title": "Test task",
            "status": "pending",
            "user_id": "user_789",
            "created_at": "2026-02-01T10:30:00Z"
        },
        "metadata": {
            "correlation_id": "req_xyz"
        }
    }

    event = TaskCreatedEvent(**event_data)
    assert event.type == "task.created"
    assert event.data.task_id == "task_456"

def test_task_created_event_missing_required():
    """Test event validation fails for missing fields"""
    event_data = {
        "type": "task.created",
        "data": {}  # Missing required fields
    }

    with pytest.raises(ValidationError):
        TaskCreatedEvent(**event_data)
```

## Next Steps

1. Read **02-pubsub-patterns.md** for publishing patterns
2. Read **04-idempotency.md** for handling duplicates
3. See **event-driven-architecture** blueprint for complete examples
