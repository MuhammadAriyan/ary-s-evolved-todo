# Quickstart Guide: Phase V Event-Driven Cloud Deployment

**Date**: 2026-01-31
**Feature**: Phase V Event-Driven Cloud Deployment
**Status**: Phase 1 Design Output

## Overview

This guide provides step-by-step instructions for setting up a local development environment for Phase V event-driven microservices architecture with Dapr, Redpanda (Kafka-compatible), Redis, and PostgreSQL.

**Prerequisites:**
- Docker Desktop installed
- Python 3.12+ installed
- Node.js 18+ installed
- kubectl installed
- Dapr CLI installed

---

## Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/arys-evolved-todo.git
cd arys-evolved-todo

# 2. Checkout Phase V branch
git checkout 011-event-driven-microservices

# 3. Start infrastructure services (Docker Compose)
docker-compose -f infrastructure/docker-compose.dev.yml up -d

# 4. Initialize Dapr
dapr init

# 5. Install backend dependencies
cd backend
pip install -r requirements.txt

# 6. Run database migrations
alembic upgrade head

# 7. Start backend with Dapr
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 \
  --components-path ./infrastructure/dapr \
  -- uvicorn src.main:app --reload

# 8. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 9. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Dapr Dashboard: http://localhost:8080
```

---

## Detailed Setup Instructions

### 1. Install Prerequisites

#### Docker Desktop
```bash
# macOS (Homebrew)
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Windows
# Download from https://www.docker.com/products/docker-desktop
```

#### Dapr CLI
```bash
# macOS/Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify installation
dapr --version
```

#### kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Windows (Chocolatey)
choco install kubernetes-cli
```

---

### 2. Infrastructure Setup (Docker Compose)

Create `infrastructure/docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL (Neon local equivalent)
  postgres:
    image: postgres:15-alpine
    container_name: postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: arys_todo_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (Dapr state store)
  redis:
    image: redis:7-alpine
    container_name: redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redpanda (Kafka-compatible)
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    container_name: redpanda-dev
    command:
      - redpanda
      - start
      - --smp 1
      - --memory 1G
      - --reserve-memory 0M
      - --overprovisioned
      - --node-id 0
      - --kafka-addr PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092
    ports:
      - "9092:9092"
      - "29092:29092"
      - "9644:9644"
    volumes:
      - redpanda_data:/var/lib/redpanda/data
    healthcheck:
      test: ["CMD-SHELL", "rpk cluster health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redpanda Console (Kafka UI)
  redpanda-console:
    image: docker.redpanda.com/redpandadata/console:latest
    container_name: redpanda-console-dev
    environment:
      KAFKA_BROKERS: redpanda:29092
    ports:
      - "8081:8080"
    depends_on:
      - redpanda

volumes:
  postgres_data:
  redis_data:
  redpanda_data:
```

Start infrastructure:
```bash
docker-compose -f infrastructure/docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f infrastructure/docker-compose.dev.yml ps

# View logs
docker-compose -f infrastructure/docker-compose.dev.yml logs -f
```

---

### 3. Initialize Dapr

```bash
# Initialize Dapr in standalone mode (local development)
dapr init

# Verify Dapr installation
dapr --version

# Check Dapr components
ls ~/.dapr/components

# Start Dapr dashboard (optional)
dapr dashboard
# Access at http://localhost:8080
```

---

### 4. Configure Dapr Components

Create Dapr component configurations in `infrastructure/dapr/`:

**infrastructure/dapr/pubsub.yaml** (already created in contracts/)
**infrastructure/dapr/statestore.yaml** (already created in contracts/)
**infrastructure/dapr/bindings.yaml** (already created in contracts/)
**infrastructure/dapr/secrets.yaml** (already created in contracts/)

Copy from contracts to infrastructure:
```bash
mkdir -p infrastructure/dapr
cp specs/011-event-driven-microservices/contracts/dapr/*.yaml infrastructure/dapr/
```

Update component configurations for local development:

```bash
# Update pubsub.yaml for local Redpanda
sed -i 's/redpanda-cloud-broker.example.com:9092/localhost:9092/g' infrastructure/dapr/pubsub.yaml
sed -i 's/authType: "password"/authType: "none"/g' infrastructure/dapr/pubsub.yaml

# Update statestore.yaml for local Redis
sed -i 's/redis-master.default.svc.cluster.local:6379/localhost:6379/g' infrastructure/dapr/statestore.yaml
```

---

### 5. Backend Setup

#### Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### Configure Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/arys_todo_dev

# Better Auth
JWT_SECRET=your-jwt-secret-key-here
AUTH_URL=http://localhost:8000/api/auth

# Dapr
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# Redis (via Dapr)
REDIS_STATE_STORE=redis-state

# Kafka (via Dapr)
KAFKA_PUBSUB=kafka-pubsub

# Email (optional for local dev)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@localhost

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Add Phase V tables"

# Review migration file
# Edit if needed: alembic/versions/xxx_add_phase_v_tables.py

# Apply migrations
alembic upgrade head

# Verify tables created
psql postgresql://postgres:postgres@localhost:5432/arys_todo_dev -c "\dt"
```

#### Seed Development Data (Optional)

```bash
# Run seed script
python scripts/seed_dev_data.py
```

---

### 6. Start Backend Services

#### Option A: Backend API with Dapr

```bash
cd backend

# Start backend API with Dapr sidecar
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  --log-level debug \
  -- uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Microservices with Dapr (Multi-Terminal)

**Terminal 1: Backend API**
```bash
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 \
  --components-path ../infrastructure/dapr \
  -- uvicorn src.main:app --reload
```

**Terminal 2: WebSocket Sync Service**
```bash
dapr run --app-id websocket-sync --app-port 8001 --dapr-http-port 3501 \
  --components-path ../infrastructure/dapr \
  -- python microservices/websocket_sync/main.py
```

**Terminal 3: Notification Service**
```bash
dapr run --app-id notification-service --app-port 8002 --dapr-http-port 3502 \
  --components-path ../infrastructure/dapr \
  -- python microservices/notification/main.py
```

**Terminal 4: Recurring Task Service**
```bash
dapr run --app-id recurring-task-service --app-port 8003 --dapr-http-port 3503 \
  --components-path ../infrastructure/dapr \
  -- python microservices/recurring_task/main.py
```

**Terminal 5: Audit Service**
```bash
dapr run --app-id audit-service --app-port 8004 --dapr-http-port 3504 \
  --components-path ../infrastructure/dapr \
  -- python microservices/audit/main.py
```

---

### 7. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8001
NEXT_PUBLIC_AUTH_URL=http://localhost:8000/api/auth
```

Start frontend:

```bash
npm run dev
```

Access at http://localhost:3000

---

### 8. Verify Setup

#### Check Services

```bash
# Check Docker containers
docker ps

# Check Dapr components
dapr components -k

# Check backend API
curl http://localhost:8000/health

# Check Dapr sidecar
curl http://localhost:3500/v1.0/healthz
```

#### Test Event Publishing

```bash
# Publish test event via Dapr
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.created",
    "event_id": "test-123",
    "timestamp": "2026-01-31T14:30:00Z",
    "task_id": "task-test",
    "user_id": "user-test",
    "task_data": {
      "title": "Test Task",
      "status": "pending"
    }
  }'
```

#### Test State Store

```bash
# Save state via Dapr
curl -X POST http://localhost:3500/v1.0/state/redis-state \
  -H "Content-Type: application/json" \
  -d '[{
    "key": "test-key",
    "value": "test-value"
  }]'

# Get state via Dapr
curl http://localhost:3500/v1.0/state/redis-state/test-key
```

#### View Kafka Topics

Access Redpanda Console at http://localhost:8081

---

### 9. Development Workflow

#### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/unit -v

# Backend integration tests
pytest tests/integration -v

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

#### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (development only!)
alembic downgrade base
alembic upgrade head
```

#### Viewing Logs

```bash
# Dapr logs
dapr logs --app-id backend-api

# Docker logs
docker-compose -f infrastructure/docker-compose.dev.yml logs -f postgres
docker-compose -f infrastructure/docker-compose.dev.yml logs -f redis
docker-compose -f infrastructure/docker-compose.dev.yml logs -f redpanda

# Application logs
tail -f backend/logs/app.log
```

