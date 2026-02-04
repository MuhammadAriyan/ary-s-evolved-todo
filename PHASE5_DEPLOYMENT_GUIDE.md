# Phase 5: Production-Ready Cloud Deployment - Implementation Guide

## Overview

This document provides comprehensive instructions for deploying the Todo application to Oracle OKE (Oracle Kubernetes Engine) with full CI/CD automation, monitoring, and operational readiness.

## Prerequisites

### Required Tools
- `kubectl` v1.28+
- `helm` v3.13+
- `oci` CLI (Oracle Cloud Infrastructure CLI)
- `docker` (for local testing)
- GitHub account with repository access

### Required Credentials
- Oracle Cloud account with OKE cluster access
- GitHub Personal Access Token (for GHCR)
- Neon PostgreSQL database credentials
- Redis instance credentials
- Redpanda Cloud (Kafka) credentials
- SendGrid API key (for email notifications)
- OpenAI API key (for chat features)

## Architecture

### Microservices
1. **Backend API** - FastAPI REST API with Better Auth
2. **Frontend** - Next.js 15+ with App Router
3. **WebSocket Sync Service** - Real-time synchronization
4. **Notification Service** - Multi-channel notifications

### Infrastructure Components
1. **Dapr Runtime** - Service mesh and event streaming
2. **Prometheus** - Metrics collection and alerting
3. **Grafana** - Visualization and dashboards
4. **Redpanda Cloud** - Kafka-compatible event streaming
5. **Redis** - State store and caching
6. **Neon PostgreSQL** - Primary database

## Deployment Steps

### Step 1: Configure Oracle OKE Cluster

```bash
# Set environment variables
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..your-compartment-id"
export OKE_CLUSTER_NAME="todo-oke-cluster"
export OCI_REGION="us-ashburn-1"

# Run configuration script
cd infrastructure/scripts
./configure-oke.sh
```

This script will:
- Fetch cluster information from Oracle Cloud
- Generate kubeconfig file
- Configure kubectl context
- Verify cluster connectivity

**Expected Output:**
```
✅ Successfully connected to cluster
Kubernetes control plane is running at https://...
✅ Configuration Complete
```

### Step 2: Deploy Dapr Runtime

```bash
# Deploy Dapr with custom components
cd infrastructure/scripts
./deploy-dapr.sh
```

This script will:
- Install Dapr runtime (v1.12+) with HA configuration
- Deploy custom Dapr components:
  - Pub/Sub (Redpanda/Kafka)
  - State Store (Redis)
  - Bindings (Cron for reminders)
  - Secrets (Kubernetes)
- Enable mTLS and metrics

**Verification:**
```bash
kubectl get pods -n dapr-system
kubectl get components -n default
```

### Step 3: Deploy Monitoring Stack

```bash
# Deploy Prometheus and Grafana
cd infrastructure/scripts
./deploy-monitoring.sh
```

This script will:
- Install Prometheus with custom scrape configs
- Install Grafana with pre-configured dashboards
- Deploy alert rules for all services
- Configure data sources

**Access Grafana:**
```bash
# Get admin password
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:80

# Open http://localhost:3000
```

### Step 4: Configure GitHub Secrets

Navigate to your GitHub repository settings and add the following secrets:

#### Oracle OKE Secrets
- `OKE_KUBECONFIG` - Base64-encoded kubeconfig for staging
- `OKE_KUBECONFIG_PROD` - Base64-encoded kubeconfig for production

```bash
# Generate base64-encoded kubeconfig
cat ~/.kube/config | base64 -w 0
```

#### Database and Infrastructure Secrets
- `DATABASE_URL` - Neon PostgreSQL connection string (staging)
- `DATABASE_URL_PROD` - Neon PostgreSQL connection string (production)
- `REDIS_URL` - Redis connection string (staging)
- `REDIS_URL_PROD` - Redis connection string (production)
- `KAFKA_BROKERS` - Redpanda Cloud broker addresses (staging)
- `KAFKA_BROKERS_PROD` - Redpanda Cloud broker addresses (production)
- `KAFKA_USERNAME` - Kafka authentication username (staging)
- `KAFKA_USERNAME_PROD` - Kafka authentication username (production)
- `KAFKA_PASSWORD` - Kafka authentication password (staging)
- `KAFKA_PASSWORD_PROD` - Kafka authentication password (production)

#### Application Secrets
- `BETTER_AUTH_SECRET` - JWT signing secret (staging)
- `BETTER_AUTH_SECRET_PROD` - JWT signing secret (production)
- `OPENAI_API_KEY` - OpenAI API key (staging)
- `OPENAI_API_KEY_PROD` - OpenAI API key (production)
- `SENDGRID_API_KEY` - SendGrid API key (staging)
- `SENDGRID_API_KEY_PROD` - SendGrid API key (production)

