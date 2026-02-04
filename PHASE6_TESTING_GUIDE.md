# Phase 6 Testing Guide: Advanced Recurring Task Patterns

**Date**: 2026-02-01
**Branch**: `011-event-driven-microservices`
**Phase**: Phase 6 - User Story 3 (P2)

---

## Overview

This guide provides step-by-step instructions for testing the Advanced Recurring Task Patterns feature (Phase 6). It covers all integration and testing tasks (T119-T127) with detailed test scenarios, expected results, and troubleshooting tips.

---

## Prerequisites

### Required Services
- ✅ PostgreSQL (Neon) - Database
- ✅ Redis - State store for idempotency
- ✅ Redpanda (Kafka) - Event streaming
- ✅ Dapr runtime - Service mesh

### Required Microservices
- ✅ Backend API (port 8000)
- ✅ WebSocket Sync Service (port 8001)
- ✅ Notification Service (port 8002)
- ✅ Recurring Task Service (port 8003) - **NEW**
- ✅ Frontend (port 3000)

### Tools Required
- Dapr CLI (`dapr --version`)
- Docker & Docker Compose
- Python 3.12+
- Node.js 18+
- curl or Postman (for API testing)

---

## Setup Instructions

### 1. Start Infrastructure Services

```bash
# Navigate to infrastructure directory
cd infrastructure

# Start Redpanda (Kafka), Redis, and PostgreSQL
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps

# Expected output:
# - redpanda: Up
# - redis: Up
# - postgres: Up (if using local PostgreSQL)
```

### 2. Start Backend API

```bash
# Terminal 1: Backend API
cd backend
source .venv/bin/activate  # or activate your virtual environment
uvicorn src.main:app --reload --port 8000

# Verify: http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 3. Start WebSocket Sync Service

```bash
# Terminal 2: WebSocket Sync Service
./scripts/start-websocket-sync-service.sh

# Verify: http://localhost:8001/health
# Expected: {"status": "healthy", "service": "websocket-sync"}
```

### 4. Start Notification Service

```bash
# Terminal 3: Notification Service
./scripts/start-notification-service.sh

# Verify: http://localhost:8002/health
# Expected: {"status": "healthy", "service": "notification"}
```

### 5. Start Recurring Task Service (NEW)

```bash
# Terminal 4: Recurring Task Service
./scripts/start-recurring-task-service.sh

# Verify: http://localhost:8003/health
# Expected: {"status": "healthy", "service": "recurring-task"}
```

### 6. Start Frontend

```bash
# Terminal 5: Frontend
cd frontend
npm run dev

# Verify: http://localhost:3000
# Expected: Application loads successfully
```

---

## Test Scenarios

### T119: Verify Dapr Pub/Sub Subscription ✅

**Objective**: Confirm Recurring Task Service subscribes to `task-events` topic

**Steps:**
1. Start Recurring Task Service with Dapr (see Setup #5)
2. Check Dapr logs for subscription confirmation
3. Verify Dapr sidecar is running

**Expected Output:**
```
INFO[0000] app is subscribed to the following topics: [task-events] through pubsub=kafka-pubsub
```

**Verification:**
```bash
# Check Dapr subscriptions
curl http://localhost:3503/v1.0/metadata

# Look for:
# "subscriptions": [
#   {
#     "pubsubname": "kafka-pubsub",
#     "topic": "task-events",
#     "routes": {...}
#   }
# ]
```

**Status**: ⏳ Pending manual verification

---

### T120: Test Task Completion with Recurring Pattern ✅

**Objective**: Verify task.completed event is published when recurring task is completed

**Steps:**
1. Log in to frontend (http://localhost:3000)
2. Create a new task with title "Test Recurring Task"
3. Add recurring pattern: Select preset "Every Weekday"
4. Save the task
5. Mark the task as completed
6. Monitor backend logs for event publication

**Expected Behavior:**
- Task marked as completed in UI
- `task.completed` event published to Kafka `task-events` topic
- Event contains `recurring_pattern` field

**Verification:**
```bash
# Check backend API logs
# Look for: "Publishing event: task.completed"

