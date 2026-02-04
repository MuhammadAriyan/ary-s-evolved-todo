# Microservices Deployment Blueprint

## Overview

This blueprint documents the complete deployment strategy for microservices on Oracle Kubernetes Engine (OKE), including Helm charts, CI/CD pipelines, and operational procedures.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Oracle Kubernetes Engine (OKE)               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Ingress Controller                     │  │
│  │              (evolved-todo.example.com)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐      ┌─────────────┐    ┌─────────────┐     │
│  │  Frontend   │      │  Backend    │    │  WebSocket  │     │
│  │  (Next.js)  │      │  API        │    │  Sync       │     │
│  │  Replicas:2 │      │  Replicas:3 │    │  Replicas:2 │     │
│  └─────────────┘      └─────────────┘    └─────────────┘     │
│                                                                 │
│  ┌─────────────┐      ┌─────────────┐    ┌─────────────┐     │
│  │Notification │      │  Recurring  │    │   Audit     │     │
│  │  Service    │      │  Task Svc   │    │   Service   │     │
│  │  Replicas:2 │      │  Replicas:2 │    │  Replicas:2 │     │
│  └─────────────┘      └─────────────┘    └─────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Dapr Runtime                          │  │
│  │  (Sidecar injected into all pods)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Monitoring Stack                            │  │
│  │  Prometheus | Grafana | Alert Manager                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ External Services
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Redpanda Cloud  │  Redis (Managed)  │  Neon PostgreSQL        │
└─────────────────────────────────────────────────────────────────┘
```

## Helm Chart Structure

### Chart Organization

```
infrastructure/helm/
├── backend/                    # Backend API
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-staging.yaml
│   ├── values-production.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── configmap.yaml
│       ├── hpa.yaml
│       └── _helpers.tpl
├── frontend/                   # Frontend Next.js
├── websocket-sync/            # WebSocket Sync Service
├── notification/              # Notification Service
├── recurring-task/            # Recurring Task Service
├── audit/                     # Audit Service
├── dapr/                      # Dapr runtime
├── prometheus/                # Prometheus monitoring
└── grafana/                   # Grafana dashboards
```

### Example Helm Chart: Backend API

#### Chart.yaml
```yaml
apiVersion: v2
name: backend-api
description: Backend API for Evolved Todo
type: application
version: 1.0.0
appVersion: "1.0.0"
dependencies: []
```

#### values.yaml
```yaml
replicaCount: 3

image:
  repository: ghcr.io/evolved-todo/backend-api
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.evolved-todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.evolved-todo.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

dapr:
  enabled: true
  appId: backend-api
  appPort: 8000
  config: dapr-config
  logLevel: info

env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: database-secret
        key: url
  - name: REDIS_HOST
    value: "redis-master"
  - name: LOG_LEVEL
    value: "INFO"
  - name: DAPR_HTTP_PORT
    value: "3500"
  - name: DAPR_GRPC_PORT
    value: "50001"

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

