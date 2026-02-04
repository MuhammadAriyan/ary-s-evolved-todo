# Error Handling in Event-Driven Systems

## Error Handling Principles

### 1. Never Throw Exceptions in Event Handlers

```python
# BAD: Throwing exceptions causes infinite retries
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    result = await process_event(event)
    if not result:
        raise Exception("Processing failed")  # ❌ Don't do this!

# GOOD: Log errors and return success
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await process_event(event)
    except Exception as e:
        logger.error(f"Error processing event {event['id']}: {e}")
        # Store in dead letter queue or database for investigation
        await store_failed_event(event, str(e))

    return {"success": True}  # ✓ Always return success
```

### 2. Categorize Errors

```python
class EventProcessingError(Exception):
    """Base class for event processing errors"""
    pass

class TransientError(EventProcessingError):
    """Temporary error that may succeed on retry"""
    pass

class PermanentError(EventProcessingError):
    """Permanent error that won't succeed on retry"""
    pass

class ValidationError(PermanentError):
    """Event validation failed"""
    pass

# Error handling
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await process_event(event)
    except ValidationError as e:
        # Permanent error - don't retry
        logger.error(f"Validation failed: {e}")
        await store_in_dead_letter_queue(event, "validation_failed")
    except TransientError as e:
        # Transient error - may retry
        logger.warning(f"Transient error: {e}")
        # Let Dapr retry mechanism handle it
        raise
    except Exception as e:
        # Unknown error - log and investigate
        logger.error(f"Unknown error: {e}")
        await store_failed_event(event, str(e))

    return {"success": True}
```

## Error Handling Patterns

### Pattern 1: Dead Letter Queue

```python
# backend/app/services/dead_letter_queue.py
from dapr.clients import DaprClient
import logging

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    """Store failed events for manual investigation"""

    async def store(self, event: dict, error: str, retry_count: int = 0):
        """
        Store failed event in dead letter queue

        Args:
            event: Original event that failed
            error: Error message
            retry_count: Number of retry attempts
        """
        failed_event = {
            "original_event": event,
            "error": error,
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat()
        }

        async with DaprClient() as client:
            # Publish to dead letter topic
            await client.publish_event(
                pubsub_name="redpanda",
                topic_name="dead-letter-queue",
                data=failed_event
            )

        logger.error(f"Event {event['id']} moved to DLQ: {error}")

# Usage
dlq = DeadLetterQueue()

@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await process_event(event)
    except Exception as e:
        await dlq.store(event, str(e))

    return {"success": True}
```

