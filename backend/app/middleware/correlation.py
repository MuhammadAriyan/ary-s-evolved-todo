"""
Correlation ID middleware for distributed tracing.

Adds correlation IDs to all requests and propagates them across services.
"""

from fastapi import Request
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def correlation_id_middleware(request: Request, call_next):
    """
    Add correlation ID to all requests for distributed tracing.

    The correlation ID is:
    1. Extracted from X-Correlation-ID header if present
    2. Generated as new UUID if not present
    3. Added to request state for access in handlers
    4. Added to logging context
    5. Added to response headers

    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain

    Returns:
        Response with correlation ID header
    """
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    # Add to request state for access in handlers
    request.state.correlation_id = correlation_id

    # Create logger adapter with correlation ID
    log_adapter = logging.LoggerAdapter(
        logger,
        {"correlation_id": correlation_id}
    )

    # Log incoming request
    log_adapter.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
        }
    )

    # Process request
    try:
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Log response
        log_adapter.info(
            f"Response: {response.status_code}",
            extra={
                "status_code": response.status_code,
            }
        )

        return response

    except Exception as e:
        # Log error with correlation ID
        log_adapter.error(
            f"Request failed: {str(e)}",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True
        )
        raise


def get_correlation_id(request: Request) -> Optional[str]:
    """
    Get correlation ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID if present, None otherwise
    """
    return getattr(request.state, "correlation_id", None)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to add correlation ID to log records.

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(CorrelationIdFilter())
    """

    def filter(self, record):
        """Add correlation_id to log record if not present"""
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "no-correlation-id"
        return True
