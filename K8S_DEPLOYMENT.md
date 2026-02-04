# Kubernetes Deployment Guide for Evolved Todo

## Overview

This guide documents the successful deployment of Evolved Todo to Minikube with high availability (2 replicas each for frontend and backend).

**Deployment Date**: 2026-01-22
**Kubernetes Version**: v1.35.0
**Minikube Version**: v1.37.0
**Helm Version**: v3.19.5

## Prerequisites

- Docker 29.1.3+
- Minikube v1.37.0+
- Helm v3.19.5+
- kubectl v1.35.0+

## Deployment Architecture

### Components

1. **Backend (FastAPI)**
   - Image: `evolved-todo/api:local`
   - Replicas: 2
   - Port: 8000
   - Resources: CPU 250m-500m, Memory 256Mi-512Mi
   - Health checks: `/health` (liveness), `/health/ready` (readiness)

2. **Frontend (Next.js)**
   - Image: `evolved-todo/web:local`
   - Replicas: 2
   - Port: 3000
   - Resources: CPU 200m-400m, Memory 256Mi-512Mi
   - Health checks: `/api/health` (liveness and readiness)

3. **Database**
   - External Neon PostgreSQL (serverless)
   - Connection via SSL

4. **Ingress**
   - NGINX Ingress Controller
   - Host: `todo.local`
   - Routes:
     - `/` → Frontend (port 3000)
     - `/api` → Backend (port 8000)

## Deployment Steps

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### 2. Configure Docker Environment

```bash
eval $(minikube docker-env)
```

### 3. Build Docker Images

```bash
# Build backend image
docker build -t evolved-todo/api:local backend/

# Build frontend image
docker build -t evolved-todo/web:local frontend/
```

**Image Sizes:**
- Backend: ~498MB
- Frontend: ~245MB

### 4. Enable Ingress Addon

```bash
minikube addons enable ingress
```

### 5. Create Secrets Configuration

Copy the example secrets file and fill in actual values:

```bash
cp k8s/evolved-todo-chart/secrets-values.yaml.example k8s/evolved-todo-chart/secrets-values.yaml
```

Edit `k8s/evolved-todo-chart/secrets-values.yaml` with your actual secrets:
- `databaseUrl`: Neon PostgreSQL connection string
- `jwtSecretKey`: JWT secret for authentication
- `betterAuthSecret`: Better Auth secret
- `openaiApiKey`: OpenAI/OpenRouter API key

### 6. Deploy with Helm

```bash
helm install evolved-todo k8s/evolved-todo-chart/ \
  -f k8s/evolved-todo-chart/secrets-values.yaml \
  --namespace default
```

### 7. Verify Deployment

```bash
# Check pods
kubectl get pods -l app=evolved-todo

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx-xxxxx         1/1     Running   0          5m
# backend-xxxxx-xxxxx         1/1     Running   0          5m
# frontend-xxxxx-xxxxx        1/1     Running   0          5m
# frontend-xxxxx-xxxxx        1/1     Running   0          5m

# Check services
kubectl get services -l app=evolved-todo

# Check ingress
kubectl get ingress
```

### 8. Configure Local Access

**IMPORTANT**: Add the following entry to your `/etc/hosts` file:

```bash
# Get Minikube IP
minikube ip
# Output: 192.168.49.2

# Add to /etc/hosts (requires sudo)
sudo sh -c 'echo "192.168.49.2 todo.local" >> /etc/hosts'
```

**Alternative**: Test using the Minikube IP directly with Host header:

```bash
curl -H "Host: todo.local" http://192.168.49.2/
```

## Accessing the Application

### Web Interface

Open your browser and navigate to:
- **Frontend**: http://todo.local
- **Backend API**: http://todo.local/api
- **API Docs**: http://todo.local/api/docs

### Testing Endpoints

```bash
# Test frontend health
curl -H "Host: todo.local" http://192.168.49.2/api/health

# Test backend health
curl -H "Host: todo.local" http://192.168.49.2/api/v1/health

# Test frontend root
curl -H "Host: todo.local" http://192.168.49.2/
```

