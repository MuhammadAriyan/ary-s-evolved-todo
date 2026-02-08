"""Dapr state store helper for Redis operations."""
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import timedelta

from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class DaprStateStore:
    """Helper class for Dapr state store operations with Redis."""

    def __init__(self, store_name: str = "redis-state"):
        """
        Initialize DaprStateStore.

        Args:
            store_name: Name of the Dapr state store component (default: redis-state)
        """
        self.store_name = store_name
        self.client: Optional[DaprClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = DaprClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the state store.

        Args:
            key: State key

        Returns:
            Value if exists, None otherwise
        """
        try:
            if not self.client:
                self.client = DaprClient()

            response = self.client.get_state(
                store_name=self.store_name,
                key=key
            )

            if response.data:
                return json.loads(response.data)
            return None

        except Exception as e:
            logger.error(f"Failed to get state for key: {key}: {str(e)}")
            raise

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set a value in the state store.

        Args:
            key: State key
            value: Value to store (will be JSON serialized)
            ttl_seconds: Optional TTL in seconds
        """
        try:
            if not self.client:
                self.client = DaprClient()

            metadata = {}
            if ttl_seconds:
                metadata["ttlInSeconds"] = str(ttl_seconds)

            self.client.save_state(
                store_name=self.store_name,
                key=key,
                value=json.dumps(value),
                state_metadata=metadata
            )

            logger.debug(f"Saved state for key: {key} (TTL: {ttl_seconds}s)")

        except Exception as e:
            logger.error(f"Failed to save state for key: {key}: {str(e)}")
            raise

    async def delete(self, key: str) -> None:
        """
        Delete a value from the state store.

        Args:
            key: State key
        """
        try:
            if not self.client:
                self.client = DaprClient()

            self.client.delete_state(
                store_name=self.store_name,
                key=key
            )

            logger.debug(f"Deleted state for key: {key}")

        except Exception as e:
            logger.error(f"Failed to delete state for key: {key}: {str(e)}")
            raise

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the state store.

        Args:
            key: State key

        Returns:
            True if key exists, False otherwise
        """
        value = await self.get(key)
        return value is not None

    async def increment(self, key: str, delta: int = 1) -> int:
        """
        Increment a counter in the state store.

        Args:
            key: State key
            delta: Amount to increment (default: 1)

        Returns:
            New counter value
        """
        current = await self.get(key) or 0
        new_value = current + delta
        await self.set(key, new_value)
        return new_value

    async def add_to_set(self, key: str, value: str) -> None:
        """
        Add a value to a set (stored as a list).

        Args:
            key: State key
            value: Value to add
        """
        current_set = await self.get(key) or []
        if value not in current_set:
            current_set.append(value)
            await self.set(key, current_set)

    async def remove_from_set(self, key: str, value: str) -> None:
        """
        Remove a value from a set.

        Args:
            key: State key
            value: Value to remove
        """
        current_set = await self.get(key) or []
        if value in current_set:
            current_set.remove(value)
            await self.set(key, current_set)

    async def get_set(self, key: str) -> List[str]:
        """
        Get all values in a set.

        Args:
            key: State key

        Returns:
            List of values
        """
        return await self.get(key) or []


# Singleton instance
_dapr_state_store: Optional[DaprStateStore] = None


def get_dapr_state_store() -> DaprStateStore:
    """
    Get the singleton DaprStateStore instance.

    Returns:
        DaprStateStore instance
    """
    global _dapr_state_store
    if _dapr_state_store is None:
        _dapr_state_store = DaprStateStore()
    return _dapr_state_store
