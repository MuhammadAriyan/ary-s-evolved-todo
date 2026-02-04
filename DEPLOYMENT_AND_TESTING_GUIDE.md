# Phase V - Complete Deployment & Testing Guide

## Current Status

✅ **Infrastructure**: All services running and healthy
✅ **Code**: 175/175 tasks implemented (100%)
✅ **Dependencies**: Backend venv ready, frontend node_modules ready

---

## 🚀 Quick Start (3 Commands in 3 Terminals)

### Terminal 1: Backend API
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Wait for:** `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend
npm run dev
```

**Wait for:** `▲ Next.js 15.x ready on http://localhost:3000`

### Terminal 3: Verify & Test
```bash
# Wait 30 seconds for services to start, then run:

# 1. Check backend health
curl http://localhost:8000/health | python3 -m json.tool

# 2. Check frontend
curl http://localhost:3000

# 3. Open in browser
xdg-open http://localhost:3000
```

---

## 🧪 Integration Testing (After Services Start)

### Test Suite 1: Infrastructure (Run Now)
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo

# PostgreSQL
docker exec todo-postgres psql -U postgres -d todo_db -c "SELECT COUNT(*) FROM tasks;"

# Redis
docker exec todo-redis redis-cli ping

# Kafka topics
docker exec todo-redpanda rpk topic list
```

### Test Suite 2: Backend API (After Backend Starts)
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
source venv/bin/activate

# Health check
curl http://localhost:8000/health

# API docs
xdg-open http://localhost:8000/docs

# Run integration tests
pytest tests/integration/ -v --cov=app
```

### Test Suite 3: Frontend E2E (After Both Start)
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e
```

### Test Suite 4: Manual E2E Testing

**Test 1: Real-Time Sync (US1)**
1. Open http://localhost:3000 in two browser tabs
2. Log in with same user in both tabs
3. Create task in tab 1
4. ✓ Verify it appears in tab 2 within 2 seconds

**Test 2: Reminders (US2)**
1. Create task with reminder 2 minutes ahead
2. Wait for reminder time
3. ✓ Verify notification arrives within 10 seconds

**Test 3: Search (US4)**
1. Create 10+ tasks with various titles
2. Search for "meeting"
3. ✓ Verify results in <1 second

---

## 📊 Frontend Architecture Answer

### Does Frontend Use Dapr? ❌ NO

**Frontend uses:**
- HTTP REST API calls to Backend API (port 8000)
- WebSocket connection to WebSocket Sync Service (port 8001)
- Standard browser APIs (fetch, WebSocket)

**Frontend does NOT use:**
- Dapr SDK (server-side only)
- Kafka client (server-side only)
- Direct event streaming

### Does Frontend Use Kafka? ❌ NO

**Event Flow:**
```
Frontend → HTTP → Backend API → Dapr → Kafka
Frontend ← WebSocket ← WebSocket Service ← Dapr ← Kafka
```

**Why This Design?**
- Browsers cannot connect directly to Kafka (TCP protocol, security)
- Dapr is a server-side runtime (not for browsers)
- WebSocket provides real-time updates from Kafka events
- Backend services handle all event-driven complexity

---

## ✅ What Frontend DOES Use

1. **Next.js 15** - React framework with App Router
2. **TanStack React Query** - Data fetching and caching
3. **Better Auth** - Authentication (JWT tokens)
4. **WebSocket (native)** - Real-time updates
5. **Fetch API** - HTTP REST calls
6. **Tailwind CSS** - Styling
7. **Framer Motion** - Animations

---

## 🎯 Summary

**Frontend Architecture:**
- ✅ Standard web application (Next.js + React)
- ✅ Communicates via HTTP REST and WebSocket
- ❌ Does NOT directly use Dapr or Kafka
- ✅ Receives real-time updates through WebSocket (which connects to Kafka via backend services)

**This is the CORRECT architecture for web applications.**

---

## Next Steps

1. **Start Services** (use the 3 terminal commands above)
2. **Run Tests** (follow the test suites above)
3. **Verify Functionality** (manual E2E testing)

Ready to proceed?
