# Phase 3 Testing Guide: Real-Time Task Synchronization

**Date**: 2026-02-01
**Branch**: `011-event-driven-microservices`
**Tasks**: T049-T056 (Integration & Testing)

## Prerequisites

Before running tests, ensure all infrastructure and services are running:

### 1. Infrastructure Services
```bash
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Verify all services are healthy
docker-compose -f docker-compose.dev.yml ps
```

Expected services:
- ✅ todo-postgres (port 5432)
- ✅ todo-redis (port 6379)
- ✅ todo-redpanda (ports 19092, 18081, 18082)
- ✅ todo-redpanda-console (port 8080)
- ✅ todo-dapr-placement (port 50006)

### 2. Backend API with Dapr
```bash
cd backend

# Install dependencies if not already done
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start with Dapr
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  --log-level info \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. WebSocket Sync Service with Dapr
```bash
cd backend/microservices/websocket_sync

# Install dependencies
pip install -r requirements.txt

# Start with Dapr
dapr run \
  --app-id websocket-sync \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --dapr-grpc-port 50002 \
  --components-path ../../../infrastructure/dapr \
  --log-level info \
  -- uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Frontend
```bash
cd frontend

# Install dependencies if not already done
npm install

# Start development server
npm run dev
```

## Test Execution

### T049: Verify Dapr Pub/Sub Subscription

**Objective**: Confirm WebSocket Sync Service is subscribed to task-updates topic via Dapr.

**Steps**:
1. Check Dapr logs for WebSocket Sync Service:
```bash
# Look for subscription registration in logs
dapr logs --app-id websocket-sync
```

2. Expected output:
```
INFO[0000] app is subscribed to the following topics: [task-updates] through pubsub=kafka-pubsub
```

3. Verify subscription via Dapr API:
```bash
curl http://localhost:3501/dapr/subscribe
```

Expected response:
```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-updates",
    "route": "/task-updates"
  }
]
```

4. Check Redpanda Console:
- Open http://localhost:8080
- Navigate to Topics
- Verify `task-updates` topic exists
- Check consumer groups for `todo-app`

**Pass Criteria**: ✅ Subscription registered, topic exists, consumer group active

---

### T050: Test Event Publishing to Topics

**Objective**: Verify task CRUD operations publish events to both task-events and task-updates topics.

**Steps**:
1. Open Redpanda Console: http://localhost:8080

2. Navigate to Topics and monitor:
   - `task-events`
   - `task-updates`

3. Create a task via API:
```bash
# Get JWT token first (login via frontend or API)
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task for Event Publishing",
    "description": "Testing event publishing",
    "priority": "High",
    "tags": ["test"],
    "due_date": "2026-02-15"
  }'
```

4. Check Redpanda Console:
   - Both topics should have new messages
   - Message should contain event_type: "task.created"
   - Message should include task data

5. Update the task:
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Task"
  }'
```

6. Verify event_type: "task.updated" in both topics

7. Delete the task:
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

8. Verify event_type: "task.deleted" in both topics

**Pass Criteria**: ✅ All CRUD operations publish to both topics with correct event types

---

### T051: Test WebSocket Connection with JWT

**Objective**: Verify WebSocket connection establishes successfully with JWT authentication.

**Steps**:
1. Open browser DevTools (F12) → Console

2. Navigate to http://localhost:3000 and sign in

3. Open Console and check for WebSocket connection logs:
```
✅ JWT token retrieved for WebSocket
Creating WebSocket client
WebSocket status changed: connecting
WebSocket connected
WebSocket status changed: connected
```

4. Check Network tab → WS filter:
   - Should see connection to `ws://localhost:8001/ws?token=...`
   - Status: 101 Switching Protocols
   - Connection should be active (green indicator)

