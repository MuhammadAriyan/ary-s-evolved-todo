---
name: event-pattern
description: Event-driven architecture patterns with Kafka, Dapr Pub/Sub, and event schemas. Use when implementing event-driven communication, designing event schemas, or setting up Pub/Sub patterns.
---

# Event Pattern Skill

Comprehensive guide for implementing event-driven architecture patterns with Dapr and Kafka.

## Included Guides

1. **00-overview.md** - Event-driven architecture overview
2. **01-event-schemas.md** - Event schema design and validation
3. **02-pubsub-patterns.md** - Pub/Sub patterns and best practices
4. **03-event-sourcing.md** - Event sourcing implementation
5. **04-idempotency.md** - Idempotent event processing
6. **05-error-handling.md** - Error handling and retry strategies
7. **06-testing.md** - Testing event-driven systems

## Quick Reference

### Event Schema Structure
```json
{
  "id": "uuid",
  "type": "task.created",
  "source": "task-service",
  "timestamp": "2026-02-01T00:00:00Z",
  "data": { ... },
  "metadata": {
    "correlation_id": "uuid",
    "user_id": "uuid"
  }
}
```

### Dapr Pub/Sub Subscription
```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    # Process event with idempotency
    pass
```

### Common Patterns
- **Event Notification**: Notify subscribers of state changes
- **Event-Carried State Transfer**: Include full state in events
- **Event Sourcing**: Store events as source of truth
- **CQRS**: Separate read and write models
