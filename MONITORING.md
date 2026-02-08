# Monitoring and Observability Guide

## Overview

This guide covers monitoring, observability, and troubleshooting for Ary's Evolved Todo microservices deployment.

## Monitoring Stack

### Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alert Manager**: Alert routing and notification
- **Dapr Metrics**: Service mesh observability

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Services                         │
│  • Backend API                                                  │
│  • Frontend                                                     │
│  • Microservices (WebSocket, Notification, Recurring, Audit)   │
│                                                                 │
│  Expose metrics at /metrics endpoint                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Scrape metrics
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Prometheus                              │
│  • Scrapes metrics every 15s                                    │
│  • Stores time-series data                                      │
│  • Evaluates alert rules                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Query metrics
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Grafana                                │
│  • Visualizes metrics                                           │
│  • Pre-built dashboards                                         │
│  • Custom queries                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Metrics

### Application Metrics

#### HTTP Requests
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Current in-flight requests

#### Business Metrics
- `tasks_created_total` - Total tasks created
- `tasks_completed_total` - Total tasks completed
- `reminders_sent_total` - Total reminders delivered
- `websocket_connections_active` - Active WebSocket connections

#### Event Processing
- `event_processing_total` - Total events processed by type
- `event_processing_duration_seconds` - Event processing latency
- `event_processing_errors_total` - Event processing errors

### Infrastructure Metrics

#### Kubernetes
- `kube_pod_status_phase` - Pod status
- `kube_pod_container_resource_requests` - Resource requests
- `kube_pod_container_resource_limits` - Resource limits

#### Dapr
- `dapr_http_server_request_count` - Dapr HTTP requests
- `dapr_component_loaded` - Loaded components
- `dapr_pubsub_ingress_count` - Pub/Sub messages received
- `dapr_pubsub_egress_count` - Pub/Sub messages published

## Accessing Monitoring

### Grafana Dashboard

```bash
# Port-forward Grafana
kubectl port-forward -n evolved-todo svc/grafana 3000:3000

# Access at http://localhost:3000
# Default credentials: admin/admin (change on first login)
```

### Prometheus UI

```bash
# Port-forward Prometheus
kubectl port-forward -n evolved-todo svc/prometheus 9090:9090

# Access at http://localhost:9090
```

## Pre-built Dashboards

### 1. Service Overview Dashboard

**Metrics**:
- Request rate (requests/second)
- Error rate (%)
- Latency (p50, p95, p99)
- Active connections

**Location**: `infrastructure/monitoring/grafana-dashboards/service-overview.json`

### 2. Event Processing Dashboard

**Metrics**:
- Events processed per second
- Processing latency
- Error rates by event type
- Consumer lag

**Location**: `infrastructure/monitoring/grafana-dashboards/event-processing.json`

### 3. Resource Utilization Dashboard

**Metrics**:
- CPU usage by pod
- Memory usage by pod
- Network I/O
- Disk I/O

**Location**: `infrastructure/monitoring/grafana-dashboards/resource-utilization.json`

### 4. Business Metrics Dashboard

**Metrics**:
- Tasks created/completed per hour
- Active users
- Reminder delivery rate
- Search queries per second

**Location**: `infrastructure/monitoring/grafana-dashboards/business-metrics.json`

## Alert Rules

### Critical Alerts

#### High Error Rate
```yaml
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
severity: critical
annotations:
  summary: "High error rate detected (>5%)"
```

#### Service Down
```yaml
alert: ServiceDown
expr: up{job="backend-api"} == 0
for: 1m
severity: critical
annotations:
  summary: "Service is down"
```

#### High Latency
```yaml
alert: HighLatency
expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
for: 5m
severity: warning
annotations:
  summary: "95th percentile latency >1s"
```

### Warning Alerts

#### High Memory Usage
```yaml
alert: HighMemoryUsage
expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
for: 10m
severity: warning
annotations:
  summary: "Memory usage >80%"
```

#### Consumer Lag
```yaml
alert: ConsumerLag
expr: kafka_consumer_lag > 1000
for: 5m
severity: warning
annotations:
  summary: "Consumer lag >1000 messages"
```

## Troubleshooting Guide

### High Error Rate

**Symptoms**: Error rate >5% for 5+ minutes

