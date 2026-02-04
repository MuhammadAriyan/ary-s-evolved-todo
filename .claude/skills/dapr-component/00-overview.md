# Dapr Components Overview

## What are Dapr Components?

Dapr components are pluggable building blocks that provide abstractions for common distributed system capabilities. They allow you to swap implementations without changing application code.

## Component Types

### 1. Pub/Sub (Publish/Subscribe)
**Purpose**: Asynchronous messaging between services

**Supported Providers**:
- Kafka / Redpanda
- Redis Streams
- RabbitMQ
- Azure Service Bus
- AWS SNS/SQS
- Google Cloud Pub/Sub

**Use Cases**:
- Event-driven architecture
- Real-time notifications
- Audit logging
- Task queues

### 2. State Store
**Purpose**: Key-value storage for application state

**Supported Providers**:
- Redis
- PostgreSQL
- MongoDB
- Azure Cosmos DB
- AWS DynamoDB
- Cassandra

**Use Cases**:
- Session management
- Idempotency tracking
- Distributed locks
- Cache

### 3. Bindings
**Purpose**: Trigger or invoke external systems

**Input Bindings** (Trigger your app):
- Cron (scheduled tasks)
- Kafka
- HTTP
- MQTT

**Output Bindings** (Invoke external systems):
- HTTP
- Email (SendGrid, AWS SES)
- SMS (Twilio)
- Storage (S3, Azure Blob)

**Use Cases**:
- Scheduled jobs
- External API calls
- Email/SMS notifications
- File processing

### 4. Secrets
**Purpose**: Secure secret management

**Supported Providers**:
- Kubernetes Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Local file (development only)

**Use Cases**:
- Database credentials
- API keys
- Certificates
- Encryption keys

### 5. Service Invocation
**Purpose**: Service-to-service communication

**Features**:
- Service discovery
- Load balancing
- Retries
- Timeouts
- mTLS encryption

**Use Cases**:
- Synchronous API calls
- Request/response patterns
- Service mesh

### 6. Configuration
**Purpose**: Application configuration management

**Supported Providers**:
- Redis
- PostgreSQL
- Azure App Configuration
- AWS Parameter Store

**Use Cases**:
- Feature flags
- Environment-specific config
- Dynamic configuration

## Component Lifecycle

### 1. Define Component
Create YAML manifest:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: my-component
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"
```

### 2. Deploy Component
```bash
# Kubernetes
kubectl apply -f component.yaml

# Local (self-hosted)
# Place in ~/.dapr/components/ or specify with --components-path
```

### 3. Use in Application
```python
from dapr.clients import DaprClient

# Pub/Sub
async with DaprClient() as client:
    await client.publish_event(
        pubsub_name="my-component",
        topic_name="my-topic",
        data={"message": "hello"}
    )

# State Store
async with DaprClient() as client:
    await client.save_state(
        store_name="my-component",
        key="my-key",
        value="my-value"
    )
```

## Component Scoping

### Namespace Scoping (Kubernetes)
```yaml
metadata:
  name: redis-state
  namespace: production  # Only available in production namespace
```

### Application Scoping
```yaml
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
  scopes:
    - notification-service  # Only notification-service can use this
    - audit-service
```

## Component Metadata

### Common Metadata Fields

**Connection Settings**:
```yaml
metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "my-service"
```

**Authentication**:
```yaml
metadata:
  - name: password
    secretKeyRef:
      name: redis-secret
      key: password
```

**Retry Configuration**:
```yaml
metadata:
  - name: maxRetries
    value: "3"
  - name: retryBackoff
    value: "1s"
```

**Timeouts**:
```yaml
metadata:
  - name: requestTimeout
    value: "30s"
  - name: dialTimeout
    value: "5s"
```

## Component Configuration Best Practices

### 1. Use Secrets for Credentials
```yaml
# ✓ Good: Reference secret
metadata:
  - name: password
    secretKeyRef:
      name: redis-secret
      key: password

# ❌ Bad: Hardcode credentials
metadata:
  - name: password
    value: "my-password"
```

### 2. Scope Components Appropriately
```yaml
# ✓ Good: Limit to specific services
scopes:
  - notification-service
  - audit-service

# ❌ Bad: No scoping (all services can access)
```

### 3. Use Namespaces for Isolation
```yaml
# ✓ Good: Separate environments
metadata:
  name: redis-state
  namespace: production

# ❌ Bad: Share components across environments
```

### 4. Configure Retries and Timeouts
```yaml
# ✓ Good: Set appropriate timeouts
metadata:
  - name: requestTimeout
    value: "30s"
  - name: maxRetries
    value: "3"

# ❌ Bad: Use defaults (may not fit your needs)
```

### 5. Version Components
```yaml
# ✓ Good: Specify version
spec:
  type: pubsub.kafka
  version: v1

# ❌ Bad: No version (may break on updates)
```

## Component Discovery

### List Components
```bash
# Kubernetes
kubectl get components -n evolved-todo

# Dapr CLI
dapr components -k
```

### Describe Component
```bash
kubectl describe component redis-state -n evolved-todo
```

### Test Component
```bash
# Test Pub/Sub
dapr publish --publish-app-id my-app --pubsub redpanda --topic test-topic --data '{"test": "data"}'

# Test State Store
dapr invoke --app-id my-app --method state --verb POST --data '{"key": "test", "value": "data"}'
```

## Component Templates

### Development (Local)
```yaml
# Use local services
metadata:
  - name: brokers
    value: "localhost:9092"
  - name: redisHost
    value: "localhost:6379"
```

### Staging
```yaml
# Use staging services
metadata:
  - name: brokers
    value: "kafka-staging.internal:9092"
  - name: redisHost
    value: "redis-staging.internal:6379"
```

### Production
```yaml
# Use production services with secrets
metadata:
  - name: brokers
    value: "kafka-prod.internal:9092"
  - name: password
    secretKeyRef:
      name: redis-prod-secret
      key: password
```

## Troubleshooting

### Component Not Found
```bash
# Check if component exists
kubectl get components -n evolved-todo

# Check component logs
kubectl logs -n evolved-todo -l app=my-service -c daprd
```

### Connection Errors
```bash
# Test connectivity
kubectl exec -it my-pod -c daprd -- curl http://localhost:3500/v1.0/metadata

# Check component status
dapr components -k
```

### Permission Errors
```yaml
# Verify scopes
spec:
  scopes:
    - my-service  # Ensure your service is listed
```

## Next Steps

1. Read **01-pubsub.md** for Pub/Sub configuration
2. Read **02-statestore.md** for State Store configuration
3. Read **03-bindings.md** for Bindings configuration
4. See **dapr-integration** blueprint for complete examples
