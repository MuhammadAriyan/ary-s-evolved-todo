# Dapr Integration Blueprint

## Overview

This blueprint documents the complete Dapr runtime integration for Ary's Evolved Todo application, including component configurations, service-to-service communication, and operational patterns.

## Dapr Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Backend API  │  │ WebSocket    │  │ Notification │        │
│  │              │  │ Sync Service │  │ Service      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                  │                  │                │
│         │ Dapr SDK         │ Dapr SDK         │ Dapr SDK      │
│         ▼                  ▼                  ▼                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/gRPC
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Dapr Sidecar (daprd)                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Pub/Sub    │  │ State Store  │  │   Bindings   │        │
│  │   Building   │  │   Building   │  │   Building   │        │
│  │   Block      │  │   Block      │  │   Block      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Secrets    │  │   Service    │  │Configuration │        │
│  │   Building   │  │  Invocation  │  │   Building   │        │
│  │   Block      │  │   Building   │  │   Block      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Component APIs
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Redpanda   │  │    Redis     │  │  Kubernetes  │        │
│  │   (Kafka)    │  │              │  │   Secrets    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Dapr Components Configuration

### Directory Structure

```
infrastructure/dapr/
├── pubsub-redpanda.yaml       # Kafka/Redpanda Pub/Sub
├── statestore-redis.yaml      # Redis State Store
├── bindings-cron.yaml         # Cron Bindings
├── secrets-kubernetes.yaml    # Kubernetes Secrets
├── config.yaml                # Dapr Configuration
└── subscriptions/             # Declarative subscriptions
    ├── task-events.yaml
    ├── notification-events.yaml
    └── audit-events.yaml
```

### Pub/Sub Component (Redpanda)

```yaml
# infrastructure/dapr/pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Broker configuration
    - name: brokers
      value: "redpanda-cloud:9092"

    # Consumer group (unique per service)
    - name: consumerGroup
      value: "default"

    # Authentication
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: redpanda-secret
        key: username
    - name: saslPassword
      secretKeyRef:
        name: redpanda-secret
        key: password

    # TLS configuration
    - name: enableTLS
      value: "true"

    # Retry and error handling
    - name: maxRetries
      value: "3"
    - name: retryBackoff
      value: "1s"
    - name: deadLetterTopic
      value: "dead-letter-queue"

    # Performance tuning
    - name: maxMessageBytes
      value: "1048576"  # 1MB
    - name: compressionType
      value: "snappy"
```

### State Store Component (Redis)

```yaml
# infrastructure/dapr/statestore-redis.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
  namespace: evolved-todo
spec:
  type: state.redis
  version: v1
  metadata:
    # Redis connection
    - name: redisHost
      value: "redis-master:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password

    # Database selection
    - name: redisDB
      value: "0"

    # TLS configuration
    - name: enableTLS
      value: "true"

    # Connection pool
    - name: maxRetries
      value: "3"
    - name: maxRetryBackoff
      value: "2s"
    - name: dialTimeout
      value: "5s"
    - name: poolSize
      value: "20"
    - name: minIdleConns
      value: "5"

    # Default TTL
    - name: ttlInSeconds
      value: "3600"  # 1 hour
```

### Cron Binding

```yaml
# infrastructure/dapr/bindings-cron.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: evolved-todo
spec:
  type: bindings.cron
  version: v1
  metadata:
    # Check reminders every minute
    - name: schedule
      value: "*/1 * * * *"
    - name: direction
      value: "input"
  scopes:
    - notification-service
```

### Secrets Component

```yaml
# infrastructure/dapr/secrets-kubernetes.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: evolved-todo
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: vaultName
      value: "evolved-todo"
```

### Dapr Configuration

```yaml
# infrastructure/dapr/config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: evolved-todo
spec:
  # Tracing configuration
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"

  # Metrics configuration
  metrics:
    enabled: true

  # Access control
  accessControl:
    defaultAction: deny
    trustDomain: "public"
    policies:
      - appId: backend-api
        defaultAction: allow
        trustDomain: "public"
        namespace: "evolved-todo"

  # API configuration
  api:
    allowed:
      - name: state
        version: v1.0
        protocol: http
      - name: pubsub
        version: v1.0
        protocol: http
      - name: bindings
        version: v1.0
        protocol: http
```

## Service Integration Patterns

### 1. Publishing Events

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
        """Publish event with CloudEvents format"""
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

# Usage in Task Service
event_publisher = EventPublisher()

async def create_task(task_data: dict, user_id: str):
    # Save to database
    task = await db.save(task_data)

    # Publish event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.created",
        data=task.dict(),
        source="task-service",
        user_id=user_id
    )

    return task
```

### 2. Subscribing to Events

```python
# backend/microservices/notification/main.py
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")
dapr_app = DaprApp(app)

@dapr_app.subscribe(
    pubsub="redpanda",
    topic="task-events",
    metadata={
        "rawPayload": "false",
        "maxConcurrentHandlers": "10"
    }
)
async def handle_task_event(event: dict):
    """Handle task events"""
    try:
        event_type = event.get("type")
        event_data = event.get("data")

        logger.info(f"Received {event_type} event: {event.get('id')}")

        # Check idempotency
        if await idempotency.is_processed(event["id"]):
            return {"success": True}

        # Process based on event type
        if event_type == "task.created":
            await process_task_created(event_data)
        elif event_type == "task.updated":
            await process_task_updated(event_data)

        return {"success": True}

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {"success": True}  # Always return success
```

### 3. State Management

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
        """Check if event has been processed"""
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
                return False  # Fail open
```

