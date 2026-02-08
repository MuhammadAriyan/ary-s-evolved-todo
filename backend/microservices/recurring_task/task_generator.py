"""Task Generator - Calculate next occurrence and create task instances.

T108: Calculate next occurrence and create new task instance
T110: Timezone-aware next occurrence calculation using croniter
T111: Idempotency checking using Redis state store

This module provides functionality to:
- Calculate next occurrence datetime from cron expression
- Handle timezone-aware scheduling
- Create new task instances from parent recurring tasks
- Implement idempotency to prevent duplicate task creation
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json

from croniter import croniter
import pytz
from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class TaskGenerator:
    """Generator for recurring task instances."""

    def __init__(
        self,
        dapr_store_name: str = "redis-statestore",
        dapr_http_port: int = 3500
    ):
        """
        Initialize the task generator.

        Args:
            dapr_store_name: Name of Dapr state store component
            dapr_http_port: Dapr HTTP port for state store operations
        """
        self.dapr_store_name = dapr_store_name
        self.dapr_http_port = dapr_http_port
        self.dapr_client: Optional[DaprClient] = None

    async def initialize(self):
        """Initialize Dapr client for state store operations."""
        try:
            self.dapr_client = DaprClient(
                f"http://localhost:{self.dapr_http_port}"
            )
            logger.info("TaskGenerator initialized with Dapr state store")
        except Exception as e:
            logger.error(f"Failed to initialize TaskGenerator: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
        if self.dapr_client:
            self.dapr_client.close()
            logger.info("TaskGenerator cleaned up")

    def calculate_next_occurrence(
        self,
        cron_expression: str,
        base_time: Optional[datetime] = None,
        user_timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Calculate the next occurrence datetime from a cron expression.

        T108: Calculate next occurrence
        T110: Timezone-aware calculation using croniter and pytz

        Args:
            cron_expression: Cron expression string
            base_time: Base datetime to calculate from (defaults to now)
            user_timezone: User's timezone (IANA timezone name, e.g., "America/New_York")

        Returns:
            Dict with next occurrence details:
            {
                "success": bool,
                "next_occurrence_utc": Optional[datetime],  # UTC datetime
                "next_occurrence_local": Optional[datetime],  # User's local time
                "timezone": str,
                "error": Optional[str]
            }
        """
        try:
            # T110: Handle timezone-aware calculation
            # Get user's timezone
            try:
                tz = pytz.timezone(user_timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                logger.warning(f"Unknown timezone '{user_timezone}', using UTC")
                tz = pytz.UTC
                user_timezone = "UTC"

            # Use current time if base_time not provided
            if base_time is None:
                # Get current time in UTC
                base_time = datetime.now(pytz.UTC)
            elif base_time.tzinfo is None:
                # If base_time is naive, assume it's in user's timezone
                base_time = tz.localize(base_time)

            # Convert to user's timezone for cron calculation
            base_time_local = base_time.astimezone(tz)

            # T110: Use croniter to calculate next occurrence
            iter_obj = croniter(cron_expression, base_time_local)
            next_occurrence_local = iter_obj.get_next(datetime)

            # Ensure the result is timezone-aware
            if next_occurrence_local.tzinfo is None:
                next_occurrence_local = tz.localize(next_occurrence_local)

            # Convert to UTC for storage
            next_occurrence_utc = next_occurrence_local.astimezone(pytz.UTC)

            logger.info(
                f"Calculated next occurrence: {next_occurrence_utc.isoformat()} UTC "
                f"({next_occurrence_local.isoformat()} {user_timezone})"
            )

            return {
                "success": True,
                "next_occurrence_utc": next_occurrence_utc,
                "next_occurrence_local": next_occurrence_local,
                "timezone": user_timezone,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error calculating next occurrence: {str(e)}")
            return {
                "success": False,
                "next_occurrence_utc": None,
                "next_occurrence_local": None,
                "timezone": user_timezone,
                "error": f"Calculation error: {str(e)}"
            }

    async def check_idempotency(
        self,
        parent_task_id: str,
        next_occurrence_date: str
    ) -> bool:
        """
        Check if a task instance has already been created for this occurrence.

        T111: Idempotency checking using Redis state store

        Args:
            parent_task_id: ID of the parent recurring task
            next_occurrence_date: Date string for the occurrence (ISO format)

        Returns:
            True if task already exists (duplicate), False if new
        """
        try:
            if not self.dapr_client:
                logger.error("Dapr client not initialized")
                return False

            # T111: Create idempotency key
            idempotency_key = f"recurring:{parent_task_id}:{next_occurrence_date}"

            # Check if key exists in Redis state store
            response = self.dapr_client.get_state(
                store_name=self.dapr_store_name,
                key=idempotency_key
            )

            if response.data:
                logger.info(f"Duplicate task detected: {idempotency_key}")
                return True  # Duplicate

            logger.debug(f"No duplicate found for: {idempotency_key}")
            return False  # New task

        except Exception as e:
            logger.error(f"Error checking idempotency: {str(e)}")
            # On error, assume not duplicate to avoid blocking task creation
            return False

    async def mark_task_created(
        self,
        parent_task_id: str,
        next_occurrence_date: str,
        new_task_id: str
    ) -> bool:
        """
        Mark that a task instance has been created for this occurrence.

        T111: Store idempotency marker in Redis

        Args:
            parent_task_id: ID of the parent recurring task
            next_occurrence_date: Date string for the occurrence (ISO format)
            new_task_id: ID of the newly created task instance

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.dapr_client:
                logger.error("Dapr client not initialized")
                return False

            # T111: Create idempotency key
            idempotency_key = f"recurring:{parent_task_id}:{next_occurrence_date}"

            # Store marker with task details
            marker_data = {
                "parent_task_id": parent_task_id,
                "next_occurrence_date": next_occurrence_date,
                "new_task_id": new_task_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            # Save to Redis state store with 90-day TTL
            self.dapr_client.save_state(
                store_name=self.dapr_store_name,
                key=idempotency_key,
                value=json.dumps(marker_data),
                state_metadata={"ttlInSeconds": "7776000"}  # 90 days
            )

            logger.info(f"Marked task created: {idempotency_key} -> {new_task_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking task created: {str(e)}")
            return False

    def generate_task_instance(
        self,
        parent_task: Dict[str, Any],
        next_occurrence_utc: datetime
    ) -> Dict[str, Any]:
        """
        Generate a new task instance from a parent recurring task.

        T108: Create new task instance with correct due date

        Args:
            parent_task: Parent task data (dict with task fields)
            next_occurrence_utc: Next occurrence datetime in UTC

        Returns:
            Dict with new task instance data
        """
        try:
            # T108: Create new task instance based on parent
            new_task = {
                "title": parent_task.get("title", "Recurring Task"),
                "description": parent_task.get("description", ""),
                "priority": parent_task.get("priority", "medium"),
                "tags": parent_task.get("tags", []),
                "due_date": next_occurrence_utc.isoformat(),
                "completed": False,
                "parent_task_id": parent_task.get("id"),
                "recurring_pattern": None,  # Instance doesn't have recurring pattern
                "user_id": parent_task.get("user_id"),
                "created_from_recurring": True
            }

            logger.info(
                f"Generated task instance from parent {parent_task.get('id')}: "
                f"due_date={next_occurrence_utc.isoformat()}"
            )

            return new_task

        except Exception as e:
            logger.error(f"Error generating task instance: {str(e)}")
            raise