### Step 5: Test CI/CD Pipeline

#### 5.1 Test PR Build Workflow

1. Create a feature branch:
```bash
git checkout -b feature/test-deployment
```

2. Make a small change and push:
```bash
echo "# Test" >> README.md
git add README.md
git commit -m "Test: CI/CD pipeline"
git push origin feature/test-deployment
```

3. Create a Pull Request on GitHub

4. Verify the following jobs run successfully:
   - Security Scan (Trivy)
   - Backend Tests
   - Frontend Tests
   - Build Backend API Image
   - Build Frontend Image
   - Build WebSocket Sync Image
   - Build Notification Service Image

**Expected Duration:** 5-10 minutes

#### 5.2 Test Staging Deployment

1. Merge the PR to `main` branch

2. The `deploy-staging.yml` workflow will automatically trigger

3. Monitor the deployment:
```bash
# Watch deployment progress
kubectl get deployments -n staging -w

# Check pod status
kubectl get pods -n staging

# View logs
kubectl logs -f deployment/backend-api -n staging
```

4. Verify health checks:
```bash
# Backend API
curl https://api-staging.todo.example.com/health

# Frontend
curl https://staging.todo.example.com

# WebSocket Sync
curl https://ws-staging.todo.example.com/health
```

**Expected Duration:** 8-12 minutes

#### 5.3 Test Production Deployment

1. Navigate to GitHub Actions → Deploy to Production

2. Click "Run workflow"

3. Enter:
   - **Version:** `main` or specific commit SHA
   - **Confirm:** Type `DEPLOY`

4. Click "Run workflow"

5. The workflow will:
   - Validate deployment request
   - Deploy all services to production namespace
   - Run comprehensive health checks
   - Automatically rollback on failure

6. Monitor deployment:
```bash
# Watch deployment progress
kubectl get deployments -n production -w

# Check HPA status
kubectl get hpa -n production

# View events
kubectl get events -n production --sort-by='.lastTimestamp'
```

**Expected Duration:** 10-15 minutes

### Step 6: Verify Deployment

#### 6.1 Check Service Health

```bash
# Backend API
curl https://api.todo.example.com/health

# Frontend
curl https://todo.example.com

# WebSocket Sync
curl https://ws.todo.example.com/health

# Notification Service (internal)
kubectl exec -it deployment/backend-api -n production -- curl http://notification:8002/health
```

#### 6.2 Check Metrics

Access Grafana dashboards:
- Backend API Metrics: http://grafana.todo.example.com/d/backend-api
- WebSocket Sync Metrics: http://grafana.todo.example.com/d/websocket-sync
- Notification Service Metrics: http://grafana.todo.example.com/d/notification

#### 6.3 Check Logs

```bash
# Backend API logs
kubectl logs -f deployment/backend-api -n production --tail=100

# WebSocket Sync logs
kubectl logs -f deployment/websocket-sync -n production --tail=100

# Notification Service logs
kubectl logs -f deployment/notification -n production --tail=100

# Dapr sidecar logs
kubectl logs -f deployment/backend-api -n production -c daprd --tail=100
```

#### 6.4 Test Real-Time Sync

1. Open two browser tabs to https://todo.example.com
2. Log in with the same user account
3. Create a task in tab 1
4. Verify it appears in tab 2 within 2 seconds

#### 6.5 Test Notifications

1. Create a task with a reminder set for 2 minutes ahead
2. Wait for the reminder time
3. Verify notification arrives within 10 seconds via:
   - Email (check inbox)
   - In-app notification (check browser)

## Monitoring and Observability

### Prometheus Metrics

Access Prometheus: http://prometheus.todo.example.com

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `websocket_active_connections` - Active WebSocket connections
- `notification_delivery_total` - Notification delivery count
- `database_connections_active` - Active database connections

### Grafana Dashboards

Access Grafana: http://grafana.todo.example.com

**Available Dashboards:**
1. **Backend API Metrics** - Request rate, error rate, latency, CPU/memory
2. **WebSocket Sync Metrics** - Active connections, message throughput, delivery latency
3. **Notification Service Metrics** - Delivery rate, success rate, processing lag

### Alerts

Prometheus alerts are configured for:
- High error rate (>5%)
- High latency (p95 >500ms)
- Service down
- High CPU usage (>80%)
- High memory usage (>85%)
- WebSocket connection failures
- Notification delivery failures
- Database connection pool exhaustion

