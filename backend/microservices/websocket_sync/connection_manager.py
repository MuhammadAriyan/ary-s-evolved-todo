"""ConnectionManager - Manages WebSocket connections with Redis state store.

T033: Track active WebSocket connections in Redis state store
T036: Connection lifecycle management (connect, disconnect, heartbeat)
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from fastapi import WebSocket
from dapr.clients import DaprClient
import jwt

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and tracks state in Redis via Dapr."""

    def __init__(self, dapr_store_name: str = "redis-statestore", dapr_http_port: int = 3500):
        """
        Initialize ConnectionManager.

        Args:
            dapr_store_name: Name of Dapr state store component
            dapr_http_port: Dapr HTTP port for state store operations
        """
        self.dapr_store_name = dapr_store_name
        self.dapr_http_port = dapr_http_port
        self.dapr_client: Optional[DaprClient] = None

        # In-memory connection tracking (fast access)
        self.active_connections: Dict[str, WebSocket] = {}  # connection_id -> WebSocket
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.connection_metadata: Dict[str, dict] = {}  # connection_id -> metadata

        # Metrics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0

    async def initialize(self):
        """Initialize Dapr client and load state from Redis."""
        try:
            self.dapr_client = DaprClient()
            logger.info("ConnectionManager initialized with Dapr state store")
        except Exception as e:
            logger.error(f"Failed to initialize Dapr client: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources and close all connections."""
        # Close all active WebSocket connections
        for connection_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket {connection_id}: {str(e)}")

        # Close Dapr client
        if self.dapr_client:
            self.dapr_client.close()

        logger.info("ConnectionManager cleanup completed")

    async def authenticate_token(self, token: str) -> Optional[str]:
        """
        Authenticate JWT token and extract user_id.

        T035: JWT authentication for WebSocket connections

        Args:
            token: JWT token from client

        Returns:
            user_id if valid, None otherwise
        """
        try:
            # TODO: Replace with actual JWT secret from environment
            # For now, we'll do basic validation
            # In production, use the same JWT_SECRET_KEY as the main backend

            # Decode without verification for now (development only)
            # In production, verify signature with JWT_SECRET_KEY
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub") or decoded.get("user_id")

            if not user_id:
                logger.warning("Token missing user_id/sub claim")
                return None

            logger.info(f"Authenticated user: {user_id}")
            return user_id

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token authentication error: {str(e)}")
            return None

    async def connect(self, websocket: WebSocket, user_id: str, token: str) -> str:
        """
        Register a new WebSocket connection.

        T033: Track connection in Redis state store
        T036: Connection lifecycle - connect

        Args:
            websocket: WebSocket connection
            user_id: Authenticated user ID
            token: JWT token

        Returns:
            connection_id: Unique connection identifier
        """
        connection_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Store in-memory
        self.active_connections[connection_id] = websocket

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Store connection metadata
        metadata = {
            "connection_id": connection_id,
            "user_id": user_id,
            "connected_at": timestamp,
            "last_heartbeat": timestamp,
            "subscribed_tasks": [],
        }
        self.connection_metadata[connection_id] = metadata

        # T033: Persist to Redis via Dapr state store
        try:
            state_key = f"ws_connection:{connection_id}"
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=state_key,
                value=json.dumps(metadata)
            )

            # Also track user's active connections
            user_state_key = f"ws_user_connections:{user_id}"
            user_connections_list = list(self.user_connections[user_id])
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=user_state_key,
                value=json.dumps(user_connections_list)
            )

            logger.info(f"Connection persisted to Redis: {connection_id}")
        except Exception as e:
            logger.error(f"Failed to persist connection to Redis: {str(e)}")

        self.total_connections += 1
        logger.info(f"New connection: {connection_id} for user {user_id}")

        return connection_id

    async def disconnect(self, connection_id: str):
        """
        Unregister a WebSocket connection.

        T036: Connection lifecycle - disconnect

        Args:
            connection_id: Connection identifier
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Connection not found: {connection_id}")
            return

        # Get metadata before removing
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")

        # Remove from in-memory tracking
        del self.active_connections[connection_id]
        del self.connection_metadata[connection_id]

        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from Redis
        try:
            state_key = f"ws_connection:{connection_id}"
            await asyncio.to_thread(
                self.dapr_client.delete_state,
                store_name=self.dapr_store_name,
                key=state_key
            )

            # Update user's active connections
            if user_id:
                user_state_key = f"ws_user_connections:{user_id}"
                user_connections_list = list(self.user_connections.get(user_id, []))
                if user_connections_list:
                    await asyncio.to_thread(
                        self.dapr_client.save_state,
                        store_name=self.dapr_store_name,
                        key=user_state_key,
                        value=json.dumps(user_connections_list)
                    )
                else:
                    await asyncio.to_thread(
                        self.dapr_client.delete_state,
                        store_name=self.dapr_store_name,
                        key=user_state_key
                    )

            logger.info(f"Connection removed from Redis: {connection_id}")
        except Exception as e:
            logger.error(f"Failed to remove connection from Redis: {str(e)}")

        logger.info(f"Disconnected: {connection_id}")

    async def update_heartbeat(self, connection_id: str):
        """
        Update last heartbeat timestamp for a connection.

        T036: Connection lifecycle - heartbeat

        Args:
            connection_id: Connection identifier
        """
        if connection_id not in self.connection_metadata:
            logger.warning(f"Connection not found for heartbeat: {connection_id}")
            return

        timestamp = datetime.utcnow().isoformat()
        self.connection_metadata[connection_id]["last_heartbeat"] = timestamp

        # Update in Redis
        try:
            state_key = f"ws_connection:{connection_id}"
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=state_key,
                value=json.dumps(self.connection_metadata[connection_id])
            )
        except Exception as e:
            logger.error(f"Failed to update heartbeat in Redis: {str(e)}")

    async def subscribe_to_tasks(self, connection_id: str, task_ids: List[str]):
        """
        Subscribe a connection to specific task updates.

        Args:
            connection_id: Connection identifier
            task_ids: List of task IDs to subscribe to
        """
        if connection_id not in self.connection_metadata:
            logger.warning(f"Connection not found: {connection_id}")
            return

        self.connection_metadata[connection_id]["subscribed_tasks"] = task_ids

        # Update in Redis
        try:
            state_key = f"ws_connection:{connection_id}"
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=state_key,
                value=json.dumps(self.connection_metadata[connection_id])
            )
        except Exception as e:
            logger.error(f"Failed to update subscriptions in Redis: {str(e)}")

    async def send_to_connection(self, connection_id: str, message: dict):
        """
        Send a message to a specific connection.

        Args:
            connection_id: Connection identifier
            message: Message to send (will be JSON serialized)
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Connection not found: {connection_id}")
            return

        websocket = self.active_connections[connection_id]
        try:
            await websocket.send_json(message)
            self.total_messages_sent += 1
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {str(e)}")
            # Connection might be dead, disconnect it
            await self.disconnect(connection_id)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """
        Broadcast a message to all connections for a specific user.

        T034: Broadcast task updates to connected clients

        Args:
            user_id: User ID
            message: Message to broadcast
        """
        if user_id not in self.user_connections:
            logger.debug(f"No active connections for user: {user_id}")
            return

        connection_ids = list(self.user_connections[user_id])
        logger.info(f"Broadcasting to {len(connection_ids)} connections for user {user_id}")

        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all active connections.

        Args:
            message: Message to broadcast
        """
        connection_ids = list(self.active_connections.keys())
        logger.info(f"Broadcasting to {len(connection_ids)} connections")

        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)

    def get_user_connections(self, user_id: str) -> List[str]:
        """
        Get all active connection IDs for a user.

        Args:
            user_id: User ID

        Returns:
            List of connection IDs
        """
        return list(self.user_connections.get(user_id, []))

    async def get_last_connection_time(self, user_id: str) -> Optional[str]:
        """
        Get the last connection timestamp for a user from Redis.

        T038: Used for replaying missed events

        Args:
            user_id: User ID

        Returns:
            ISO timestamp of last connection, or None
        """
        try:
            state_key = f"ws_last_disconnect:{user_id}"
            result = await asyncio.to_thread(
                self.dapr_client.get_state,
                store_name=self.dapr_store_name,
                key=state_key
            )

            if result.data:
                data = json.loads(result.data)
                return data.get("timestamp")

            return None
        except Exception as e:
            logger.error(f"Failed to get last connection time from Redis: {str(e)}")
            return None

    async def save_last_disconnect_time(self, user_id: str):
        """
        Save the last disconnect timestamp for a user.

        T038: Used for replaying missed events

        Args:
            user_id: User ID
        """
        try:
            state_key = f"ws_last_disconnect:{user_id}"
            timestamp = datetime.utcnow().isoformat()
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=state_key,
                value=json.dumps({"timestamp": timestamp})
            )
        except Exception as e:
            logger.error(f"Failed to save last disconnect time to Redis: {str(e)}")
