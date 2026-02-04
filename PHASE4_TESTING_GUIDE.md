# Phase 4 Testing Guide: Precise Time-Based Task Reminders

**Feature**: Phase V Event-Driven Cloud Deployment - User Story 2
**Branch**: `011-event-driven-microservices`
**Date**: 2026-02-01

## Overview

This guide covers testing for Phase 4 (T074-T082), which implements precise time-based task reminders using Dapr Bindings, multi-channel notifications, and timezone-aware scheduling.

## Prerequisites

1. **Infrastructure Running**:
   - PostgreSQL (Neon or local)
   - Redis (for Dapr state store)
   - Redpanda/Kafka (for event streaming)
   - Dapr runtime installed

2. **Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://...
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDGRID_FROM_EMAIL=noreply@example.com
   ```

3. **Services Running**:
   - Backend API (port 8000)
   - WebSocket Sync Service (port 8001)
   - Notification Service (port 8002)
   - Frontend (port 3000)

## Test Cases

### T074: Start Notification Service with Dapr Sidecar

**Objective**: Verify Notification Service starts successfully with Dapr sidecar and Bindings subscription.

**Steps**:
```bash
# Start the service
./scripts/start-notification-service.sh
```

**Expected Results**:
- ✅ Service starts on port 8002
- ✅ Dapr sidecar starts on HTTP port 3500, gRPC port 50001
- ✅ Dapr loads cron binding from `infrastructure/dapr/bindings-cron.yaml`
- ✅ Health check responds: `curl http://localhost:8002/health`
- ✅ Logs show: "Notification Service started successfully"

**Verification**:
```bash
# Check health
curl http://localhost:8002/health

# Check metrics
curl http://localhost:8002/metrics

# Check Dapr components
dapr components -k
```

---

### T075: Test Reminder Scheduling Creates Entry in Database

**Objective**: Verify reminder creation via API creates entry in `scheduled_reminders` table.

**Steps**:
```bash
# 1. Get JWT token (login via frontend or API)
TOKEN="your_jwt_token"

# 2. Create a task
TASK_ID=$(curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task for Reminder",
    "description": "Testing reminder functionality",
    "priority": "high",
    "completed": false
  }' | jq -r '.id')

# 3. Schedule a reminder for 5 minutes from now
REMINDER_TIME=$(date -u -d "+5 minutes" +"%Y-%m-%dT%H:%M:%S")

curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"task_id\": \"$TASK_ID\",
    \"reminder_time\": \"$REMINDER_TIME\",
    \"timezone\": \"UTC\",
    \"notification_channels\": [\"in_app\", \"email\"]
  }"
```

**Expected Results**:
- ✅ API returns 201 Created with reminder ID
- ✅ Database query shows new entry:
  ```sql
  SELECT * FROM scheduled_reminders WHERE task_id = '$TASK_ID';
  ```
- ✅ Status is 'pending'
- ✅ Notification channels array contains ['in_app', 'email']

---

### T076: Test Dapr Bindings Triggers ReminderScheduler Callback

**Objective**: Verify Dapr cron binding triggers `/cron` endpoint every minute.

**Steps**:
```bash
# Watch Notification Service logs
tail -f notification-service.log
```

**Expected Results**:
- ✅ Every 60 seconds, logs show: "Cron trigger received - checking for due reminders"
- ✅ ReminderScheduler.check_and_send_reminders() is called
- ✅ Metrics endpoint shows increasing `total_reminders_checked` count
- ✅ `last_check_time` updates every minute

**Verification**:
```bash
# Check metrics multiple times (1 minute apart)
watch -n 60 'curl -s http://localhost:8002/metrics | jq'
```

---

### T077: Test Due Reminder Sends Notification via Email Channel

**Objective**: Verify email notifications are sent when reminder is due.

**Prerequisites**:
- Valid SendGrid API key configured
- Email address verified in SendGrid