### 4. Cron Bindings

```python
# backend/microservices/notification/main.py
@app.post("/reminder-check")
async def check_reminders():
    """
    Called by Dapr cron binding every minute

    Dapr automatically invokes this endpoint based on cron schedule
    """
    logger.info("Checking for due reminders...")

    # Get reminders due in next minute
    due_reminders = await db.query(
        """
        SELECT * FROM scheduled_reminders
        WHERE scheduled_time <= NOW() + INTERVAL '1 minute'
        AND scheduled_time > NOW()
        """
    )

    for reminder in due_reminders:
        # Check idempotency
        key = f"reminder:{reminder.task_id}:{reminder.scheduled_time}"
        if await idempotency.is_processed(key):
            continue

        # Send notification
        await send_notification(reminder)

    return {"success": True, "processed": len(due_reminders)}
```

### 5. Service-to-Service Invocation

```python
# backend/app/services/task_service.py
from dapr.clients import DaprClient

async def get_user_preferences(user_id: str) -> dict:
    """Call user service to get preferences"""
    async with DaprClient() as client:
        response = await client.invoke_method(
            app_id="user-service",
            method_name=f"users/{user_id}/preferences",
            http_verb="GET"
        )
        return response.json()
```

## Deployment with Dapr

### Kubernetes Deployment with Dapr Annotations

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: evolved-todo
spec:
  replicas: 2
  template:
    metadata:
      annotations:
        # Enable Dapr sidecar injection
        dapr.io/enabled: "true"

        # Dapr app ID (used for service invocation)
        dapr.io/app-id: "notification-service"

        # Port your app listens on
        dapr.io/app-port: "8000"

        # Dapr configuration
        dapr.io/config: "dapr-config"

        # Log level
        dapr.io/log-level: "info"

        # Enable metrics
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"

        # Enable profiling (optional)
        dapr.io/enable-profiling: "false"
    spec:
      containers:
      - name: notification-service
        image: notification-service:latest
        ports:
        - containerPort: 8000
```

### Local Development with Dapr

```bash
# Start service with Dapr sidecar
dapr run \
  --app-id notification-service \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ./infrastructure/dapr \
  --config ./infrastructure/dapr/config.yaml \
  -- python main.py
```

## Testing Dapr Integration

### Test Pub/Sub

```bash
# Publish test event
dapr publish \
  --publish-app-id notification-service \
  --pubsub redpanda \
  --topic task-events \
  --data '{"type": "task.created", "data": {"task_id": "test_123"}}'
```

### Test State Store

```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/redis-state \
  -H "Content-Type: application/json" \
  -d '[{"key": "test", "value": "data"}]'

# Get state
curl http://localhost:3500/v1.0/state/redis-state/test
```

### Test Service Invocation

```bash
# Invoke service method
curl -X GET http://localhost:3500/v1.0/invoke/notification-service/method/health
```

## Monitoring Dapr

### Dapr Dashboard

```bash
# Install Dapr dashboard
dapr dashboard -k

# Access at http://localhost:8080
```

### Prometheus Metrics

Dapr exposes metrics at:
- `http://localhost:9090/metrics` (Dapr sidecar)

Key metrics:
- `dapr_http_server_request_count`
- `dapr_http_server_request_duration_ms`
- `dapr_component_loaded`
- `dapr_pubsub_ingress_count`
- `dapr_pubsub_egress_count`

## Troubleshooting

### Sidecar Not Injected

```bash
# Check if Dapr is installed
kubectl get pods -n dapr-system

# Verify annotations
kubectl get pod notification-service-xxx -o yaml | grep dapr.io
```

### Component Not Found

```bash
# List components
kubectl get components -n evolved-todo

# Describe component
kubectl describe component redpanda -n evolved-todo

# Check sidecar logs
kubectl logs notification-service-xxx -c daprd -n evolved-todo
```

### Pub/Sub Not Working

```bash
# Check subscription
kubectl get subscriptions -n evolved-todo

# Test publishing
dapr publish --publish-app-id test --pubsub redpanda --topic task-events --data '{}'

# Check consumer group
kafka-consumer-groups.sh --bootstrap-server redpanda:9092 --group notification-service --describe
```

## Best Practices

1. **Use Dapr SDK** - Don't call HTTP API directly
2. **Configure retries** - Set appropriate retry policies
3. **Implement idempotency** - Handle duplicate events
4. **Use secrets** - Never hardcode credentials
5. **Monitor metrics** - Track Dapr performance
6. **Test locally** - Use Dapr CLI for development
7. **Version components** - Specify component versions
8. **Scope components** - Limit access to specific services
9. **Configure timeouts** - Set appropriate timeouts
10. **Enable tracing** - Use distributed tracing

## Related Skills
- **event-pattern**: Event design patterns
- **dapr-component**: Component configuration
- **monitoring-setup**: Observability

## Related Blueprints
- **event-driven-architecture**: Event patterns
- **microservices-deployment**: Deployment strategies
