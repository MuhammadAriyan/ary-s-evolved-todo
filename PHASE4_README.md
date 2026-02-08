# Phase 4: Precise Time-Based Task Reminders - Quick Start Guide

**Feature**: Phase V Event-Driven Cloud Deployment - User Story 2
**Branch**: `011-event-driven-microservices`
**Status**: ✅ Implementation Complete

## Overview

Phase 4 adds precise time-based reminders to the task management application. Users can schedule reminders with exact times and receive notifications via multiple channels (email, in-app, push) within 10 seconds of the scheduled time.

## Architecture

```
User → Frontend → Backend API → Database (scheduled_reminders)
                                    ↓
                            Dapr Cron Binding (every 1 minute)
                                    ↓
                          Notification Service
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            EmailChannel (SendGrid)      InAppChannel (Kafka → WebSocket)
```

## Prerequisites

### Required Services
- PostgreSQL (Neon or local)
- Redis (for Dapr state store)
- Redpanda/Kafka (for event streaming)
- Dapr runtime (v1.12+)

### Required Tools
- Python 3.12+
- Node.js 18+
- Dapr CLI
- Docker (optional, for local infrastructure)

### Environment Variables

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SENDGRID_API_KEY=SG.your_api_key_here
SENDGRID_FROM_EMAIL=noreply@example.com
```

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your_secret_here
```

## Quick Start

### 1. Start Infrastructure

```bash
# Start PostgreSQL, Redis, Redpanda
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose ps
```

### 2. Initialize Database

```bash
cd backend

# Run migrations to create scheduled_reminders table
alembic upgrade head

# Verify table exists
psql $DATABASE_URL -c "\d scheduled_reminders"
```

### 3. Start Backend API

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn main:app --reload --port 8000
```

### 4. Start WebSocket Sync Service

```bash
cd backend/microservices/websocket_sync

# Start with Dapr
dapr run \
  --app-id websocket-sync \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py
```

### 5. Start Notification Service

```bash
# Use the provided script
./scripts/start-notification-service.sh

# Or manually:
cd backend/microservices/notification
dapr run \
  --app-id notification-service \
  --app-port 8002 \
  --dapr-http-port 3500 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py
```

### 6. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 7. Verify Services

```bash
# Backend API
curl http://localhost:8000/health

# WebSocket Sync Service
curl http://localhost:8001/health

# Notification Service
curl http://localhost:8002/health

# Check Dapr components
dapr components -k
```

## Usage

### 1. Create a Task

```bash
# Login to get JWT token
TOKEN="your_jwt_token"

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important Meeting",
    "description": "Quarterly review meeting",
    "priority": "high",
    "completed": false
  }'
```

### 2. Schedule a Reminder

```bash
# Schedule reminder for 5 minutes from now
REMINDER_TIME=$(date -u -d "+5 minutes" +"%Y-%m-%dT%H:%M:%S")

curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"task_id\": \"{task_id}\",
    \"reminder_time\": \"$REMINDER_TIME\",
    \"timezone\": \"America/New_York\",
    \"notification_channels\": [\"in_app\", \"email\"]
  }"
```

### 3. View Reminders

```bash
# List all reminders for a task
curl http://localhost:8000/api/v1/tasks/{task_id}/reminders \
  -H "Authorization: Bearer $TOKEN"

# Get specific reminder
curl http://localhost:8000/api/v1/reminders/{reminder_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Receive Notifications

**In-App (WebSocket)**:
- Open frontend in browser
- Navigate to task detail page
- Notification toast will appear when reminder is due

**Email**:
- Check email inbox
- Email will arrive within 10 seconds of scheduled time

## Frontend Usage

### 1. Navigate to Task Detail

```
http://localhost:3000/tasks/{task_id}
```

### 2. Add Reminder

1. Click "Reminders" tab
2. Click "Add Reminder" button
3. Select date and time
4. Choose timezone (auto-detected)
5. Select notification channels
6. Click "Create Reminder"

### 3. View Reminders

- All scheduled reminders appear in the Reminders tab
- Shows reminder time, timezone, channels, and status
- Delete button to remove reminders

### 4. Receive Notifications

- Toast notification appears in top-right corner
- Shows task title and reminder message
- Auto-dismisses after 5 seconds
- Click X to dismiss manually

## Configuration

### Dapr Cron Binding

**File**: `infrastructure/dapr/bindings-cron.yaml`

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
    value: "@every 1m"  # Check every minute
  - name: direction
    value: "input"
```

**Adjust frequency**:
- `@every 30s` - Every 30 seconds (more frequent)
- `@every 2m` - Every 2 minutes (less frequent)
- `*/5 * * * *` - Every 5 minutes (cron syntax)

### Notification Channels

**Enable/Disable Channels**:

Edit `backend/microservices/notification/scheduler.py`:

```python
# Disable email channel
self.email_channel = None

# Disable in-app channel
self.in_app_channel = None
```

### Timezone Support

**Add Custom Timezones**:

Edit `frontend/components/tasks/ReminderForm.tsx`:

```typescript
const TIMEZONES = [
  { value: "UTC", label: "UTC" },
  { value: "Your/Timezone", label: "Your Label" },
  // Add more timezones
]
```

## Troubleshooting

### Issue: Cron binding not triggering

**Symptoms**: No logs showing "Cron trigger received"

**Solutions**:
```bash
# Check Dapr components
dapr components -k

