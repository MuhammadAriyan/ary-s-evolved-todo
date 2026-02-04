# Event-Driven Architecture Blueprint

## Overview

This blueprint documents the complete event-driven architecture for Ary's Evolved Todo application, including event schemas, Pub/Sub patterns, microservices communication, and operational patterns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Task UI      │  │ WebSocket    │  │ Notifications│        │
│  │              │  │ Client       │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Task Service │  │ Auth         │  │ Search       │        │
│  │              │  │ Middleware   │  │ Service      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                                                       │
│         │ Publish Events                                       │
│         ▼                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Dapr Pub/Sub
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Redpanda (Kafka-compatible)                        │
│                                                                 │
│  Topics:                                                        │
│  • task-events        (all task operations)                    │
│  • task-updates       (real-time sync)                         │
│  • notification-events (reminder delivery)                     │
│  • audit-events       (audit trail)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Subscribe
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Event-Driven Microservices                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ WebSocket    │  │ Notification │  │ Recurring    │        │
│  │ Sync Service │  │ Service      │  │ Task Service │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ Audit        │                                              │
│  │ Service      │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ State/Data
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ PostgreSQL   │  │ Redis        │                           │
│  │ (Neon)       │  │ (State Store)│                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Event Schemas

### Task Events

#### task.created
```json
{
  "id": "evt_a1b2c3d4",
  "source": "task-service",
  "type": "task.created",
  "time": "2026-02-01T10:30:00Z",
  "data": {
    "task_id": "task_123",
    "title": "Complete Phase 8",
    "description": "Implement reusable intelligence",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-02-02T18:00:00Z",
    "user_id": "user_456",
    "created_at": "2026-02-01T10:30:00Z"
  },
  "metadata": {
    "correlation_id": "req_xyz789",
    "user_id": "user_456"
  }
}
```

#### task.updated
```json
{
  "id": "evt_b2c3d4e5",
  "source": "task-service",
  "type": "task.updated",
  "time": "2026-02-01T11:00:00Z",
  "data": {
    "task_id": "task_123",
    "changes": {
      "status": {"old": "pending", "new": "in_progress"}
    },
    "updated_fields": ["status"],
    "user_id": "user_456",
    "updated_at": "2026-02-01T11:00:00Z"
  },
  "metadata": {
    "correlation_id": "req_abc123",
    "user_id": "user_456"
  }
}
```

#### task.completed
```json
{
  "id": "evt_c3d4e5f6",
  "source": "task-service",
  "type": "task.completed",
  "time": "2026-02-01T15:00:00Z",
  "data": {
    "task_id": "task_123",
    "title": "Complete Phase 8",
    "completed_at": "2026-02-01T15:00:00Z",
    "completed_by": "user_456",
    "recurring_pattern": "0 9 * * 1-5"  # If recurring
  },
  "metadata": {
    "correlation_id": "req_def456",
    "user_id": "user_456"
  }
}
```

## Microservices

### 1. WebSocket Sync Service

**Purpose**: Real-time task synchronization across devices

**Subscribes to**: `task-updates` topic

**Event Types**:
- `task.created`
- `task.updated`
- `task.deleted`

**Flow**:
1. Task Service publishes event to `task-updates`
2. WebSocket Sync Service receives event
3. Service broadcasts to connected WebSocket clients
4. Frontend updates UI in real-time

**Implementation**:
```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-updates")
async def handle_task_update(event: dict):
    # Check idempotency
    if await idempotency.is_processed(event["id"]):
        return {"success": True}

    # Get user connections from Redis
    user_id = event["data"]["user_id"]
    connections = await get_user_connections(user_id)

    # Broadcast to all user connections
    for connection_id in connections:
        await websocket_manager.send(connection_id, event)

    return {"success": True}
```

### 2. Notification Service

**Purpose**: Deliver time-based reminders

**Subscribes to**: Cron binding (every minute)

**Event Types Published**:
- `notification.sent`
- `notification.failed`

**Flow**:
1. Cron binding triggers service every minute
2. Service queries database for due reminders
3. Sends notifications via email/in-app channels
4. Publishes `notification.sent` event
5. Uses idempotency to prevent duplicates

