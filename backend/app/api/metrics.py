"""Prometheus metrics endpoint for monitoring."""
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

task_operations_total = Counter(
    'task_operations_total',
    'Total task operations',
    ['operation', 'user_id']
)

event_published_total = Counter(
    'event_published_total',
    'Total events published',
    ['topic', 'event_type']
)

event_consumed_total = Counter(
    'event_consumed_total',
    'Total events consumed',
    ['topic', 'event_type']
)

websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections',
    ['user_id']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus-formatted metrics
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Helper functions for recording metrics

def record_http_request(method: str, endpoint: str, status: int):
    """Record an HTTP request."""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()


def record_http_duration(method: str, endpoint: str, duration: float):
    """Record HTTP request duration."""
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def record_task_operation(operation: str, user_id: str):
    """Record a task operation."""
    task_operations_total.labels(
        operation=operation,
        user_id=user_id
    ).inc()


def record_event_published(topic: str, event_type: str):
    """Record an event publication."""
    event_published_total.labels(
        topic=topic,
        event_type=event_type
    ).inc()


def record_event_consumed(topic: str, event_type: str):
    """Record an event consumption."""
    event_consumed_total.labels(
        topic=topic,
        event_type=event_type
    ).inc()


def set_websocket_connections(user_id: str, count: int):
    """Set active WebSocket connections for a user."""
    websocket_connections_active.labels(user_id=user_id).set(count)


def record_database_query(operation: str, duration: float):
    """Record database query duration."""
    database_query_duration_seconds.labels(operation=operation).observe(duration)


def record_cache_hit(cache_type: str):
    """Record a cache hit."""
    cache_hits_total.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record a cache miss."""
    cache_misses_total.labels(cache_type=cache_type).inc()
