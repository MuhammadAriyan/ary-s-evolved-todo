# Infrastructure Setup Guide

This directory contains all infrastructure configurations for Phase V Event-Driven Cloud Deployment.

## Directory Structure

```
infrastructure/
├── dapr/                    # Dapr component configurations
│   ├── pubsub-local.yaml    # Kafka/Redpanda Pub/Sub (local)
│   ├── statestore-local.yaml # Redis state store (local)
│   ├── bindings-local.yaml  # Cron bindings (local)
│   └── secrets-local.yaml   # Local file-based secrets
├── helm/                    # Helm charts for Kubernetes deployment
│   ├── backend/             # Backend API Helm chart
│   ├── frontend/            # Frontend Helm chart
│   ├── websocket-sync/      # WebSocket Sync Service Helm chart
│   ├── notification/        # Notification Service Helm chart
│   ├── recurring-task/      # Recurring Task Service Helm chart
│   ├── audit/               # Audit Service Helm chart
│   ├── dapr/                # Dapr runtime Helm chart
│   ├── prometheus/          # Prometheus monitoring Helm chart
│   └── grafana/             # Grafana dashboards Helm chart
├── monitoring/              # Monitoring configurations
│   ├── prometheus.yaml      # Prometheus scrape configs
│   ├── grafana-dashboards/  # Grafana dashboard JSON files
│   └── alerts.yaml          # Prometheus alert rules
├── ci-cd/                   # CI/CD configurations
├── docker-compose.dev.yml   # Local development environment
└── README.md                # This file
```

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (or Docker Engine + Docker Compose)
- **Dapr CLI** (v1.12+)
- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL Client** (psql) - optional, for database access

### Installation Commands

```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

# Verify Dapr installation
dapr --version

# Initialize Dapr (installs runtime components)
dapr init

# Verify Python version
python --version  # Should be 3.12+

# Verify Node.js version
node --version  # Should be 20+
```

## Local Development Setup

### Step 1: Start Infrastructure Services

Start PostgreSQL, Redis, Redpanda, and Dapr Placement Service:

```bash
# From project root
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Verify all services are running
docker-compose -f docker-compose.dev.yml ps

# Expected output:
# - todo-postgres (healthy)
# - todo-redis (healthy)
# - todo-redpanda (healthy)
# - todo-redpanda-console (running)
# - todo-dapr-placement (running)
```

### Step 2: Configure Environment Variables

```bash
# Backend
cd ../backend
cp .env.example .env
# Edit .env and update values as needed

# Frontend
cd ../frontend
cp .env.example .env.local
# Edit .env.local and update values as needed
```

### Step 3: Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### Step 4: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### Step 5: Seed Development Data (Optional)

```bash
cd backend
python scripts/seed_dev_data.py
```

### Step 6: Start Backend API with Dapr

```bash
cd backend

# Start backend with Dapr sidecar
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 8: Start Microservices (Optional - for Phase 3+)

```bash
# WebSocket Sync Service
cd backend/microservices/websocket_sync
dapr run \
  --app-id websocket-sync \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Notification Service
cd backend/microservices/notification
dapr run \
  --app-id notification-service \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Recurring Task Service
cd backend/microservices/recurring_task
dapr run \
  --app-id recurring-task-service \
  --app-port 8003 \
  --dapr-http-port 3503 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Audit Service
cd backend/microservices/audit
dapr run \
  --app-id audit-service \
  --app-port 8004 \
  --dapr-http-port 3504 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py
```

## Accessing Services

Once all services are running, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redpanda Console**: http://localhost:8080 (Kafka UI)
- **Dapr Dashboard**: http://localhost:8080 (run `dapr dashboard`)

## Useful Commands

### Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Stop all services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.dev.yml logs -f postgres

# Restart a service
docker-compose -f docker-compose.dev.yml restart redis

# Remove all data (WARNING: deletes volumes)
docker-compose -f docker-compose.dev.yml down -v
```

### Dapr

```bash
# Check Dapr status
dapr status

# View Dapr dashboard
dapr dashboard

# View logs for a Dapr app
dapr logs --app-id backend-api

# Stop a Dapr app
dapr stop --app-id backend-api

# List running Dapr apps
dapr list
```

### Database

