"""
Scheduler service for recurring tasks using APScheduler.
"""

from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from app.database import engine
from app.models.task import Task
import logging

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


async def generate_recurring_tasks():
    """
    Background job to generate new instances of recurring tasks.
    Runs daily at midnight to check for tasks that need new instances.
    """
    logger.info("Starting recurring task generation job")

    with Session(engine) as session:
        # Find all tasks with recurring field set
        statement = select(Task).where(Task.recurring.isnot(None))
        recurring_tasks = session.exec(statement).all()

        logger.info(f"Found {len(recurring_tasks)} recurring tasks to process")

        for task in recurring_tasks:
            try:
                should_create = _should_create_new_instance(task)

                if should_create:
                    new_task = _create_task_instance(task, session)
                    logger.info(
                        f"Created new instance of recurring task '{task.title}' "
                        f"(ID: {task.id}) with new ID: {new_task.id}"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing recurring task '{task.title}' (ID: {task.id}): {e}"
                )
                continue

        session.commit()

    logger.info("Completed recurring task generation job")


def _should_create_new_instance(task: Task) -> bool:
    """
    Determine if a new instance of a recurring task should be created.

    Logic:
    - If task is not completed, don't create a new instance
    - If task has no due_date, use created_at as reference
    - Check if enough time has passed based on recurring pattern
    """
    if not task.completed:
        return False

    if not task.due_date:
        # Use created_at as reference if no due_date
        reference_date = task.created_at.date()
    else:
        reference_date = task.due_date

    today = datetime.utcnow().date()

    if task.recurring == "daily":
        # Create new instance if reference date is yesterday or earlier
        return reference_date < today
    elif task.recurring == "weekly":
        # Create new instance if reference date is 7+ days ago
        return (today - reference_date).days >= 7
    elif task.recurring == "monthly":
        # Create new instance if reference date is 30+ days ago
        return (today - reference_date).days >= 30

    return False


def _create_task_instance(original_task: Task, session: Session) -> Task:
    """
    Create a new instance of a recurring task.

    The new task:
    - Has the same title, description, priority, tags, recurring pattern
    - Is marked as not completed
    - Has a new due_date based on the recurring pattern
    - Belongs to the same user
    """
    # Calculate new due date
    if original_task.due_date:
        reference_date = original_task.due_date
    else:
        reference_date = original_task.created_at.date()

    if original_task.recurring == "daily":
        new_due_date = reference_date + timedelta(days=1)
    elif original_task.recurring == "weekly":
        new_due_date = reference_date + timedelta(weeks=1)
    elif original_task.recurring == "monthly":
        # Approximate month as 30 days
        new_due_date = reference_date + timedelta(days=30)
    else:
        new_due_date = None

    # Create new task instance
    new_task = Task(
        user_id=original_task.user_id,
        title=original_task.title,
        description=original_task.description,
        completed=False,
        priority=original_task.priority,
        tags=original_task.tags,
        due_date=new_due_date,
        recurring=original_task.recurring,
    )

    session.add(new_task)
    return new_task


def start_scheduler():
    """
    Start the APScheduler with recurring task generation job.
    Called during application startup.
    """
    scheduler = get_scheduler()

    # Add job to run daily at midnight UTC
    scheduler.add_job(
        generate_recurring_tasks,
        trigger=CronTrigger(hour=0, minute=0),
        id="generate_recurring_tasks",
        name="Generate recurring task instances",
        replace_existing=True,
    )

    # Also run immediately on startup for testing
    scheduler.add_job(
        generate_recurring_tasks,
        id="generate_recurring_tasks_startup",
        name="Generate recurring tasks on startup",
    )

    scheduler.start()
    logger.info("Scheduler started successfully")


def shutdown_scheduler():
    """
    Shutdown the APScheduler gracefully.
    Called during application shutdown.
    """
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")
