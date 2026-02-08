---
name: helm-chart
description: Helm chart best practices for microservices with proper resource limits, health checks, and configurations. Use when creating Helm charts, deploying to Kubernetes, or configuring service deployments.
---

# Helm Chart Skill

Comprehensive guide for creating production-ready Helm charts for microservices.

## Included Guides

1. **00-overview.md** - Helm charts overview
2. **01-chart-structure.md** - Chart directory structure and files
3. **02-deployment.md** - Deployment manifest templates
4. **03-service.md** - Service and Ingress configuration
5. **04-configmap-secrets.md** - ConfigMaps and Secrets management
6. **05-values.md** - Values file organization
7. **06-best-practices.md** - Production best practices

## Quick Reference

### Chart Structure
```
helm-chart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
├── templates/          # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── _helpers.tpl   # Template helpers
└── README.md          # Chart documentation
```

### Basic Deployment Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "chart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
```

## Common Patterns
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Liveness and readiness probes
- **Auto-scaling**: HorizontalPodAutoscaler
- **Dapr Integration**: Annotations for sidecar injection