## High Availability Configuration

### Replica Configuration

Both frontend and backend run with 2 replicas for high availability:

```yaml
replicaCount: 2
```

### Load Balancing

NGINX Ingress Controller automatically load balances requests across replicas:
- Frontend: 2 pods (10.244.0.13:3000, 10.244.0.14:3000)
- Backend: 2 pods (10.244.0.11:8000, 10.244.0.12:8000)

### Health Probes

**Liveness Probes** (restart unhealthy pods):
- Backend: `GET /health` every 30s
- Frontend: `GET /api/health` every 30s

**Readiness Probes** (remove from load balancer when not ready):
- Backend: `GET /health/ready` every 10s
- Frontend: `GET /api/health` every 10s

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app=evolved-todo

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Health Probes Failing

```bash
# Check if health endpoints are accessible
kubectl exec -it <pod-name> -- curl localhost:8000/health  # Backend
kubectl exec -it <pod-name> -- curl localhost:3000/api/health  # Frontend
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress evolved-todo-ingress

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Database Connection Issues

```bash
# Check if DATABASE_URL secret is set correctly
kubectl get secret evolved-todo-secrets -o jsonpath='{.data.database-url}' | base64 -d

# Check backend logs for connection errors
kubectl logs -l app=evolved-todo,component=backend
```

## Updating the Deployment

### Update Docker Images

```bash
# Rebuild images
docker build -t evolved-todo/api:local backend/
docker build -t evolved-todo/web:local frontend/

# Restart deployments to use new images
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend

# Watch rollout status
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend
```

### Update Configuration

```bash
# Update values or secrets
helm upgrade evolved-todo k8s/evolved-todo-chart/ \
  -f k8s/evolved-todo-chart/secrets-values.yaml \
  --namespace default
```

## Uninstalling

```bash
# Uninstall Helm release
helm uninstall evolved-todo --namespace default

# Verify resources are deleted
kubectl get all -l app=evolved-todo
```

## Security Considerations

1. **Non-Root Containers**: All containers run as non-root users
   - Backend: UID 1000 (appuser)
   - Frontend: UID 1001 (nextjs)

2. **Secrets Management**: Sensitive data stored in Kubernetes Secrets
   - Database credentials
   - JWT secrets
   - API keys

3. **Network Policies**: Consider adding NetworkPolicies for production

4. **Resource Limits**: All pods have CPU and memory limits to prevent resource exhaustion

## Performance Optimization

### Image Optimization

- **Backend**: Multi-stage build reduces image from ~500MB to ~498MB
- **Frontend**: Standalone Next.js output reduces image from ~400MB to ~245MB

### Caching Strategy

- Docker layer caching for faster rebuilds
- Kubernetes image pull policy: `Never` (use local images)

### Resource Allocation

Optimized for local development:
- Backend: 250m CPU, 256Mi memory (requests)
- Frontend: 200m CPU, 256Mi memory (requests)

## Monitoring and Observability

### Pod Status

```bash
# Watch pod status in real-time
kubectl get pods -l app=evolved-todo -w
```

### Resource Usage

```bash
# Check resource usage
kubectl top pods -l app=evolved-todo
kubectl top nodes
```

### Logs

```bash
# Stream logs from all backend pods
kubectl logs -f -l app=evolved-todo,component=backend

# Stream logs from all frontend pods
kubectl logs -f -l app=evolved-todo,component=frontend
```

## Related Documentation

- `CONTAINERIZATION.md`: Docker optimization decisions
- `.claude/skills/operating-k8s-local/`: Kubernetes operations patterns
- `.claude/skills/containerize-apps/`: Containerization best practices

## Deployment Status

✅ **Successfully Deployed**

- All pods running (2 backend, 2 frontend)
- Services created and accessible
- Ingress configured with NGINX
- Health probes passing
- High availability enabled (2 replicas)
- External database connectivity verified
