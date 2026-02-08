"""WebSocket Sync Service - Real-time task synchronization microservice.

This service:
- Subscribes to task-updates topic via Dapr Pub/Sub
- Manages WebSocket connections with JWT authentication
- Broadcasts task updates to connected clients in real-time
- Tracks connections in Redis state store
- Replays missed events on reconnection
"""
import asyncio
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient

from connection_manager import ConnectionManager
from event_handler import EventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
connection_manager: Optional[ConnectionManager] = None
event_handler: Optional[EventHandler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global connection_manager, event_handler

    logger.info("Starting WebSocket Sync Service...")

    # Initialize ConnectionManager with Redis state store
    connection_manager = ConnectionManager(
        dapr_store_name="redis-statestore",
        dapr_http_port=3500
    )
    await connection_manager.initialize()

    # Initialize EventHandler
    event_handler = EventHandler(connection_manager)

    logger.info("WebSocket Sync Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down WebSocket Sync Service...")
    if connection_manager:
        await connection_manager.cleanup()
    logger.info("WebSocket Sync Service stopped")


# Create FastAPI app
app = FastAPI(
    title="WebSocket Sync Service",
    description="Real-time task synchronization via WebSockets",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Dapr app for Pub/Sub subscriptions
dapr_app = DaprApp(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "websocket-sync",
        "connections": len(connection_manager.active_connections) if connection_manager else 0
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring."""
    if not connection_manager:
        return {"error": "ConnectionManager not initialized"}

    return {
        "active_connections": len(connection_manager.active_connections),
        "total_connections": connection_manager.total_connections,
        "total_messages_sent": connection_manager.total_messages_sent,
        "total_messages_received": connection_manager.total_messages_received,
    }


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time task synchronization.

    T035: WebSocket endpoint with JWT authentication
    T036: Connection lifecycle management (connect, disconnect, heartbeat)

    Args:
        websocket: WebSocket connection
        token: JWT token for authentication
    """
    user_id = None

    try:
        # T035: Authenticate user via JWT token
        user_id = await connection_manager.authenticate_token(token)
        if not user_id:
            logger.warning("WebSocket connection rejected: Invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # T036: Accept connection and register with ConnectionManager
        await websocket.accept()
        connection_id = await connection_manager.connect(websocket, user_id, token)
        logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")

        # T038: Replay missed events since last connection
        await event_handler.replay_missed_events(user_id, connection_id)

        # T036: Connection lifecycle - message loop with heartbeat
        try:
            while True:
                # Receive messages from client (heartbeat, commands)
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "heartbeat":
                    # T036: Heartbeat to keep connection alive
                    await connection_manager.update_heartbeat(connection_id)
                    await websocket.send_json({
                        "type": "heartbeat_ack",
                        "timestamp": message.get("timestamp")
                    })
                elif message.get("type") == "subscribe":
                    # Client requesting to subscribe to specific task updates
                    task_ids = message.get("task_ids", [])
                    await connection_manager.subscribe_to_tasks(connection_id, task_ids)
                    logger.info(f"Connection {connection_id} subscribed to tasks: {task_ids}")
                else:
                    logger.warning(f"Unknown message type: {message.get('type')}")

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket message loop: {str(e)}")
        finally:
            # T036: Disconnect and cleanup
            await connection_manager.disconnect(connection_id)
            logger.info(f"Connection cleaned up: {connection_id}")

    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        if user_id:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@dapr_app.subscribe(pubsub="kafka-pubsub", topic="task-updates")
async def task_updates_handler(event_data: dict):
    """
    Dapr Pub/Sub subscription handler for task-updates topic.

    T032: Subscribe to task-updates via Dapr Pub/Sub
    T034: Consume task-updates events and broadcast to connected clients
    T037: Event filtering - only broadcast to users with task access

    Args:
        event_data: Event payload from Kafka
    """
    try:
        logger.info(f"Received task-updates event: {event_data.get('event_type')}")

        # Extract event details
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        task_data = event_data.get("data", {})

        if not event_type or not user_id:
            logger.warning("Invalid event data: missing event_type or user_id")
            return {"success": False}

        # T034 & T037: Process event and broadcast to authorized clients
        await event_handler.handle_task_event(
            event_type=event_type,
            user_id=user_id,
            task_data=task_data,
            event_id=event_data.get("event_id"),
            timestamp=event_data.get("timestamp")
        )

        return {"success": True}

    except Exception as e:
        logger.error(f"Error handling task-updates event: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
