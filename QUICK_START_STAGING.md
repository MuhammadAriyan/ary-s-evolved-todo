# Quick Start: Deploy Staging in 5 Minutes

## Current Status
- ✅ All deployment scripts created and executable
- ✅ Infrastructure ready (Helm charts, Docker Compose, Dockerfiles)
- ⚠️ **Docker Desktop is installed but not running**

## Immediate Action Required

### Step 1: Start Docker Desktop (1 minute)

**Option A: Launch from Applications Menu**
1. Open your applications menu
2. Search for "Docker Desktop"
3. Click to launch
4. Wait for Docker icon in system tray to show "Docker Desktop is running"

**Option B: Start from Terminal**
```bash
systemctl --user start docker-desktop
```

**Verify Docker is Running:**
```bash
docker ps
```

Expected output: Empty table (no error message)

---

## Step 2: Deploy Staging (5 minutes)

Once Docker is running, choose your deployment option:

### Option A: Docker Compose (Recommended for Quick Start)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
./scripts/deploy-staging-local.sh
```

**What this does:**
- Starts PostgreSQL, Redis, Redpanda, Dapr
- Takes 5-10 minutes
- No cloud credentials needed

**After deployment:**
```bash
# Verify infrastructure
./scripts/verify-deployment.sh local

# Start backend (in new terminal)
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
uvicorn app.main:app --reload --port 8000

# Start frontend (in new terminal)
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Redpanda Console: http://localhost:8080

---

### Option B: Minikube (For Kubernetes Testing)

```bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo
./scripts/deploy-staging-minikube.sh
```

**What this does:**
- Starts Minikube cluster
- Deploys all services to Kubernetes
- Tests Helm charts
- Takes 15-20 minutes

**After deployment:**
```bash
# Verify deployment
./scripts/verify-deployment.sh minikube

# Access services
minikube service list -n staging
minikube service frontend -n staging
```

---

## Step 3: Verify Everything Works

```bash
# Check infrastructure
./scripts/verify-deployment.sh local  # or 'minikube'

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

---

## Troubleshooting

### Docker Won't Start
```bash
# Check status
systemctl --user status docker-desktop

# View logs
journalctl --user -u docker-desktop -n 50
```

### Port Already in Use
```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Services Not Starting
```bash
# View logs (Docker Compose)
docker compose -f infrastructure/docker-compose.dev.yml logs -f

# View logs (Minikube)
kubectl logs -f deployment/backend-api -n staging
```

---

## Files Created

1. **Deployment Checklist** (comprehensive guide)
   `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/STAGING_DEPLOYMENT_CHECKLIST.md`

2. **Deploy Local Script** (Docker Compose)
   `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/deploy-staging-local.sh`

3. **Deploy Minikube Script** (Kubernetes)
   `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/deploy-staging-minikube.sh`

4. **Verify Script** (Health checks)
   `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/scripts/verify-deployment.sh`

5. **This Quick Start Guide**
   `/home/ary/Dev/abc/Ary-s-Evolutioned-Todo/QUICK_START_STAGING.md`

---

## What's Next?

After staging is running:

1. **Run Tests**
   ```bash
   cd backend
   pytest tests/
   ```

2. **Load Testing**
   ```bash
   # Install k6 or use Apache Bench
   ab -n 1000 -c 10 http://localhost:8000/api/v1/tasks
   ```

3. **Prepare for Production**
   - Set up Oracle OKE cluster
   - Configure GitHub secrets
   - Test CI/CD pipeline

---

## Summary

**To deploy staging RIGHT NOW:**

1. Start Docker Desktop (from applications menu)
2. Run: `./scripts/deploy-staging-local.sh`
3. Run: `./scripts/verify-deployment.sh local`
4. Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
5. Start frontend: `cd frontend && npm run dev`
6. Open: http://localhost:3000

**Total time:** 10-15 minutes