### Pattern 2: Retry with Exponential Backoff

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> T:
    """
    Retry function with exponential backoff

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                break

            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                f"Retrying in {delay}s..."
            )

            await asyncio.sleep(delay)

    raise last_exception

# Usage
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    try:
        await retry_with_backoff(
            lambda: send_notification(event),
            max_retries=3,
            base_delay=1.0
        )
    except Exception as e:
        logger.error(f"Failed after retries: {e}")
        await dlq.store(event, str(e))

    return {"success": True}
```

### Pattern 3: Circuit Breaker

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Circuit breaker for external service calls

    Prevents cascading failures by stopping calls to failing services
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    async def call(self, func: Callable) -> any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Async function to execute

        Returns:
            Result from function

        Raises:
            CircuitBreakerOpenError if circuit is open
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func()

            # Success handling
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    logger.info("Circuit breaker transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.failure_threshold:
                logger.warning("Circuit breaker transitioning to OPEN")
                self.state = CircuitState.OPEN

            raise

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Usage
email_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

@dapr_app.subscribe(pubsub="redpanda", topic="notification-events")
async def handle_notification_event(event: dict):
    try:
        await email_circuit_breaker.call(
            lambda: send_email(event["data"])
        )
    except CircuitBreakerOpenError:
        logger.warning("Email service circuit breaker is open")
        # Use fallback notification method
        await send_in_app_notification(event["data"])
    except Exception as e:
        logger.error(f"Notification failed: {e}")

    return {"success": True}
```

### Pattern 4: Graceful Degradation

```python
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    """Handle task event with graceful degradation"""

    # Primary processing
    try:
        await process_with_external_service(event)
    except Exception as e:
        logger.warning(f"Primary processing failed: {e}")

        # Fallback to local processing
        try:
            await process_locally(event)
        except Exception as e2:
            logger.error(f"Fallback processing failed: {e2}")

            # Last resort: store for manual processing
            await store_for_manual_processing(event)

    return {"success": True}
```

## Monitoring and Alerting

### Error Metrics

```python
from prometheus_client import Counter, Histogram

# Define metrics
event_processing_errors = Counter(
    'event_processing_errors_total',
    'Total number of event processing errors',
    ['event_type', 'error_type']
)

event_processing_duration = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration',
    ['event_type']
)

# Track errors
@dapr_app.subscribe(pubsub="redpanda", topic="task-events")
async def handle_task_event(event: dict):
    event_type = event.get("type")

    with event_processing_duration.labels(event_type=event_type).time():
        try:
            await process_event(event)
        except ValidationError as e:
            event_processing_errors.labels(
                event_type=event_type,
                error_type="validation"
            ).inc()
            logger.error(f"Validation error: {e}")
        except Exception as e:
            event_processing_errors.labels(
                event_type=event_type,
                error_type="unknown"
            ).inc()
            logger.error(f"Unknown error: {e}")

    return {"success": True}
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured JSON logging for event processing"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def log_event_processing(
        self,
        event_id: str,
        event_type: str,
        status: str,
        duration_ms: float,
        error: str = None
    ):
        """Log event processing with structured format"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event_id": event_id,
            "event_type": event_type,
            "status": status,
            "duration_ms": duration_ms,
            "error": error
        }

        if status == "success":
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.error(json.dumps(log_entry))

# Usage
logger = StructuredLogger("notification-service")

@dapr_app.subscribe(pubsub="redpanda", topic="notification-events")
async def handle_notification_event(event: dict):
    start_time = datetime.utcnow()
    event_id = event.get("id")
    event_type = event.get("type")

    try:
        await process_event(event)
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.log_event_processing(
            event_id=event_id,
            event_type=event_type,
            status="success",
            duration_ms=duration
        )

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.log_event_processing(
            event_id=event_id,
            event_type=event_type,
            status="error",
            duration_ms=duration,
            error=str(e)
        )

    return {"success": True}
```

## Best Practices

### 1. Always Return Success
```python
# ✓ Good: Return success to acknowledge message
return {"success": True}

# ❌ Bad: Throw exception (causes infinite retries)
raise Exception("Processing failed")
```

### 2. Log All Errors
```python
# ✓ Good: Structured logging with context
logger.error(f"Event processing failed", extra={
    "event_id": event["id"],
    "event_type": event["type"],
    "error": str(e)
})

# ❌ Bad: Silent failure
pass
```

### 3. Use Dead Letter Queues
```python
# ✓ Good: Store failed events for investigation
await dlq.store(event, str(e))

# ❌ Bad: Discard failed events
pass
```

### 4. Implement Circuit Breakers
```python
# ✓ Good: Protect against cascading failures
await circuit_breaker.call(lambda: external_service_call())

# ❌ Bad: Keep calling failing service
await external_service_call()
```

### 5. Monitor Error Rates
```python
# ✓ Good: Track metrics for alerting
event_processing_errors.labels(event_type=event_type).inc()

# ❌ Bad: No visibility into errors
pass
```

## Common Pitfalls

### 1. Throwing Exceptions
**Problem**: Causes infinite retries and consumer lag
**Solution**: Catch all exceptions and return success

### 2. No Error Categorization
**Problem**: Can't distinguish transient from permanent errors
**Solution**: Use custom exception classes

### 3. No Dead Letter Queue
**Problem**: Failed events are lost
**Solution**: Store failed events for investigation

### 4. No Circuit Breaker
**Problem**: Cascading failures across services
**Solution**: Implement circuit breaker for external calls

### 5. Poor Logging
**Problem**: Can't debug production issues
**Solution**: Use structured logging with correlation IDs

## Next Steps

1. Read **06-testing.md** for testing strategies
2. See **event-driven-architecture** blueprint for complete examples
3. Review monitoring-setup skill for observability