---

### 10. Troubleshooting

#### Dapr Not Starting

```bash
# Reinitialize Dapr
dapr uninstall
dapr init

# Check Dapr status
dapr --version
docker ps | grep dapr
```

#### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql postgresql://postgres:postgres@localhost:5432/arys_todo_dev -c "SELECT 1"

# Reset database
docker-compose -f infrastructure/docker-compose.dev.yml down -v
docker-compose -f infrastructure/docker-compose.dev.yml up -d postgres
```

#### Kafka/Redpanda Issues

```bash
# Check Redpanda is running
docker ps | grep redpanda

# View Redpanda logs
docker logs redpanda-dev

# List topics
docker exec -it redpanda-dev rpk topic list

# Create topic manually
docker exec -it redpanda-dev rpk topic create task-events --partitions 3
```

#### Port Conflicts

```bash
# Check what's using a port
lsof -i :8000  # Backend API
lsof -i :3000  # Frontend
lsof -i :3500  # Dapr HTTP
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :9092  # Kafka

# Kill process using port
kill -9 <PID>
```

---

### 11. Useful Commands

#### Dapr

```bash
# List running Dapr apps
dapr list

# Stop Dapr app
dapr stop --app-id backend-api

# Invoke Dapr service
dapr invoke --app-id backend-api --method health --verb GET

# Publish event
dapr publish --publish-app-id backend-api --pubsub kafka-pubsub --topic task-events --data '{"test": true}'
```

#### Docker Compose

```bash
# Start all services
docker-compose -f infrastructure/docker-compose.dev.yml up -d

# Stop all services
docker-compose -f infrastructure/docker-compose.dev.yml down

# Restart service
docker-compose -f infrastructure/docker-compose.dev.yml restart postgres

# View logs
docker-compose -f infrastructure/docker-compose.dev.yml logs -f

# Remove volumes (reset data)
docker-compose -f infrastructure/docker-compose.dev.yml down -v
```

#### Database

```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@localhost:5432/arys_todo_dev

# Dump database
pg_dump postgresql://postgres:postgres@localhost:5432/arys_todo_dev > backup.sql

# Restore database
psql postgresql://postgres:postgres@localhost:5432/arys_todo_dev < backup.sql
```

---

### 12. Next Steps

After completing local setup:

1. **Review Architecture**: Read `specs/011-event-driven-microservices/plan.md`
2. **Understand Data Model**: Review `specs/011-event-driven-microservices/data-model.md`
3. **Study Event Schemas**: Check `specs/011-event-driven-microservices/contracts/events.yaml`
4. **Explore API**: Review `specs/011-event-driven-microservices/contracts/api.yaml`
5. **Start Implementation**: Follow tasks in `specs/011-event-driven-microservices/tasks.md` (to be created)

---

### 13. Resources

- **Dapr Documentation**: https://docs.dapr.io/
- **Redpanda Documentation**: https://docs.redpanda.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/

---

### 14. Development Tips

1. **Use Dapr Dashboard**: Monitor services, components, and events at http://localhost:8080
2. **Use Redpanda Console**: View Kafka topics and messages at http://localhost:8081
3. **Enable Debug Logging**: Set `DEBUG=true` in `.env` for detailed logs
4. **Use Hot Reload**: Both backend (uvicorn --reload) and frontend (npm run dev) support hot reload
5. **Test Events**: Use Dapr CLI or Redpanda Console to publish test events
6. **Monitor State**: Use Redis CLI to inspect state store: `redis-cli -h localhost -p 6379`

---

## Summary

You now have a complete local development environment for Phase V event-driven microservices architecture with:

- ✅ PostgreSQL database (Neon local equivalent)
- ✅ Redis state store (Dapr state management)
- ✅ Redpanda (Kafka-compatible event streaming)
- ✅ Dapr runtime (Pub/Sub, State, Bindings, Secrets)
- ✅ Backend API with FastAPI
- ✅ Frontend with Next.js
- ✅ 4 Event-driven microservices

**Happy coding! 🚀**