**Implementation**:
```python
@app.post("/reminder-check")
async def check_reminders():
    # Get reminders due in next minute
    due_reminders = await db.query(
        "SELECT * FROM scheduled_reminders WHERE scheduled_time <= NOW() + INTERVAL '1 minute'"
    )

    for reminder in due_reminders:
        # Check idempotency
        key = f"reminder:{reminder.task_id}:{reminder.scheduled_time}"
        if await idempotency.is_processed(key):
            continue

        # Send notification
        await send_notification(reminder)

        # Publish event
        await event_publisher.publish(
            topic="notification-events",
            event_type="notification.sent",
            data={"reminder_id": reminder.id, "task_id": reminder.task_id}
        )

    return {"success": True}
```

### 3. Recurring Task Service

**Purpose**: Generate recurring task instances

**Subscribes to**: `task-events` topic

**Event Types**:
- `task.completed` (with recurring_pattern)

**Flow**:
1. User completes recurring task
2. Task Service publishes `task.completed` event
3. Recurring Task Service receives event
4. Calculates next occurrence using croniter
5. Creates new task instance
6. Publishes `task.created` event

**Implementation**:
```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    if event["type"] != "task.completed":
        return {"success": True}

    data = event["data"]
    recurring_pattern = data.get("recurring_pattern")

    if not recurring_pattern:
        return {"success": True}

    # Check idempotency
    key = f"recurring:{data['task_id']}:{data['completed_at']}"
    if await idempotency.is_processed(key):
        return {"success": True}

    # Calculate next occurrence
    next_occurrence = calculate_next_occurrence(recurring_pattern)

    # Create new task instance
    new_task = await create_task_instance(data, next_occurrence)

    # Publish task.created event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.created",
        data=new_task
    )

    return {"success": True}
```

### 4. Audit Service

**Purpose**: Maintain complete audit trail

**Subscribes to**: `task-events` topic (all events)

**Flow**:
1. Any task operation publishes event
2. Audit Service receives all events
3. Persists to audit_logs table
4. Batches writes for efficiency

**Implementation**:
```python
batch_processor = BatchProcessor(batch_size=100, flush_interval=5.0)

@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    # Add to batch queue
    await batch_processor.add_event(event)
    return {"success": True}

async def process_batch(events: list):
    """Batch insert audit logs"""
    await db.execute_many(
        "INSERT INTO audit_logs (event_id, event_type, event_data, created_at) VALUES (?, ?, ?, ?)",
        [(e["id"], e["type"], e["data"], e["time"]) for e in events]
    )
```

## Operational Patterns

### Idempotency

All event handlers implement idempotency using Redis:

```python
async def is_processed(event_id: str) -> bool:
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="redis-state",
            key=f"idempotency:{event_id}"
        )

        if state.data:
            return True

        await client.save_state(
            store_name="redis-state",
            key=f"idempotency:{event_id}",
            value="processed",
            state_metadata={"ttlInSeconds": "86400"}
        )

        return False
```

### Error Handling

All handlers return success and log errors:

```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await process_event(event)
    except Exception as e:
        logger.error(f"Error processing event {event['id']}: {e}")
        await store_in_dead_letter_queue(event, str(e))

    return {"success": True}  # Always return success
```

### Monitoring

All services expose Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

event_processing_total = Counter(
    'event_processing_total',
    'Total events processed',
    ['event_type', 'status']
)

event_processing_duration = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration',
    ['event_type']
)
```

## Testing Strategy

### Unit Tests
- Test event handlers in isolation
- Mock Dapr client
- Verify idempotency logic

### Integration Tests
- Test with real Kafka/Redpanda
- Verify end-to-end event flow
- Test error scenarios

### Contract Tests
- Validate event schemas
- Ensure backward compatibility
- Test schema versioning

## Deployment

All microservices deployed with:
- Dapr sidecar annotations
- Resource limits
- Health checks
- Auto-scaling
- Monitoring

See **microservices-deployment** blueprint for details.

## Related Skills
- **event-pattern**: Event design patterns
- **dapr-component**: Dapr configuration
- **monitoring-setup**: Observability

## Related Agents
- **microservice-creator**: Generate new services
