"""
Structured JSON logging configuration.

Provides consistent, machine-readable logging across all services.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import sys


class StructuredLogger(logging.Formatter):
    """
    Structured JSON logging formatter.

    Outputs logs in JSON format for easy parsing by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add user ID if present
        user_id = getattr(record, "user_id", None)
        if user_id:
            log_data["user_id"] = user_id

        # Add request ID if present
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_data["request_id"] = request_id

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development.

    Provides human-readable colored output for local development.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Get correlation ID if present
        correlation_id = getattr(record, "correlation_id", None)
        correlation_str = f" [{correlation_id[:8]}]" if correlation_id else ""

        # Format message
        message = record.getMessage()

        # Format exception if present
        exception_str = ""
        if record.exc_info:
            exception_str = f"\n{self.formatException(record.exc_info)}"

        return (
            f"{color}{timestamp} {record.levelname:8s}{reset} "
            f"{record.name}{correlation_str} - {message}{exception_str}"
        )


def setup_logging(
    service_name: str = "backend",
    log_level: str = "INFO",
    json_logs: bool = False
) -> None:
    """
    Configure logging for the application.

    Args:
        service_name: Name of the service for log identification
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, use JSON formatter; if False, use colored console formatter
    """
    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on environment
    if json_logs:
        formatter = StructuredLogger()
    else:
        formatter = ColoredConsoleFormatter()

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Set service name
    root_logger.name = service_name

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("dapr").setLevel(logging.INFO)

    # Log startup message
    root_logger.info(
        f"Logging configured for {service_name}",
        extra={
            "log_level": log_level,
            "json_logs": json_logs
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding context to logs.

    Usage:
        with LogContext(correlation_id="123", user_id="user-456"):
            logger.info("Processing request")
    """

    def __init__(self, **kwargs):
        """
        Initialize log context.

        Args:
            **kwargs: Context fields to add to logs
        """
        self.context = kwargs
        self.old_factory = None

    def __enter__(self):
        """Enter context and add fields to log records"""
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        self.old_factory = old_factory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original factory"""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


# Example usage functions
def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Log HTTP request with structured data.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        correlation_id: Request correlation ID
        user_id: User ID if authenticated
    """
    logger.info(
        f"{method} {path} {status_code} {duration_ms:.2f}ms",
        extra={
            "http": {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms
            },
            "correlation_id": correlation_id,
            "user_id": user_id
        }
    )


def log_event(
    logger: logging.Logger,
    event_type: str,
    event_data: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> None:
    """
    Log event with structured data.

    Args:
        logger: Logger instance
        event_type: Type of event
        event_data: Event data
        correlation_id: Correlation ID
    """
    logger.info(
        f"Event: {event_type}",
        extra={
            "event": {
                "type": event_type,
                "data": event_data
            },
            "correlation_id": correlation_id
        }
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> None:
    """
    Log error with structured data.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context
        correlation_id: Correlation ID
    """
    logger.error(
        f"Error: {str(error)}",
        extra={
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "context": context or {}
            },
            "correlation_id": correlation_id
        },
        exc_info=True
    )
