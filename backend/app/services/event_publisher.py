"""EventPublisher service for publishing events to Kafka via Dapr Pub/Sub."""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

from dapr.clients import DaprClient
from dapr.clients.grpc._response import TopicEventResponse

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing events to Kafka topics via Dapr Pub/Sub."""

    def __init__(self, pubsub_name: str = "kafka-pubsub"):
        """
        Initialize EventPublisher.

        Args:
            pubsub_name: Name of the Dapr Pub/Sub component (default: kafka-pubsub)
        """
        self.pubsub_name = pubsub_name
        self.client: Optional[DaprClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = DaprClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            self.client.close()

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        user_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publish an event to a Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (e.g., 'task-events', 'task-updates')
            event_type: Type of event (e.g., 'task.created', 'task.updated')
            data: Event payload data
            user_id: User ID who triggered the event
            metadata: Optional metadata for the event

        Returns:
            Event ID (UUID)

        Raises:
            Exception: If publishing fails
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Construct event payload
        event_payload = {
            "event_id": event_id,
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": timestamp,
            "data": data,
            "metadata": metadata or {}
        }

        try:
            # Publish to Dapr Pub/Sub
            if not self.client:
                self.client = DaprClient()

            self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(event_payload),
                data_content_type="application/json"
            )

            logger.info(
                f"Published event: {event_type} to topic: {topic} "
                f"(event_id: {event_id}, user_id: {user_id})"
            )

            return event_id

        except Exception as e:
            logger.error(
                f"Failed to publish event: {event_type} to topic: {topic} "
                f"(event_id: {event_id}, user_id: {user_id}): {str(e)}"
            )
            raise

    async def publish_task_event(
        self,
        event_type: str,
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any],
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a task-related event.

        Args:
            event_type: Event type (e.g., 'task.created', 'task.updated', 'task.deleted')
            task_id: Task ID
            user_id: User ID who triggered the event
            task_data: Current task data
            before_state: Task state before the change (for updates)
            after_state: Task state after the change (for updates)

        Returns:
            Event ID
        """
        data = {
            "task_id": task_id,
            "task": task_data
        }

        if before_state:
            data["before_state"] = before_state
        if after_state:
            data["after_state"] = after_state

        # Publish to both task-events (for audit) and task-updates (for real-time sync)
        event_id = await self.publish_event(
            topic="task-events",
            event_type=event_type,
            data=data,
            user_id=user_id
        )

        # Also publish to task-updates for real-time synchronization
        if event_type in ["task.created", "task.updated", "task.deleted", "task.completed"]:
            await self.publish_event(
                topic="task-updates",
                event_type=event_type,
                data=data,
                user_id=user_id,
                metadata={"original_event_id": event_id}
            )

        return event_id

    async def publish_reminder_event(
        self,
        event_type: str,
        reminder_id: int,
        task_id: str,
        user_id: str,
        reminder_data: Dict[str, Any]
    ) -> str:
        """
        Publish a reminder-related event.

        Args:
            event_type: Event type (e.g., 'reminder.scheduled', 'reminder.triggered')
            reminder_id: Reminder ID
            task_id: Associated task ID
            user_id: User ID
            reminder_data: Reminder data

        Returns:
            Event ID
        """
        data = {
            "reminder_id": reminder_id,
            "task_id": task_id,
            "reminder": reminder_data
        }

        return await self.publish_event(
            topic="reminders",
            event_type=event_type,
            data=data,
            user_id=user_id
        )

    async def publish_audit_event(
        self,
        operation: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Publish an audit log event.

        Args:
            operation: Operation performed (e.g., 'create', 'update', 'delete')
            resource_type: Type of resource (e.g., 'task', 'reminder', 'group')
            resource_id: Resource ID
            user_id: User ID who performed the operation
            before_state: State before the operation
            after_state: State after the operation
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Event ID
        """
        data = {
            "operation": operation,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "before_state": before_state,
            "after_state": after_state,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        return await self.publish_event(
            topic="audit-logs",
            event_type=f"{resource_type}.{operation}",
            data=data,
            user_id=user_id
        )


# Singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get the singleton EventPublisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