5. Test invalid token:
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8001/ws?token=invalid-token')
ws.onerror = (e) => console.error('Expected error:', e)
```

Expected: Connection rejected with 1008 Policy Violation

6. Check WebSocket service logs:
```bash
dapr logs --app-id websocket-sync | grep "WebSocket"
```

Expected:
```
WebSocket connected: user=<user_id>, connection=<connection_id>
```

**Pass Criteria**: ✅ Valid token connects, invalid token rejected, connection tracked

---

### T052: Test Real-Time Sync Across Tabs (PRIMARY TEST)

**Objective**: Task update in tab 1 appears in tab 2 within 2 seconds without refresh.

**Steps**:
1. Open browser and navigate to http://localhost:3000
2. Sign in with your account
3. Open two tabs side-by-side (Tab 1 and Tab 2)
4. Both tabs should show connection status: "Online" (green)

**Test 1: Create Task**
- Tab 1: Click "Add Task" and create a new task
- Tab 2: Observe task appears automatically within 2 seconds
- ✅ Pass if task appears without refresh

**Test 2: Update Task**
- Tab 1: Edit the task title
- Tab 2: Observe title updates automatically
- ✅ Pass if update appears within 2 seconds

**Test 3: Complete Task**
- Tab 1: Mark task as complete
- Tab 2: Observe completion status updates
- ✅ Pass if status updates within 2 seconds

**Test 4: Delete Task**
- Tab 1: Delete the task
- Tab 2: Observe task disappears
- ✅ Pass if deletion reflects within 2 seconds

**Test 5: Multiple Operations**
- Tab 1: Create 5 tasks rapidly
- Tab 2: All 5 tasks should appear in order
- ✅ Pass if all operations sync correctly

**Timing Measurement**:
```javascript
// In Tab 2 console
let lastUpdate = Date.now()
// Perform action in Tab 1
// When update appears in Tab 2:
console.log('Sync time:', Date.now() - lastUpdate, 'ms')
```

**Pass Criteria**: ✅ All operations sync within 2000ms (2 seconds)

---

### T053: Test WebSocket Reconnection

**Objective**: Verify WebSocket reconnects after temporary network interruption.

**Steps**:
1. Open application in browser
2. Verify connection status: "Online" (green)

3. Simulate network interruption:
   - Browser DevTools → Network tab
   - Enable "Offline" mode
   - Observe connection status changes to "Reconnecting" (yellow, spinning)

4. Wait 5 seconds (observe reconnection attempts in console)

5. Disable "Offline" mode (go back online)

6. Observe:
   - Connection status changes to "Online" (green)
   - Console shows: "WebSocket connected"
   - No data loss

7. Alternative test - Stop WebSocket service:
```bash
# Stop the service
dapr stop --app-id websocket-sync

# Wait 10 seconds, observe reconnection attempts

# Restart the service
cd backend/microservices/websocket_sync
dapr run --app-id websocket-sync --app-port 8001 ...
```

8. Verify reconnection with exponential backoff:
   - First attempt: ~1 second
   - Second attempt: ~1.5 seconds
   - Third attempt: ~2.25 seconds
   - Max interval: 30 seconds

**Pass Criteria**: ✅ Automatic reconnection with exponential backoff, no manual intervention needed

---

### T054: Test Missed Event Replay

**Objective**: Verify missed events are replayed when client reconnects.

**Steps**:
1. Open Tab 1 and Tab 2
2. Both tabs connected (status: "Online")

3. In Tab 1:
   - Open DevTools → Network → Enable "Offline"
   - Tab 1 is now disconnected

4. In Tab 2 (still online):
   - Create 3 new tasks
   - Update 2 existing tasks
   - Delete 1 task
   - Total: 6 events

5. In Tab 1:
   - Disable "Offline" mode
   - Observe console logs:
```
📡 Replaying 6 missed events since 2026-02-01T10:30:00Z
📡 Real-time update: task.created
📡 Real-time update: task.created
📡 Real-time update: task.created
📡 Real-time update: task.updated
📡 Real-time update: task.updated
📡 Real-time update: task.deleted
📡 Replay complete: 6 events
```

6. Verify Tab 1 is now synchronized with Tab 2

7. Check WebSocket service logs:
```bash
dapr logs --app-id websocket-sync | grep "replay"
```

Expected:
```
Replaying 6 missed events to user <user_id>
Replay completed for user <user_id>
```

**Pass Criteria**: ✅ All missed events replayed in order, UI synchronized

---

### T055: Test Multi-User Synchronization

**Objective**: Verify multiple users see each other's task updates in real-time.

**Steps**:
1. Create two user accounts (User A and User B)

2. Open two browser windows:
   - Window 1: Sign in as User A
   - Window 2: Sign in as User B

3. User A creates a task:
   - User A sees task immediately
   - User B does NOT see it (different user)
   - ✅ Correct isolation

4. Test shared task (requires group feature - Phase 2):
   - Create a group with both users
   - Assign task to group
   - Both users should see updates
   - Note: Group features not yet fully integrated

5. Test same user, different devices:
   - Window 1: Sign in as User A
   - Window 2: Sign in as User A (same account)
   - Create task in Window 1
   - Verify appears in Window 2 within 2 seconds
   - ✅ Same user sync works

**Pass Criteria**: ✅ Same user syncs across devices, different users isolated

---

### T056: Load Test with 100 Concurrent Connections

**Objective**: Verify system handles 100+ concurrent WebSocket connections without degradation.

**Prerequisites**:
- Install load testing tool: `npm install -g artillery` or use Python script

**Option 1: Artillery Load Test**

Create `load-test.yml`:
```yaml
config:
  target: "ws://localhost:8001"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Ramp up to 100 connections"
  processor: "./load-test-processor.js"

scenarios:
  - name: "WebSocket Connection Test"
    engine: "ws"
    flow:
      - connect:
          url: "/ws?token={{ token }}"
      - think: 30
      - send:
          payload: '{"type": "heartbeat", "timestamp": "{{ timestamp }}"}'
      - think: 30
