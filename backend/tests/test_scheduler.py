"""
Tests for recurring task scheduler service.
"""

import pytest
from datetime import datetime, timedelta, date
from sqlmodel import Session, select
from app.models.task import Task
from app.services.scheduler import (
    _should_create_new_instance,
    _create_task_instance,
    generate_recurring_tasks,
)


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test-user-123"


@pytest.fixture
def daily_task(sample_user_id):
    """Create a sample daily recurring task."""
    return Task(
        id=1,
        user_id=sample_user_id,
        title="Daily standup",
        description="Daily team standup meeting",
        completed=True,
        priority="High",
        tags=["work", "meeting"],
        due_date=date.today() - timedelta(days=1),  # Yesterday
        recurring="daily",
        created_at=datetime.utcnow() - timedelta(days=1),
    )


@pytest.fixture
def weekly_task(sample_user_id):
    """Create a sample weekly recurring task."""
    return Task(
        id=2,
        user_id=sample_user_id,
        title="Weekly review",
        description="Review weekly progress",
        completed=True,
        priority="Medium",
        tags=["work", "review"],
        due_date=date.today() - timedelta(days=7),  # Last week
        recurring="weekly",
        created_at=datetime.utcnow() - timedelta(days=7),
    )


@pytest.fixture
def monthly_task(sample_user_id):
    """Create a sample monthly recurring task."""
    return Task(
        id=3,
        user_id=sample_user_id,
        title="Monthly report",
        description="Submit monthly report",
        completed=True,
        priority="High",
        tags=["work", "report"],
        due_date=date.today() - timedelta(days=30),  # Last month
        recurring="monthly",
        created_at=datetime.utcnow() - timedelta(days=30),
    )


class TestShouldCreateNewInstance:
    """Tests for _should_create_new_instance function."""

    def test_should_create_daily_task_when_completed_yesterday(self, daily_task):
        """Should create new instance for daily task completed yesterday."""
        assert _should_create_new_instance(daily_task) is True

    def test_should_not_create_daily_task_when_not_completed(self, daily_task):
        """Should not create new instance if task is not completed."""
        daily_task.completed = False
        assert _should_create_new_instance(daily_task) is False

    def test_should_not_create_daily_task_when_due_today(self, daily_task):
        """Should not create new instance if due date is today."""
        daily_task.due_date = date.today()
        assert _should_create_new_instance(daily_task) is False

    def test_should_create_weekly_task_after_7_days(self, weekly_task):
        """Should create new instance for weekly task after 7 days."""
        assert _should_create_new_instance(weekly_task) is True

    def test_should_not_create_weekly_task_before_7_days(self, weekly_task):
        """Should not create new instance for weekly task before 7 days."""
        weekly_task.due_date = date.today() - timedelta(days=5)
        assert _should_create_new_instance(weekly_task) is False

    def test_should_create_monthly_task_after_30_days(self, monthly_task):
        """Should create new instance for monthly task after 30 days."""
        assert _should_create_new_instance(monthly_task) is True

    def test_should_not_create_monthly_task_before_30_days(self, monthly_task):
        """Should not create new instance for monthly task before 30 days."""
        monthly_task.due_date = date.today() - timedelta(days=20)
        assert _should_create_new_instance(monthly_task) is False

    def test_should_handle_task_without_due_date(self, daily_task):
        """Should use created_at when task has no due_date."""
        daily_task.due_date = None
        daily_task.created_at = datetime.utcnow() - timedelta(days=2)
        assert _should_create_new_instance(daily_task) is True


class TestCreateTaskInstance:
    """Tests for _create_task_instance function."""

    def test_create_daily_task_instance(self, daily_task, db_session: Session):
        """Should create new daily task instance with correct due date."""
        new_task = _create_task_instance(daily_task, db_session)

        assert new_task.user_id == daily_task.user_id
        assert new_task.title == daily_task.title
        assert new_task.description == daily_task.description
        assert new_task.completed is False
        assert new_task.priority == daily_task.priority
        assert new_task.tags == daily_task.tags
        assert new_task.recurring == daily_task.recurring
        assert new_task.due_date == daily_task.due_date + timedelta(days=1)

    def test_create_weekly_task_instance(self, weekly_task, db_session: Session):
        """Should create new weekly task instance with correct due date."""
        new_task = _create_task_instance(weekly_task, db_session)

        assert new_task.completed is False
        assert new_task.due_date == weekly_task.due_date + timedelta(weeks=1)

    def test_create_monthly_task_instance(self, monthly_task, db_session: Session):
        """Should create new monthly task instance with correct due date."""
        new_task = _create_task_instance(monthly_task, db_session)

        assert new_task.completed is False
        assert new_task.due_date == monthly_task.due_date + timedelta(days=30)

    def test_create_task_instance_without_due_date(
        self, daily_task, db_session: Session
    ):
        """Should handle task without due_date using created_at."""
        daily_task.due_date = None
        new_task = _create_task_instance(daily_task, db_session)

        expected_due_date = daily_task.created_at.date() + timedelta(days=1)
        assert new_task.due_date == expected_due_date

    def test_new_task_instance_is_added_to_session(
        self, daily_task, db_session: Session
    ):
        """Should add new task instance to database session."""
        new_task = _create_task_instance(daily_task, db_session)

        # Verify task is in session
        assert new_task in db_session.new


