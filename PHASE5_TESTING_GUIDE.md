# Phase V: Integration Testing Guide

## Overview

This guide provides step-by-step instructions for testing all Phase V event-driven features.

## Prerequisites

- All services running (use `/dev` skill)
- Browser with JavaScript enabled
- Two browser tabs or different browsers for real-time sync testing

## Test Suite 1: Real-Time Task Synchronization (Phase 3)

### T049: Verify WebSocket Sync Service

```bash
# Check service health
curl http://localhost:8001/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "service": "websocket-sync",
#   "connections": <number>
# }
```

### T050: Verify Event Publishing

```bash
# Create a task and check backend logs
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test Event Publishing",
    "description": "Testing Kafka events",
    "priority": "High",
    "completed": false
  }'

# Check Kafka topics
docker exec todo-redpanda rpk topic list
docker exec todo-redpanda rpk topic consume task-events --num 1
docker exec todo-redpanda rpk topic consume task-updates --num 1
```

### T051: Test WebSocket Connection

1. Open browser DevTools (F12)
2. Navigate to http://localhost:3000/todo
3. Check Console for WebSocket connection messages:
   - "✅ JWT token retrieved successfully"
   - "WebSocket connected: user=..."
4. Check Network tab → WS filter → verify connection established

### T052: Test Real-Time Sync (2 Tabs)

**Critical Test - Core Feature**

1. Open http://localhost:3000/todo in Tab 1
2. Open http://localhost:3000/todo in Tab 2 (or different browser)
3. Log in with same account in both tabs
4. In Tab 1: Create a new task
5. **Verify**: Task appears in Tab 2 within 2 seconds ✨
6. In Tab 2: Mark task as complete
7. **Verify**: Task shows as completed in Tab 1 within 2 seconds

**Expected Behavior**:
- Task appears instantly in both tabs
- No manual refresh needed
- Connection status indicator shows "Online" (green)

### T053: Test Reconnection

1. Open browser DevTools → Network tab
2. Throttle network to "Offline"
3. Wait 5 seconds
4. Set network back to "Online"
5. **Verify**: Connection status changes from "Reconnecting" to "Online"
6. **Verify**: Any missed updates are synchronized

### T054: Test Event Replay

1. Create a task in Tab 1
2. Close Tab 2 (disconnect WebSocket)
3. Create 3 more tasks in Tab 1
4. Reopen Tab 2
5. **Verify**: All 4 tasks appear (including the 3 created while disconnected)

### T055: Test Multi-User Sync

1. Log in as User A in Browser 1
2. Log in as User B in Browser 2
3. User A creates a task
4. **Verify**: User A sees the task in all their tabs
5. **Verify**: User B does NOT see User A's task (user isolation)

### T056: Load Test

```bash
# Run load test script
cd backend/tests/integration
python test_websocket_load.py

# Expected: 100 concurrent connections without errors
```

**Acceptance Criteria**:
- ✅ WebSocket service healthy
- ✅ Events published to Kafka
- ✅ WebSocket connection establishes with JWT
- ✅ Real-time sync works within 2 seconds
- ✅ Reconnection works after network interruption
- ✅ Missed events replayed on reconnect
- ✅ Multi-user isolation works correctly
- ✅ System handles 100+ concurrent connections

---

## Test Suite 2: Precise Time-Based Reminders (Phase 4)

### T074: Verify Notification Service

```bash
# Check service health
curl http://localhost:8002/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "service": "notification",
#   "scheduler_active": true
# }
```

### T075: Test Reminder Scheduling

1. Open http://localhost:3000/todo
2. Create a new task
3. Click "Add Reminder"
4. Set reminder for 5 minutes from now
5. Save the task
6. **Verify**: Entry created in `scheduled_reminders` table

```bash
# Check database
docker exec todo-postgres psql -U postgres -d todo -c \
  "SELECT * FROM scheduled_reminders WHERE sent = false;"
```

### T076: Verify Dapr Bindings

```bash
# Check Notification Service logs for cron triggers
tail -f /tmp/claude/.../tasks/<notification-service-task-id>.output | grep "reminder-cron"

# Expected: Log entry every minute showing cron trigger
```

### T077: Test Email Notification

1. Schedule a reminder for 2 minutes from now
2. Wait for reminder time
3. **Verify**: Email sent (check SendGrid dashboard or logs)

```bash
# Check logs
tail -f /tmp/claude/.../tasks/<notification-service-task-id>.output | grep "email"
```

### T078: Test In-App Notification