**View Active Alerts:**
http://prometheus.todo.example.com/alerts

## Troubleshooting

### Deployment Failures

**Issue:** Deployment stuck in "Pending" state
```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check resource availability
kubectl top nodes
kubectl describe nodes
```

**Issue:** Health checks failing
```bash
# Check pod logs
kubectl logs <pod-name> -n <namespace>

# Check service endpoints
kubectl get endpoints -n <namespace>

# Test health endpoint from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend-api:8000/health
```

**Issue:** Image pull errors
```bash
# Check image pull secrets
kubectl get secrets -n <namespace>

# Verify image exists
docker pull ghcr.io/your-org/todo-backend-api:latest

# Check GHCR authentication
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Rollback Procedures

**Automatic Rollback:**
CI/CD workflows automatically rollback on health check failures.

**Manual Rollback:**
```bash
# List Helm releases
helm list -n production

# Rollback to previous version
helm rollback backend-api -n production
helm rollback frontend -n production
helm rollback websocket-sync -n production
helm rollback notification -n production

# Verify rollback
kubectl rollout status deployment/backend-api -n production
```

### Performance Issues

**High CPU Usage:**
```bash
# Check HPA status
kubectl get hpa -n production

# Manually scale up
kubectl scale deployment/backend-api --replicas=5 -n production

# Check resource limits
kubectl describe deployment/backend-api -n production
```

**High Memory Usage:**
```bash
# Check memory usage
kubectl top pods -n production

# Restart pods to clear memory leaks
kubectl rollout restart deployment/backend-api -n production
```

**Database Connection Issues:**
```bash
# Check database connectivity
kubectl exec -it deployment/backend-api -n production -- curl $DATABASE_URL

# Check connection pool metrics
curl https://api.todo.example.com/metrics | grep database_connections
```

## Maintenance

### Updating Services

```bash
# Update Backend API
helm upgrade backend-api ./infrastructure/helm/backend \
    --namespace=production \
    --set image.tag=v1.2.0 \
    --wait

# Update Frontend
helm upgrade frontend ./infrastructure/helm/frontend \
    --namespace=production \
    --set image.tag=v1.2.0 \
    --wait
```

### Scaling Services

```bash
# Scale manually
kubectl scale deployment/backend-api --replicas=10 -n production

# Update HPA limits
kubectl patch hpa backend-api -n production -p '{"spec":{"maxReplicas":20}}'
```

### Rotating Secrets

```bash
# Update secret
kubectl create secret generic backend-secrets \
    --from-literal=database-url="new-value" \
    --namespace=production \
    --dry-run=client -o yaml | kubectl apply -f -

# Restart deployments to pick up new secrets
kubectl rollout restart deployment/backend-api -n production
kubectl rollout restart deployment/websocket-sync -n production
kubectl rollout restart deployment/notification -n production
```

## Cost Optimization

### Oracle Cloud Free Tier Limits
- 2 AMD-based Compute VMs (1/8 OCPU, 1 GB memory each)
- 4 Arm-based Ampere A1 cores (24 GB memory total)
- 200 GB Block Volume storage
- 10 GB Object Storage

### Resource Allocation Strategy
- **Production:** Use Arm-based instances (better performance/cost)
- **Staging:** Use AMD-based instances (smaller footprint)
- **Monitoring:** Share resources with staging

### Monitoring Costs
- Prometheus retention: 30 days (adjust based on storage)
- Grafana: Minimal resource usage
- Logs: Use kubectl logs, defer Loki to save resources

## Security Best Practices

1. **Secrets Management:**
   - Never commit secrets to version control
   - Use Kubernetes Secrets with encryption at rest
   - Rotate secrets regularly (every 90 days)

2. **Network Security:**
   - Enable mTLS for Dapr communication
   - Use Network Policies to restrict pod-to-pod traffic
   - Configure Ingress with TLS/SSL certificates

3. **Access Control:**
   - Use RBAC for Kubernetes access
   - Limit service account permissions
   - Enable audit logging

4. **Image Security:**
   - Scan images with Trivy in CI/CD
   - Use minimal base images
   - Keep dependencies up to date

## Support and Resources

### Documentation
- Kubernetes: https://kubernetes.io/docs/
- Helm: https://helm.sh/docs/
- Dapr: https://docs.dapr.io/
- Oracle OKE: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm

### Monitoring
- Prometheus: http://prometheus.todo.example.com
- Grafana: http://grafana.todo.example.com

### Logs
```bash
# View all logs
kubectl logs -l app.kubernetes.io/name=backend-api -n production --tail=100 -f
```

### Contact
For issues or questions, contact the development team or create an issue in the GitHub repository.
