# Testing Event-Driven Systems

## Testing Strategy

### Test Pyramid for Event-Driven Systems

```
        /\
       /  \      E2E Tests (10%)
      /____\     - Full event flow
     /      \    - Multiple services
    /________\   Integration Tests (30%)
   /          \  - Event publishing/consuming
  /____________\ - Contract tests
 /              \ Unit Tests (60%)
/______________\ - Event handlers
                 - Business logic
```

## Unit Testing

### Testing Event Handlers

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.handlers.task_handler import handle_task_event

@pytest.mark.asyncio
async def test_handle_task_created_event():
    """Test task created event handler"""
    event = {
        "id": "evt_test_123",
        "type": "task.created",
        "source": "task-service",
        "data": {
            "task_id": "task_456",
            "title": "Test task",
            "user_id": "user_789"
        },
        "metadata": {
            "correlation_id": "req_xyz"
        }
    }

    # Mock dependencies
    with patch('app.services.notification_service.send_notification') as mock_send:
        mock_send.return_value = AsyncMock()

        # Call handler
        result = await handle_task_event(event)

        # Assertions
        assert result["success"] is True
        mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_handle_invalid_event():
    """Test handler with invalid event"""
    event = {
        "id": "evt_test_456",
        "type": "task.created",
        "data": {}  # Missing required fields
    }

    # Should handle gracefully
    result = await handle_task_event(event)

    assert result["success"] is True  # Returns success even on error
```

### Testing Event Publishing

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.event_publisher import EventPublisher

@pytest.mark.asyncio
async def test_publish_event():
    """Test event publishing"""
    publisher = EventPublisher()

    with patch('dapr.clients.DaprClient') as mock_dapr:
        mock_client = AsyncMock()
        mock_dapr.return_value.__aenter__.return_value = mock_client

        await publisher.publish(
            topic="task-events",
            event_type="task.created",
            data={"task_id": "123"},
            source="task-service",
            user_id="user_456"
        )

        # Verify Dapr client was called
        mock_client.publish_event.assert_called_once()
        call_args = mock_client.publish_event.call_args

        assert call_args.kwargs["pubsub_name"] == "redpanda"
        assert call_args.kwargs["topic_name"] == "task-events"
```

### Testing Idempotency

```python
import pytest
from app.services.idempotency import IdempotencyChecker

@pytest.mark.asyncio
async def test_idempotency_first_call():
    """First call should return False (not processed)"""
    checker = IdempotencyChecker()
    event_id = "evt_test_first"

    is_processed = await checker.is_processed(event_id)

    assert is_processed is False

@pytest.mark.asyncio
async def test_idempotency_duplicate_call():
    """Duplicate call should return True (already processed)"""
    checker = IdempotencyChecker()
    event_id = "evt_test_duplicate"

    # First call
    await checker.is_processed(event_id)

    # Second call (duplicate)
    is_processed = await checker.is_processed(event_id)

    assert is_processed is True
```

## Integration Testing

### Testing with Test Topics

```python
import pytest
from dapr.clients import DaprClient
import asyncio

@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_flow_end_to_end():
    """Test complete event flow from publish to consume"""

    # Publish event to test topic
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="redpanda",
            topic_name="test-task-events",
            data={
                "id": "evt_integration_test",
                "type": "task.created",
                "data": {"task_id": "test_123"}
            }
        )

    # Wait for event to be processed
    await asyncio.sleep(2)

    # Verify event was processed
    # (Check database, state store, or other side effects)
    result = await verify_event_processed("evt_integration_test")
    assert result is True
```

### Testing Event Subscriptions

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.integration
def test_dapr_subscription_endpoint():
    """Test Dapr subscription endpoint"""
    client = TestClient(app)

    # Dapr calls this endpoint to get subscriptions
    response = client.get("/dapr/subscribe")

    assert response.status_code == 200
    subscriptions = response.json()

    # Verify subscription configuration
    assert len(subscriptions) > 0
    assert any(s["topic"] == "task-events" for s in subscriptions)
```

### Testing with Docker Compose

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  redpanda:
    image: vectorized/redpanda:latest
    command:
      - redpanda start
      - --smp 1
      - --memory 1G
      - --overprovisioned
      - --node-id 0
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
    ports:
      - "9092:9092"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  test-service:
    build: .
    environment:
      - DAPR_HTTP_PORT=3500
      - KAFKA_BROKERS=redpanda:9092
      - REDIS_HOST=redis
    depends_on:
      - redpanda
      - redis
```

```bash
# Run integration tests
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/
docker-compose -f docker-compose.test.yml down
```

## Contract Testing

### Event Schema Contracts

```python
import pytest
from pydantic import ValidationError
from app.utils.event_schemas import TaskCreatedEvent

def test_task_created_event_schema():
    """Test task created event schema contract"""
    valid_event = {
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

    # Should validate successfully
    event = TaskCreatedEvent(**valid_event)
    assert event.type == "task.created"
    assert event.data.task_id == "task_456"

def test_task_created_event_missing_required_field():
    """Test schema validation fails for missing required fields"""
    invalid_event = {
        "id": "evt_123",
        "type": "task.created",
        "data": {
            "task_id": "task_456"
            # Missing required fields: title, status, user_id, created_at
        }
    }

    with pytest.raises(ValidationError):
        TaskCreatedEvent(**invalid_event)
```

### Consumer Contract Tests

