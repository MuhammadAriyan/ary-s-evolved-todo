"""Notification Service - Time-based reminder notifications microservice.

This service:
- Subscribes to Dapr Bindings (cron) for periodic reminder checks
- Checks for due reminders every minute
- Sends notifications via multiple channels (email, in-app, push)
- Implements idempotency to prevent duplicate notifications
- Handles timezone conversion for accurate reminder delivery
"""
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient

from scheduler import ReminderScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
reminder_scheduler: Optional[ReminderScheduler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global reminder_scheduler

    logger.info("Starting Notification Service...")

    # Initialize ReminderScheduler
    reminder_scheduler = ReminderScheduler(
        dapr_store_name="redis-statestore",
        dapr_http_port=3500,
        database_url=None  # Will use environment variable
    )
    await reminder_scheduler.initialize()

    logger.info("Notification Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down Notification Service...")
    if reminder_scheduler:
        await reminder_scheduler.cleanup()
    logger.info("Notification Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Time-based reminder notifications via multiple channels",
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

# Create Dapr app for Bindings subscriptions
dapr_app = DaprApp(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification",
        "scheduler_active": reminder_scheduler is not None
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring."""
    if not reminder_scheduler:
        return {"error": "ReminderScheduler not initialized"}

    return {
        "total_reminders_checked": reminder_scheduler.total_reminders_checked,
        "total_notifications_sent": reminder_scheduler.total_notifications_sent,
        "total_errors": reminder_scheduler.total_errors,
        "last_check_time": reminder_scheduler.last_check_time.isoformat() if reminder_scheduler.last_check_time else None,
    }


@app.post("/cron")
async def cron_handler():
    """
    Dapr Bindings handler for cron trigger.

    T057: Dapr Bindings subscription endpoint
    T058: Triggers ReminderScheduler to check for due reminders

    This endpoint is called by Dapr every minute via the cron binding.
    """
    try:
        logger.info("Cron trigger received - checking for due reminders")

        if not reminder_scheduler:
            logger.error("ReminderScheduler not initialized")
            return {"success": False, "error": "Scheduler not initialized"}

        # T058: Check for due reminders and send notifications
        await reminder_scheduler.check_and_send_reminders()

        return {"success": True}

    except Exception as e:
        logger.error(f"Error in cron handler: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