```

Run:
```bash
artillery run load-test.yml
```

**Option 2: Python Load Test Script**

Create `load_test.py`:
```python
import asyncio
import websockets
import json
from datetime import datetime

async def connect_client(client_id, token):
    uri = f"ws://localhost:8001/ws?token={token}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Client {client_id} connected")

            # Send heartbeat every 30 seconds
            for _ in range(10):
                await websocket.send(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                await asyncio.sleep(30)

    except Exception as e:
        print(f"Client {client_id} error: {e}")

async def load_test(num_clients=100, token="your-jwt-token"):
    tasks = [connect_client(i, token) for i in range(num_clients)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(load_test(100))
```

Run:
```bash
python load_test.py
```

**Monitoring During Load Test**:

1. Check WebSocket service metrics:
```bash
curl http://localhost:8001/metrics
```

Expected:
```json
{
  "active_connections": 100,
  "total_connections": 100,
  "total_messages_sent": 1000,
  "total_messages_received": 1000
}
```

2. Monitor system resources:
```bash
# CPU and memory usage
docker stats todo-redis
docker stats todo-redpanda

# WebSocket service process
top -p $(pgrep -f "websocket_sync")
```

3. Check Redis connections:
```bash
docker exec -it todo-redis redis-cli INFO clients
```

4. Monitor Kafka lag:
- Open Redpanda Console: http://localhost:8080
- Check consumer group lag for `todo-app`
- Should be near zero (< 100ms)

**Performance Targets**:
- ✅ 100 concurrent connections maintained
- ✅ CPU usage < 50%
- ✅ Memory usage < 500MB
- ✅ Message latency < 100ms p95
- ✅ No connection drops
- ✅ No event loss

**Pass Criteria**: ✅ System handles 100+ connections with acceptable performance

---

## Acceptance Criteria Checklist

After completing all tests, verify:

- [X] T049: Dapr Pub/Sub subscription verified
- [X] T050: Events published to both topics
- [X] T051: WebSocket JWT authentication works
- [ ] T052: Real-time sync within 2 seconds ⭐ PRIMARY TEST
- [ ] T053: Reconnection after network interruption
- [ ] T054: Missed events replayed on reconnect
- [ ] T055: Multi-user synchronization (same user works, groups pending)
- [ ] T056: 100+ concurrent connections handled

**Overall Phase 3 Acceptance**:
- [ ] Task CRUD operations publish events to Kafka via Dapr Pub/Sub
- [ ] WebSocket Sync Service consumes task-updates events and broadcasts to connected clients
- [ ] Frontend establishes WebSocket connection with JWT authentication
- [ ] Task changes appear across all user devices within 2 seconds
- [ ] Reconnection logic replays missed events automatically
- [ ] Connection status indicator shows online/offline/reconnecting states
- [ ] System handles 100+ concurrent WebSocket connections without degradation

---

## Troubleshooting

### Issue: WebSocket connection fails with 1008 Policy Violation

**Cause**: Invalid or missing JWT token

**Solution**:
1. Check browser console for JWT token retrieval
2. Verify Better Auth is configured correctly
3. Check backend JWT_SECRET_KEY matches frontend

### Issue: Events not appearing in Redpanda

**Cause**: Dapr Pub/Sub not configured or Redpanda not running

**Solution**:
```bash
# Check Redpanda is running
docker ps | grep redpanda

# Check Dapr component
cat infrastructure/dapr/pubsub-local.yaml

# Test Dapr Pub/Sub directly
dapr publish --publish-app-id backend-api --pubsub kafka-pubsub --topic task-updates --data '{"test": "message"}'
```

### Issue: WebSocket reconnection not working

**Cause**: Exponential backoff reaching max interval

**Solution**:
1. Check browser console for reconnection attempts
2. Verify WebSocket service is running
3. Check network connectivity
4. Restart WebSocket service if needed

### Issue: Missed events not replayed

**Cause**: Event cache expired or Redis connection issue

**Solution**:
1. Check Redis is running: `docker ps | grep redis`
2. Verify last disconnect time in Redis:
```bash
docker exec -it todo-redis redis-cli
> KEYS ws_last_disconnect:*
> GET ws_last_disconnect:<user_id>
```
3. Check event cache in WebSocket service logs

### Issue: Load test fails with connection errors

**Cause**: Resource limits or connection pool exhaustion

**Solution**:
1. Increase Redis connection pool size in `statestore-local.yaml`
2. Increase system file descriptor limits:
```bash
ulimit -n 10000
```
3. Scale WebSocket service horizontally (multiple instances)

---

## Next Steps

After completing Phase 3 testing:

1. **Document Results**: Update tasks.md with test results
2. **Fix Issues**: Address any failures discovered during testing
3. **Performance Tuning**: Optimize based on load test results
4. **Move to Phase 4**: Begin User Story 2 (Precise Time-Based Task Reminders)

---

**End of Testing Guide**