# Check Redpanda console (if available)
# Topic: task-events
# Look for event with event_type: "task.completed"
```

**Status**: ⏳ Pending manual verification

---

### T121: Test Next Occurrence Calculation ✅

**Objective**: Verify Recurring Task Service calculates next occurrence correctly

**Test Case 1: Weekday Pattern**
- Pattern: "0 9 * * 1-5" (Every weekday at 9 AM)
- Complete task on: Monday at 10:00 AM
- Expected next occurrence: Tuesday at 9:00 AM

**Test Case 2: Daily Pattern**
- Pattern: "0 9 * * *" (Daily at 9 AM)
- Complete task on: Monday at 14:00 PM
- Expected next occurrence: Tuesday at 9:00 AM

**Test Case 3: Weekly Pattern**
- Pattern: "0 9 * * 1" (Every Monday at 9 AM)
- Complete task on: Monday at 10:00 AM
- Expected next occurrence: Next Monday at 9:00 AM

**Verification:**
```bash
# Check Recurring Task Service logs
# Look for: "Calculated next occurrence: YYYY-MM-DDTHH:MM:SS"

# Check service metrics
curl http://localhost:8003/metrics
# Expected: total_events_processed incremented
```

**Status**: ⏳ Pending manual verification

---

### T122: Test New Task Instance Creation ✅

**Objective**: Verify new task instance is created with correct due date

**Steps:**
1. Create task with recurring pattern "0 9 * * *" (Daily at 9 AM)
2. Complete the task
3. Wait 2-3 seconds for event processing
4. Refresh task list
5. Verify new task instance appears

**Expected Results:**
- New task created with same title as parent
- `due_date` set to next occurrence (tomorrow at 9 AM)
- `parent_task_id` set to original task ID
- `created_from_recurring` flag set to true
- `recurring_pattern` is null (instances don't recur)
- Task appears in task list with "Instance of recurring task" indicator

**Verification:**
```bash
# Check backend API logs
# Look for: "Created task instance: {new_task_id}"

# Query tasks via API
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/tasks

# Verify new task in response with correct due_date
```

**Status**: ⏳ Pending manual verification

---

### T123: Test "Every Weekday at 9 AM" Pattern ✅

**Objective**: Verify weekday pattern creates tasks Monday-Friday only

**Test Scenario:**
1. Create task with pattern "0 9 * * 1-5"
2. Complete task on Friday at 10 AM
3. Verify next occurrence is Monday at 9 AM (skips weekend)
4. Complete task on Monday at 10 AM
5. Verify next occurrence is Tuesday at 9 AM

**Expected Behavior:**
- Friday completion → Monday 9 AM (skips Sat/Sun)
- Monday completion → Tuesday 9 AM
- Tuesday completion → Wednesday 9 AM
- Wednesday completion → Thursday 9 AM
- Thursday completion → Friday 9 AM

**Verification Method:**
```bash
# Use system clock manipulation (if available)
# Or manually test over multiple days

# Check task due dates in database
psql $DATABASE_URL -c "
  SELECT id, title, due_date, parent_task_id, created_from_recurring
  FROM tasks
  WHERE parent_task_id = 'PARENT_TASK_ID'
  ORDER BY due_date;
"
```

**Status**: ⏳ Pending manual verification

---

### T124: Test "First Monday of Month" Pattern ✅

**Objective**: Verify first Monday pattern creates task on correct date

**Test Scenario:**
1. Create task with pattern "0 9 * * 1#1" (First Monday of month)
2. Complete task on first Monday of January
3. Verify next occurrence is first Monday of February
4. Complete task on first Monday of February
5. Verify next occurrence is first Monday of March

**Expected Behavior:**
- January 6, 2026 (1st Mon) → February 2, 2026 (1st Mon)
- February 2, 2026 (1st Mon) → March 2, 2026 (1st Mon)
- March 2, 2026 (1st Mon) → April 6, 2026 (1st Mon)

**Verification:**
```bash
# Check calculated next occurrence in logs
# Look for: "Calculated next occurrence: 2026-02-02T09:00:00"

