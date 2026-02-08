"""InAppChannel - Send in-app notifications via WebSocket."""
import logging
from typing import Dict, Any, Optional

from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class InAppChannel:
    """
    In-app notification channel via WebSocket.

    T060: Implement InAppChannel publishing to WebSocket
    """

    def __init__(self, dapr_pubsub_name: str = "kafka-pubsub", dapr_http_port: int = 3500):
        self.dapr_pubsub_name = dapr_pubsub_name
        self.dapr_http_port = dapr_http_port
        self.dapr_client: Optional[DaprClient] = None
        self.enabled = False

    async def initialize(self):
        """Initialize Dapr client for Pub/Sub."""
        try:
            self.dapr_client = DaprClient()
            self.enabled = True
            logger.info("InAppChannel initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing InAppChannel: {str(e)}")
            self.enabled = False

    async def send(self, notification_data: Dict[str, Any]):
        """
        Send in-app notification via WebSocket.

        Publishes notification event to task-updates topic, which is consumed
        by WebSocket Sync Service and broadcast to connected clients.

        Args:
            notification_data: Dictionary containing:
                - user_id: User ID
                - task_id: Task ID
                - reminder_id: Reminder ID
                - message: Notification message
        """
        if not self.enabled:
            logger.warning("InAppChannel not enabled - skipping in-app notification")
            return

        try:
            # Construct notification event
            event_data = {
                "event_type": "notification.reminder",
                "user_id": notification_data.get('user_id'),
                "data": {
                    "type": "reminder",
                    "task_id": notification_data.get('task_id'),
                    "reminder_id": notification_data.get('reminder_id'),
                    "message": notification_data.get('message'),
                    "timestamp": notification_data.get('reminder_time')
                }
            }

            # Publish to task-updates topic via Dapr Pub/Sub
            self.dapr_client.publish_event(
                pubsub_name=self.dapr_pubsub_name,
                topic_name="task-updates",
                data=event_data,
                data_content_type="application/json"
            )

            logger.info(f"In-app notification published for user {notification_data.get('user_id')}")

        except Exception as e:
            logger.error(f"Error sending in-app notification: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
        if self.dapr_client:
            self.dapr_client.close()