```bash
# Connect to PostgreSQL
docker exec -it todo-postgres psql -U postgres -d todo_dev

# Run migrations
cd backend
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "Description"

# View migration history
alembic history
```

### Kafka/Redpanda

```bash
# List topics
docker exec -it todo-redpanda rpk topic list

# Create topic
docker exec -it todo-redpanda rpk topic create task-events

# Consume messages from topic
docker exec -it todo-redpanda rpk topic consume task-events

# Produce test message
docker exec -it todo-redpanda rpk topic produce task-events
```

### Redis

```bash
# Connect to Redis CLI
docker exec -it todo-redis redis-cli

# View all keys
docker exec -it todo-redis redis-cli KEYS '*'

# Get value for key
docker exec -it todo-redis redis-cli GET "ws:user:user-1"

# Flush all data (WARNING: deletes all data)
docker exec -it todo-redis redis-cli FLUSHALL
```

## Troubleshooting

### Port Conflicts

If you encounter port conflicts, update the port mappings in `docker-compose.dev.yml`:

```yaml
ports:
  - "5433:5432"  # Change 5432 to 5433 if PostgreSQL is already running
```

### Dapr Initialization Issues

```bash
# Uninstall Dapr
dapr uninstall

# Reinstall Dapr
dapr init
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# View PostgreSQL logs
docker-compose -f docker-compose.dev.yml logs postgres

# Verify connection string in .env
echo $DATABASE_URL
```

### Redpanda Not Starting

```bash
# Check Redpanda logs
docker-compose -f docker-compose.dev.yml logs redpanda

# Restart Redpanda
docker-compose -f docker-compose.dev.yml restart redpanda

# If issues persist, remove volume and restart
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

## Development Workflow

### Making Changes

1. **Backend Changes**: Edit files in `backend/`, server auto-reloads with `--reload` flag
2. **Frontend Changes**: Edit files in `frontend/`, Next.js auto-reloads
3. **Database Schema Changes**: Create Alembic migration, run `alembic upgrade head`
4. **Dapr Component Changes**: Edit files in `infrastructure/dapr/`, restart Dapr apps

### Testing Event-Driven Features

```bash
# Publish test event to Kafka
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "task.created", "task_id": "test-123", "user_id": "user-1"}'

# Check Redis state
docker exec -it todo-redis redis-cli GET "ws:user:user-1"

# View Kafka messages in Redpanda Console
# Open http://localhost:8080 in browser
```

## Next Steps

1. Complete Phase 1 setup (this guide)
2. Implement Phase 2 foundational components
3. Build Phase 3 real-time sync features
4. Add Phase 4 reminder notifications
5. Deploy to Oracle OKE (Phase 5)

## Additional Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

## Kubernetes Deployment (Production)

### Prerequisites for Kubernetes Deployment

- **kubectl** (v1.28+): Kubernetes command-line tool
- **Helm** (v3.13+): Kubernetes package manager
- **Docker** (v24+): Container runtime
- **Dapr CLI** (v1.12+): Dapr command-line tool

### Installation

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
kubectl version --client
helm version
```

### Quick Start - Kubernetes Deployment

#### 1. Deploy Dapr Runtime

```bash
cd infrastructure/scripts
./deploy-dapr.sh
```

#### 2. Create Kubernetes Secrets

```bash
# Database credentials
kubectl create secret generic database-secret-production \
  --from-literal=url="postgresql://user:password@host:5432/dbname" \
  -n todo-app-production

# Search service credentials
kubectl create secret generic search-secret-production \
  --from-literal=elasticsearch-url="http://elasticsearch:9200" \
  -n todo-app-production

# Monitoring credentials
kubectl create secret generic monitoring-secrets \
  --from-literal=sentry-dsn="https://your-sentry-dsn" \
  -n todo-app-production
```

#### 3. Deploy All Microservices

```bash
cd infrastructure/scripts
./deploy-microservices.sh production
```

#### 4. Verify Deployment

```bash
./health-check.sh todo-app-production
```

### Deployment Scripts

#### Deploy Microservices

```bash
# Deploy to staging
./scripts/deploy-microservices.sh staging

# Deploy to production
./scripts/deploy-microservices.sh production

# Deploy specific service
helm upgrade --install audit helm/audit \
  --namespace todo-app-production \
  --create-namespace \
  -f helm/audit/values-production.yaml
```