**Investigation**:
```bash
# Check pod logs
kubectl logs -n evolved-todo -l app=backend-api --tail=100

# Check recent errors
kubectl logs -n evolved-todo -l app=backend-api | grep ERROR

# Check pod status
kubectl get pods -n evolved-todo
```

**Common Causes**:
- Database connection issues
- External service failures
- Resource exhaustion
- Configuration errors

### High Latency

**Symptoms**: p95 latency >1 second

**Investigation**:
```bash
# Check resource usage
kubectl top pods -n evolved-todo

# Check database queries
# Review slow query logs in Neon dashboard

# Check external service latency
# Review Dapr metrics for service invocation
```

**Common Causes**:
- Slow database queries
- External API timeouts
- Resource constraints
- Network issues

### Service Down

**Symptoms**: Service not responding

**Investigation**:
```bash
# Check pod status
kubectl get pods -n evolved-todo

# Describe pod
kubectl describe pod <pod-name> -n evolved-todo

# Check events
kubectl get events -n evolved-todo --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n evolved-todo
```

**Common Causes**:
- Pod crash loop
- Failed health checks
- Resource limits exceeded
- Image pull errors

### Consumer Lag

**Symptoms**: Kafka consumer lag >1000 messages

**Investigation**:
```bash
# Check consumer group status
kafka-consumer-groups.sh \
  --bootstrap-server <redpanda-host>:9092 \
  --group notification-service \
  --describe

# Check pod logs
kubectl logs -n evolved-todo -l app=notification-service

# Check resource usage
kubectl top pods -n evolved-todo -l app=notification-service
```

**Common Causes**:
- Slow event processing
- Resource constraints
- Service errors
- High event volume

### Database Connection Issues

**Symptoms**: Database connection errors in logs

**Investigation**:
```bash
# Test database connectivity
kubectl run psql-test --image=postgres:15 --rm -i --restart=Never \
  -n evolved-todo \
  -- psql "<connection-string>" -c "SELECT 1"

# Check database secret
kubectl get secret database-secret -n evolved-todo -o yaml

# Check connection pool metrics
# Review Prometheus metrics for database connections
```

**Common Causes**:
- Invalid credentials
- Network issues
- Connection pool exhaustion
- Database maintenance

## Performance Optimization

### Query Optimization

**Monitor slow queries**:
- Review Neon slow query logs
- Add indexes for frequently queried fields
- Use EXPLAIN ANALYZE for query plans

### Resource Tuning

**Adjust resource limits**:
```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

**Configure HPA**:
```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### Caching Strategy

**Implement caching**:
- Use Redis for frequently accessed data
- Cache search results
- Cache user sessions

## Log Aggregation

### Structured Logging

All services use structured JSON logging:

```json
{
  "timestamp": "2026-02-01T10:30:00Z",
  "level": "INFO",
  "service": "backend-api",
  "correlation_id": "req_xyz789",
  "message": "Task created successfully",
  "task_id": "task_123",
  "user_id": "user_456"
}
```

### Viewing Logs

```bash
# View logs for specific service
kubectl logs -n evolved-todo -l app=backend-api -f

# View logs with grep
kubectl logs -n evolved-todo -l app=backend-api | grep ERROR

# View logs for specific time range
kubectl logs -n evolved-todo backend-api-xxx --since=1h
```

## Distributed Tracing

### Correlation IDs

All requests include correlation IDs for tracing:

```python
correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
```

### Tracing Events

Events include correlation IDs in metadata:

```json
{
  "metadata": {
    "correlation_id": "req_xyz789",
    "user_id": "user_456"
  }
}
```

## Health Checks

### Endpoints

All services expose:
- `/health` - Liveness probe
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Best Practices

1. **Monitor the Four Golden Signals**: Latency, Traffic, Errors, Saturation
2. **Set up alerts for critical metrics**: Error rate, latency, service availability
3. **Use structured logging**: JSON format with correlation IDs
4. **Implement distributed tracing**: Track requests across services
5. **Monitor business metrics**: Tasks created, reminders sent, etc.
6. **Set appropriate resource limits**: Prevent resource exhaustion
7. **Configure auto-scaling**: Handle traffic spikes
8. **Regular performance testing**: Load test before production
9. **Review dashboards regularly**: Identify trends and issues
10. **Document runbooks**: Standard operating procedures

## Support

For monitoring issues:
- Check Grafana dashboards
- Review Prometheus alerts
- Examine pod logs
- Consult DEPLOYMENT.md for deployment issues
