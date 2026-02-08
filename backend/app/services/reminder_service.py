"""ReminderService - CRUD operations for scheduled reminders."""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service for managing scheduled reminders.

    T062: CRUD operations on scheduled_reminders table
    """

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.engine = None

    def initialize(self):
        """Initialize database connection."""
        if self.database_url:
            self.engine = create_engine(self.database_url)
            logger.info("ReminderService initialized")
        else:
            logger.warning("Database URL not configured")

    def create_reminder(
        self,
        task_id: str,
        user_id: str,
        reminder_time: datetime,
        timezone: str = "UTC",
        notification_channels: Optional[List[str]] = None,
        cron_expression: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new scheduled reminder.

        Args:
            task_id: Task ID
            user_id: User ID
            reminder_time: When to send the reminder
            timezone: User's timezone
            notification_channels: List of channels (email, in_app, push)
            cron_expression: Optional cron expression for recurring reminders

        Returns:
            Reminder ID if successful, None otherwise
        """
        if not self.engine:
            logger.error("Database engine not initialized")
            return None

        try:
            with Session(self.engine) as session:
                # Insert reminder
                query = """
                    INSERT INTO scheduled_reminders
                    (task_id, user_id, reminder_time, timezone, notification_channels,
                     cron_expression, status, created_at, updated_at)
                    VALUES (:task_id, :user_id, :reminder_time, :timezone, :channels,
                            :cron_expression, 'pending', NOW(), NOW())
                    RETURNING id
                """
                result = session.execute(
                    query,
                    {
                        "task_id": task_id,
                        "user_id": user_id,
                        "reminder_time": reminder_time,
                        "timezone": timezone,
                        "channels": notification_channels or ["in_app"],
                        "cron_expression": cron_expression
                    }
                )
                reminder_id = result.scalar()
                session.commit()

                logger.info(f"Created reminder {reminder_id} for task {task_id}")
                return reminder_id

        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}")
            return None

    def get_reminders_for_task(self, task_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all reminders for a specific task.

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)

        Returns:
            List of reminder dictionaries
        """
        if not self.engine:
            return []

        try:
            with Session(self.engine) as session:
                query = """
                    SELECT id, task_id, user_id, reminder_time, timezone,
                           notification_channels, cron_expression, status,
                           last_triggered_at, created_at, updated_at
                    FROM scheduled_reminders
                    WHERE task_id = :task_id AND user_id = :user_id
                    ORDER BY reminder_time ASC
                """
                result = session.execute(query, {"task_id": task_id, "user_id": user_id})
                reminders = [dict(row) for row in result]
                return reminders

        except Exception as e:
            logger.error(f"Error getting reminders: {str(e)}")
            return []

    def get_reminder(self, reminder_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific reminder by ID.

        Args:
            reminder_id: Reminder ID
            user_id: User ID (for authorization)

        Returns:
            Reminder dictionary if found, None otherwise
        """
        if not self.engine:
            return None

        try:
            with Session(self.engine) as session:
                query = """
                    SELECT id, task_id, user_id, reminder_time, timezone,
                           notification_channels, cron_expression, status,
                           last_triggered_at, created_at, updated_at
                    FROM scheduled_reminders
                    WHERE id = :reminder_id AND user_id = :user_id
                """
                result = session.execute(query, {"reminder_id": reminder_id, "user_id": user_id})
                row = result.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting reminder: {str(e)}")
            return None

    def update_reminder(
        self,
        reminder_id: int,
        user_id: str,
        reminder_time: Optional[datetime] = None,
        timezone: Optional[str] = None,
        notification_channels: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> bool:
        """
        Update a scheduled reminder.

        Args:
            reminder_id: Reminder ID
            user_id: User ID (for authorization)
            reminder_time: New reminder time
            timezone: New timezone
            notification_channels: New notification channels
            status: New status

        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            return False

        try:
            with Session(self.engine) as session:
                # Build update query dynamically
                updates = []
                params = {"reminder_id": reminder_id, "user_id": user_id}

                if reminder_time is not None:
                    updates.append("reminder_time = :reminder_time")
                    params["reminder_time"] = reminder_time

                if timezone is not None:
                    updates.append("timezone = :timezone")
                    params["timezone"] = timezone

                if notification_channels is not None:
                    updates.append("notification_channels = :channels")
                    params["channels"] = notification_channels

                if status is not None:
                    updates.append("status = :status")
                    params["status"] = status

                if not updates:
                    return True  # Nothing to update

                updates.append("updated_at = NOW()")

                query = f"""
                    UPDATE scheduled_reminders
                    SET {', '.join(updates)}
                    WHERE id = :reminder_id AND user_id = :user_id
                """
                result = session.execute(query, params)
                session.commit()

                logger.info(f"Updated reminder {reminder_id}")
                return result.rowcount > 0

        except Exception as e:
            logger.error(f"Error updating reminder: {str(e)}")
            return False

    def delete_reminder(self, reminder_id: int, user_id: str) -> bool:
        """
        Delete a scheduled reminder.

        Args:
            reminder_id: Reminder ID
            user_id: User ID (for authorization)

        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            return False

        try:
            with Session(self.engine) as session:
                query = """
                    DELETE FROM scheduled_reminders
                    WHERE id = :reminder_id AND user_id = :user_id
                """
                result = session.execute(query, {"reminder_id": reminder_id, "user_id": user_id})
                session.commit()

                logger.info(f"Deleted reminder {reminder_id}")
                return result.rowcount > 0

        except Exception as e:
            logger.error(f"Error deleting reminder: {str(e)}")
            return False

    def cleanup(self):
        """Cleanup resources."""
        if self.engine:
            self.engine.dispose()
