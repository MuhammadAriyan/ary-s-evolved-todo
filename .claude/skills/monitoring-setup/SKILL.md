---
name: monitoring-setup
description: Prometheus, Grafana, alerts, and dashboards setup for microservices observability. Use when setting up monitoring, creating dashboards, or configuring alerts.
---

# Monitoring Setup Skill

Comprehensive guide for setting up observability with Prometheus and Grafana.

## Included Guides

1. **00-overview.md** - Monitoring architecture overview
2. **01-prometheus.md** - Prometheus configuration and scraping
3. **02-grafana.md** - Grafana dashboards and data sources
4. **03-alerts.md** - Alert rules and notification channels
5. **04-metrics.md** - Application metrics instrumentation
6. **05-dashboards.md** - Dashboard design patterns
7. **06-troubleshooting.md** - Common monitoring issues

## Quick Reference

### Prometheus Scrape Config
```yaml
scrape_configs:
  - job_name: 'microservices'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Application Metrics
```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

### Alert Rule
```yaml
groups:
  - name: microservices
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
```

## Common Patterns
- **RED Metrics**: Rate, Errors, Duration
- **USE Metrics**: Utilization, Saturation, Errors
- **Golden Signals**: Latency, Traffic, Errors, Saturation