**Steps**:
```bash
# 1. Create reminder for 2 minutes from now
REMINDER_TIME=$(date -u -d "+2 minutes" +"%Y-%m-%dT%H:%M:%S")

curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"task_id\": \"$TASK_ID\",
    \"reminder_time\": \"$REMINDER_TIME\",
    \"timezone\": \"UTC\",
    \"notification_channels\": [\"email\"]
  }"

# 2. Wait 2-3 minutes
# 3. Check email inbox
```

**Expected Results**:
- ✅ Email received within 10 seconds of scheduled time
- ✅ Email contains task details and reminder message
- ✅ Email has proper HTML formatting
- ✅ Logs show: "Email sent successfully to user@example.com"
- ✅ Reminder status updated to 'sent' in database

---

### T078: Test Due Reminder Sends Notification via In-App Channel

**Objective**: Verify in-app notifications are sent via WebSocket.

**Steps**:
```bash
# 1. Open frontend in browser (http://localhost:3000)
# 2. Login and navigate to task detail page
# 3. Create reminder for 2 minutes from now with "in_app" channel
# 4. Keep browser tab open and wait
```

**Expected Results**:
- ✅ Toast notification appears in browser within 10 seconds of scheduled time
- ✅ Notification shows task title and reminder message
- ✅ WebSocket Sync Service logs show event broadcast
- ✅ Notification Service logs show: "In-app notification published"

**Verification**:
```bash
# Check WebSocket Sync Service logs
tail -f websocket-sync-service.log | grep "notification.reminder"
```

---

### T079: Test Idempotency Prevents Duplicate Notifications

**Objective**: Verify idempotency checking prevents duplicate notifications.

**Steps**:
```bash
# 1. Create reminder for 1 minute from now
# 2. Manually trigger cron endpoint multiple times after reminder is due
curl -X POST http://localhost:8002/cron
curl -X POST http://localhost:8002/cron
curl -X POST http://localhost:8002/cron

# 3. Check Redis state store
redis-cli GET "reminder:$TASK_ID:$REMINDER_TIME"
```

**Expected Results**:
- ✅ Only ONE notification sent (check email/in-app)
- ✅ Logs show: "Reminder already sent, skipping" for subsequent calls
- ✅ Redis contains idempotency key with timestamp
- ✅ Metrics show `total_notifications_sent` increments only once

---

### T080: Test Timezone Conversion Works Correctly

**Objective**: Verify timezone conversion for different user timezones.

**Test Cases**:

**Case 1: UTC to America/New_York**
```bash
# Schedule reminder for 15:00 UTC (10:00 AM EST)
curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "'$TASK_ID'",
    "reminder_time": "2026-02-01T15:00:00",
    "timezone": "America/New_York",
    "notification_channels": ["in_app"]
  }'
```

**Expected**: Notification sent at 15:00 UTC (10:00 AM EST)

**Case 2: UTC to Asia/Tokyo**
```bash
# Schedule reminder for 09:00 JST (00:00 UTC)
curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "'$TASK_ID'",
    "reminder_time": "2026-02-01T09:00:00",
    "timezone": "Asia/Tokyo",
    "notification_channels": ["in_app"]
  }'
```

**Expected**: Notification sent at 00:00 UTC (09:00 JST)

**Verification**:
- ✅ Notifications arrive at correct UTC time
- ✅ Logs show timezone conversion: "Converting from Asia/Tokyo to UTC"
- ✅ No off-by-one-hour errors (DST handling)

---

### T081: Test Notification Arrives Within 10 Seconds of Scheduled Time

**Objective**: Verify timing accuracy of reminder delivery.

**Steps**:
```bash
# 1. Create reminder for exactly 5 minutes from now
REMINDER_TIME=$(date -u -d "+5 minutes" +"%Y-%m-%dT%H:%M:%S")
SCHEDULED_EPOCH=$(date -u -d "$REMINDER_TIME" +%s)

curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"task_id\": \"$TASK_ID\",
    \"reminder_time\": \"$REMINDER_TIME\",
    \"timezone\": \"UTC\",
    \"notification_channels\": [\"in_app\"]
  }"

# 2. Record when notification arrives
# 3. Calculate delta
```