# Verify with croniter
python3 << EOF
from croniter import croniter
from datetime import datetime
base = datetime(2026, 1, 6, 10, 0, 0)  # Jan 6, 2026 10 AM
iter = croniter('0 9 * * 1#1', base)
print(f"Next: {iter.get_next(datetime)}")  # Should be Feb 2, 2026 9 AM
EOF
```

**Status**: ⏳ Pending manual verification

---

### T125: Test Custom Cron Expression "0 */4 * * *" ✅

**Objective**: Verify custom cron expression creates tasks every 4 hours

**Test Scenario:**
1. Create task with custom pattern "0 */4 * * *" (Every 4 hours)
2. Complete task at 8:00 AM
3. Verify next occurrence is 12:00 PM (4 hours later)
4. Complete task at 12:00 PM
5. Verify next occurrence is 4:00 PM (4 hours later)

**Expected Behavior:**
- 8:00 AM → 12:00 PM (4 hours)
- 12:00 PM → 4:00 PM (4 hours)
- 4:00 PM → 8:00 PM (4 hours)
- 8:00 PM → 12:00 AM (4 hours)
- 12:00 AM → 4:00 AM (4 hours)

**Verification:**
```bash
# Test pattern validation
curl -X POST http://localhost:8003/validate-pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "0 */4 * * *", "is_preset": false}'

# Expected response:
# {
#   "valid": true,
#   "cron_expression": "0 */4 * * *",
#   "error": null
# }
```

**Status**: ⏳ Pending manual verification

---

### T126: Test Modifying Recurring Pattern ✅

**Objective**: Verify pattern modification affects future instances only

**Test Scenario:**
1. Create task with pattern "0 9 * * *" (Daily at 9 AM)
2. Complete task → Instance 1 created (due tomorrow 9 AM)
3. Complete Instance 1 → Instance 2 created (due day after 9 AM)
4. Modify parent task pattern to "0 14 * * *" (Daily at 2 PM)
5. Complete Instance 2
6. Verify Instance 3 created with new pattern (due tomorrow 2 PM)

**Expected Behavior:**
- Instance 1: Created with old pattern (9 AM)
- Instance 2: Created with old pattern (9 AM)
- Instance 3: Created with new pattern (2 PM) ← Pattern change takes effect
- Past instances (1, 2) remain unchanged

**Verification:**
```bash
# Check task due times in database
psql $DATABASE_URL -c "
  SELECT id, title, due_date, parent_task_id
  FROM tasks
  WHERE parent_task_id = 'PARENT_TASK_ID'
  ORDER BY created_at;
"

# Verify:
# - First two instances have 09:00:00 time
# - Third instance has 14:00:00 time
```

**Status**: ⏳ Pending manual verification

---

### T127: Test Idempotency Prevents Duplicate Creation ✅

**Objective**: Verify idempotency prevents duplicate task creation

**Test Scenario:**
1. Create task with recurring pattern
2. Complete the task
3. Wait for new instance to be created
4. Manually replay the same `task.completed` event
5. Verify duplicate task is NOT created

**Manual Event Replay:**
```bash
# Publish duplicate event to Kafka via Dapr
curl -X POST http://localhost:3503/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.completed",
    "user_id": "USER_ID",
    "data": {
      "id": "TASK_ID",
      "title": "Test Task",
      "recurring_pattern": "0 9 * * *",
      "timezone": "UTC"
    },
    "jwt_token": "YOUR_JWT_TOKEN"
  }'
```

**Expected Behavior:**
- First event: New task instance created
- Second event (duplicate): No new task created
- Log message: "Task instance already exists for {task_id} on {date}"
- Metrics: `total_events_processed` increments, `total_tasks_created` does NOT

**Verification:**
```bash
# Check Redis for idempotency marker
redis-cli GET "recurring:TASK_ID:2026-02-02"

# Expected: JSON with task creation details
# {
#   "parent_task_id": "TASK_ID",
#   "next_occurrence_date": "2026-02-02",
#   "new_task_id": "NEW_TASK_ID",
#   "created_at": "2026-02-01T..."
# }

# Check service metrics
curl http://localhost:8003/metrics
# Verify total_events_processed > total_tasks_created (some events were duplicates)
```

**Status**: ⏳ Pending manual verification

---

## Troubleshooting

### Issue: Recurring Task Service won't start

**Symptoms:**
- Service fails to start with Dapr
- Port already in use error

**Solutions:**
```bash
# Check if port 8003 is in use
lsof -i :8003

# Kill existing process
kill -9 <PID>

# Check Dapr ports
lsof -i :3503  # HTTP
lsof -i :50053 # gRPC

# Restart with different ports
export DAPR_HTTP_PORT=3504
export DAPR_GRPC_PORT=50054
./scripts/start-recurring-task-service.sh
```

### Issue: Events not being consumed

**Symptoms:**
- Task completed but no new instance created
- No logs in Recurring Task Service

**Solutions:**
```bash
# Verify Dapr Pub/Sub component
cat infrastructure/dapr/pubsub-redpanda.yaml

