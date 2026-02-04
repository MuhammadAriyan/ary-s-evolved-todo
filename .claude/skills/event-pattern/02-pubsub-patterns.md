# Pub/Sub Patterns with Dapr

## Publishing Events

### Basic Publishing

```python
from dapr.clients import DaprClient
import json

async def publish_event(topic: str, event_data: dict):
    """Publish event to Dapr Pub/Sub"""
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="redpanda",
            topic_name=topic,
            data=json.dumps(event_data),
            data_content_type="application/json"
        )
```

### Event Publisher Service

```python
# backend/app/services/event_publisher.py
from dapr.clients import DaprClient
from typing import Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class EventPublisher:
    """Centralized event publishing service"""

    def __init__(self, pubsub_name: str = "redpanda"):
        self.pubsub_name = pubsub_name

    async def publish(
        self,
        topic: str,
        event_type: str,
        data: dict,
        source: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Publish event with CloudEvents format

        Args:
            topic: Kafka topic name
            event_type: Event type (e.g., "task.created")
            data: Event payload
            source: Service name
            correlation_id: Request correlation ID
            user_id: User who triggered event
        """
        event = {
            "id": f"evt_{uuid.uuid4().hex[:12]}",
            "source": source,
            "type": event_type,
            "time": datetime.utcnow().isoformat(),
            "data": data,
            "metadata": {
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "user_id": user_id
            }
        }

        try:
            async with DaprClient() as client:
                await client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=event,
                    data_content_type="application/json"
                )

            logger.info(f"Published event {event['id']} to {topic}")

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise

# Usage
event_publisher = EventPublisher()

await event_publisher.publish(
    topic="task-events",
    event_type="task.created",
    data={"task_id": "123", "title": "New task"},
    source="task-service",
    user_id="user_456"
)
```

## Subscribing to Events

### Declarative Subscription

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    """
    Handle task events from Kafka

    Dapr automatically:
    - Deserializes JSON
    - Handles retries
    - Manages consumer offsets
    - Provides at-least-once delivery
    """
    event_type = event.get("type")
    event_data = event.get("data")

    logger.info(f"Received {event_type} event: {event.get('id')}")

    if event_type == "task.created":
        await process_task_created(event_data)
    elif event_type == "task.updated":
        await process_task_updated(event_data)
    elif event_type == "task.completed":
        await process_task_completed(event_data)

    return {"success": True}
```

### Programmatic Subscription

```yaml
# infrastructure/dapr/subscriptions.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: redpanda
  topic: task-events
  route: /events/task
  metadata:
    consumerGroup: notification-service
```

## Topic Design

### Topic Naming Convention

```
<domain>-<entity>-<purpose>

Examples:
- task-events: All task events
- task-updates: Real-time sync events
- notification-events: Notification delivery
- audit-events: Audit trail
```

### Topic Organization

**Option 1: Single Topic per Entity**
```
task-events:
  - task.created
  - task.updated
  - task.completed
  - task.deleted
```

**Option 2: Topic per Event Type**
```
task-created-events
task-updated-events
task-completed-events
```

**Recommendation**: Use single topic per entity for simplicity and ordering guarantees.

### Partitioning Strategy

```python
# Partition by user_id for ordering
await client.publish_event(
    pubsub_name="redpanda",
    topic_name="task-events",
    data=event,
    metadata={
        "partitionKey": event["data"]["user_id"]
    }
)
```

## Consumer Groups

### Multiple Consumers

```yaml
# Service 1: Notification Service
metadata:
  consumerGroup: notification-service

# Service 2: Audit Service
metadata:
  consumerGroup: audit-service

# Service 3: Search Indexer
metadata:
  consumerGroup: search-indexer
```

Each consumer group receives all events independently.

### Load Balancing

```yaml
# Multiple instances of same service
metadata:
  consumerGroup: notification-service
  # Dapr automatically load balances across instances
```

## Message Filtering

### Filter by Event Type

```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    event_type = event.get("type")

    # Filter events
    if event_type not in ["task.created", "task.updated"]:
        return {"success": True}  # Ignore other events

    await process_event(event)
```

### Filter by User

```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    user_id = event.get("metadata", {}).get("user_id")

    # Only process events for specific users
    if not await is_premium_user(user_id):
        return {"success": True}

    await process_premium_feature(event)
```

## Dead Letter Queues

### Configuration

```yaml
# infrastructure/dapr/pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-cloud:9092"
    - name: consumerGroup
      value: "default"
    - name: maxRetries
      value: "3"
    - name: deadLetterTopic
      value: "dead-letter-queue"
```

### Handling Failed Events

```python
@dapr_app.subscribe(pubsub="redpanda", topic="dead-letter-queue")
async def handle_failed_events(event: dict):
    """Process events that failed after max retries"""
    logger.error(f"Event failed after retries: {event}")

    # Store in database for manual review
    await db.save_failed_event(event)

    # Alert operations team
    await send_alert(f"Event processing failed: {event['id']}")

    return {"success": True}
```

## Retry Strategies

### Exponential Backoff

```python
import asyncio
from typing import Callable

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s")
            await asyncio.sleep(delay)

# Usage
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    await retry_with_backoff(
        lambda: process_event(event),
        max_retries=3
    )
```

### Circuit Breaker

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker for external service calls"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable):
        if self.state == "open":
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func()
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.utcnow()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise

# Usage
circuit_breaker = CircuitBreaker()

@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await circuit_breaker.call(
            lambda: send_email_notification(event)
        )
    except Exception as e:
        logger.error(f"Circuit breaker prevented call: {e}")
```

## Performance Optimization

### Batch Processing

```python
from asyncio import Queue, create_task
from typing import List

class BatchProcessor:
    """Process events in batches for efficiency"""

    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue: Queue = Queue()
        self.running = False

    async def start(self):
        """Start batch processing"""
        self.running = True
        create_task(self._process_batches())

    async def add_event(self, event: dict):
        """Add event to batch queue"""
        await self.queue.put(event)

    async def _process_batches(self):
        """Process events in batches"""
        batch: List[dict] = []

        while self.running:
            try:
                # Wait for event or timeout
                event = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=self.flush_interval
                )
                batch.append(event)

                # Process when batch is full
                if len(batch) >= self.batch_size:
                    await self._flush_batch(batch)
                    batch = []

            except asyncio.TimeoutError:
                # Flush on timeout
                if batch:
                    await self._flush_batch(batch)
                    batch = []

    async def _flush_batch(self, batch: List[dict]):
        """Process batch of events"""
        logger.info(f"Processing batch of {len(batch)} events")
        await process_events_batch(batch)

# Usage
batch_processor = BatchProcessor(batch_size=100, flush_interval=5.0)
await batch_processor.start()

@dapr_app.subscribe(pubsub="redpanda", topic="audit-events")
async def handle_audit_event(event: dict):
    await batch_processor.add_event(event)
    return {"success": True}
```

## Best Practices

1. **Always return success**: Return `{"success": True}` to acknowledge message
2. **Log errors**: Log but don't throw exceptions to prevent infinite retries
3. **Use correlation IDs**: Track events across services
4. **Implement idempotency**: Handle duplicate events gracefully
5. **Monitor consumer lag**: Alert when consumers fall behind
6. **Use dead letter queues**: Capture failed events for investigation
7. **Partition strategically**: Use partition keys for ordering
8. **Test with realistic volumes**: Load test with production-like traffic

## Next Steps

1. Read **04-idempotency.md** for handling duplicates
2. Read **05-error-handling.md** for error strategies
3. See **event-driven-architecture** blueprint for complete examples
