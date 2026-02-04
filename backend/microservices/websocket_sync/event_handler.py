"""EventHandler - Processes task events and broadcasts to WebSocket clients.

T034: Consume task-updates events and broadcast to connected clients
T037: Event filtering - only broadcast to users with task access permissions
T038: Replay missed events from Kafka when client reconnects
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class EventHandler:
    """Handles task events and broadcasts to appropriate WebSocket connections."""

    def __init__(self, connection_manager):
        """
        Initialize EventHandler.

        Args:
            connection_manager: ConnectionManager instance for broadcasting
        """
        self.connection_manager = connection_manager
        self.dapr_client = DaprClient()

        # Event cache for replay (in-memory, limited size)
        self.event_cache: Dict[str, List[dict]] = {}  # user_id -> list of events
        self.max_cache_size = 100  # Max events per user
        self.cache_ttl_hours = 24  # Cache events for 24 hours

    async def handle_task_event(
        self,
        event_type: str,
        user_id: str,
        task_data: dict,
        event_id: str,
        timestamp: str
    ):
        """
        Handle a task event and broadcast to appropriate clients.

        T034: Consume task-updates events and broadcast to connected clients
        T037: Event filtering - only broadcast to users with task access

        Args:
            event_type: Type of event (task.created, task.updated, etc.)
            user_id: User ID who owns the task
            task_data: Task data from event
            event_id: Unique event ID
            timestamp: Event timestamp
        """
        try:
            # T037: Event filtering - check if user has access to this task
            # For now, we only broadcast to the task owner
            # In future, extend to check group memberships, assignments, etc.
            authorized_users = await self._get_authorized_users(task_data, user_id)

            # Construct message to broadcast
            message = {
                "type": "task_update",
                "event_type": event_type,
                "event_id": event_id,
                "timestamp": timestamp,
                "task": task_data.get("task", task_data),
            }

            # T034: Broadcast to all authorized users
            for authorized_user_id in authorized_users:
                # Check if user has active connections
                connections = self.connection_manager.get_user_connections(authorized_user_id)

                if connections:
                    # User is online, broadcast immediately
                    await self.connection_manager.broadcast_to_user(authorized_user_id, message)
                    logger.info(
                        f"Broadcasted {event_type} to user {authorized_user_id} "
                        f"({len(connections)} connections)"
                    )
                else:
                    # User is offline, cache event for replay
                    await self._cache_event_for_replay(authorized_user_id, message)
                    logger.debug(f"Cached {event_type} for offline user {authorized_user_id}")

        except Exception as e:
            logger.error(f"Error handling task event: {str(e)}")

    async def _get_authorized_users(self, task_data: dict, owner_user_id: str) -> List[str]:
        """
        Get list of users authorized to receive this task update.

        T037: Event filtering based on task access permissions

        Args:
            task_data: Task data
            owner_user_id: Task owner user ID

        Returns:
            List of authorized user IDs
        """
        authorized_users = [owner_user_id]

        # TODO: Extend to include:
        # - Group members if task belongs to a group
        # - Users assigned to the task
        # - Users with shared access

        task = task_data.get("task", task_data)
        group_id = task.get("group_id")

        if group_id:
            # TODO: Query group members from database or cache
            # For now, just return owner
            pass

        return authorized_users

    async def _cache_event_for_replay(self, user_id: str, event: dict):
        """
        Cache an event for later replay when user reconnects.

        T038: Cache events for replay on reconnection

        Args:
            user_id: User ID
            event: Event to cache
        """
        if user_id not in self.event_cache:
            self.event_cache[user_id] = []

        # Add event with cache metadata
        cached_event = {
            **event,
            "cached_at": datetime.utcnow().isoformat()
        }
        self.event_cache[user_id].append(cached_event)

        # Limit cache size (FIFO)
        if len(self.event_cache[user_id]) > self.max_cache_size:
            self.event_cache[user_id] = self.event_cache[user_id][-self.max_cache_size:]

        logger.debug(f"Cached event for user {user_id} (cache size: {len(self.event_cache[user_id])})")

    async def replay_missed_events(self, user_id: str, connection_id: str):
        """
        Replay missed events to a reconnecting client.

        T038: Replay missed events from cache when client reconnects

        Args:
            user_id: User ID
            connection_id: Connection ID to send events to
        """
        try:
            # Get last disconnect time from ConnectionManager
            last_disconnect = await self.connection_manager.get_last_connection_time(user_id)

            if not last_disconnect:
                logger.info(f"No previous disconnect time for user {user_id}, skipping replay")
                return

            # Get cached events for this user
            cached_events = self.event_cache.get(user_id, [])

            if not cached_events:
                logger.info(f"No cached events for user {user_id}")
                return

            # Filter events that occurred after last disconnect
            last_disconnect_dt = datetime.fromisoformat(last_disconnect)
            missed_events = []

            for event in cached_events:
                event_timestamp = event.get("timestamp")
                if event_timestamp:
                    event_dt = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00'))
                    if event_dt > last_disconnect_dt:
                        missed_events.append(event)

            if missed_events:
                logger.info(f"Replaying {len(missed_events)} missed events to user {user_id}")

                # Send replay start notification
                await self.connection_manager.send_to_connection(connection_id, {
                    "type": "replay_start",
                    "count": len(missed_events),
                    "since": last_disconnect
                })

                # Replay events in order
                for event in missed_events:
                    # Mark as replayed event
                    replay_event = {
                        **event,
                        "replayed": True
                    }
                    await self.connection_manager.send_to_connection(connection_id, replay_event)
                    # Small delay to avoid overwhelming the client
                    await asyncio.sleep(0.01)

                # Send replay complete notification
                await self.connection_manager.send_to_connection(connection_id, {
                    "type": "replay_complete",
                    "count": len(missed_events)
                })

                logger.info(f"Replay completed for user {user_id}")
            else:
                logger.info(f"No missed events for user {user_id} since {last_disconnect}")

        except Exception as e:
            logger.error(f"Error replaying missed events: {str(e)}")

    async def cleanup_old_cache_entries(self):
        """
        Cleanup old cached events based on TTL.

        Should be called periodically (e.g., every hour).
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cache_ttl_hours)

            for user_id in list(self.event_cache.keys()):
                events = self.event_cache[user_id]
                filtered_events = [
                    event for event in events
                    if datetime.fromisoformat(event.get("cached_at", "")) > cutoff_time
                ]

                if filtered_events:
                    self.event_cache[user_id] = filtered_events
                else:
                    del self.event_cache[user_id]

            logger.info("Cleaned up old cache entries")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")

    async def get_cache_stats(self) -> dict:
        """
        Get statistics about the event cache.

        Returns:
            Dictionary with cache statistics
        """
        total_events = sum(len(events) for events in self.event_cache.values())
        return {
            "total_users": len(self.event_cache),
            "total_events": total_events,
            "max_cache_size": self.max_cache_size,
            "cache_ttl_hours": self.cache_ttl_hours
        }
