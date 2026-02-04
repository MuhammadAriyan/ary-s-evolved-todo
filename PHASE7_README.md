# Phase 7 Quick Start Guide

**Feature**: Intelligent Task Search + Audit Trail
**Branch**: 011-event-driven-microservices
**Date**: 2026-02-01

---

## Quick Start (5 Minutes)

### 1. Database Setup

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend

# Run migration to add pg_trgm extension and indexes
alembic upgrade head

# Verify setup
psql $DATABASE_URL -c "SELECT extname FROM pg_extension WHERE extname = 'pg_trgm';"
```

### 2. Start Backend API

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend

# Activate virtual environment
source .venv/bin/activate

# Start backend API
uvicorn main:app --reload --port 8000
```

### 3. Start Audit Service (New Terminal)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend/microservices/audit

# Start with Dapr sidecar
dapr run \
  --app-id audit-service \
  --app-port 8004 \
  --dapr-http-port 3504 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py
```

### 4. Start Frontend (New Terminal)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

### 5. Test Search

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

# Test search
curl -X GET "http://localhost:8000/api/v1/search/tasks?q=meeting" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results[] | {title: .task.title, score: .score}'
```

### 6. Test Audit Trail

```bash
# Create a task
TASK_ID=$(curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "High"}' \
  | jq -r '.id')

# Update the task
curl -X PATCH "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task"}'

# Wait for audit processing
sleep 3

# View audit logs
curl -X GET "http://localhost:8000/api/v1/audit/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.logs[] | {operation: .operation, timestamp: .timestamp}'
```

---

## UI Testing

### Search UI

1. Open browser: `http://localhost:3000`
2. Login with test credentials
3. Navigate to search page: `http://localhost:3000/search`
4. Enter search query: "meeting"
5. Verify results are displayed with highlighting
6. Test filters (status, priority, tags)
7. Test fuzzy search toggle

### Audit Log Viewer

1. Navigate to any task detail page
2. Scroll to "Audit Trail" section
3. Verify timeline displays all changes
4. Click expand button to see before/after state
5. Test export buttons (JSON, CSV)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  SearchBar   │  │ Search Page  │  │ AuditViewer  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ SearchService│  │ Search API   │  │  Audit API   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                            │                                 │
│                            ▼                                 │
│                    ┌──────────────┐                         │
│                    │EventPublisher│                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Kafka/Redpanda                            │
│                   (task-events topic)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Audit Service                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  LogWriter   │  │    Export    │  │  Dapr Pub/Sub│     │
│  │ (Batch 100)  │  │  (JSON/CSV)  │  │ Subscription │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL                                │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    tasks     │  │  audit_logs  │                        │
│  │ (search_vec) │  │ (JSONB state)│                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### Search
- **Full-text search** with PostgreSQL tsvector and ts_rank
- **Fuzzy search** with pg_trgm for typo tolerance
- **Advanced filters**: status, priority, tags, date range
- **Result highlighting** with <mark> tags
- **Search suggestions** and popular searches
- **Performance**: <1 second for 10k+ tasks

### Audit Trail
- **Event-driven** architecture with Kafka/Redpanda
- **Batch processing** (100 events or 5 seconds)
- **Complete history** with before/after state (JSONB)
- **Export** to JSON and CSV formats
- **Timeline UI** with expandable change details
- **Metadata**: IP address, user agent, timestamp

---

## API Endpoints

### Search
- `GET /api/v1/search/tasks` - Search tasks with filters
- `GET /api/v1/search/suggestions` - Get search suggestions
- `GET /api/v1/search/popular` - Get popular search terms

### Audit
- `GET /api/v1/audit/tasks/{task_id}` - Get audit logs for task
- `GET /api/v1/audit/user` - Get all user audit logs
- `POST /api/v1/audit/export` - Export audit logs (JSON/CSV)

### Audit Service (Internal)
- `GET /health` - Health check
- `GET /metrics` - Processing metrics
- `POST /flush` - Manual buffer flush

---

## Configuration

### Environment Variables

**Backend API**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
REDIS_URL=redis://localhost:6379
KAFKA_BROKERS=localhost:9092
JWT_SECRET_KEY=your-secret-key
```

**Audit Service**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
PORT=8004
```

### Dapr Components

**Pub/Sub** (`infrastructure/dapr/pubsub-redpanda.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "audit-service"
```

---

## Troubleshooting

### Search not working
```bash
# Check if pg_trgm extension is enabled
psql $DATABASE_URL -c "\dx pg_trgm"

# Check if search_vector is populated
psql $DATABASE_URL -c "SELECT id, title, search_vector FROM tasks LIMIT 5;"

# Trigger search_vector update
psql $DATABASE_URL -c "UPDATE tasks SET updated_at = NOW();"
```

### Audit Service not receiving events
```bash
# Check Dapr subscription
curl http://localhost:3504/v1.0/metadata | jq '.subscriptions'

# Check Audit Service logs
# Look for "Received event" messages

# Check Audit Service health
curl http://localhost:8004/health
```

### Slow search performance
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

# Look for "Index Scan" or "Bitmap Index Scan"
# If you see "Seq Scan", indexes are not being used
```

---

## Performance Targets

- **Search latency**: <1 second for 10k+ tasks
- **Audit event processing**: <100ms p95
- **Batch write**: 100 events or 5 seconds
- **Database write**: <50ms for batch of 100 logs

---

## Next Steps

1. Run integration tests (T144-T152)
2. Performance benchmarking with 10k+ tasks
3. Set up monitoring (Prometheus metrics)
4. Deploy to staging environment
5. Begin Phase 8 (Reusable Intelligence)

---

## Documentation

- **Implementation Summary**: `/PHASE7_IMPLEMENTATION_SUMMARY.md`
- **Testing Guide**: `/PHASE7_TESTING_GUIDE.md`
- **Research**: `/specs/011-event-driven-microservices/research.md`
- **Tasks**: `/specs/011-event-driven-microservices/tasks.md`

---

**Quick Start Date**: 2026-02-01
**Status**: Ready for Testing
