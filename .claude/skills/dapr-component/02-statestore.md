# State Store Component Configuration

## Redis State Store Component

### Basic Configuration

```yaml
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
      value: "redis:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password

    # Database selection
    - name: redisDB
      value: "0"

    # Connection pool
    - name: maxRetries
      value: "3"
    - name: maxRetryBackoff
      value: "2s"
```

### Advanced Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
  namespace: evolved-todo
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

    # TLS configuration
    - name: enableTLS
      value: "true"
    - name: skipVerify
      value: "false"

    # Connection pool
    - name: maxRetries
      value: "3"
    - name: maxRetryBackoff
      value: "2s"
    - name: dialTimeout
      value: "5s"
    - name: readTimeout
      value: "3s"
    - name: writeTimeout
      value: "3s"
    - name: poolSize
      value: "20"
    - name: minIdleConns
      value: "5"

    # TTL configuration
    - name: ttlInSeconds
      value: "3600"  # Default TTL: 1 hour
```

## Use Cases

### 1. Idempotency Tracking

```python
from dapr.clients import DaprClient

async def check_idempotency(event_id: str) -> bool:
    """Check if event has been processed"""
    async with DaprClient() as client:
        # Try to get existing state
        state = await client.get_state(
            store_name="redis-state",
            key=f"idempotency:{event_id}"
        )

        if state.data:
            return True  # Already processed

        # Mark as processed
        await client.save_state(
            store_name="redis-state",
            key=f"idempotency:{event_id}",
            value="processed",
            state_metadata={"ttlInSeconds": "86400"}  # 24 hours
        )

        return False
```

### 2. Session Management

```python
async def save_session(user_id: str, session_data: dict):
    """Save user session"""
    async with DaprClient() as client:
        await client.save_state(
            store_name="redis-state",
            key=f"session:{user_id}",
            value=session_data,
            state_metadata={"ttlInSeconds": "3600"}  # 1 hour
        )

async def get_session(user_id: str) -> dict:
    """Get user session"""
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="redis-state",
            key=f"session:{user_id}"
        )
        return state.data if state.data else None
```

### 3. Distributed Locks

```python
import asyncio
from datetime import datetime, timedelta

async def acquire_lock(lock_key: str, ttl_seconds: int = 30) -> bool:
    """Acquire distributed lock"""
    async with DaprClient() as client:
        # Try to set lock with NX (only if not exists)
        result = await client.try_lock(
            store_name="redis-state",
            resource_id=lock_key,
            lock_owner="my-service",
            expiry_in_seconds=ttl_seconds
        )
        return result.success

async def release_lock(lock_key: str):
    """Release distributed lock"""
    async with DaprClient() as client:
        await client.unlock(
            store_name="redis-state",
            resource_id=lock_key,
            lock_owner="my-service"
        )

# Usage
async def process_with_lock(task_id: str):
    """Process task with distributed lock"""
    lock_key = f"lock:task:{task_id}"

    if await acquire_lock(lock_key):
        try:
            await process_task(task_id)
        finally:
            await release_lock(lock_key)
    else:
        print(f"Task {task_id} is locked by another instance")
```

### 4. Rate Limiting

```python
from datetime import datetime, timedelta

async def check_rate_limit(user_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Check if user has exceeded rate limit"""
    async with DaprClient() as client:
        key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"

        # Get current count
        state = await client.get_state(
            store_name="redis-state",
            key=key
        )

        count = int(state.data) if state.data else 0

        if count >= limit:
            return False  # Rate limit exceeded

        # Increment count
        await client.save_state(
            store_name="redis-state",
            key=key,
            value=str(count + 1),
            state_metadata={"ttlInSeconds": str(window_seconds)}
        )

        return True
```

### 5. WebSocket Connection Tracking

```python
async def register_connection(user_id: str, connection_id: str):
    """Register WebSocket connection"""
    async with DaprClient() as client:
        # Get existing connections
        state = await client.get_state(
            store_name="redis-state",
            key=f"connections:{user_id}"
        )

        connections = state.data if state.data else []
        connections.append(connection_id)

        # Save updated connections
        await client.save_state(
            store_name="redis-state",
            key=f"connections:{user_id}",
            value=connections,
            state_metadata={"ttlInSeconds": "3600"}
        )

async def get_user_connections(user_id: str) -> list:
    """Get all connections for user"""
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="redis-state",
            key=f"connections:{user_id}"
        )
        return state.data if state.data else []
```

## State Operations

### Save State

```python
# Simple save
await client.save_state(
    store_name="redis-state",
    key="my-key",
    value="my-value"
)

# Save with TTL
await client.save_state(
    store_name="redis-state",
    key="my-key",
    value="my-value",
    state_metadata={"ttlInSeconds": "3600"}
)

# Save with ETag (optimistic locking)
await client.save_state(
    store_name="redis-state",
    key="my-key",
    value="my-value",
    etag="previous-etag"
)
```

### Get State

```python
# Simple get
state = await client.get_state(
    store_name="redis-state",
    key="my-key"
)
value = state.data

# Get with consistency
state = await client.get_state(
    store_name="redis-state",
    key="my-key",
    state_metadata={"consistency": "strong"}
)
```

### Delete State

```python
# Simple delete
await client.delete_state(
    store_name="redis-state",
    key="my-key"
)

# Delete with ETag
await client.delete_state(
    store_name="redis-state",
    key="my-key",
    etag="current-etag"
)
```

### Bulk Operations

```python
# Bulk save
await client.save_bulk_state(
    store_name="redis-state",
    states=[
        {"key": "key1", "value": "value1"},
        {"key": "key2", "value": "value2"},
        {"key": "key3", "value": "value3"}
    ]
)

# Bulk get
states = await client.get_bulk_state(
    store_name="redis-state",
    keys=["key1", "key2", "key3"]
)
```

## Local Development Configuration

```yaml
# infrastructure/dapr/statestore-local.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "localhost:6379"
    - name: redisPassword
      value: ""
    - name: redisDB
      value: "0"
```

## Production Configuration

```yaml
# infrastructure/dapr/statestore-production.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
  namespace: evolved-todo
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-prod.internal:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-prod-secret
        key: password
    - name: enableTLS
      value: "true"
    - name: maxRetries
      value: "5"
    - name: poolSize
      value: "50"
```

## Testing

### Test State Store

```bash
# Save state
dapr invoke \
  --app-id my-service \
  --method state \
  --verb POST \
  --data '{"key": "test", "value": "data"}'

# Get state
dapr invoke \
  --app-id my-service \
  --method state/test \
  --verb GET

# Check component status
kubectl get component redis-state -n evolved-todo -o yaml
```

## Troubleshooting

### Connection Issues

```bash
# Test Redis connectivity
kubectl exec -it redis-0 -- redis-cli ping

# Check component logs
kubectl logs -n evolved-todo -l app=my-service -c daprd
```

### Performance Issues

```bash
# Monitor Redis
kubectl exec -it redis-0 -- redis-cli INFO stats

# Check connection pool
kubectl exec -it redis-0 -- redis-cli CLIENT LIST
```

## Best Practices

1. **Always set TTL** to prevent memory leaks
2. **Use bulk operations** for multiple keys
3. **Implement retry logic** for transient failures
4. **Use ETags** for optimistic locking
5. **Monitor Redis memory** usage
6. **Configure connection pooling** appropriately
7. **Use secrets** for passwords
8. **Enable TLS** in production

## Next Steps

1. Read **03-bindings.md** for Bindings configuration
2. Read **04-secrets.md** for Secrets management
3. See **event-pattern** skill for idempotency patterns
