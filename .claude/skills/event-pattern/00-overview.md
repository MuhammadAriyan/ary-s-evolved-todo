# Event-Driven Architecture Overview

## What is Event-Driven Architecture?

Event-driven architecture (EDA) is a software design pattern where services communicate through events rather than direct API calls. Events represent state changes or significant occurrences in the system.

## Benefits

### 1. Loose Coupling
- Services don't need to know about each other
- Easy to add new subscribers without modifying publishers
- Independent deployment and scaling

### 2. Scalability
- Asynchronous processing
- Natural load balancing through message queues
- Horizontal scaling of consumers

### 3. Resilience
- Services can fail independently
- Message persistence ensures no data loss
- Retry mechanisms for transient failures

### 4. Auditability
- Complete event log for debugging
- Event sourcing for full history
- Compliance and audit trails

## Core Concepts

### Events
Immutable records of something that happened:
```json
{
  "id": "evt_123",
  "type": "task.created",
  "timestamp": "2026-02-01T10:30:00Z",
  "data": {
    "task_id": "task_456",
    "title": "Complete Phase 8",
    "user_id": "user_789"
  }
}
```

### Publishers
Services that emit events when state changes occur:
```python
async def create_task(task_data: dict):
    # Save to database
    task = await db.save(task_data)

    # Publish event
    await event_publisher.publish(
        topic="task-events",
        event={
            "type": "task.created",
            "data": task.dict()
        }
    )
```

### Subscribers
Services that listen for and react to events:
```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    if event["type"] == "task.created":
        await send_notification(event["data"])
```

### Topics
Logical channels for event distribution:
- `task-events`: All task-related events
- `task-updates`: Real-time sync events
- `notification-events`: Notification delivery events
- `audit-events`: Audit trail events

## Architecture Patterns

### 1. Event Notification
Notify subscribers that something happened:
```
Task Service → [task.created] → Notification Service
                              → Audit Service
                              → Search Indexer
```

### 2. Event-Carried State Transfer
Include full state in events to avoid lookups:
```json
{
  "type": "task.updated",
  "data": {
    "task_id": "123",
    "title": "Updated title",
    "status": "completed",
    "completed_at": "2026-02-01T10:30:00Z",
    "user_id": "456"
  }
}
```

### 3. Event Sourcing
Store events as the source of truth:
```
Events: [task.created, task.updated, task.completed]
Current State: Derived by replaying events
```

### 4. CQRS (Command Query Responsibility Segregation)
Separate read and write models:
```
Write: Task Service → Events → Event Store
Read: Events → Read Model Builder → Optimized Read Database
```

## Technology Stack

### Kafka (Redpanda)
- Distributed event streaming platform
- High throughput and low latency
- Persistent message storage
- Horizontal scalability

### Dapr Pub/Sub
- Abstraction over message brokers
- Pluggable components (Kafka, Redis, RabbitMQ)
- Built-in retry and dead letter queues
- CloudEvents standard support

### Redis State Store
- Idempotency tracking
- Consumer offsets
- Distributed locks
- Session management

## Best Practices

### 1. Event Schema Design
- Use CloudEvents standard format
- Include correlation IDs for tracing
- Version your event schemas
- Make events immutable

### 2. Idempotency
- Track processed event IDs in Redis
- Use unique event IDs
- Design idempotent handlers
- Handle duplicate events gracefully

### 3. Error Handling
- Log errors but don't throw exceptions
- Use dead letter queues for poison messages
- Implement exponential backoff
- Monitor error rates

### 4. Ordering
- Don't rely on global ordering
- Use partition keys for related events
- Design for eventual consistency
- Handle out-of-order events

### 5. Testing
- Unit test event handlers
- Integration test with test topics
- Contract test event schemas
- Load test with realistic volumes

## Common Pitfalls

### 1. Event Explosion
**Problem**: Too many fine-grained events
**Solution**: Group related changes into single events

### 2. Tight Coupling
**Problem**: Events contain service-specific details
**Solution**: Use domain events, not implementation details

### 3. Missing Idempotency
**Problem**: Duplicate processing on retries
**Solution**: Always implement idempotency checks

### 4. No Schema Versioning
**Problem**: Breaking changes break consumers
**Solution**: Version events and support multiple versions

### 5. Synchronous Thinking
**Problem**: Expecting immediate consistency
**Solution**: Design for eventual consistency

## Next Steps

1. Read **01-event-schemas.md** for schema design
2. Read **02-pubsub-patterns.md** for Pub/Sub patterns
3. Read **04-idempotency.md** for idempotency implementation
4. See **event-driven-architecture** blueprint for complete examples