1. Schedule a reminder for 2 minutes from now
2. Keep browser tab open
3. Wait for reminder time
4. **Verify**: Toast notification appears in browser
5. **Verify**: WebSocket message received in DevTools Console

### T079: Test Idempotency

1. Schedule a reminder
2. Manually trigger notification service twice
3. **Verify**: Only one notification sent (check logs)

```bash
# Check Redis for idempotency key
docker exec todo-redis redis-cli KEYS "reminder:*"
```

### T080: Test Timezone Conversion

1. Set browser timezone to UTC-5 (New York)
2. Schedule reminder for 3:00 PM local time
3. **Verify**: Reminder stored in UTC in database
4. **Verify**: Notification arrives at correct local time

### T081: Test Delivery Timing

1. Schedule reminder for exactly 5 minutes from now
2. Note the exact time
3. Wait for notification
4. **Verify**: Notification arrives within 10 seconds of scheduled time

### T082: Test Multiple Reminders

1. Create 5 tasks with reminders at different times
2. Wait for all reminders to trigger
3. **Verify**: All 5 notifications delivered correctly
4. **Verify**: No missed or duplicate notifications

**Acceptance Criteria**:
- ✅ Notification service healthy
- ✅ Reminders scheduled correctly
- ✅ Dapr Bindings trigger every minute
- ✅ Email notifications sent
- ✅ In-app notifications delivered via WebSocket
- ✅ Idempotency prevents duplicates
- ✅ Timezone conversion works correctly
- ✅ Notifications arrive within 10 seconds
- ✅ Multiple reminders handled correctly

---

## Test Suite 3: Recurring Task Patterns (Phase 6)

### T119: Verify Recurring Task Service

```bash
# Check service health
curl http://localhost:8003/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "service": "recurring-task",
#   "parser_active": true,
#   "generator_active": true
# }
```

### T120: Test Task Completion Event

1. Create a task with recurring pattern "daily"
2. Mark the task as complete
3. **Verify**: `task.completed` event published to Kafka

```bash
# Check Kafka
docker exec todo-redpanda rpk topic consume task-events --num 1
```

### T121: Test Next Occurrence Calculation

1. Create task with pattern "daily at 9:00 AM"
2. Complete the task
3. **Verify**: Next occurrence calculated correctly (tomorrow at 9:00 AM)

```bash
# Check logs
tail -f /tmp/claude/.../tasks/<recurring-task-service-id>.output | grep "next_occurrence"
```

### T122: Test Task Instance Creation

1. Create recurring task "daily at 9:00 AM"
2. Complete the task
3. **Verify**: New task instance created with correct due date
4. **Verify**: New task has `parent_task_id` set

### T123: Test Weekday Pattern

1. Create task with pattern "every weekday at 9:00 AM"
2. Simulate task completion on Friday
3. **Verify**: Next occurrence is Monday (not Saturday)

### T124: Test Monthly Pattern

1. Create task with pattern "first Monday of each month"
2. Complete the task
3. **Verify**: Next occurrence is first Monday of next month

### T125: Test Custom Cron Expression

1. Create task with cron "0 */4 * * *" (every 4 hours)
2. Complete the task
3. **Verify**: Next occurrence is 4 hours from now

### T126: Test Pattern Modification

1. Create recurring task "daily"
2. Create 3 instances by completing 3 times
3. Modify pattern to "weekly"
4. **Verify**: Future instances follow new pattern
5. **Verify**: Past instances unchanged

### T127: Test Idempotency

1. Create recurring task
2. Complete the task
3. Manually trigger recurring service twice
4. **Verify**: Only one new instance created

**Acceptance Criteria**:
- ✅ Recurring Task service healthy
- ✅ Task completion triggers event
- ✅ Next occurrence calculated correctly
- ✅ New task instances created
- ✅ Weekday pattern works (Monday-Friday only)
- ✅ Monthly pattern works correctly
- ✅ Custom cron expressions work
- ✅ Pattern modification affects future only
- ✅ Idempotency prevents duplicates

---

## Test Suite 4: Search & Audit Trail (Phase 7)

### T144: Test Search Performance

1. Create 50 tasks with various content
2. Search for "client meeting"
3. **Verify**: Results returned in <1 second
4. **Verify**: Results ranked by relevance

```bash
# Measure search performance
time curl "http://localhost:8000/api/v1/search?query=client+meeting"
```

### T145: Test Fuzzy Search

1. Search for "meetng" (typo)
2. **Verify**: System suggests "meeting"
3. **Verify**: Results include tasks with "meeting"

### T146: Test Search Filters

