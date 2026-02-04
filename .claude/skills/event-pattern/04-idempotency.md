# Idempotent Event Processing

## Why Idempotency Matters

Event-driven systems provide **at-least-once delivery**, meaning events may be delivered multiple times. Idempotency ensures processing the same event multiple times produces the same result.

## Idempotency Strategies

### 1. Event ID Tracking (Recommended)

Track processed event IDs in Redis:

```python
# backend/app/services/idempotency.py
from dapr.clients import DaprClient
import logging

logger = logging.getLogger(__name__)

class IdempotencyChecker:
    """Check if event has been processed using Dapr state store"""

    def __init__(self, store_name: str = "redis-state"):
        self.store_name = store_name

    async def is_processed(self, event_id: str, ttl_seconds: int = 86400) -> bool:
        """
        Check if event has been processed

        Args:
            event_id: Unique event identifier
            ttl_seconds: Time to live for idempotency key (default 24 hours)

        Returns:
            True if event was already processed
        """
        async with DaprClient() as client:
            try:
                # Try to get existing state
                state = await client.get_state(
                    store_name=self.store_name,
                    key=f"idempotency:{event_id}"
                )

                if state.data:
                    logger.info(f"Event {event_id} already processed")
                    return True

                # Mark as processed
                await client.save_state(
                    store_name=self.store_name,
                    key=f"idempotency:{event_id}",
                    value="processed",
                    state_metadata={"ttlInSeconds": str(ttl_seconds)}
                )

                return False

            except Exception as e:
                logger.error(f"Idempotency check failed: {e}")
                # Fail open - allow processing to prevent blocking
                return False

# Usage
idempotency = IdempotencyChecker()

@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    event_id = event.get("id")

    # Check if already processed
    if await idempotency.is_processed(event_id):
        return {"success": True}

    # Process event
    await process_event(event)

    return {"success": True}
```

### 2. Natural Idempotency

Design operations to be naturally idempotent:

```python
# Idempotent: Setting a value
async def update_task_status(task_id: str, status: str):
    """Naturally idempotent - setting same value multiple times is safe"""
    await db.execute(
        "UPDATE tasks SET status = :status WHERE id = :task_id",
        {"status": status, "task_id": task_id}
    )

# NOT idempotent: Incrementing a counter
async def increment_view_count(task_id: str):
    """NOT idempotent - multiple calls produce different results"""
    await db.execute(
        "UPDATE tasks SET view_count = view_count + 1 WHERE id = :task_id",
        {"task_id": task_id}
    )

# Make it idempotent with event ID
async def increment_view_count_idempotent(task_id: str, event_id: str):
    """Idempotent version using event ID"""
    if await idempotency.is_processed(f"view:{task_id}:{event_id}"):
        return

    await db.execute(
        "UPDATE tasks SET view_count = view_count + 1 WHERE id = :task_id",
        {"task_id": task_id}
    )
```

### 3. Database Constraints

Use unique constraints to prevent duplicates:

```python
# Database schema
CREATE TABLE processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(100),
    INDEX idx_processed_at (processed_at)
);

# Idempotent processing
async def process_event_with_db(event: dict):
    """Use database constraint for idempotency"""
    event_id = event.get("id")

    try:
        # Try to insert event ID
        await db.execute(
            "INSERT INTO processed_events (event_id, event_type) VALUES (:id, :type)",
            {"id": event_id, "type": event.get("type")}
        )

        # Process event
        await process_event(event)

    except IntegrityError:
        # Event already processed
        logger.info(f"Event {event_id} already processed")
```

### 4. Optimistic Locking

Use version numbers to prevent concurrent updates:

```python
# Database schema
ALTER TABLE tasks ADD COLUMN version INTEGER DEFAULT 1;

# Optimistic locking
async def update_task_with_version(task_id: str, updates: dict, expected_version: int):
    """Update task only if version matches"""
    result = await db.execute(
        """
        UPDATE tasks
        SET title = :title,
            status = :status,
            version = version + 1
        WHERE id = :task_id AND version = :expected_version
        """,
        {
            "task_id": task_id,
            "title": updates["title"],
            "status": updates["status"],
            "expected_version": expected_version
        }
    )

    if result.rowcount == 0:
        raise ConcurrentModificationError("Task was modified by another process")

# Event handler with optimistic locking
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_update(event: dict):
    data = event.get("data")
    task_id = data["task_id"]
    version = data["version"]

    try:
        await update_task_with_version(task_id, data, version)
    except ConcurrentModificationError:
        logger.warning(f"Concurrent modification detected for task {task_id}")
        # Event already processed by another instance
```

## Idempotency Key Patterns

### Pattern 1: Event ID Only

```python
key = f"idempotency:{event_id}"
# Example: idempotency:evt_a1b2c3d4
```

