# Staging Deployment Checklist

## Current Environment Status

**Date:** 2026-02-01
**Project:** Ary's Evolutioned Todo - Phase V Event-Driven Cloud Deployment
**Location:** `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo`

### Tool Availability

| Tool | Status | Version | Notes |
|------|--------|---------|-------|
| Docker | ⚠️ Installed but NOT running | v29.1.3 | **ACTION REQUIRED: Start Docker daemon** |
| Minikube | ✅ Installed | v1.37.0 | Ready to use |
| kubectl | ✅ Installed | v1.35.0 | Ready to use |
| Helm | ✅ Installed | v3.19.5 | Ready to use |

### Infrastructure Ready

- ✅ Dockerfiles for all services (Backend, Frontend, 4 microservices)
- ✅ Helm charts for all services
- ✅ Docker Compose configurations (dev and simple)
- ✅ CI/CD workflows (build-test, deploy-staging, deploy-prod)
- ✅ Dapr components configured
- ✅ Monitoring stack (Prometheus, Grafana)

---

## CRITICAL FIRST STEP: Start Docker Daemon

Before any deployment option, Docker must be running.

### Check Docker Status

```bash
docker ps
```

### If Docker is Not Running

**Option 1: Start Docker Desktop (if installed)**
```bash
# On Linux with Docker Desktop
systemctl --user start docker-desktop

# Or launch Docker Desktop from applications menu
```

**Option 2: Start Docker Engine (if using Docker Engine)**
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Enable auto-start on boot

# Add your user to docker group (if not already)
sudo usermod -aG docker $USER
newgrp docker  # Activate group without logout
```

**Option 3: Install Docker Engine (if needed)**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Verify Docker is Running

```bash
docker ps
docker --version
docker info
```

**Expected Output:**
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

---

## Deployment Options

### Option A: Local Staging with Docker Compose (RECOMMENDED)

**Best for:** Quick staging deployment, no cloud needed, fastest setup

**Prerequisites:**
- ✅ Docker daemon running
- ✅ Docker Compose (included with Docker)
- ✅ 8GB RAM available
- ✅ 10GB disk space

**Time to Deploy:** 5-10 minutes

**Services Deployed:**
- PostgreSQL (database)
- Redis (state store)
- Redpanda (Kafka-compatible event streaming)
- Dapr Placement Service
- Backend API
- Frontend
- WebSocket Sync Service
- Notification Service
- Recurring Task Service

**Deployment Steps:**

1. **Start Infrastructure Services**
   ```bash
   cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
   ./scripts/deploy-staging-local.sh
   ```

2. **Verify Services**
   ```bash
   ./scripts/verify-deployment.sh local
   ```

3. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Redpanda Console: http://localhost:8080
   - Health Check: http://localhost:8000/health

**Stopping Services:**
```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure
docker-compose -f docker-compose.dev.yml down
```

**Viewing Logs:**
```bash
# All services
docker-compose -f infrastructure/docker-compose.dev.yml logs -f

# Specific service
docker-compose -f infrastructure/docker-compose.dev.yml logs -f backend-api
```

---

### Option B: Local Kubernetes with Minikube

**Best for:** Testing Kubernetes deployment locally, validating Helm charts

**Prerequisites:**
- ✅ Docker daemon running
- ✅ Minikube installed
- ✅ kubectl installed
- ✅ Helm installed
- ✅ 8GB RAM available
- ✅ 20GB disk space

**Time to Deploy:** 15-20 minutes

**Deployment Steps:**

1. **Start Minikube Cluster**
   ```bash
   cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
   ./scripts/deploy-staging-minikube.sh
   ```

2. **Verify Deployment**
   ```bash
   ./scripts/verify-deployment.sh minikube
   ```

3. **Access Applications**
   ```bash
   # Get service URLs
   minikube service list -n staging

   # Access frontend
   minikube service frontend -n staging

   # Access backend API
   minikube service backend-api -n staging
   ```

**Stopping Minikube:**
```bash
minikube stop
```

**Deleting Cluster:**
```bash
minikube delete
```

**Viewing Logs:**
```bash
# List pods
kubectl get pods -n staging

# View logs
kubectl logs -f deployment/backend-api -n staging
kubectl logs -f deployment/frontend -n staging
```

---

### Option C: Oracle OKE (Cloud Kubernetes)

**Best for:** Production-like staging environment, testing cloud deployment

**Prerequisites:**
- ⚠️ Oracle Cloud account with OKE cluster access
- ⚠️ OCI CLI configured
- ⚠️ Kubeconfig for OKE cluster
- ⚠️ GitHub secrets configured
- ⚠️ External database (Neon PostgreSQL)
- ⚠️ External Redis instance
- ⚠️ Redpanda Cloud account

**Time to Deploy:** 30-45 minutes (including setup)

**Deployment Steps:**

See `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/PHASE5_DEPLOYMENT_GUIDE.md` for detailed instructions.

**Quick Start:**
```bash
# Configure OKE cluster
cd infrastructure/scripts
./configure-oke.sh