```python
import pytest
from app.handlers.notification_handler import handle_task_event

@pytest.mark.contract
@pytest.mark.asyncio
async def test_notification_handler_contract():
    """Test notification handler accepts expected event format"""

    # Define expected event contract
    event = {
        "id": "evt_contract_test",
        "type": "task.created",
        "source": "task-service",
        "data": {
            "task_id": "task_123",
            "title": "Contract test",
            "user_id": "user_456"
        },
        "metadata": {
            "correlation_id": "req_xyz"
        }
    }

    # Handler should process without errors
    result = await handle_task_event(event)
    assert result["success"] is True
```

## Load Testing

### Event Publishing Load Test

```python
import asyncio
import time
from dapr.clients import DaprClient

async def publish_event(client: DaprClient, event_id: int):
    """Publish single event"""
    await client.publish_event(
        pubsub_name="redpanda",
        topic_name="load-test-events",
        data={
            "id": f"evt_load_{event_id}",
            "type": "task.created",
            "data": {"task_id": f"task_{event_id}"}
        }
    )

async def load_test_publishing(num_events: int = 1000):
    """Load test event publishing"""
    start_time = time.time()

    async with DaprClient() as client:
        tasks = [
            publish_event(client, i)
            for i in range(num_events)
        ]
        await asyncio.gather(*tasks)

    duration = time.time() - start_time
    throughput = num_events / duration

    print(f"Published {num_events} events in {duration:.2f}s")
    print(f"Throughput: {throughput:.2f} events/second")

    assert throughput > 100  # Minimum 100 events/second

# Run load test
asyncio.run(load_test_publishing(1000))
```

### Event Processing Load Test

```python
import pytest
from locust import HttpUser, task, between

class EventConsumerLoadTest(HttpUser):
    """Load test for event consumer"""
    wait_time = between(0.1, 0.5)

    @task
    def publish_event(self):
        """Simulate event publishing"""
        self.client.post("/events/task", json={
            "id": f"evt_load_{self.environment.runner.user_count}",
            "type": "task.created",
            "data": {"task_id": "test_123"}
        })

# Run with: locust -f load_test.py --host=http://localhost:8000
```

## Test Fixtures

### Event Fixtures

```python
import pytest
from datetime import datetime

@pytest.fixture
def task_created_event():
    """Fixture for task created event"""
    return {
        "id": "evt_fixture_123",
        "source": "task-service",
        "type": "task.created",
        "time": datetime.utcnow().isoformat(),
        "data": {
            "task_id": "task_456",
            "title": "Test task",
            "status": "pending",
            "user_id": "user_789",
            "created_at": datetime.utcnow().isoformat()
        },
        "metadata": {
            "correlation_id": "req_test"
        }
    }

@pytest.fixture
def task_updated_event():
    """Fixture for task updated event"""
    return {
        "id": "evt_fixture_456",
        "source": "task-service",
        "type": "task.updated",
        "time": datetime.utcnow().isoformat(),
        "data": {
            "task_id": "task_456",
            "changes": {"status": {"old": "pending", "new": "completed"}},
            "updated_fields": ["status"],
            "user_id": "user_789",
            "updated_at": datetime.utcnow().isoformat()
        },
        "metadata": {
            "correlation_id": "req_test"
        }
    }

# Usage
@pytest.mark.asyncio
async def test_with_fixture(task_created_event):
    """Test using event fixture"""
    result = await handle_task_event(task_created_event)
    assert result["success"] is True
```

### Mock Dapr Client

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_dapr_client():
    """Mock Dapr client for testing"""
    client = AsyncMock()
    client.publish_event = AsyncMock()
    client.get_state = AsyncMock()
    client.save_state = AsyncMock()
    return client

# Usage
@pytest.mark.asyncio
async def test_with_mock_dapr(mock_dapr_client):
    """Test with mocked Dapr client"""
    with patch('dapr.clients.DaprClient') as mock_dapr:
        mock_dapr.return_value.__aenter__.return_value = mock_dapr_client

        await publish_event("task-events", {"test": "data"})

        mock_dapr_client.publish_event.assert_called_once()
```

## Best Practices

### 1. Test Event Handlers in Isolation
```python
# ✓ Good: Mock dependencies
with patch('app.services.notification_service') as mock:
    await handle_task_event(event)

# ❌ Bad: Test with real dependencies
await handle_task_event(event)  # Calls real notification service
```

### 2. Use Test Topics
```python
# ✓ Good: Separate test topics
topic = "test-task-events" if is_test else "task-events"

# ❌ Bad: Use production topics in tests
topic = "task-events"
```

### 3. Test Idempotency
```python
# ✓ Good: Test duplicate handling
await handle_event(event)
await handle_event(event)  # Should be idempotent

# ❌ Bad: Only test happy path
await handle_event(event)
```

### 4. Test Error Handling
```python
# ✓ Good: Test error scenarios
with patch('external_service.call', side_effect=Exception):
    result = await handle_event(event)
    assert result["success"] is True  # Should handle gracefully

# ❌ Bad: Only test success cases
```

### 5. Use Contract Tests
```python
# ✓ Good: Verify event schema contracts
event = TaskCreatedEvent(**event_data)

# ❌ Bad: No schema validation
event = event_data  # Just use dict
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Test Event-Driven Services

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redpanda:
        image: vectorized/redpanda:latest
        ports:
          - 9092:9092

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov

      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          KAFKA_BROKERS: localhost:9092
          REDIS_HOST: localhost

      - name: Run contract tests
        run: pytest tests/contract/ -v
```

## Next Steps

1. Review **event-driven-architecture** blueprint for complete examples
2. See **monitoring-setup** skill for observability
3. Check **microservice-creator** agent for service templates
