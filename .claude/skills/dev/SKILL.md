---
name: dev
description: Start both frontend and backend development servers
---

# Skill: dev

Starts all development services for Ary's Evolved Todo application.

## What this skill does

1. **Checks infrastructure services** (Docker containers)
   - PostgreSQL (Neon-compatible local instance)
   - Redis (state store)
   - Redpanda (Kafka-compatible event streaming)
   - Dapr Placement service

2. **Starts infrastructure if needed**
   - Uses `docker compose -f infrastructure/docker-compose.dev.yml up -d`
   - Waits for services to be healthy

3. **Starts backend with Dapr**
   - Activates Python virtual environment
   - Runs backend with Dapr sidecar on port 8000
   - Dapr HTTP port: 3500
   - Dapr gRPC port: 50001

4. **Starts frontend**
   - Runs Next.js development server on port 3000

5. **Verifies all services are running**
   - Checks backend health endpoint
   - Confirms frontend is responding

## Usage

```bash
/dev
```

## Service URLs

After running this skill, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **Dapr HTTP**: http://localhost:3500

## Prerequisites

- Docker Desktop running
- Dapr CLI installed and initialized
- Python virtual environment set up in `backend/venv`
- Node.js and npm installed

## Troubleshooting

### Port conflicts
- Port 8080 (Redpanda Console) may conflict - this is optional and can be ignored
- Ports 3000, 8000, 3500, 50001 must be free

### Services not starting
- Check Docker Desktop is running: `docker ps`
- Check Dapr is initialized: `dapr --version`
- Check Python venv exists: `ls backend/venv`

### Authentication issues
- Verify BETTER_AUTH_URL in `backend/.env` matches frontend port (3000)
- Check CORS_ORIGINS includes `http://localhost:3000`

## Implementation

When this skill is invoked, execute the following steps:

### Step 1: Check and start infrastructure

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure
docker compose -f docker-compose.dev.yml up -d
```

Wait 5 seconds for services to initialize.

### Step 2: Start backend with Dapr (background)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
source venv/bin/activate
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  --log-level info \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run this in background and capture the task ID.

### Step 3: Start frontend (background)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend
npm run dev
```

Run this in background and capture the task ID.

### Step 4: Wait for services to be ready

Wait 10 seconds for backend and frontend to fully start.

### Step 5: Verify services

```bash
# Check backend health
curl -s http://localhost:8000/health | jq .

# Check frontend is responding
curl -s http://localhost:3000 | grep -o "<title>.*</title>"
```

### Step 6: Display status

Show a summary of all running services:
- Infrastructure containers (docker ps)
- Backend health status
- Frontend status
- Service URLs

## Notes

- All services run in background
- Use `pkill -f uvicorn` to stop backend
- Use `pkill -f next` to stop frontend
- Use `docker compose -f infrastructure/docker-compose.dev.yml down` to stop infrastructure
- Backend and frontend logs are written to `/tmp/claude/...` files
