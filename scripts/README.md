# Deployment Scripts README

## Overview

This directory contains automated deployment scripts for the Todo application staging environment. All scripts are production-ready and include comprehensive error handling, health checks, and verification steps.

## Scripts

### 1. deploy-staging-local.sh

**Purpose:** Deploy staging environment using Docker Compose

**Usage:**
```bash
./scripts/deploy-staging-local.sh
```

**What it does:**
- Checks Docker daemon is running
- Creates environment files from examples
- Stops any existing containers
- Starts infrastructure services (PostgreSQL, Redis, Redpanda, Dapr)
- Waits for services to be healthy
- Displays access information

**Time:** 5-10 minutes

**Requirements:**
- Docker daemon running
- 8GB RAM available
- 10GB disk space

**Services deployed:**
- PostgreSQL (port 5432)
- Redis (port 6379)
- Redpanda/Kafka (port 19092)
- Redpanda Console (port 8080)
- Dapr Placement (port 50006)

**Note:** Application services (backend, frontend, microservices) need to be started separately.

---

### 2. deploy-staging-minikube.sh

**Purpose:** Deploy full staging environment to local Kubernetes cluster

**Usage:**
```bash
./scripts/deploy-staging-minikube.sh
```

**What it does:**
- Checks prerequisites (Docker, Minikube, kubectl, Helm)
- Starts Minikube cluster with 8GB RAM and 4 CPUs
- Enables required addons (ingress, metrics-server)
- Creates staging namespace
- Builds Docker images in Minikube environment
- Creates Kubernetes secrets
- Deploys infrastructure (PostgreSQL, Redis, Redpanda)
- Installs Dapr runtime
- Deploys Dapr components
- Deploys application services using Helm charts

**Time:** 15-20 minutes

**Requirements:**
- Docker daemon running
- Minikube installed
- kubectl installed
- Helm installed
- 8GB RAM available
- 20GB disk space

**Services deployed:**
- All infrastructure services
- Backend API (with Dapr sidecar)
- Frontend
- WebSocket Sync Service
- Notification Service
- Recurring Task Service

---

### 3. verify-deployment.sh

**Purpose:** Verify staging deployment health and readiness

**Usage:**
```bash
./scripts/verify-deployment.sh [local|minikube]
```

**What it does:**
- Checks deployment type (local or minikube)
- Verifies all services are running
- Tests health endpoints
- Checks port availability
- Displays access commands
- Provides troubleshooting guidance

**Exit codes:**
- 0: All checks passed
- 1: Some checks failed

**Output:**
- Green checkmarks for passing tests
- Red X marks for failing tests
- Yellow warnings for non-critical issues
- Summary with pass/fail counts

---

### 4. start-notification-service.sh

**Purpose:** Start notification microservice with Dapr sidecar

**Usage:**
```bash
./scripts/start-notification-service.sh
```

**What it does:**
- Starts notification service on port 8002
- Configures Dapr sidecar on port 3502
- Enables Pub/Sub for notification events

---

### 5. start-recurring-task-service.sh

**Purpose:** Start recurring task microservice with Dapr sidecar

**Usage:**
```bash
./scripts/start-recurring-task-service.sh
```

**What it does:**
- Starts recurring task service on port 8003
- Configures Dapr sidecar on port 3503
- Enables scheduled task processing

---

## Quick Start

### For Immediate Testing (Docker Compose)

```bash
# 1. Start Docker Desktop (from applications menu)

# 2. Deploy infrastructure
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
./scripts/deploy-staging-local.sh

# 3. Verify deployment
./scripts/verify-deployment.sh local

# 4. Start backend (new terminal)
cd backend
uvicorn app.main:app --reload --port 8000

# 5. Start frontend (new terminal)
cd frontend
npm run dev

# 6. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### For Kubernetes Testing (Minikube)

```bash
# 1. Start Docker Desktop (from applications menu)

# 2. Deploy to Minikube
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
./scripts/deploy-staging-minikube.sh

# 3. Verify deployment
./scripts/verify-deployment.sh minikube

# 4. Access services
minikube service list -n staging
minikube service frontend -n staging
```

---

## Common Operations

### View Logs

**Docker Compose:**
```bash
# All services
docker compose -f infrastructure/docker-compose.dev.yml logs -f

# Specific service
docker compose -f infrastructure/docker-compose.dev.yml logs -f postgres
```

**Minikube:**
```bash
# List pods
kubectl get pods -n staging

# View logs
kubectl logs -f deployment/backend-api -n staging
kubectl logs -f deployment/frontend -n staging

# View Dapr sidecar logs
kubectl logs -f deployment/backend-api -n staging -c daprd
```

### Stop Services

**Docker Compose:**
```bash
cd infrastructure
docker compose -f docker-compose.dev.yml down

# Remove volumes too
docker compose -f docker-compose.dev.yml down -v
```

**Minikube:**
```bash
# Stop cluster
minikube stop

