"""Audit Service - Main application with Dapr Pub/Sub subscription."""
import asyncio
import os
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool

from log_writer import LogWriter


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/todo")
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Global log writer instance
log_writer: LogWriter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global log_writer

    # Startup
    print("Starting Audit Service...")
    session = Session(engine)
    log_writer = LogWriter(session)
    log_writer.start()
    print("Audit Service started successfully")

    yield

    # Shutdown
    print("Shutting down Audit Service...")
    if log_writer:
        await log_writer.stop()
    print("Audit Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Audit Service",
    description="Event-driven audit logging service for task operations",
    version="1.0.0",
    lifespan=lifespan
)

# Create Dapr app
dapr_app = DaprApp(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audit-service",
        "timestamp": datetime.utcnow().isoformat(),
        "buffer_size": log_writer.get_buffer_size() if log_writer else 0
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring."""
    if not log_writer:
        return {"error": "LogWriter not initialized"}

    return {
        "events_processed": log_writer.events_processed,
        "events_written": log_writer.events_written,
        "buffer_size": log_writer.get_buffer_size(),
        "last_write_time": log_writer.last_write_time.isoformat() if log_writer.last_write_time else None
    }


@dapr_app.subscribe(pubsub="kafka-pubsub", topic="task-events")
async def task_events_handler(event: Dict[str, Any]):
    """
    Handle task events from Kafka via Dapr Pub/Sub.

    Subscribes to task-events topic and logs all task operations:
    - task.created
    - task.updated
    - task.deleted
    - task.completed
    - task.assigned
    - task.commented
    """
    try:
        print(f"Received event: {event.get('event_type')} for task {event.get('task_id')}")

        # Add event to buffer for batch writing
        if log_writer:
            await log_writer.add_event(event)
        else:
            print("WARNING: LogWriter not initialized, event dropped")

        return {"success": True}

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/flush")
async def flush_buffer():
    """
    Manually flush the event buffer to database.
    Useful for testing and debugging.
    """
    if not log_writer:
        return {"error": "LogWriter not initialized"}

    await log_writer.flush()
    return {
        "success": True,
        "message": "Buffer flushed successfully",
        "events_written": log_writer.events_written
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8004"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
