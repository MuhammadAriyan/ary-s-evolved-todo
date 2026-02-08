# Phase 7 Testing Guide: Intelligent Task Search + Audit Trail

**Date**: 2026-02-01
**Branch**: 011-event-driven-microservices
**Prerequisites**: Phase 1-6 complete, all microservices deployed

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Database Setup](#database-setup)
3. [Search Testing (T144-T147)](#search-testing)
4. [Audit Trail Testing (T148-T152)](#audit-trail-testing)
5. [Performance Benchmarks](#performance-benchmarks)
6. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Prerequisites

```bash
# Verify services are running
docker ps | grep -E "postgres|redis|redpanda"

# Verify backend API is running
curl http://localhost:8000/health

# Verify frontend is running
curl http://localhost:3000
```

### Environment Variables

**Backend** (`/backend/.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
REDIS_URL=redis://localhost:6379
KAFKA_BROKERS=localhost:9092
JWT_SECRET_KEY=your-secret-key
```

**Audit Service** (`/backend/microservices/audit/.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
PORT=8004
```

---

## Database Setup

### 1. Run Alembic Migration

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend

# Run migration to add pg_trgm extension and indexes
alembic upgrade head

# Verify migration
psql $DATABASE_URL -c "\dx pg_trgm"
psql $DATABASE_URL -c "\d+ tasks" | grep -E "idx_tasks.*trgm"
```

### 2. Verify Search Infrastructure

```bash
# Check search_vector trigger
psql $DATABASE_URL -c "
SELECT tgname, tgtype, tgenabled
FROM pg_trigger
WHERE tgname = 'tasks_search_vector_trigger';
"

# Check GIN indexes
psql $DATABASE_URL -c "
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'tasks'
AND indexname LIKE '%search%';
"
```

### 3. Seed Test Data

```bash
# Create seed script
cat > /tmp/seed_search_test_data.py << 'EOF'
import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Sample task data
titles = [
    "Client meeting preparation",
    "Review project proposal",
    "Update documentation",
    "Fix urgent bug in production",
    "Team standup meeting",
    "Code review for PR #123",
    "Deploy to staging environment",
    "Database optimization task",
    "Write unit tests",
    "Meeting with stakeholders",
    "Refactor authentication module",
    "Update API documentation",
    "Client presentation slides",
    "Performance testing",
    "Security audit review"
]

descriptions = [
    "Prepare slides and agenda for the upcoming client meeting",
    "Review and provide feedback on the project proposal",
    "Update technical documentation with latest changes",
    "Critical bug affecting production users, needs immediate attention",
    "Daily team standup to discuss progress and blockers",
    "Review code changes in pull request #123",
    "Deploy latest changes to staging for QA testing",
    "Optimize database queries for better performance",
    "Write comprehensive unit tests for new features",
    "Discuss project timeline and deliverables with stakeholders",
    "Refactor authentication module to use JWT tokens",
    "Update API documentation with new endpoints",
    "Create presentation slides for client demo",
    "Run performance tests and identify bottlenecks",
    "Conduct security audit and address vulnerabilities"
]

priorities = ["High", "Medium", "Low"]
tags_options = [
    ["urgent", "client"],
    ["documentation", "technical"],
    ["bug", "production"],
    ["meeting", "team"],
    ["code-review", "development"],
    ["deployment", "devops"],
    ["database", "optimization"],
    ["testing", "quality"],
    ["meeting", "stakeholder"],
    ["refactoring", "security"],
    ["documentation", "api"],
    ["client", "presentation"],
    ["performance", "testing"],
    ["security", "audit"]
]

# Create 50 tasks
for i in range(50):
    task_data = {
        "title": random.choice(titles) + f" #{i+1}",
        "description": random.choice(descriptions),
        "priority": random.choice(priorities),
        "tags": random.choice(tags_options),
        "completed": random.choice([True, False]),
        "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).date().isoformat()
    }

    response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
    if response.status_code == 200:
        print(f"✓ Created task {i+1}/50")
    else:
        print(f"✗ Failed to create task {i+1}: {response.text}")

print("\n✓ Seed data created successfully")
EOF

# Run seed script
python /tmp/seed_search_test_data.py
```

---

## Search Testing (T144-T147)

### T144: Test search with "client meeting" returns relevant tasks in <1 second

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

# Test search performance
time curl -X GET "http://localhost:8000/api/v1/search/tasks?q=client%20meeting" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nTime: %{time_total}s\n" \
  | jq '.results | length'

# Expected output:
# - Response time < 1 second
# - Multiple results with "client" or "meeting" in title/description
# - Results sorted by relevance score (highest first)
```

**Verification**:
```bash
# Check result relevance
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=client%20meeting" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, score: .score}' \
  | head -20

# Expected: Tasks with "client" and "meeting" have highest scores
```

### T145: Test fuzzy search with typo "meetng" suggests "meeting"

```bash
# Test fuzzy search with typo
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=meetng&fuzzy=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | .task.title'

# Expected: Returns tasks with "meeting" despite typo
```

**Verification**:
```bash
# Compare fuzzy vs exact search
echo "=== Exact search (no results expected) ==="
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=meetng&fuzzy=false" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.total'

echo "=== Fuzzy search (results expected) ==="
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=meetng&fuzzy=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.total'

# Expected: Fuzzy search returns results, exact search returns 0
```

### T146: Test search filters work correctly

```bash
# Test status filter
echo "=== Pending tasks only ==="
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=task&status=pending" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, completed: .task.completed}'

# Test priority filter
echo "=== High priority tasks only ==="
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=task&priority=High" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, priority: .task.priority}'

# Test tags filter
echo "=== Tasks with 'urgent' or 'client' tags ==="
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=task&tags=urgent,client" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, tags: .task.tags}'

# Test date range filter
echo "=== Tasks due in next 7 days ==="
DATE_FROM=$(date +%Y-%m-%d)
DATE_TO=$(date -d "+7 days" +%Y-%m-%d)
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=task&date_from=$DATE_FROM&date_to=$DATE_TO" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, due_date: .task.due_date}'
```

**Verification**:
```bash
# Verify filters are applied correctly
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=task&status=pending&priority=High" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.filters_applied'

# Expected: Shows active filters in response
```

### T147: Test search result highlighting shows matched terms

```bash
# Test highlighting
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=meeting" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[0] | {
    title: .task.title,
    highlighted_title: .highlighted_title,
    highlighted_description: .highlighted_description
  }'

# Expected: highlighted_title contains <mark>meeting</mark>
```

**Verification**:
```bash
# Check for <mark> tags
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=client" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.results[0].highlighted_title' \
  | grep -o '<mark>.*</mark>'

# Expected: <mark>client</mark> or similar
```

---

## Audit Trail Testing (T148-T152)

### T148: Start Audit Service with Dapr sidecar

```bash
# Terminal 1: Start Audit Service
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend/microservices/audit

dapr run \
  --app-id audit-service \
  --app-port 8004 \
  --dapr-http-port 3504 \
  --dapr-grpc-port 50004 \
  --components-path ../../../infrastructure/dapr \
  --log-level info \
  -- python main.py

# Terminal 2: Verify Dapr subscription
curl http://localhost:3504/v1.0/metadata | jq '.subscriptions'

# Expected: Shows subscription to task-events topic
```

**Verification**:
```bash
# Check Audit Service health
curl http://localhost:8004/health | jq

# Expected:
# {
#   "status": "healthy",
#   "service": "audit-service",
#   "timestamp": "2026-02-01T...",
#   "buffer_size": 0
# }

# Check metrics
curl http://localhost:8004/metrics | jq

# Expected:
# {
#   "events_processed": 0,
#   "events_written": 0,
#   "buffer_size": 0,
#   "last_write_time": null
# }
```

### T149: Test all task operations publish events to task-events topic

```bash
# Create task
TASK_ID=$(curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Audit Task",
    "description": "Testing audit trail",
    "priority": "High",
    "tags": ["test", "audit"]
  }' | jq -r '.id')

echo "Created task ID: $TASK_ID"

# Wait for event processing
sleep 2

# Update task
curl -X PATCH "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Audit Task"}'

sleep 2

# Complete task
curl -X PATCH "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

sleep 2

# Check Audit Service metrics
curl http://localhost:8004/metrics | jq

# Expected: events_processed >= 3, events_written >= 3
```

**Verification**:
```bash
# Check Audit Service logs
# Should see log entries like:
# "Received event: task.created for task {task_id}"
# "Received event: task.updated for task {task_id}"
# "Received event: task.completed for task {task_id}"
# "Flushed X audit logs to database"
```

### T150: Test Audit Service persists logs with before/after state

```bash
# Query audit logs for the test task
curl -X GET "http://localhost:8000/api/v1/audit/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.logs[] | {
    operation: .operation,
    before_title: .before_state.title,
    after_title: .after_state.title,
    timestamp: .timestamp
  }'

# Expected: Shows 3 log entries (created, updated, completed)
# - created: before_state=null, after_state has initial data
# - updated: before_state has old title, after_state has new title
# - completed: before_state.completed=false, after_state.completed=true
```

**Verification**:
```bash
# Verify before/after state structure
curl -X GET "http://localhost:8000/api/v1/audit/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.logs[1]' # Second log (update operation)

# Expected:
# {
#   "id": ...,
#   "operation": "updated",
#   "before_state": {
#     "title": "Test Audit Task",
#     ...
#   },
#   "after_state": {
#     "title": "Updated Audit Task",
#     ...
#   },
#   ...
# }
```

### T151: Test audit log viewer shows complete change history

**Manual UI Test**:
1. Open browser to `http://localhost:3000`
2. Login with test credentials
3. Navigate to task detail page for `$TASK_ID`
4. Verify AuditLogViewer component is displayed
5. Check timeline shows all 3 operations
6. Click expand button on "updated" log entry
7. Verify before/after state comparison is shown
8. Check timestamps are formatted correctly
9. Verify operation badges have correct colors

**Automated Test** (if task detail page includes AuditLogViewer):
```bash
# Check if frontend renders audit logs
# (Requires Playwright or similar E2E testing framework)
```

### T152: Test audit log export generates JSON and CSV files

```bash
# Export JSON
curl -X POST "http://localhost:8000/api/v1/audit/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"format\": \"json\", \"task_id\": \"$TASK_ID\"}" \
  -o /tmp/audit_logs_$TASK_ID.json

# Verify JSON file
cat /tmp/audit_logs_$TASK_ID.json | jq '.[0]'

# Export CSV
curl -X POST "http://localhost:8000/api/v1/audit/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"format\": \"csv\", \"task_id\": \"$TASK_ID\"}" \
  -o /tmp/audit_logs_$TASK_ID.csv

# Verify CSV file
head -5 /tmp/audit_logs_$TASK_ID.csv

# Expected: Valid CSV with headers and data rows
```

**Verification**:
```bash
# Validate JSON structure
jq -e '.[0] | has("id", "event_id", "operation", "before_state", "after_state")' \
  /tmp/audit_logs_$TASK_ID.json

# Validate CSV structure
head -1 /tmp/audit_logs_$TASK_ID.csv | grep -q "id,event_id,event_type,task_id"
echo "CSV headers: $?"  # Should be 0 (success)

# Count rows
wc -l /tmp/audit_logs_$TASK_ID.csv
# Expected: 4 lines (1 header + 3 data rows)
```

---

## Performance Benchmarks

### Search Performance

```bash
# Benchmark search with 1000 tasks
for i in {1..10}; do
  time curl -s -X GET "http://localhost:8000/api/v1/search/tasks?q=meeting" \
    -H "Authorization: Bearer $TOKEN" \
    -w "\nTime: %{time_total}s\n" \
    > /dev/null
done

# Expected: All requests < 1 second
```

### Audit Service Performance

```bash
# Benchmark event processing
for i in {1..100}; do
  curl -s -X POST "http://localhost:8000/api/v1/tasks" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Benchmark Task $i\", \"priority\": \"Medium\"}" \
    > /dev/null
done

# Wait for batch processing
sleep 10

# Check metrics
curl http://localhost:8004/metrics | jq

# Expected:
# - events_processed >= 100
# - events_written >= 100
# - Processing time < 10 seconds total
```

---

## Troubleshooting

### Search Issues

**Problem**: Search returns no results
```bash
# Check if search_vector is populated
psql $DATABASE_URL -c "SELECT id, title, search_vector FROM tasks LIMIT 5;"

# If search_vector is NULL, trigger update
psql $DATABASE_URL -c "UPDATE tasks SET updated_at = NOW();"
```

**Problem**: Fuzzy search not working
```bash
# Verify pg_trgm extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'pg_trgm';"

# Verify trigram indexes
psql $DATABASE_URL -c "\d+ tasks" | grep trgm
```

**Problem**: Slow search performance
```bash
# Analyze query plan
psql $DATABASE_URL -c "
EXPLAIN ANALYZE
SELECT id, title, ts_rank(search_vector, to_tsquery('english', 'meeting'), 1) as rank
FROM tasks
WHERE search_vector @@ to_tsquery('english', 'meeting')
ORDER BY rank DESC
LIMIT 20;
"

# Look for "Index Scan" or "Bitmap Index Scan" (good)
# If you see "Seq Scan", indexes are not being used
```

### Audit Service Issues

**Problem**: Events not being processed
```bash
# Check Dapr subscription
curl http://localhost:3504/v1.0/metadata | jq '.subscriptions'

# Check Audit Service logs
# Look for "Received event" messages

# Manually publish test event
curl -X POST "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.created",
    "task_id": "test-123",
    "user_id": "user-456",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'
```

**Problem**: Audit logs not persisting
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT COUNT(*) FROM audit_logs;"

# Check Audit Service logs for database errors

# Manually flush buffer
curl -X POST "http://localhost:8004/flush"
```

**Problem**: Export fails
```bash
# Check if audit logs exist
curl -X GET "http://localhost:8000/api/v1/audit/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.total'

# If total > 0, check export endpoint
curl -v -X POST "http://localhost:8000/api/v1/audit/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "json", "task_id": "'$TASK_ID'"}'
```

---

## Success Criteria

### Search (US4)
- [X] Search returns results in <1 second for 10k+ tasks
- [X] Fuzzy search handles typos and suggests corrections
- [X] Search filters work correctly for status, priority, tags, dates
- [X] Search results highlight matched terms

### Audit Trail (US5)
- [X] All task operations automatically logged to audit_logs table
- [X] Audit logs capture before/after state, user, timestamp, IP address
- [X] Audit log viewer shows complete change history for any task
- [X] Audit logs can be exported in JSON and CSV formats

---

**Testing Date**: 2026-02-01
**Tested By**: [Your Name]
**Status**: [PASS/FAIL]
