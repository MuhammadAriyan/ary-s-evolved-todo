---
name: dapr-component
description: Dapr component configuration patterns for Pub/Sub, State Store, Bindings, and Secrets. Use when configuring Dapr components, setting up service communication, or integrating with external services.
---

# Dapr Component Skill

Comprehensive guide for configuring Dapr components for event-driven microservices.

## Included Guides

1. **00-overview.md** - Dapr components overview
2. **01-pubsub.md** - Pub/Sub component configuration (Kafka/Redpanda)
3. **02-statestore.md** - State Store component configuration (Redis)
4. **03-bindings.md** - Bindings component configuration (Cron, HTTP)
5. **04-secrets.md** - Secrets component configuration (Kubernetes, local)
6. **05-service-invocation.md** - Service-to-service invocation
7. **06-observability.md** - Observability configuration

## Quick Reference

### Pub/Sub Component (Redpanda/Kafka)
```yaml
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
```

### State Store Component (Redis)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password
```

### Cron Binding
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/1 * * * *"  # Every minute
```

## Common Patterns
- **Event Streaming**: Kafka/Redpanda Pub/Sub
- **Session Management**: Redis State Store
- **Scheduled Tasks**: Cron Bindings
- **Secret Management**: Kubernetes Secrets
- **Service Communication**: Service Invocation