**Expected Results**:
- ✅ Notification arrives within 10 seconds of scheduled time
- ✅ Average latency < 5 seconds
- ✅ No notifications missed
- ✅ Cron runs every 60 seconds (max delay = 60s + processing time)

**Measurement**:
```python
# In notification handler
scheduled_time = datetime.fromisoformat(reminder_time)
actual_time = datetime.utcnow()
delta = (actual_time - scheduled_time).total_seconds()
print(f"Delivery latency: {delta}s")
```

---

### T082: Test Multiple Reminders for Different Tasks

**Objective**: Verify system handles multiple concurrent reminders correctly.

**Steps**:
```bash
# 1. Create 5 tasks
for i in {1..5}; do
  TASK_ID=$(curl -X POST http://localhost:8000/api/v1/tasks \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Task $i\",
      \"priority\": \"medium\",
      \"completed\": false
    }" | jq -r '.id')

  # 2. Schedule reminder for each task (2 minutes from now)
  REMINDER_TIME=$(date -u -d "+2 minutes" +"%Y-%m-%dT%H:%M:%S")

  curl -X POST http://localhost:8000/api/v1/tasks/$TASK_ID/reminders \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"task_id\": \"$TASK_ID\",
      \"reminder_time\": \"$REMINDER_TIME\",
      \"timezone\": \"UTC\",
      \"notification_channels\": [\"in_app\"]
    }"
done

# 3. Wait and verify all 5 notifications arrive
```

**Expected Results**:
- ✅ All 5 reminders created successfully
- ✅ All 5 notifications delivered within 10 seconds of scheduled time
- ✅ No notifications lost or duplicated
- ✅ Correct task details in each notification
- ✅ Metrics show `total_notifications_sent` = 5

---

## Acceptance Criteria Verification

### ✅ Users can schedule reminders with exact times via UI
- Frontend reminder form works
- Date/time picker functional
- Timezone selector defaults to user's browser timezone

### ✅ Notification Service checks for due reminders every minute via Dapr Bindings
- Cron binding configured correctly
- `/cron` endpoint called every 60 seconds
- ReminderScheduler processes due reminders

### ✅ Reminders are delivered within 10 seconds of scheduled time
- Timing tests pass (T081)
- Average latency < 5 seconds

### ✅ Notifications sent via email and in-app channels
- Email channel works (T077)
- In-app channel works (T078)
- Multi-channel support functional

### ✅ Idempotency prevents duplicate notifications
- Redis state store tracks sent reminders
- Duplicate prevention works (T079)

### ✅ Timezone conversion works correctly for users in different locations
- pytz handles timezone conversion
- DST transitions handled correctly (T080)

### ✅ Missed reminders are handled gracefully
- Service restart replays missed reminders (within 2-minute window)
- No reminders lost during downtime

---

## Troubleshooting

### Issue: Cron binding not triggering

**Solution**:
```bash
# Check Dapr components
dapr components -k

# Verify binding configuration
cat infrastructure/dapr/bindings-cron.yaml

# Check Dapr logs
dapr logs --app-id notification-service
```

### Issue: Email notifications not sending

**Solution**:
```bash
# Verify SendGrid API key
echo $SENDGRID_API_KEY

# Check SendGrid activity log
# https://app.sendgrid.com/email_activity

# Test SendGrid connection
python -c "
from sendgrid import SendGridAPIClient
import os
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
print('SendGrid connected successfully')
"
```

### Issue: Timezone conversion errors

**Solution**:
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
```

---

## Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Reminder delivery latency | < 10s | TBD |
| Cron trigger interval | 60s | TBD |
| Concurrent reminders | 100+ | TBD |
| Database query time | < 50ms | TBD |
| Email send time | < 2s | TBD |
| In-app notification latency | < 1s | TBD |

---

## Next Steps

After completing Phase 4 testing:
1. Document any issues found
2. Fix critical bugs
3. Optimize performance if needed
4. Proceed to Phase 5: Production-Ready Cloud Deployment
