# Bindings Component Configuration

## Cron Binding (Scheduled Tasks)

### Basic Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: evolved-todo
spec:
  type: bindings.cron
  version: v1
  metadata:
    # Cron schedule (every minute)
    - name: schedule
      value: "*/1 * * * *"

    # Optional: Direction (input only for cron)
    - name: direction
      value: "input"
```

### Cron Schedule Examples

```yaml
# Every minute
schedule: "*/1 * * * *"

# Every 5 minutes
schedule: "*/5 * * * *"

# Every hour at minute 0
schedule: "0 * * * *"

# Every day at 9 AM
schedule: "0 9 * * *"

# Every weekday at 9 AM
schedule: "0 9 * * 1-5"

# First day of month at midnight
schedule: "0 0 1 * *"

# Every 15 minutes during business hours (9 AM - 5 PM)
schedule: "*/15 9-17 * * *"
```

### Using Cron Binding

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@app.post("/reminder-check")
async def check_reminders():
    """
    Called by Dapr cron binding every minute

    Dapr automatically invokes this endpoint based on cron schedule
    """
    logger.info("Checking for due reminders...")

    # Get reminders due in next minute
    due_reminders = await get_due_reminders()

    # Send notifications
    for reminder in due_reminders:
        await send_notification(reminder)

    return {"success": True, "processed": len(due_reminders)}
```

### Multiple Cron Schedules

```yaml
# Check reminders every minute
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/1 * * * *"

---
# Generate recurring tasks every hour
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: recurring-task-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "0 * * * *"

---
# Cleanup old data daily at 2 AM
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cleanup-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "0 2 * * *"
```

## HTTP Output Binding

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: external-api
  namespace: evolved-todo
spec:
  type: bindings.http
  version: v1
  metadata:
    - name: url
      value: "https://api.external-service.com"

    # Optional: HTTP method
    - name: method
      value: "POST"

    # Optional: Headers
    - name: headers
      value: |
        Content-Type: application/json
        Authorization: Bearer ${SECRET_TOKEN}
```

### Using HTTP Binding

```python
from dapr.clients import DaprClient

async def call_external_api(data: dict):
    """Call external API using HTTP binding"""
    async with DaprClient() as client:
        response = await client.invoke_binding(
            binding_name="external-api",
            operation="post",
            data=data
        )
        return response.data
```

## Email Binding (SendGrid)

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: sendgrid-email
  namespace: evolved-todo
spec:
  type: bindings.twilio.sendgrid
  version: v1
  metadata:
    - name: apiKey
      secretKeyRef:
        name: sendgrid-secret
        key: api-key

    - name: emailFrom
      value: "noreply@evolvedtodo.com"

    - name: emailFromName
      value: "Evolved Todo"
```

### Using Email Binding

```python
async def send_email_notification(to_email: str, subject: str, body: str):
    """Send email using SendGrid binding"""
    async with DaprClient() as client:
        await client.invoke_binding(
            binding_name="sendgrid-email",
            operation="create",
            data={
                "emailTo": to_email,
                "subject": subject,
                "emailBody": body
            }
        )
```

## AWS SES Email Binding

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: aws-ses-email
  namespace: evolved-todo
spec:
  type: bindings.aws.ses
  version: v1
  metadata:
    - name: region
      value: "us-east-1"

    - name: accessKey
      secretKeyRef:
        name: aws-secret
        key: access-key

    - name: secretKey
      secretKeyRef:
        name: aws-secret
        key: secret-key

    - name: emailFrom
      value: "noreply@evolvedtodo.com"
```

## Kafka Input Binding

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-input
  namespace: evolved-todo
spec:
  type: bindings.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"

    - name: topics
      value: "external-events"

    - name: consumerGroup
      value: "evolved-todo-consumer"

    - name: authRequired
      value: "false"
```

### Using Kafka Input Binding

```python
@app.post("/kafka-events")
async def handle_kafka_event(event: dict):
    """Handle events from Kafka input binding"""
    logger.info(f"Received Kafka event: {event}")

    # Process event
    await process_external_event(event)

    return {"success": True}
```

## Testing Bindings

### Test Cron Binding

```bash
# Check if cron binding is registered
kubectl get component reminder-cron -n evolved-todo

# Check service logs for cron invocations
kubectl logs -n evolved-todo -l app=notification-service --tail=100

# Manually trigger endpoint (for testing)
curl -X POST http://localhost:8000/reminder-check
```

### Test HTTP Binding

```bash
# Test HTTP binding invocation
dapr invoke \
  --app-id notification-service \
  --method external-api \
  --verb POST \
  --data '{"test": "data"}'
```

### Test Email Binding

```bash
# Test email sending
dapr invoke \
  --app-id notification-service \
  --method sendgrid-email \
  --verb POST \
  --data '{"emailTo": "test@example.com", "subject": "Test", "emailBody": "Test email"}'
```

## Troubleshooting

### Cron Not Triggering

```bash
# Check component status
kubectl describe component reminder-cron -n evolved-todo

# Check Dapr sidecar logs
kubectl logs -n evolved-todo notification-service -c daprd

# Verify endpoint exists
curl http://localhost:8000/reminder-check
```

### HTTP Binding Errors

```bash
# Check binding configuration
kubectl get component external-api -o yaml

# Test connectivity
kubectl exec -it notification-service -- curl https://api.external-service.com
```

### Email Binding Failures

```bash
# Check secret exists
kubectl get secret sendgrid-secret -n evolved-todo

# Verify API key
kubectl get secret sendgrid-secret -o jsonpath='{.data.api-key}' | base64 -d
```

## Best Practices

1. **Use secrets for API keys and credentials**
2. **Set appropriate cron schedules** (avoid too frequent)
3. **Implement idempotency** for cron-triggered operations
4. **Add error handling** for external API calls
5. **Monitor binding invocations** with metrics
6. **Use circuit breakers** for external services
7. **Test bindings locally** before deploying
8. **Document binding dependencies** in README

## Next Steps

1. Read **04-secrets.md** for Secrets management
2. Read **05-service-invocation.md** for service-to-service calls
3. See **microservice-creator** agent for complete service templates