#### templates/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "backend-api.fullname" . }}
  labels:
    {{- include "backend-api.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "backend-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        {{- if .Values.dapr.enabled }}
        dapr.io/enabled: "true"
        dapr.io/app-id: "{{ .Values.dapr.appId }}"
        dapr.io/app-port: "{{ .Values.dapr.appPort }}"
        dapr.io/config: "{{ .Values.dapr.config }}"
        dapr.io/log-level: "{{ .Values.dapr.logLevel }}"
        {{- end }}
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
      labels:
        {{- include "backend-api.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "backend-api.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        env:
          {{- toYaml .Values.env | nindent 10 }}
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

## CI/CD Pipeline

### GitHub Actions Workflow

#### .github/workflows/deploy-staging.yml
```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix={{branch}}-
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Backend API
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Microservices
        run: |
          for service in websocket-sync notification recurring-task audit; do
            docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/$service:${{ github.sha }} \
              ./backend/microservices/$service
            docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/$service:${{ github.sha }}
          done

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to Staging
        run: |
          # Deploy Backend API
          helm upgrade --install backend-api \
            infrastructure/helm/backend \
            --namespace evolved-todo-staging \
            --create-namespace \
            --values infrastructure/helm/backend/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 5m

          # Deploy Frontend
          helm upgrade --install frontend \
            infrastructure/helm/frontend \
            --namespace evolved-todo-staging \
            --values infrastructure/helm/frontend/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 5m

          # Deploy Microservices
          for service in websocket-sync notification recurring-task audit; do
            helm upgrade --install $service \
              infrastructure/helm/$service \
              --namespace evolved-todo-staging \
              --values infrastructure/helm/$service/values-staging.yaml \
              --set image.tag=${{ github.sha }} \
              --wait --timeout 5m
          done

      - name: Run Health Checks
        run: |
          kubectl wait --for=condition=ready pod \
            -l app=backend-api \
            -n evolved-todo-staging \
            --timeout=300s

          # Test health endpoint
          kubectl run curl-test --image=curlimages/curl:latest --rm -i --restart=Never \
            -n evolved-todo-staging \
            -- curl -f http://backend-api:8000/health

      - name: Rollback on Failure
        if: failure()
        run: |
          helm rollback backend-api -n evolved-todo-staging
          helm rollback frontend -n evolved-todo-staging
```

## Deployment Procedures

### Initial Deployment

```bash
# 1. Create namespace
kubectl create namespace evolved-todo

# 2. Create secrets
kubectl create secret generic database-secret \
  --from-literal=url="postgresql://..." \
  -n evolved-todo

kubectl create secret generic redis-secret \
  --from-literal=password="..." \
  -n evolved-todo

kubectl create secret generic redpanda-secret \
  --from-literal=username="..." \
  --from-literal=password="..." \
  -n evolved-todo

# 3. Deploy Dapr runtime
helm upgrade --install dapr \
  infrastructure/helm/dapr \
  -n evolved-todo

# 4. Deploy monitoring
helm upgrade --install prometheus \
  infrastructure/helm/prometheus \
  -n evolved-todo

helm upgrade --install grafana \
  infrastructure/helm/grafana \
  -n evolved-todo

# 5. Deploy services
helm upgrade --install backend-api \
  infrastructure/helm/backend \
  -n evolved-todo

helm upgrade --install frontend \
  infrastructure/helm/frontend \
  -n evolved-todo

# Deploy microservices
for service in websocket-sync notification recurring-task audit; do
  helm upgrade --install $service \
    infrastructure/helm/$service \
    -n evolved-todo
done
```

### Rolling Update

```bash
# Update with new image tag
helm upgrade backend-api \
  infrastructure/helm/backend \
  --set image.tag=v1.2.3 \
  -n evolved-todo \
  --wait
```

### Rollback

```bash
# Rollback to previous version
helm rollback backend-api -n evolved-todo

# Rollback to specific revision
helm rollback backend-api 5 -n evolved-todo
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment backend-api \
  --replicas=5 \
  -n evolved-todo

# Update HPA
helm upgrade backend-api \
  infrastructure/helm/backend \
  --set autoscaling.minReplicas=5 \
  --set autoscaling.maxReplicas=20 \
  -n evolved-todo
```

## Monitoring and Observability

### Health Checks

All services expose:
- `/health` - Liveness probe
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
tasks_created_total = Counter('tasks_created_total', 'Total tasks created')
active_websocket_connections = Gauge('active_websocket_connections', 'Active WebSocket connections')
```

### Grafana Dashboards

See `infrastructure/monitoring/grafana-dashboards/` for:
- Service overview dashboard
- Request rate and latency
- Error rates
- Resource utilization
- Business metrics

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n evolved-todo

# Describe pod
kubectl describe pod backend-api-xxx -n evolved-todo

# Check logs
kubectl logs backend-api-xxx -n evolved-todo
kubectl logs backend-api-xxx -c daprd -n evolved-todo  # Dapr sidecar
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n evolved-todo

# Test service internally
kubectl run curl-test --image=curlimages/curl:latest --rm -i --restart=Never \
  -n evolved-todo \
  -- curl http://backend-api:8000/health

# Check ingress
kubectl get ingress -n evolved-todo
```

### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n evolved-todo

# Update resource limits
helm upgrade backend-api \
  infrastructure/helm/backend \
  --set resources.limits.memory=2Gi \
  -n evolved-todo
```

## Best Practices

1. **Always use Helm for deployments** - Consistent, repeatable
2. **Set resource limits** - Prevent resource exhaustion
3. **Configure health checks** - Enable self-healing
4. **Use HPA** - Auto-scale based on load
5. **Enable monitoring** - Prometheus + Grafana
6. **Use secrets** - Never hardcode credentials
7. **Test in staging first** - Validate before production
8. **Implement rollback strategy** - Quick recovery
9. **Use namespaces** - Isolate environments
10. **Document procedures** - Runbooks for operations

## Related Skills
- **helm-chart**: Helm chart patterns
- **monitoring-setup**: Observability setup
- **dapr-component**: Dapr configuration

## Related Blueprints
- **event-driven-architecture**: Event patterns
- **dapr-integration**: Dapr integration
