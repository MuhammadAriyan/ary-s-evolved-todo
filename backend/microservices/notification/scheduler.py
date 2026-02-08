"""ReminderScheduler - Checks for due reminders and sends notifications."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os

import pytz
from croniter import croniter
from dapr.clients import DaprClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from channels.email import EmailChannel
from channels.in_app import InAppChannel
from channels.push import PushChannel

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Scheduler that checks for due reminders and sends notifications.

    T058: Check for due reminders every minute
    T063: Idempotency checking using Redis state store
    T064: Timezone conversion logic
    """

    def __init__(
        self,
        dapr_store_name: str = "redis-statestore",
        dapr_http_port: int = 3500,
        database_url: Optional[str] = None
    ):
        self.dapr_store_name = dapr_store_name
        self.dapr_http_port = dapr_http_port
        self.database_url = database_url or os.getenv("DATABASE_URL")

        # Notification channels
        self.email_channel: Optional[EmailChannel] = None
        self.in_app_channel: Optional[InAppChannel] = None
        self.push_channel: Optional[PushChannel] = None

        # Dapr client for state store
        self.dapr_client: Optional[DaprClient] = None

        # Database engine
        self.engine = None

        # Metrics
        self.total_reminders_checked = 0
        self.total_notifications_sent = 0
        self.total_errors = 0
        self.last_check_time: Optional[datetime] = None

    async def initialize(self):
        """Initialize scheduler and notification channels."""
        logger.info("Initializing ReminderScheduler...")

        # Initialize Dapr client
        self.dapr_client = DaprClient()

        # Initialize database engine
        if self.database_url:
            self.engine = create_engine(self.database_url)

        # T059: Initialize EmailChannel
        self.email_channel = EmailChannel()
        await self.email_channel.initialize()

        # T060: Initialize InAppChannel
        self.in_app_channel = InAppChannel(
            dapr_pubsub_name="kafka-pubsub",
            dapr_http_port=self.dapr_http_port
        )
        await self.in_app_channel.initialize()

        # T061: Initialize PushChannel (stub)
        self.push_channel = PushChannel()
        await self.push_channel.initialize()

        logger.info("ReminderScheduler initialized successfully")

    async def cleanup(self):
        """Cleanup resources."""
        if self.dapr_client:
            self.dapr_client.close()
        if self.engine:
            self.engine.dispose()

    async def check_and_send_reminders(self):
        """
        Check for due reminders and send notifications.

        T058: Main scheduler logic
        T063: Idempotency checking
        T064: Timezone conversion
        """
        try:
            self.last_check_time = datetime.utcnow()

            # Get due reminders from database
            due_reminders = await self._get_due_reminders()
            self.total_reminders_checked += len(due_reminders)

            logger.info(f"Found {len(due_reminders)} due reminders")

            # Process each reminder
            for reminder in due_reminders:
                try:
                    # T063: Check idempotency - prevent duplicate notifications
                    if await self._is_already_sent(reminder):
                        logger.info(f"Reminder {reminder['id']} already sent, skipping")
                        continue

                    # T064: Convert reminder time to user's timezone
                    reminder_time_utc = await self._convert_to_utc(
                        reminder['reminder_time'],
                        reminder['timezone']
                    )

                    # Check if reminder is actually due (within last minute)
                    now_utc = datetime.utcnow()
                    if reminder_time_utc > now_utc:
                        logger.debug(f"Reminder {reminder['id']} not yet due")
                        continue

                    # Send notifications via configured channels
                    await self._send_notifications(reminder)

                    # T063: Mark as sent in idempotency store
                    await self._mark_as_sent(reminder)

                    # Update reminder status in database
                    await self._update_reminder_status(reminder['id'], 'sent')

                    self.total_notifications_sent += 1
                    logger.info(f"Successfully sent reminder {reminder['id']}")

                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.get('id')}: {str(e)}")
                    self.total_errors += 1

        except Exception as e:
            logger.error(f"Error in check_and_send_reminders: {str(e)}")
            self.total_errors += 1

    async def _get_due_reminders(self) -> List[Dict[str, Any]]:
        """
        Get reminders that are due for notification.

        Returns reminders where:
        - status is 'pending'
        - reminder_time is in the past (considering timezone)
        - within the last 2 minutes (to handle service restarts)
        """
        if not self.engine:
            logger.warning("Database engine not initialized")
            return []

        try:
            with Session(self.engine) as session:
                # Query for due reminders
                # Note: This is a simplified query. In production, you'd use SQLModel
                query = """
                    SELECT id, task_id, user_id, reminder_time, timezone,
                           notification_channels, status
                    FROM scheduled_reminders
                    WHERE status = 'pending'
                      AND reminder_time <= NOW() + INTERVAL '2 minutes'
                      AND reminder_time >= NOW() - INTERVAL '2 minutes'
                    ORDER BY reminder_time ASC
                    LIMIT 100
                """
                result = session.execute(query)
                reminders = [dict(row) for row in result]
                return reminders

        except Exception as e:
            logger.error(f"Error querying due reminders: {str(e)}")
            return []

    async def _is_already_sent(self, reminder: Dict[str, Any]) -> bool:
        """
        T063: Check if reminder has already been sent (idempotency).

        Uses Redis state store with key: reminder:{task_id}:{reminder_time}
        """
        try:
            idempotency_key = f"reminder:{reminder['task_id']}:{reminder['reminder_time']}"

            # Check Redis state store via Dapr
            state = await asyncio.to_thread(
                self.dapr_client.get_state,
                store_name=self.dapr_store_name,
                key=idempotency_key
            )

            return state.data is not None

        except Exception as e:
            logger.error(f"Error checking idempotency: {str(e)}")
            # On error, assume not sent to avoid missing notifications
            return False

    async def _mark_as_sent(self, reminder: Dict[str, Any]):
        """
        T063: Mark reminder as sent in idempotency store.

        Stores with TTL of 7 days to prevent indefinite growth.
        """
        try:
            idempotency_key = f"reminder:{reminder['task_id']}:{reminder['reminder_time']}"

            # Store in Redis state store via Dapr with TTL
            await asyncio.to_thread(
                self.dapr_client.save_state,
                store_name=self.dapr_store_name,
                key=idempotency_key,
                value=str(datetime.utcnow().isoformat()),
                options={"ttlInSeconds": 604800}  # 7 days
            )

        except Exception as e:
            logger.error(f"Error marking as sent: {str(e)}")

    async def _convert_to_utc(self, reminder_time: datetime, timezone_str: str) -> datetime:
        """
        T064: Convert reminder time from user's timezone to UTC.

        Args:
            reminder_time: Naive datetime in user's timezone
            timezone_str: Timezone string (e.g., 'America/New_York')

        Returns:
            Timezone-aware datetime in UTC
        """
        try:
            # Get user's timezone
            user_tz = pytz.timezone(timezone_str)

            # If reminder_time is naive, localize it to user's timezone
            if reminder_time.tzinfo is None:
                localized_time = user_tz.localize(reminder_time)
            else:
                localized_time = reminder_time

            # Convert to UTC
            utc_time = localized_time.astimezone(pytz.utc)

            return utc_time

        except Exception as e:
            logger.error(f"Error converting timezone: {str(e)}")
            # Fallback: assume UTC
            return reminder_time.replace(tzinfo=pytz.utc) if reminder_time.tzinfo is None else reminder_time

    async def _send_notifications(self, reminder: Dict[str, Any]):
        """
        Send notifications via configured channels.

        T059: Email channel
        T060: In-app channel
        T061: Push channel
        """
        channels = reminder.get('notification_channels', ['in_app'])

        # Prepare notification data
        notification_data = {
            'reminder_id': reminder['id'],
            'task_id': reminder['task_id'],
            'user_id': reminder['user_id'],
            'reminder_time': reminder['reminder_time'],
            'message': f"Reminder: Task {reminder['task_id']} is due"
        }

        # Send via each configured channel
        for channel in channels:
            try:
                if channel == 'email' and self.email_channel:
                    await self.email_channel.send(notification_data)
                elif channel == 'in_app' and self.in_app_channel:
                    await self.in_app_channel.send(notification_data)
                elif channel == 'push' and self.push_channel:
                    await self.push_channel.send(notification_data)
                else:
                    logger.warning(f"Unknown or uninitialized channel: {channel}")

            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {str(e)}")

    async def _update_reminder_status(self, reminder_id: int, status: str):
        """Update reminder status in database."""
        if not self.engine:
            return

        try:
            with Session(self.engine) as session:
                query = """
                    UPDATE scheduled_reminders
                    SET status = :status, last_triggered_at = NOW(), updated_at = NOW()
                    WHERE id = :reminder_id
                """
                session.execute(query, {"status": status, "reminder_id": reminder_id})
                session.commit()

        except Exception as e:
            logger.error(f"Error updating reminder status: {str(e)}")