**Use when**: Events are globally unique

### Pattern 2: Entity + Event ID

```python
key = f"idempotency:{entity_type}:{entity_id}:{event_id}"
# Example: idempotency:task:task_123:evt_a1b2c3d4
```

**Use when**: Need to track per-entity processing

### Pattern 3: Operation + Entity + Timestamp

```python
key = f"idempotency:{operation}:{entity_id}:{timestamp}"
# Example: idempotency:send_reminder:task_123:2026-02-01T10:30:00Z
```

**Use when**: Events don't have unique IDs

### Pattern 4: Composite Key

```python
key = f"idempotency:{user_id}:{task_id}:{action}:{date}"
# Example: idempotency:user_456:task_123:complete:2026-02-01
```

**Use when**: Need complex uniqueness constraints

## TTL Configuration

### Short TTL (1 hour)
```python
ttl_seconds = 3600  # 1 hour
```
**Use for**: High-frequency events, limited storage

### Medium TTL (24 hours)
```python
ttl_seconds = 86400  # 24 hours
```
**Use for**: Most use cases, balance between safety and storage

### Long TTL (7 days)
```python
ttl_seconds = 604800  # 7 days
```
**Use for**: Critical operations, audit requirements

### No TTL (permanent)
```python
# Store in database instead of Redis
await db.save_processed_event(event_id)
```
**Use for**: Compliance, permanent audit trail

## Testing Idempotency

### Unit Test

```python
import pytest
from app.services.idempotency import IdempotencyChecker

@pytest.mark.asyncio
async def test_idempotency_first_call():
    """First call should return False (not processed)"""
    checker = IdempotencyChecker()
    event_id = "evt_test_123"

    is_processed = await checker.is_processed(event_id)

    assert is_processed is False

@pytest.mark.asyncio
async def test_idempotency_second_call():
    """Second call should return True (already processed)"""
    checker = IdempotencyChecker()
    event_id = "evt_test_456"

    # First call
    await checker.is_processed(event_id)

    # Second call
    is_processed = await checker.is_processed(event_id)

    assert is_processed is True
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_duplicate_event_handling():
    """Test that duplicate events are handled correctly"""
    event = {
        "id": "evt_duplicate_test",
        "type": "task.created",
        "data": {"task_id": "task_789", "title": "Test"}
    }

    # Process event twice
    result1 = await handle_task_event(event)
    result2 = await handle_task_event(event)

    # Both should succeed
    assert result1["success"] is True
    assert result2["success"] is True

    # But task should only be created once
    tasks = await db.query("SELECT * FROM tasks WHERE id = 'task_789'")
    assert len(tasks) == 1
```

## Best Practices

### 1. Always Use Event IDs
```python
# Good: Use event ID from CloudEvents
event_id = event.get("id")

# Bad: Generate your own ID
event_id = str(uuid.uuid4())
```

### 2. Set Appropriate TTL
```python
# Good: Set TTL based on use case
ttl = 86400  # 24 hours for most cases

# Bad: No TTL (fills up Redis)
ttl = None
```

### 3. Handle Idempotency Check Failures
```python
# Good: Fail open to prevent blocking
try:
    if await idempotency.is_processed(event_id):
        return {"success": True}
except Exception as e:
    logger.error(f"Idempotency check failed: {e}")
    # Continue processing

# Bad: Fail closed (blocks all processing)
if await idempotency.is_processed(event_id):
    return {"success": True}
```

### 4. Log Duplicate Events
```python
# Good: Log for monitoring
if await idempotency.is_processed(event_id):
    logger.info(f"Duplicate event detected: {event_id}")
    return {"success": True}

# Bad: Silent ignore
if await idempotency.is_processed(event_id):
    return {"success": True}
```

### 5. Use Composite Keys for Complex Cases
```python
# Good: Composite key for reminder delivery
key = f"reminder:{task_id}:{scheduled_time}"

# Bad: Simple key (may not be unique enough)
key = f"reminder:{task_id}"
```

## Common Pitfalls

### 1. Not Checking Idempotency
**Problem**: Duplicate events cause duplicate processing
**Solution**: Always check idempotency before processing

### 2. Checking After Processing
**Problem**: Race condition between check and process
**Solution**: Check idempotency BEFORE processing

### 3. Using Wrong Key
**Problem**: Different events have same key
**Solution**: Use unique, descriptive keys

### 4. No TTL
**Problem**: Redis fills up with old keys
**Solution**: Always set appropriate TTL

### 5. Throwing Exceptions on Duplicates
**Problem**: Dapr retries, causing more duplicates
**Solution**: Return success for duplicate events

## Next Steps

1. Read **05-error-handling.md** for error strategies
2. Read **06-testing.md** for testing patterns
3. See **event-driven-architecture** blueprint for complete examples