1. Search with filters: `?query=task&status=pending&priority=High`
2. **Verify**: Only pending high-priority tasks returned
3. Test date range filter
4. Test tag filter

### T147: Test Result Highlighting

1. Search for "important project"
2. **Verify**: Matched terms highlighted in results
3. **Verify**: Highlighting works in title and description

### T148: Verify Audit Service

```bash
# Check service health
curl http://localhost:8004/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "service": "audit-service",
#   "buffer_size": <number>
# }
```

### T149: Test Event Publishing

1. Create a task
2. Update the task 3 times
3. Delete the task
4. **Verify**: All 5 operations published to `task-events` topic

```bash
# Check Kafka
docker exec todo-redpanda rpk topic consume task-events --num 5
```

### T150: Test Audit Log Persistence

1. Perform task operations (create, update, delete)
2. **Verify**: Audit logs written to `audit_log` table

```bash
# Check database
docker exec todo-postgres psql -U postgres -d todo -c \
  "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10;"
```

### T151: Test Audit Log Viewer

1. Open task detail page
2. Click "View History"
3. **Verify**: All changes shown with timestamps
4. **Verify**: Before/after values displayed
5. **Verify**: User attribution shown

### T152: Test Audit Log Export

1. Navigate to audit log page
2. Click "Export"
3. Select JSON format
4. **Verify**: File downloads with all audit logs
5. Repeat with CSV format

**Acceptance Criteria**:
- ✅ Search returns results <1 second
- ✅ Fuzzy search handles typos
- ✅ Search filters work correctly
- ✅ Result highlighting works
- ✅ Audit service healthy
- ✅ All operations publish events
- ✅ Audit logs persisted to database
- ✅ Audit log viewer shows complete history
- ✅ Audit logs exportable in JSON/CSV

---

## Test Suite 5: System Integration

### End-to-End Workflow Test

1. **User Registration & Login**
   - Register new user
   - Log in
   - Verify JWT token issued

2. **Task Management**
   - Create task
   - Update task
   - Mark complete
   - Delete task
   - Verify all operations work

3. **Real-Time Sync**
   - Open 2 tabs
   - Create task in Tab 1
   - Verify appears in Tab 2

4. **Reminders**
   - Schedule reminder
   - Wait for notification
   - Verify delivery

5. **Recurring Tasks**
   - Create recurring task
   - Complete task
   - Verify new instance created

6. **Search**
   - Search for tasks
   - Verify results

7. **Audit Trail**
   - View task history
   - Verify all changes logged

### Performance Benchmarks

```bash
# Run performance tests
cd backend/tests/integration
python test_performance.py

# Expected results:
# - API response time: p95 < 200ms
# - Search query time: < 1 second
# - Event processing: p95 < 100ms
# - WebSocket delivery: < 2 seconds
```

### Health Check All Services

```bash
# Check all services
curl http://localhost:8000/health | jq .  # Backend API
curl http://localhost:8001/health | jq .  # WebSocket Sync
curl http://localhost:8002/health | jq .  # Notification
curl http://localhost:8003/health | jq .  # Recurring Task
curl http://localhost:8004/health | jq .  # Audit Service

# All should return "healthy"
```

---

## Troubleshooting

### WebSocket Not Connecting

1. Check JWT token is valid
2. Verify BETTER_AUTH_URL matches frontend port
3. Check CORS configuration
4. Check browser console for errors

### Events Not Flowing

1. Verify Kafka topics exist
2. Check Dapr components loaded
3. Verify microservices subscribed to topics
4. Check service logs for errors

### Reminders Not Triggering

1. Verify Notification Service running
2. Check Dapr Bindings configuration
3. Verify cron triggers in logs
4. Check scheduled_reminders table

### Search Not Working

1. Verify search_vector column exists
2. Check PostgreSQL full-text search configuration
3. Verify GIN indexes created
4. Check search endpoint logs

---

## Success Criteria

All tests must pass for Phase V to be considered complete:

- ✅ Real-time sync works within 2 seconds
- ✅ Reminders delivered within 10 seconds
- ✅ Recurring patterns work correctly
- ✅ Search returns results <1 second
- ✅ Audit logs capture all operations
- ✅ System handles 100+ concurrent connections
- ✅ All services healthy
- ✅ No data loss or corruption
- ✅ User isolation works correctly
- ✅ Performance targets met

---

## Next Steps

After all tests pass:

1. Deploy to Oracle OKE (Phase 5 - Cloud Deployment)
2. Set up monitoring dashboards
3. Configure CI/CD pipeline
4. Complete reusable intelligence (agents, skills, blueprints)
5. Final polish and documentation