# Deploy Dapr
./deploy-dapr.sh

# Deploy monitoring
./deploy-monitoring.sh

# Deploy application (via GitHub Actions)
# Push to main branch or manually trigger deploy-staging workflow
```

---

## Recommended Deployment Path

### For Immediate Testing (Today)

**Use Option A: Docker Compose**

1. Start Docker daemon
2. Run `./scripts/deploy-staging-local.sh`
3. Verify with `./scripts/verify-deployment.sh local`
4. Test application at http://localhost:3000

**Why:** Fastest path to running staging environment, no cloud setup needed.

### For Kubernetes Validation (This Week)

**Use Option B: Minikube**

1. Ensure Docker is running
2. Run `./scripts/deploy-staging-minikube.sh`
3. Verify with `./scripts/verify-deployment.sh minikube`
4. Test Helm charts and K8s configurations

**Why:** Validates Kubernetes deployment locally before cloud deployment.

### For Production-Ready Staging (When Ready)

**Use Option C: Oracle OKE**

1. Set up Oracle Cloud account
2. Configure credentials and secrets
3. Follow PHASE5_DEPLOYMENT_GUIDE.md
4. Deploy via CI/CD pipeline

**Why:** Production-like environment with full cloud infrastructure.

---

## Verification Checklist

### Health Checks

- [ ] Backend API health endpoint responds: `curl http://localhost:8000/health`
- [ ] Frontend loads: `curl http://localhost:3000`
- [ ] Database connection works
- [ ] Redis connection works
- [ ] Kafka/Redpanda connection works

### Functional Tests

- [ ] User can register/login
- [ ] User can create tasks
- [ ] User can update tasks
- [ ] User can delete tasks
- [ ] Real-time sync works (WebSocket)
- [ ] Notifications are sent
- [ ] Recurring tasks are processed

### Performance Tests

- [ ] API response time < 200ms (p95)
- [ ] WebSocket latency < 100ms
- [ ] No memory leaks after 1 hour
- [ ] CPU usage < 50% under normal load

### Monitoring

- [ ] Prometheus metrics available
- [ ] Grafana dashboards accessible
- [ ] Logs are being collected
- [ ] Alerts are configured

---

## Troubleshooting

### Docker Daemon Not Running

**Error:** `failed to connect to the docker API`

**Solution:**
```bash
# Check Docker status
systemctl --user status docker-desktop
# OR
sudo systemctl status docker

# Start Docker
systemctl --user start docker-desktop
# OR
sudo systemctl start docker
```

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Out of Memory

**Error:** `Cannot allocate memory`

**Solution:**
```bash
# Check available memory
free -h

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > Increase to 8GB

# Or reduce services in docker-compose.yml
```

### Database Connection Failed

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs todo-postgres

# Restart PostgreSQL
docker-compose -f infrastructure/docker-compose.dev.yml restart postgres
```

### Minikube Won't Start

**Error:** `Exiting due to PROVIDER_DOCKER_NOT_RUNNING`

**Solution:**
```bash
# Ensure Docker is running
docker ps

# Delete and recreate cluster
minikube delete
minikube start --driver=docker --memory=8192 --cpus=4
```

---

## Next Steps After Staging Deployment

1. **Run Integration Tests**
   ```bash
   cd backend
   pytest tests/integration/
   ```

2. **Load Testing**
   ```bash
   # Install k6 or use Apache Bench
   ab -n 1000 -c 10 http://localhost:8000/api/v1/tasks
   ```

3. **Security Scan**
   ```bash
   # Scan Docker images
   docker scan todo-backend-api:latest

   # Or use Trivy
   trivy image todo-backend-api:latest
   ```

4. **Update Documentation**
   - Document any issues found
   - Update deployment scripts if needed
   - Create runbook for common operations

5. **Prepare for Production**
   - Set up Oracle OKE cluster
   - Configure GitHub secrets
   - Test CI/CD pipeline
   - Set up monitoring and alerts

---

## Support

### Documentation
- Phase 5 Deployment Guide: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/PHASE5_DEPLOYMENT_GUIDE.md`
- Infrastructure README: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/infrastructure/README.md`

### Scripts
- Deploy Local: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/deploy-staging-local.sh`
- Deploy Minikube: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/deploy-staging-minikube.sh`
- Verify Deployment: `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/verify-deployment.sh`

### Logs Location
- Docker Compose: `docker-compose logs`
- Minikube: `kubectl logs -n staging`
- Local files: `/var/log/` (if configured)

---

## Summary

**Current Status:** Ready to deploy to staging with Docker Compose (Option A)

**Blocker:** Docker daemon must be started first

**Recommended Action:**
1. Start Docker daemon
2. Run `./scripts/deploy-staging-local.sh`
3. Verify deployment with `./scripts/verify-deployment.sh local`
4. Test application functionality

**Estimated Time:** 10-15 minutes (including Docker startup)
