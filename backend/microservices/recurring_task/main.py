"""Recurring Task Service - Advanced recurring task pattern microservice.

T106: Create Recurring Task Service with Dapr Pub/Sub subscription to task-events

This service:
- Subscribes to task-events topic via Dapr Pub/Sub
- Listens for task.completed events with recurring patterns
- Calculates next occurrence using croniter with timezone awareness
- Creates new task instances automatically
- Implements idempotency to prevent duplicate task creation
- Supports preset patterns and custom cron expressions
"""
import asyncio
import logging
import os
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
import httpx

from pattern_parser import PatternParser
from task_generator import TaskGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
pattern_parser: Optional[PatternParser] = None
task_generator: Optional[TaskGenerator] = None
backend_api_url: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Metrics
total_events_processed = 0
total_tasks_created = 0
total_errors = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global pattern_parser, task_generator

    logger.info("Starting Recurring Task Service...")

    # T107: Initialize PatternParser
    pattern_parser = PatternParser()

    # T108, T110, T111: Initialize TaskGenerator with Redis state store
    task_generator = TaskGenerator(
        dapr_store_name="redis-statestore",
        dapr_http_port=3500
    )
    await task_generator.initialize()

    logger.info("Recurring Task Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down Recurring Task Service...")
    if task_generator:
        await task_generator.cleanup()
    logger.info("Recurring Task Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Advanced recurring task patterns with cron expressions",
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
        "service": "recurring-task",
        "parser_active": pattern_parser is not None,
        "generator_active": task_generator is not None
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring."""
    return {
        "total_events_processed": total_events_processed,
        "total_tasks_created": total_tasks_created,
        "total_errors": total_errors,
    }


async def create_task_instance(task_data: Dict[str, Any], jwt_token: str) -> Optional[str]:
    """
    Create a new task instance via backend API.

    Args:
        task_data: Task data to create
        jwt_token: JWT token for authentication

    Returns:
        New task ID if successful, None otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_api_url}/api/v1/tasks",
                json=task_data,
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 201:
                result = response.json()
                new_task_id = result.get("id")
                logger.info(f"Created task instance: {new_task_id}")
                return new_task_id
            else:
                logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        logger.error(f"Error creating task instance: {str(e)}")
        return None


@dapr_app.subscribe(pubsub="kafka-pubsub", topic="task-events")
async def task_events_handler(event_data: dict):
    """
    Dapr Pub/Sub subscription handler for task-events topic.

    T106: Subscribe to task-events via Dapr Pub/Sub
    T120: Listen for task.completed events with recurring patterns
    T121: Calculate next occurrence correctly
    T122: Create new task instance with correct due date
    T111: Implement idempotency checking

    Args:
        event_data: Event payload from Kafka
    """
    global total_events_processed, total_tasks_created, total_errors

    try:
        total_events_processed += 1

        logger.info(f"Received task-events: {event_data.get('event_type')}")

        # Extract event details
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        task_data = event_data.get("data", {})
        jwt_token = event_data.get("jwt_token")  # For creating new tasks

        # T120: Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return {"success": True, "message": "Event type not relevant"}

        # Check if task has recurring pattern
        recurring_pattern = task_data.get("recurring_pattern")
        if not recurring_pattern:
            logger.debug(f"Task {task_data.get('id')} has no recurring pattern")
            return {"success": True, "message": "No recurring pattern"}

        parent_task_id = task_data.get("id")
        user_timezone = task_data.get("timezone", "UTC")

        logger.info(
            f"Processing recurring task completion: task_id={parent_task_id}, "
            f"pattern={recurring_pattern}, timezone={user_timezone}"
        )

        # T107: Parse and validate the recurring pattern
        parsed = pattern_parser.parse_pattern(recurring_pattern, is_preset=False)
        if not parsed["valid"]:
            logger.error(f"Invalid recurring pattern: {parsed['error']}")
            total_errors += 1
            return {"success": False, "error": parsed["error"]}

        cron_expression = parsed["cron_expression"]

        # T121: Calculate next occurrence with timezone awareness
        next_occurrence = task_generator.calculate_next_occurrence(
            cron_expression=cron_expression,
            base_time=None,  # Use current time
            user_timezone=user_timezone
        )

        if not next_occurrence["success"]:
            logger.error(f"Failed to calculate next occurrence: {next_occurrence['error']}")
            total_errors += 1
            return {"success": False, "error": next_occurrence["error"]}

        next_occurrence_utc = next_occurrence["next_occurrence_utc"]
        next_occurrence_date = next_occurrence_utc.strftime("%Y-%m-%d")

        # T111: Check idempotency - prevent duplicate task creation
        is_duplicate = await task_generator.check_idempotency(
            parent_task_id=parent_task_id,
            next_occurrence_date=next_occurrence_date
        )

        if is_duplicate:
            logger.info(f"Task instance already exists for {parent_task_id} on {next_occurrence_date}")
            return {"success": True, "message": "Task instance already exists"}

        # T108, T122: Generate new task instance with correct due date
        new_task_data = task_generator.generate_task_instance(
            parent_task=task_data,
            next_occurrence_utc=next_occurrence_utc
        )

        # Create the task via backend API
        if not jwt_token:
            logger.error("No JWT token provided in event data")
            total_errors += 1
            return {"success": False, "error": "Missing JWT token"}

        new_task_id = await create_task_instance(new_task_data, jwt_token)

        if not new_task_id:
            logger.error("Failed to create task instance")
            total_errors += 1
            return {"success": False, "error": "Failed to create task"}

        # T111: Mark task as created for idempotency
        await task_generator.mark_task_created(
            parent_task_id=parent_task_id,
            next_occurrence_date=next_occurrence_date,
            new_task_id=new_task_id
        )

        total_tasks_created += 1

        logger.info(
            f"Successfully created recurring task instance: "
            f"parent={parent_task_id}, new={new_task_id}, due={next_occurrence_utc.isoformat()}"
        )

        return {
            "success": True,
            "new_task_id": new_task_id,
            "next_occurrence": next_occurrence_utc.isoformat()
        }

    except Exception as e:
        logger.error(f"Error handling task-events: {str(e)}")
        total_errors += 1
        return {"success": False, "error": str(e)}


@app.post("/validate-pattern")
async def validate_pattern_endpoint(request: Dict[str, Any]):
    """
    Endpoint to validate a cron pattern.

    T109: Validate cron expressions

    Args:
        request: {"pattern": str, "is_preset": bool}

    Returns:
        Validation result
    """
    try:
        pattern = request.get("pattern")
        is_preset = request.get("is_preset", False)

        if not pattern:
            return {
                "valid": False,
                "error": "Pattern is required"
            }

        # Parse and validate
        result = pattern_parser.parse_pattern(pattern, is_preset=is_preset)

        return result

    except Exception as e:
        logger.error(f"Error validating pattern: {str(e)}")
        return {
            "valid": False,
            "error": str(e)
        }


@app.get("/preset-patterns")
async def get_preset_patterns():
    """
    Get all available preset patterns.

    Returns:
        Dict of preset patterns
    """
    try:
        presets = pattern_parser.get_preset_patterns()

        # Add descriptions
        result = {}
        for name, cron_expr in presets.items():
            result[name] = {
                "cron_expression": cron_expr,
                "description": pattern_parser.describe_pattern(cron_expr)
            }

        return result

    except Exception as e:
        logger.error(f"Error getting preset patterns: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
