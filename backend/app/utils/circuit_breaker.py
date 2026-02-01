"""
Circuit breaker pattern for external service calls.

Implements circuit breaker to prevent cascading failures when external services are down.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    Prevents cascading failures by failing fast when a service is down.

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Service is down, all requests fail immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed

    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After timeout_seconds elapsed
    - HALF_OPEN -> CLOSED: After success_threshold consecutive successes
    - HALF_OPEN -> OPEN: On any failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name for logging
            failure_threshold: Number of failures before opening circuit
            success_threshold: Number of successes before closing circuit from half-open
            timeout_seconds: Seconds to wait before trying half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.utcnow()

        # Lock for thread-safe state changes
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from func
        """
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable. Retry after {self._time_until_retry()} seconds."
                    )

        # Execute the function
        try:
            result = await func(*args, **kwargs)

            async with self._lock:
                self._on_success()

            return result

        except Exception as e:
            async with self._lock:
                self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True

        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed > timedelta(seconds=self.timeout_seconds)

    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed"""
        if not self.last_failure_time:
            return 0

        elapsed = datetime.utcnow() - self.last_failure_time
        remaining = timedelta(seconds=self.timeout_seconds) - elapsed
        return max(0, int(remaining.total_seconds()))

    def _transition_to_half_open(self):
        """Transition from OPEN to HALF_OPEN state"""
        logger.info(
            f"Circuit breaker '{self.name}' transitioning to HALF_OPEN",
            extra={"circuit_breaker": self.name, "state": "HALF_OPEN"}
        )
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.last_state_change = datetime.utcnow()

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"Circuit breaker '{self.name}' success in HALF_OPEN state "
                f"({self.success_count}/{self.success_threshold})",
                extra={
                    "circuit_breaker": self.name,
                    "success_count": self.success_count,
                    "success_threshold": self.success_threshold
                }
            )

            if self.success_count >= self.success_threshold:
                self._transition_to_closed()

        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self, error: Exception):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        logger.warning(
            f"Circuit breaker '{self.name}' failure: {str(error)}",
            extra={
                "circuit_breaker": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "error": str(error)
            }
        )

        if self.state == CircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN state opens the circuit
            self._transition_to_open()

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def _transition_to_open(self):
        """Transition to OPEN state"""
        logger.error(
            f"Circuit breaker '{self.name}' opening circuit after {self.failure_count} failures",
            extra={
                "circuit_breaker": self.name,
                "state": "OPEN",
                "failure_count": self.failure_count
            }
        )
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.utcnow()

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        logger.info(
            f"Circuit breaker '{self.name}' closing circuit after {self.success_count} successes",
            extra={
                "circuit_breaker": self.name,
                "state": "CLOSED",
                "success_count": self.success_count
            }
        )
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.utcnow()

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0
        }


# Global circuit breakers for external services
email_circuit_breaker = CircuitBreaker(
    name="email_service",
    failure_threshold=5,
    success_threshold=2,
    timeout_seconds=60
)

kafka_circuit_breaker = CircuitBreaker(
    name="kafka_service",
    failure_threshold=3,
    success_threshold=2,
    timeout_seconds=30
)

database_circuit_breaker = CircuitBreaker(
    name="database",
    failure_threshold=10,
    success_threshold=3,
    timeout_seconds=30
)
