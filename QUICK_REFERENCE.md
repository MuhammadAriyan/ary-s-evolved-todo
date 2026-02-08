# Quick Reference - Deployment Commands

## Prerequisites Check

```bash
# Verify tools are installed
kubectl version --client
helm version
dapr --version
docker --version

# Verify cluster connection
kubectl cluster-info
kubectl config current-context
```

## Local Development

### Start Infrastructure

```bash
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Verify services
docker-compose -f docker-compose.dev.yml ps
```

### Start Backend with Dapr

```bash
cd backend
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../infrastructure/dapr \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

## Kubernetes Deployment

### Quick Deploy (Production)

```bash
cd infrastructure/scripts

# 1. Deploy Dapr runtime
./deploy-dapr.sh

# 2. Create secrets
kubectl create secret generic database-secret-production \
  --from-literal=url="postgresql://user:pass@host:5432/db" \
  -n todo-app-production

# 3. Deploy all microservices
./deploy-microservices.sh production

# 4. Verify deployment
./health-check.sh todo-app-production
```

### Quick Deploy (Staging)

```bash
cd infrastructure/scripts

# Deploy to staging
./deploy-microservices.sh staging

# Verify staging
./health-check.sh todo-app-staging
```

### Deploy Individual Service

```bash
# Deploy specific service
helm upgrade --install audit infrastructure/helm/audit \
  --namespace todo-app-production \
  --create-namespace \
  -f infrastructure/helm/audit/values-production.yaml

# Verify deployment
kubectl rollout status deployment/audit -n todo-app-production
```

### Rollback Deployment

```bash
# Rollback to previous version
./scripts/rollback-microservices.sh audit

# Rollback to specific revision
./scripts/rollback-microservices.sh audit 3

# View history
helm history audit -n todo-app-production
```

## Monitoring & Debugging

### Check Pod Status

```bash
# List all pods
kubectl get pods -n todo-app-production

# Describe pod
kubectl describe pod <pod-name> -n todo-app-production

# View logs
kubectl logs -f deployment/audit -n todo-app-production

# View Dapr sidecar logs
kubectl logs -f deployment/audit -c daprd -n todo-app-production
```

### Check Service Health

```bash
# Run comprehensive health check
./scripts/health-check.sh todo-app-production

# Check specific service endpoint
kubectl port-forward svc/audit 8001:8001 -n todo-app-production
curl http://localhost:8001/health
```

### Check HPA Status

```bash
# View HPA status
kubectl get hpa -n todo-app-production

# Describe HPA
kubectl describe hpa audit -n todo-app-production
```

### Resource Usage

```bash
# Check pod resource usage
kubectl top pods -n todo-app-production

# Check node resource usage
kubectl top nodes
```

### Dapr Dashboard

```bash
# Launch Dapr dashboard
dapr dashboard -k -p 9999

# Access at http://localhost:9999
```

## Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment audit --replicas=5 -n todo-app-production

# Verify scaling
kubectl get deployment audit -n todo-app-production
```

### Update HPA

```bash
# Edit HPA settings
kubectl edit hpa audit -n todo-app-production

# Or update via Helm
helm upgrade audit infrastructure/helm/audit \
  --namespace todo-app-production \
  --set autoscaling.minReplicas=5 \
  --set autoscaling.maxReplicas=15
```

## CI/CD Pipeline

### Trigger Manual Deployment

```bash
# Deploy to production
gh workflow run deploy-microservices.yml \
  -f environment=production

# Deploy specific service to staging
gh workflow run deploy-microservices.yml \
  -f environment=staging \
  -f service=audit
```

### View Workflow Status

```bash
# List workflow runs
gh run list --workflow=deploy-microservices.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app-production

# Check logs
kubectl logs <pod-name> -n todo-app-production

# Check previous logs (if pod restarted)
kubectl logs <pod-name> -n todo-app-production --previous
```

### Service Not Reachable

```bash
# Check service endpoints
kubectl get endpoints -n todo-app-production

# Test connectivity
kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -n todo-app-production -- \
  curl -v http://audit:8001/health
```

### Dapr Issues

```bash
# Check Dapr components
kubectl get components -n todo-app-production

# Check Dapr configuration
kubectl get configuration -n todo-app-production

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app-production
```

### Database Connection Issues

```bash
# Verify secret exists
kubectl get secret database-secret-production -n todo-app-production

# Check secret contents (base64 encoded)
kubectl get secret database-secret-production -n todo-app-production -o yaml

# Test database connection from pod
kubectl exec -it <pod-name> -n todo-app-production -- \
  psql $DATABASE_URL -c "SELECT 1"
```

## Cleanup

### Delete Deployment

```bash
# Delete specific service
helm uninstall audit -n todo-app-production

# Delete all services
helm list -n todo-app-production | awk 'NR>1 {print $1}' | xargs -I {} helm uninstall {} -n todo-app-production

# Delete namespace
kubectl delete namespace todo-app-production
```

### Local Cleanup

```bash
# Stop all containers
docker-compose -f docker-compose.dev.yml down

# Remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.dev.yml down -v
```

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kl='kubectl logs -f'
alias kd='kubectl describe'
alias ke='kubectl exec -it'

# Helm aliases
alias h='helm'
alias hl='helm list'
alias hi='helm install'
alias hu='helm upgrade'
alias hr='helm rollback'

# Dapr aliases
alias ds='dapr status'
alias dd='dapr dashboard'
alias dl='dapr list'

# Project-specific
alias todo-prod='kubectl config set-context --current --namespace=todo-app-production'
alias todo-staging='kubectl config set-context --current --namespace=todo-app-staging'
alias todo-health='./infrastructure/scripts/health-check.sh'
alias todo-deploy='./infrastructure/scripts/deploy-microservices.sh'
```

## Environment Variables

### Required Secrets

```bash
# Production
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export ELASTICSEARCH_URL="http://elasticsearch:9200"
export SENTRY_DSN="https://your-sentry-dsn"

# Staging
export DATABASE_URL_STAGING="postgresql://user:pass@host:5432/db_staging"
export ELASTICSEARCH_URL_STAGING="http://elasticsearch-staging:9200"
```

### GitHub Secrets

Required in GitHub repository settings:

- `KUBECONFIG`: Base64-encoded kubeconfig file
- `SLACK_WEBHOOK`: Slack webhook URL for notifications

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 -w 0
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | Main FastAPI backend |
| Audit | 8001 | Audit logging service |
| Search Indexer | 8002 | Search indexing service |
| Recurring Task | 8003 | Recurring task processor |
| DLQ Handler | 8004 | Dead letter queue handler |
| Frontend | 3000 | Next.js frontend |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache/state store |
| Redpanda | 9092 | Kafka-compatible message broker |
| Redpanda Console | 8080 | Kafka UI |
| Dapr HTTP | 3500 | Dapr HTTP API |
| Dapr gRPC | 50001 | Dapr gRPC API |
| Prometheus | 9090 | Metrics |

## Additional Resources

- [Infrastructure README](infrastructure/README.md) - Comprehensive deployment guide
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Detailed deployment procedures
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Complete implementation details
- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
