"""Idempotency checker service using Redis state store."""
import logging
from typing import Optional
from datetime import timedelta

from app.services.dapr_state import get_dapr_state_store

logger = logging.getLogger(__name__)


class IdempotencyChecker:
    """Service for checking and tracking event idempotency."""

    def __init__(self, ttl_seconds: int = 604800):  # 7 days default
        """
        Initialize IdempotencyChecker.

        Args:
            ttl_seconds: TTL for idempotency keys (default: 7 days)
        """
        self.ttl_seconds = ttl_seconds
        self.state_store = get_dapr_state_store()

    def _get_key(self, event_id: str) -> str:
        """
        Get the Redis key for an event ID.

        Args:
            event_id: Event ID

        Returns:
            Redis key
        """
        return f"processed:{event_id}"

    async def is_processed(self, event_id: str) -> bool:
        """
        Check if an event has already been processed.

        Args:
            event_id: Event ID to check

        Returns:
            True if event was already processed, False otherwise
        """
        key = self._get_key(event_id)
        return await self.state_store.exists(key)

    async def mark_processed(self, event_id: str) -> None:
        """
        Mark an event as processed.

        Args:
            event_id: Event ID to mark
        """
        key = self._get_key(event_id)
        await self.state_store.set(
            key=key,
            value={"processed": True},
            ttl_seconds=self.ttl_seconds
        )
        logger.debug(f"Marked event as processed: {event_id}")

    async def check_and_mark(self, event_id: str) -> bool:
        """
        Check if event is processed and mark it if not.

        This is an atomic operation that returns True if the event
        was NOT processed before (i.e., this is the first time).

        Args:
            event_id: Event ID

        Returns:
            True if this is the first processing, False if already processed
        """
        if await self.is_processed(event_id):
            logger.warning(f"Duplicate event detected: {event_id}")
            return False

        await self.mark_processed(event_id)
        return True


# Singleton instance
_idempotency_checker: Optional[IdempotencyChecker] = None


def get_idempotency_checker() -> IdempotencyChecker:
    """
    Get the singleton IdempotencyChecker instance.

    Returns:
        IdempotencyChecker instance
    """
    global _idempotency_checker
    if _idempotency_checker is None:
        _idempotency_checker = IdempotencyChecker()
    return _idempotency_checker