# Verify binding file exists
ls infrastructure/dapr/bindings-cron.yaml

# Check Dapr logs
dapr logs --app-id notification-service

# Restart service
./scripts/start-notification-service.sh
```

### Issue: Email notifications not sending

**Symptoms**: No emails received

**Solutions**:
```bash
# Verify SendGrid API key
echo $SENDGRID_API_KEY

# Test SendGrid connection
python -c "
from sendgrid import SendGridAPIClient
import os
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
print('Connected successfully')
"

# Check SendGrid activity log
# https://app.sendgrid.com/email_activity
```

### Issue: In-app notifications not appearing

**Symptoms**: No toast notifications in browser

**Solutions**:
```bash
# Check WebSocket connection
# Open browser console, look for WebSocket connection logs

# Verify WebSocket Sync Service is running
curl http://localhost:8001/health

# Check Kafka topic
# Verify task-updates topic exists and has messages
```

### Issue: Timezone conversion errors

**Symptoms**: Reminders sent at wrong time

**Solutions**:
```bash
# Verify pytz installation
pip show pytz

# Test timezone conversion
python -c "
import pytz
from datetime import datetime
tz = pytz.timezone('America/New_York')
print(tz.localize(datetime.now()))
"

# Check reminder timezone in database
psql $DATABASE_URL -c "SELECT id, reminder_time, timezone FROM scheduled_reminders;"
```

### Issue: Duplicate notifications

**Symptoms**: Multiple notifications for same reminder

**Solutions**:
```bash
# Check Redis state store
redis-cli KEYS "reminder:*"

# Verify idempotency key exists
redis-cli GET "reminder:{task_id}:{reminder_time}"

# Clear idempotency keys (if needed)
redis-cli FLUSHDB
```

## Testing

### Manual Testing

Follow the comprehensive testing guide:
```bash
cat PHASE4_TESTING_GUIDE.md
```

### Automated Testing

```bash
# Backend unit tests
cd backend
pytest tests/test_reminder_service.py
pytest tests/test_notification_service.py

# Frontend tests
cd frontend
npm test
```

### Integration Testing

```bash
# Run all integration tests
./scripts/run-phase4-tests.sh
```

## Monitoring

### Health Checks

```bash
# All services
curl http://localhost:8000/health  # Backend API
curl http://localhost:8001/health  # WebSocket Sync
curl http://localhost:8002/health  # Notification Service
```

### Metrics

```bash
# Notification Service metrics
curl http://localhost:8002/metrics

# Example output:
{
  "total_reminders_checked": 150,
  "total_notifications_sent": 45,
  "total_errors": 2,
  "last_check_time": "2026-02-01T12:34:56"
}
```

### Logs

```bash
# Notification Service logs
tail -f backend/microservices/notification/notification-service.log

# Dapr logs
dapr logs --app-id notification-service

# Backend API logs
tail -f backend/backend.log
```

## Performance

### Expected Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Reminder delivery latency | < 10s | From scheduled time to notification |
| Cron trigger interval | 60s | Configurable in bindings-cron.yaml |
| Database query time | < 50ms | For due reminders query |
| Email send time | < 2s | SendGrid API call |
| In-app notification latency | < 1s | Kafka + WebSocket |
| Concurrent reminders | 100+ | Per minute |

### Optimization Tips

1. **Reduce cron interval** for more frequent checks (higher accuracy, more load)
2. **Increase batch size** in ReminderScheduler (100 → 500)
3. **Add database indexes** on reminder_time and status columns
4. **Use connection pooling** for database connections
5. **Enable Redis clustering** for high availability

## Security

### Authentication
- All API endpoints require JWT token
- Token validated via Better Auth
- User ID extracted from token for authorization

### Authorization
- Users can only access their own reminders
- All queries filtered by user_id
- No cross-user data access

### Secrets Management
- SendGrid API key stored in environment variables
- Database credentials in environment variables
- Dapr Secrets API for production (Phase 5)

## Next Steps

1. **Complete Integration Testing** (T074-T082)
   - Follow PHASE4_TESTING_GUIDE.md
   - Verify all acceptance criteria

2. **Performance Testing**
   - Load test with 100+ concurrent reminders
   - Measure delivery latency
   - Optimize if needed

3. **Phase 5: Production Deployment**
   - Create Helm charts
   - Set up CI/CD pipelines
   - Deploy to Oracle OKE
   - Configure monitoring and alerting

## Resources

- **Implementation Summary**: `PHASE4_IMPLEMENTATION_SUMMARY.md`
- **Testing Guide**: `PHASE4_TESTING_GUIDE.md`
- **Tasks**: `specs/011-event-driven-microservices/tasks.md`
- **Plan**: `specs/011-event-driven-microservices/plan.md`
- **Dapr Documentation**: https://docs.dapr.io
- **SendGrid Documentation**: https://docs.sendgrid.com

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review implementation summary
3. Check Dapr and SendGrid documentation
4. Review service logs for error messages

---

**Status**: ✅ Phase 4 Implementation Complete - Ready for Testing
