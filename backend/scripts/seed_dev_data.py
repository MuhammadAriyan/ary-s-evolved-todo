"""
Database Seed Script for Phase V Development Data

This script populates the database with sample data for local development and testing.

Usage:
    python backend/scripts/seed_dev_data.py

Requirements:
    - Database must be running and migrations applied
    - Environment variables must be set (DATABASE_URL)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, select
from app.config import settings
from app.models.task import Task
from app.models.user import User


def create_sample_users(session: Session) -> list[User]:
    """Create sample users for development"""
    print("Creating sample users...")

    # Note: In production, users are managed by Better Auth
    # For development, we'll create mock users directly
    users = [
        User(
            id="user-1",
            email="alice@example.com",
            name="Alice Johnson",
            created_at=datetime.utcnow()
        ),
        User(
            id="user-2",
            email="bob@example.com",
            name="Bob Smith",
            created_at=datetime.utcnow()
        ),
        User(
            id="user-3",
            email="charlie@example.com",
            name="Charlie Brown",
            created_at=datetime.utcnow()
        ),
    ]

    for user in users:
        # Check if user already exists
        existing = session.exec(select(User).where(User.id == user.id)).first()
        if not existing:
            session.add(user)
            print(f"  ✓ Created user: {user.name} ({user.email})")
        else:
            print(f"  - User already exists: {user.name}")

    session.commit()
    return users


def create_sample_tasks(session: Session, users: list[User]) -> list[Task]:
    """Create sample tasks for development"""
    print("\nCreating sample tasks...")

    tasks = []

    # Tasks for Alice (user-1)
    alice_tasks = [
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-1",
            title="Complete project proposal",
            description="Write and submit the Q1 project proposal for the new feature",
            status="in_progress",
            priority="high",
            tags=["work", "urgent", "proposal"],
            due_date=datetime.utcnow() + timedelta(days=3),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-1",
            title="Review pull requests",
            description="Review and approve pending PRs from the team",
            status="pending",
            priority="medium",
            tags=["work", "code-review"],
            due_date=datetime.utcnow() + timedelta(days=1),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-1",
            title="Buy groceries",
            description="Milk, eggs, bread, vegetables",
            status="pending",
            priority="low",
            tags=["personal", "shopping"],
            due_date=datetime.utcnow() + timedelta(days=2),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-1",
            title="Schedule team meeting",
            description="Set up weekly sync meeting with the development team",
            status="completed",
            priority="medium",
            tags=["work", "meeting"],
            completed_at=datetime.utcnow() - timedelta(days=1),
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
    ]

    # Tasks for Bob (user-2)
    bob_tasks = [
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-2",
            title="Fix authentication bug",
            description="Investigate and fix the JWT token expiration issue",
            status="in_progress",
            priority="high",
            tags=["work", "bug", "urgent"],
            due_date=datetime.utcnow() + timedelta(hours=12),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-2",
            title="Update documentation",
            description="Update API documentation with new endpoints",
            status="pending",
            priority="medium",
            tags=["work", "documentation"],
            due_date=datetime.utcnow() + timedelta(days=5),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-2",
            title="Gym workout",
            description="Chest and triceps day",
            status="pending",
            priority="low",
            tags=["personal", "health"],
            due_date=datetime.utcnow() + timedelta(hours=6),
            created_at=datetime.utcnow()
        ),
    ]

    # Tasks for Charlie (user-3)
    charlie_tasks = [
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-3",
            title="Design new landing page",
            description="Create mockups for the new product landing page",
            status="in_progress",
            priority="high",
            tags=["work", "design"],
            due_date=datetime.utcnow() + timedelta(days=4),
            created_at=datetime.utcnow()
        ),
        Task(
            id=f"task-{uuid.uuid4()}",
            user_id="user-3",
            title="Client meeting preparation",
            description="Prepare slides and demo for client presentation",
            status="pending",
            priority="high",
            tags=["work", "meeting", "client"],
            due_date=datetime.utcnow() + timedelta(days=2),
            created_at=datetime.utcnow()
        ),
    ]

    all_tasks = alice_tasks + bob_tasks + charlie_tasks

    for task in all_tasks:
        session.add(task)
        print(f"  ✓ Created task: {task.title} (user: {task.user_id})")

    session.commit()
    return all_tasks


def create_sample_reminders(session: Session, tasks: list[Task]) -> None:
    """Create sample scheduled reminders"""
    print("\nCreating sample reminders...")

    # Note: This requires the ScheduledReminder model to be imported
    # For now, we'll skip this as the model might not be created yet
    print("  - Skipping reminders (model not yet implemented)")


def create_sample_audit_logs(session: Session, tasks: list[Task]) -> None:
    """Create sample audit logs"""
    print("\nCreating sample audit logs...")

    # Note: This requires the AuditLog model to be imported
    # For now, we'll skip this as the model might not be created yet
    print("  - Skipping audit logs (model not yet implemented)")


def main():
    """Main seed function"""
    print("=" * 60)
    print("Phase V Development Database Seeding")
    print("=" * 60)

    # Create database engine
    engine = create_engine(str(settings.DATABASE_URL), echo=False)

    try:
        with Session(engine) as session:
            # Create sample data
            users = create_sample_users(session)
            tasks = create_sample_tasks(session, users)
            create_sample_reminders(session, tasks)
            create_sample_audit_logs(session, tasks)

            print("\n" + "=" * 60)
            print("✓ Database seeding completed successfully!")
            print("=" * 60)
            print(f"\nCreated:")
            print(f"  - {len(users)} users")
            print(f"  - {len(tasks)} tasks")
            print(f"\nYou can now start the development servers.")

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