#### Rollback Deployments

```bash
# Rollback specific service to previous version
./scripts/rollback-microservices.sh audit

# Rollback to specific revision
./scripts/rollback-microservices.sh audit 3

# View rollback history
helm history audit -n todo-app-production
```

#### Health Checks

```bash
# Run comprehensive health checks
./scripts/health-check.sh todo-app-production

# Check specific deployment
kubectl rollout status deployment/audit -n todo-app-production

# View pod status
kubectl get pods -n todo-app-production
```

### Helm Charts

Each microservice has a complete Helm chart:

- **audit**: Audit logging service
- **search-indexer**: Search indexing service
- **dlq-handler**: Dead Letter Queue handler
- **recurring-task**: Recurring task processor

#### Chart Structure

```
helm/<service>/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default values
├── values-staging.yaml        # Staging overrides
├── values-production.yaml     # Production overrides
└── templates/
    ├── deployment.yaml        # Deployment config
    ├── service.yaml           # Service config
    ├── serviceaccount.yaml    # Service account
    ├── hpa.yaml               # Horizontal Pod Autoscaler
    └── _helpers.tpl           # Template helpers
```

#### Customizing Deployments

Edit environment-specific values:

```yaml
# helm/audit/values-production.yaml
replicaCount: 3

resources:
  limits:
    cpu: 1000m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
```

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy-microservices.yml`) automates:

1. **Build**: Build Docker images for all microservices
2. **Push**: Push images to GitHub Container Registry
3. **Deploy**: Deploy to Kubernetes using Helm
4. **Health Check**: Verify deployment health
5. **Rollback**: Automatic rollback on failure

#### Required GitHub Secrets

- `KUBECONFIG`: Base64-encoded kubeconfig file
- `SLACK_WEBHOOK`: Slack webhook URL for notifications

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 -w 0
```

#### Manual Workflow Trigger

```bash
# Trigger deployment via GitHub CLI
gh workflow run deploy-microservices.yml \
  -f environment=production \
  -f service=audit
```

### Monitoring and Observability

#### Metrics

Each service exposes Prometheus metrics on port 9090:

```bash
# Port-forward to access metrics
kubectl port-forward svc/audit 9090:9090 -n todo-app-production

# Access metrics
curl http://localhost:9090/metrics
```

#### Logs

```bash
# View service logs
kubectl logs -f deployment/audit -n todo-app-production

# View Dapr sidecar logs
kubectl logs -f deployment/audit -c daprd -n todo-app-production

# View logs from all pods
kubectl logs -l app.kubernetes.io/name=audit -n todo-app-production --tail=100
```

#### Dapr Dashboard

```bash
# Launch Dapr dashboard for Kubernetes
dapr dashboard -k -p 9999

# Access at http://localhost:9999
```

### Scaling

#### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment audit --replicas=5 -n todo-app-production

# Verify scaling
kubectl get deployment audit -n todo-app-production
```

#### Horizontal Pod Autoscaling

HPA is configured in production:

```bash
# Check HPA status
kubectl get hpa -n todo-app-production

# Describe HPA
kubectl describe hpa audit -n todo-app-production
```

### Troubleshooting Kubernetes Deployments

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app-production

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app-production

# Check pod logs
kubectl logs <pod-name> -n todo-app-production
```

#### Service Not Reachable

```bash
# Check service endpoints
kubectl get endpoints -n todo-app-production

# Test service connectivity
kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -n todo-app-production -- \
  curl -v http://audit:8001/health
```

#### Dapr Sidecar Issues

```bash
# Check Dapr sidecar status
kubectl logs <pod-name> -c daprd -n todo-app-production

# Verify Dapr components
kubectl get components -n todo-app-production

# Check Dapr configuration
kubectl get configuration -n todo-app-production
```

## Support

For issues or questions:

### Local Development
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Check Dapr logs: `dapr logs --app-id <app-id>`
4. Consult the project documentation in `specs/011-event-driven-microservices/`

### Kubernetes Deployment
1. Run health checks: `./scripts/health-check.sh todo-app-production`
2. Check pod logs: `kubectl logs <pod-name> -n todo-app-production`
3. Review Dapr dashboard: `dapr dashboard -k`
4. Consult deployment documentation above
