# Pub/Sub Component Configuration

## Kafka/Redpanda Pub/Sub Component

### Basic Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Broker addresses
    - name: brokers
      value: "redpanda-cloud:9092"

    # Consumer group (unique per service)
    - name: consumerGroup
      value: "notification-service"

    # Authentication (if required)
    - name: authType
      value: "password"
    - name: saslUsername
      value: "admin"
    - name: saslPassword
      secretKeyRef:
        name: redpanda-secret
        key: password

    # TLS configuration
    - name: enableTLS
      value: "true"
    - name: skipVerify
      value: "false"
```

### Advanced Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-cloud:9092"
    - name: consumerGroup
      value: "notification-service"

    # Retry configuration
    - name: maxRetries
      value: "3"
    - name: retryBackoff
      value: "1s"

    # Dead letter queue
    - name: deadLetterTopic
      value: "dead-letter-queue"

    # Consumer configuration
    - name: sessionTimeout
      value: "30s"
    - name: heartbeatInterval
      value: "3s"
    - name: maxPollInterval
      value: "300s"

    # Producer configuration
    - name: maxMessageBytes
      value: "1048576"  # 1MB
    - name: compressionType
      value: "snappy"

    # Offset management
    - name: initialOffset
      value: "newest"  # or "oldest"
```

### Multiple Consumer Groups

```yaml
# Service 1: Notification Service
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-cloud:9092"
    - name: consumerGroup
      value: "notification-service"
  scopes:
    - notification-service

---
# Service 2: Audit Service
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-cloud:9092"
    - name: consumerGroup
      value: "audit-service"
  scopes:
    - audit-service
```

## Local Development Configuration

```yaml
# infrastructure/dapr/pubsub-local.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "localhost:9092"
    - name: consumerGroup
      value: "local-dev"
    - name: authRequired
      value: "false"
```

## Production Configuration

```yaml
# infrastructure/dapr/pubsub-production.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redpanda
  namespace: evolved-todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-prod.cloud:9092"
    - name: consumerGroup
      value: "notification-service"

    # Authentication
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: redpanda-prod-secret
        key: username
    - name: saslPassword
      secretKeyRef:
        name: redpanda-prod-secret
        key: password

    # TLS
    - name: enableTLS
      value: "true"
    - name: caCert
      secretKeyRef:
        name: redpanda-prod-secret
        key: ca-cert

    # Performance tuning
    - name: maxMessageBytes
      value: "2097152"  # 2MB
    - name: compressionType
      value: "snappy"
    - name: maxRetries
      value: "5"
```

## Topic Configuration

### Programmatic Subscription

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
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
    return {"success": True}
```

### Declarative Subscription

```yaml
# infrastructure/dapr/subscriptions/task-events.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
  namespace: evolved-todo
spec:
  pubsubname: redpanda
  topic: task-events
  route: /events/task
  metadata:
    rawPayload: "false"
    maxConcurrentHandlers: "10"
  scopes:
    - notification-service
    - audit-service
```

## Message Routing

### Route by Event Type

```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-routing
spec:
  pubsubname: redpanda
  topic: task-events
  routes:
    rules:
      - match: event.type == "task.created"
        path: /events/task/created
      - match: event.type == "task.updated"
        path: /events/task/updated
      - match: event.type == "task.completed"
        path: /events/task/completed
    default: /events/task/default
```

### Route by User

```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: premium-user-events
spec:
  pubsubname: redpanda
  topic: task-events
  routes:
    rules:
      - match: event.data.user_tier == "premium"
        path: /events/premium
    default: /events/standard
```

## Testing

### Test Pub/Sub Component

```bash
# Publish test event
dapr publish \
  --publish-app-id notification-service \
  --pubsub redpanda \
  --topic task-events \
  --data '{"type": "task.created", "data": {"task_id": "test_123"}}'

# Check component status
kubectl get component redpanda -n evolved-todo -o yaml
```

### Verify Subscription

```bash
# List subscriptions
kubectl get subscriptions -n evolved-todo

# Check service logs
kubectl logs -n evolved-todo -l app=notification-service -c daprd
```

## Troubleshooting

### Connection Issues

```bash
# Check broker connectivity
kubectl exec -it notification-service -c daprd -- \
  curl http://localhost:3500/v1.0/metadata

# Verify component configuration
kubectl describe component redpanda -n evolved-todo
```

### Consumer Lag

```bash
# Check consumer group lag
kafka-consumer-groups.sh \
  --bootstrap-server redpanda-cloud:9092 \
  --group notification-service \
  --describe
```

### Message Not Delivered

```bash
# Check topic exists
kafka-topics.sh \
  --bootstrap-server redpanda-cloud:9092 \
  --list

# Check subscription route
kubectl get subscription task-events-subscription -o yaml
```

## Best Practices

1. **Use separate consumer groups per service**
2. **Configure dead letter queues for failed messages**
3. **Set appropriate retry limits and backoff**
4. **Use secrets for credentials**
5. **Enable TLS in production**
6. **Monitor consumer lag**
7. **Configure appropriate timeouts**
8. **Use message compression for large payloads**

## Next Steps

1. Read **02-statestore.md** for State Store configuration
2. Read **03-bindings.md** for Bindings configuration
3. See **event-pattern** skill for event design patterns