@pytest.mark.asyncio
class TestGenerateRecurringTasks:
    """Tests for generate_recurring_tasks function."""

    async def test_generate_tasks_for_completed_recurring_tasks(
        self, db_session: Session, sample_user_id
    ):
        """Should generate new instances for all eligible recurring tasks."""
        # Create completed recurring tasks
        task1 = Task(
            user_id=sample_user_id,
            title="Daily task",
            completed=True,
            priority="High",
            tags=["daily"],
            due_date=date.today() - timedelta(days=1),
            recurring="daily",
        )
        task2 = Task(
            user_id=sample_user_id,
            title="Weekly task",
            completed=True,
            priority="Medium",
            tags=["weekly"],
            due_date=date.today() - timedelta(days=7),
            recurring="weekly",
        )

        db_session.add(task1)
        db_session.add(task2)
        db_session.commit()

        # Run the generation job
        await generate_recurring_tasks()

        # Verify new instances were created
        statement = select(Task).where(Task.user_id == sample_user_id)
        all_tasks = db_session.exec(statement).all()

        # Should have 4 tasks total (2 original + 2 new instances)
        assert len(all_tasks) == 4

        # Verify new instances are not completed
        new_tasks = [t for t in all_tasks if not t.completed]
        assert len(new_tasks) == 2

    async def test_skip_incomplete_recurring_tasks(
        self, db_session: Session, sample_user_id
    ):
        """Should not generate new instances for incomplete recurring tasks."""
        # Create incomplete recurring task
        task = Task(
            user_id=sample_user_id,
            title="Daily task",
            completed=False,
            priority="High",
            tags=["daily"],
            due_date=date.today() - timedelta(days=1),
            recurring="daily",
        )

        db_session.add(task)
        db_session.commit()

        # Run the generation job
        await generate_recurring_tasks()

        # Verify no new instances were created
        statement = select(Task).where(Task.user_id == sample_user_id)
        all_tasks = db_session.exec(statement).all()

        # Should still have only 1 task
        assert len(all_tasks) == 1

    async def test_skip_tasks_without_recurring_field(
        self, db_session: Session, sample_user_id
    ):
        """Should not process tasks without recurring field."""
        # Create non-recurring task
        task = Task(
            user_id=sample_user_id,
            title="One-time task",
            completed=True,
            priority="High",
            tags=["once"],
            due_date=date.today() - timedelta(days=1),
            recurring=None,
        )

        db_session.add(task)
        db_session.commit()

        # Run the generation job
        await generate_recurring_tasks()

        # Verify no new instances were created
        statement = select(Task).where(Task.user_id == sample_user_id)
        all_tasks = db_session.exec(statement).all()

        # Should still have only 1 task
        assert len(all_tasks) == 1

    async def test_user_isolation_in_recurring_tasks(
        self, db_session: Session, sample_user_id
    ):
        """Should maintain user isolation when generating recurring tasks."""
        user2_id = "test-user-456"

        # Create recurring tasks for two different users
        task1 = Task(
            user_id=sample_user_id,
            title="User 1 daily task",
            completed=True,
            priority="High",
            tags=["user1"],
            due_date=date.today() - timedelta(days=1),
            recurring="daily",
        )
        task2 = Task(
            user_id=user2_id,
            title="User 2 daily task",
            completed=True,
            priority="High",
            tags=["user2"],
            due_date=date.today() - timedelta(days=1),
            recurring="daily",
        )

        db_session.add(task1)
        db_session.add(task2)
        db_session.commit()

        # Run the generation job
        await generate_recurring_tasks()

        # Verify each user has their own new instance
        statement1 = select(Task).where(Task.user_id == sample_user_id)
        user1_tasks = db_session.exec(statement1).all()
        assert len(user1_tasks) == 2

        statement2 = select(Task).where(Task.user_id == user2_id)
        user2_tasks = db_session.exec(statement2).all()
        assert len(user2_tasks) == 2

        # Verify user isolation
        assert all(t.user_id == sample_user_id for t in user1_tasks)
        assert all(t.user_id == user2_id for t in user2_tasks)
