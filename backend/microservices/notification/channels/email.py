"""EmailChannel - Send email notifications via SendGrid."""
import logging
import os
from typing import Dict, Any, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent

logger = logging.getLogger(__name__)


class EmailChannel:
    """
    Email notification channel using SendGrid.

    T059: Implement EmailChannel using SendGrid/AWS SES
    """

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
        self.client: Optional[SendGridAPIClient] = None
        self.enabled = False

    async def initialize(self):
        """Initialize SendGrid client."""
        if not self.api_key:
            logger.warning("SendGrid API key not configured - email notifications disabled")
            self.enabled = False
            return

        try:
            self.client = SendGridAPIClient(self.api_key)
            self.enabled = True
            logger.info("EmailChannel initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing EmailChannel: {str(e)}")
            self.enabled = False

    async def send(self, notification_data: Dict[str, Any]):
        """
        Send email notification.

        Args:
            notification_data: Dictionary containing:
                - user_id: User ID
                - task_id: Task ID
                - reminder_id: Reminder ID
                - message: Notification message
                - user_email: (optional) User's email address
        """
        if not self.enabled:
            logger.warning("EmailChannel not enabled - skipping email notification")
            return

        try:
            # Get user email (in production, fetch from database)
            user_email = notification_data.get('user_email', 'user@example.com')

            # Construct email
            subject = "Task Reminder"
            html_content = self._build_email_html(notification_data)

            message = Mail(
                from_email=From(self.from_email, "Task Manager"),
                to_emails=To(user_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content)
            )

            # Send via SendGrid
            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {user_email}")
            else:
                logger.warning(f"Email send returned status {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            raise

    def _build_email_html(self, notification_data: Dict[str, Any]) -> str:
        """Build HTML email content."""
        task_id = notification_data.get('task_id', 'Unknown')
        message = notification_data.get('message', 'You have a task reminder')
        reminder_time = notification_data.get('reminder_time', '')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 20px; margin-top: 20px; }}
                .button {{ background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Task Reminder</h1>
                </div>
                <div class="content">
                    <h2>You have a task reminder!</h2>
                    <p><strong>Task ID:</strong> {task_id}</p>
                    <p><strong>Message:</strong> {message}</p>
                    <p><strong>Reminder Time:</strong> {reminder_time}</p>
                    <a href="http://localhost:3000/tasks/{task_id}" class="button">View Task</a>
                </div>
                <div class="footer">
                    <p>This is an automated reminder from your Task Manager.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
