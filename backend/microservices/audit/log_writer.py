"""LogWriter - Batch writing of audit logs to PostgreSQL."""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError

from app.models.audit_log import AuditLog


class LogWriter:
    """
    Batch writer for audit logs with configurable buffer size and flush interval.

    Features:
    - Buffers events in memory (max 100 events or 5 seconds)
    - Batch writes to PostgreSQL for performance
    - Automatic flush on buffer full or timeout
    - Thread-safe event queue
    """

    def __init__(
        self,
        session: Session,
        buffer_size: int = 100,
        flush_interval: float = 5.0
    ):
        """
        Initialize LogWriter.

        Args:
            session: SQLModel database session
            buffer_size: Maximum events to buffer before flush (default: 100)
            flush_interval: Maximum seconds between flushes (default: 5.0)
        """
        self.session = session
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        self.buffer: List[Dict[str, Any]] = []
        self.lock = asyncio.Lock()
        self.flush_task = None
        self.running = False

        # Metrics
        self.events_processed = 0
        self.events_written = 0
        self.last_write_time: datetime = None

    def start(self):
        """Start the background flush task."""
        self.running = True
        self.flush_task = asyncio.create_task(self._periodic_flush())
        print(f"LogWriter started (buffer_size={self.buffer_size}, flush_interval={self.flush_interval}s)")

    async def stop(self):
        """Stop the background flush task and flush remaining events."""
        self.running = False

        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass

        # Flush any remaining events
        await self.flush()
        print("LogWriter stopped")

    async def add_event(self, event: Dict[str, Any]):
        """
        Add event to buffer for batch writing.

        Args:
            event: Event data from Kafka
        """
        async with self.lock:
            self.buffer.append(event)
            self.events_processed += 1

            # Flush if buffer is full
            if len(self.buffer) >= self.buffer_size:
                await self._flush_internal()

    async def flush(self):
        """Manually flush the buffer to database."""
        async with self.lock:
            await self._flush_internal()

    async def _flush_internal(self):
        """Internal flush method (must be called with lock held)."""
        if not self.buffer:
            return

        events_to_write = self.buffer.copy()
        self.buffer.clear()

        try:
            # Convert events to AuditLog models
            audit_logs = []
            for event in events_to_write:
                audit_log = self._event_to_audit_log(event)
                if audit_log:
                    audit_logs.append(audit_log)

            # Batch insert to database
            if audit_logs:
                self.session.add_all(audit_logs)
                self.session.commit()

                self.events_written += len(audit_logs)
                self.last_write_time = datetime.utcnow()

                print(f"Flushed {len(audit_logs)} audit logs to database")

        except SQLAlchemyError as e:
            print(f"Database error during flush: {str(e)}")
            self.session.rollback()

            # Re-add events to buffer for retry
            self.buffer.extend(events_to_write)

        except Exception as e:
            print(f"Unexpected error during flush: {str(e)}")
            self.session.rollback()

    async def _periodic_flush(self):
        """Background task to flush buffer periodically."""
        while self.running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic flush: {str(e)}")

    def _event_to_audit_log(self, event: Dict[str, Any]) -> AuditLog:
        """
        Convert Kafka event to AuditLog model.

        Args:
            event: Event data from Kafka

        Returns:
            AuditLog model instance
        """
        try:
            # Extract common fields
            event_type = event.get("event_type", "unknown")
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            timestamp = event.get("timestamp")

            # Parse timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()

            # Extract before/after state
            before_state = event.get("before_state")
            after_state = event.get("after_state")

            # Extract metadata
            metadata = event.get("metadata", {})
            ip_address = metadata.get("ip_address")
            user_agent = metadata.get("user_agent")
            request_id = metadata.get("request_id")

            # Determine operation from event_type
            operation = event_type.split('.')[-1] if '.' in event_type else event_type

            # Create AuditLog instance
            audit_log = AuditLog(
                task_id=task_id,
                user_id=user_id,
                operation=operation,
                before_state=before_state,
                after_state=after_state,
                timestamp=timestamp,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                event_type=event_type
            )

            return audit_log

        except Exception as e:
            print(f"Error converting event to AuditLog: {str(e)}")
            print(f"Event data: {event}")
            return None

    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)