# Delete cluster
minikube delete
```

### Restart Services

**Docker Compose:**
```bash
cd infrastructure
docker compose -f docker-compose.dev.yml restart <service-name>
```

**Minikube:**
```bash
kubectl rollout restart deployment/<deployment-name> -n staging
```

---

## Troubleshooting

### Docker Daemon Not Running

**Error:** `failed to connect to the docker API`

**Solution:**
```bash
# Start Docker Desktop
systemctl --user start docker-desktop

# Or launch from applications menu
```

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Minikube Won't Start

**Error:** `Exiting due to PROVIDER_DOCKER_NOT_RUNNING`

**Solution:**
```bash
# Ensure Docker is running
docker ps

# Delete and recreate
minikube delete
minikube start --driver=docker --memory=8192 --cpus=4
```

### Service Health Check Failing

**Docker Compose:**
```bash
# Check container status
docker ps -a

# View logs
docker logs <container-name>

# Restart service
docker compose -f infrastructure/docker-compose.dev.yml restart <service>
```

**Minikube:**
```bash
# Check pod status
kubectl get pods -n staging

# Describe pod
kubectl describe pod <pod-name> -n staging

# View events
kubectl get events -n staging --sort-by='.lastTimestamp'
```

---

## Environment Variables

### Backend (.env)

Required variables are in `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend/.env.example`

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`: Redis host
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka brokers
- `BETTER_AUTH_SECRET`: JWT secret
- `DAPR_HTTP_PORT`: Dapr HTTP port (3500)

### Frontend (.env.local)

Required variables are in `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend/.env.example`

Key variables:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `BETTER_AUTH_URL`: Auth service URL
- `BETTER_AUTH_SECRET`: JWT secret
- `DATABASE_URL`: PostgreSQL connection string

---

## Architecture

### Docker Compose Deployment

```
┌─────────────────────────────────────────────┐
│           Docker Compose Network            │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │PostgreSQL│  │  Redis   │  │ Redpanda │ │
│  │  :5432   │  │  :6379   │  │  :19092  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │      Dapr Placement Service          │  │
│  │            :50006                    │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         ↑                    ↑
         │                    │
    ┌────────┐          ┌──────────┐
    │Backend │          │ Frontend │
    │ :8000  │          │  :3000   │
    └────────┘          └──────────┘
    (Started manually)
```

### Minikube Deployment

```
┌─────────────────────────────────────────────────────┐
│              Minikube Cluster                       │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │         Namespace: staging                  │  │
│  │                                             │  │
│  │  Infrastructure:                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │PostgreSQL│  │  Redis   │  │ Redpanda │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘ │  │
│  │                                             │  │
│  │  Application Services:                      │  │
│  │  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │  Backend API │  │   Frontend   │       │  │
│  │  │  + Dapr      │  │              │       │  │
│  │  └──────────────┘  └──────────────┘       │  │
│  │                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │ WebSocket    │  │ Notification │       │  │
│  │  │ Sync + Dapr  │  │ Svc + Dapr   │       │  │
│  │  └──────────────┘  └──────────────┘       │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │         Namespace: dapr-system              │  │
│  │  ┌──────────────────────────────────────┐  │  │
│  │  │  Dapr Control Plane Components       │  │  │
│  │  │  (Operator, Sidecar Injector, etc.)  │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### Docker Compose
- **Memory:** 8GB recommended (4GB minimum)
- **CPU:** 4 cores recommended (2 cores minimum)
- **Disk:** 10GB free space
- **Network:** All services on same bridge network (low latency)

### Minikube
- **Memory:** 8GB allocated to Minikube
- **CPU:** 4 cores allocated to Minikube
- **Disk:** 20GB free space
- **Network:** Kubernetes networking (slightly higher latency)

---

## Security Notes

### Development Environment
- Default passwords are used (postgres/postgres)
- Secrets are generated randomly for Minikube
- No TLS/SSL in local environment
- All ports exposed to localhost

### Production Environment
- Use strong, unique passwords
- Store secrets in Kubernetes Secrets or external vault
- Enable TLS/SSL for all external endpoints
- Use Network Policies to restrict traffic
- Enable RBAC for access control

---

## Support

### Documentation
- Staging Deployment Checklist: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/STAGING_DEPLOYMENT_CHECKLIST.md`
- Quick Start Guide: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/QUICK_START_STAGING.md`
- Phase 5 Deployment Guide: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/PHASE5_DEPLOYMENT_GUIDE.md`

### Infrastructure
- Infrastructure README: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure/README.md`
- Helm Charts: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure/helm/`
- Dapr Components: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure/dapr/`

---

## Version History

- **2026-02-01**: Initial creation of deployment scripts
  - deploy-staging-local.sh
  - deploy-staging-minikube.sh
  - verify-deployment.sh