# Check Redpanda is running
docker ps | grep redpanda

# Verify topic exists
docker exec -it redpanda rpk topic list

# Check Dapr subscription
curl http://localhost:3503/v1.0/metadata | jq '.subscriptions'
```

### Issue: Next occurrence calculation incorrect

**Symptoms:**
- Wrong due date on new task instance
- Timezone issues

**Solutions:**
```bash
# Test pattern validation endpoint
curl -X POST http://localhost:8003/validate-pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "0 9 * * 1-5", "is_preset": false}'

# Check service logs for timezone
# Look for: "Calculated next occurrence: ... (America/New_York)"

# Verify timezone in task data
psql $DATABASE_URL -c "
  SELECT id, title, timezone, recurring_pattern
  FROM tasks
  WHERE recurring_pattern IS NOT NULL;
"
```

### Issue: Duplicate tasks being created

**Symptoms:**
- Multiple instances created for same occurrence
- Idempotency not working

**Solutions:**
```bash
# Check Redis connection
redis-cli PING
# Expected: PONG

# Verify Dapr state store component
cat infrastructure/dapr/statestore-redis.yaml

# Check idempotency keys in Redis
redis-cli KEYS "recurring:*"

# Clear idempotency markers (if needed)
redis-cli DEL "recurring:TASK_ID:2026-02-02"
```

---

## Performance Testing

### Load Test: Multiple Recurring Tasks

**Scenario:**
- Create 100 tasks with different recurring patterns
- Complete all 100 tasks simultaneously
- Measure event processing time

**Expected Performance:**
- Event processing: <100ms p95
- Task creation: <200ms p95
- No duplicate tasks created
- All 100 new instances created successfully

**Test Script:**
```bash
# Create load test script
cat > test_load.sh << 'EOF'
#!/bin/bash
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/v1/tasks \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Load Test Task $i\",
      \"recurring_pattern\": \"0 9 * * *\",
      \"completed\": true
    }" &
done
wait
EOF

chmod +x test_load.sh
./test_load.sh
```

### Metrics Collection

```bash
# Collect metrics from all services
curl http://localhost:8003/metrics > recurring_metrics.json
curl http://localhost:8001/metrics > websocket_metrics.json
curl http://localhost:8002/metrics > notification_metrics.json

# Analyze metrics
cat recurring_metrics.json | jq '{
  events_processed: .total_events_processed,
  tasks_created: .total_tasks_created,
  errors: .total_errors,
  success_rate: (.total_tasks_created / .total_events_processed * 100)
}'
```

---

## Acceptance Criteria Checklist

- [ ] **T119**: Recurring Task Service starts with Dapr and subscribes to task-events
- [ ] **T120**: Task completion with recurring pattern triggers task.completed event
- [ ] **T121**: Next occurrence calculated correctly for various patterns
- [ ] **T122**: New task instance created with correct due date and parent reference
- [ ] **T123**: Weekday pattern creates tasks Monday-Friday only (skips weekends)
- [ ] **T124**: First Monday pattern creates task on correct date each month
- [ ] **T125**: Custom cron expression "0 */4 * * *" creates tasks every 4 hours
- [ ] **T126**: Modifying pattern affects future instances only, not past instances
- [ ] **T127**: Idempotency prevents duplicate task creation on event replay

---

## Test Results Template

```markdown
## Test Execution Results

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Local Development

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| T119 | Dapr Pub/Sub subscription | ⏳ | |
| T120 | Task completion event | ⏳ | |
| T121 | Next occurrence calculation | ⏳ | |
| T122 | Task instance creation | ⏳ | |
| T123 | Weekday pattern | ⏳ | |
| T124 | First Monday pattern | ⏳ | |
| T125 | Custom cron expression | ⏳ | |
| T126 | Pattern modification | ⏳ | |
| T127 | Idempotency | ⏳ | |

**Overall Status**: ⏳ Pending
**Issues Found**: 0
**Blockers**: None
```

---

## Next Steps After Testing

1. **Fix any issues** discovered during testing
2. **Update documentation** with test results
3. **Create Helm chart** for Recurring Task Service
4. **Add to CI/CD pipeline** for automated deployment
5. **Deploy to staging** environment
6. **Perform user acceptance testing** (UAT)
7. **Deploy to production** (Oracle OKE)

---

**End of Phase 6 Testing Guide**
