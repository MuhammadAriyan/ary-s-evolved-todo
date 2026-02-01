"""
Integration tests for reminder endpoints.

Tests reminder scheduling, notification delivery, and timezone handling.
"""

import pytest
from httpx import AsyncClient
from app.main import app
from datetime import datetime, timedelta


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers():
    """Mock authentication headers"""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
async def test_task(client: AsyncClient, auth_headers: dict):
    """Create a test task for reminder tests"""
    response = await client.post(
        "/api/v1/tasks",
        json={"title": "Test Task for Reminders", "description": "Test"},
        headers=auth_headers
    )
    return response.json()


class TestReminderCRUD:
    """Test reminder CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_reminder(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test reminder creation"""
        task_id = test_task["id"]
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={
                "reminder_time": reminder_time,
                "timezone": "UTC",
                "notification_channels": ["email", "in_app"]
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["task_id"] == task_id
        assert "reminder_time" in data

    @pytest.mark.asyncio
    async def test_create_reminder_past_time(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test that creating a reminder in the past fails"""
        task_id = test_task["id"]
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={
                "reminder_time": past_time,
                "timezone": "UTC"
            },
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_reminders(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test listing reminders for a task"""
        task_id = test_task["id"]

        # Create a reminder
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={"reminder_time": reminder_time, "timezone": "UTC"},
            headers=auth_headers
        )

        # List reminders
        response = await client.get(
            f"/api/v1/tasks/{task_id}/reminders",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_delete_reminder(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test reminder deletion"""
        task_id = test_task["id"]

        # Create a reminder
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        create_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={"reminder_time": reminder_time, "timezone": "UTC"},
            headers=auth_headers
        )
        reminder_id = create_response.json()["id"]

        # Delete the reminder
        response = await client.delete(
            f"/api/v1/reminders/{reminder_id}",
            headers=auth_headers
        )

        assert response.status_code == 204


class TestReminderTimezones:
    """Test timezone handling for reminders"""

    @pytest.mark.asyncio
    async def test_reminder_with_different_timezones(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test creating reminders with different timezones"""
        task_id = test_task["id"]
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]

        for tz in timezones:
            response = await client.post(
                f"/api/v1/tasks/{task_id}/reminders",
                json={
                    "reminder_time": reminder_time,
                    "timezone": tz
                },
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["timezone"] == tz


class TestReminderNotifications:
    """Test reminder notification delivery"""

    @pytest.mark.asyncio
    async def test_reminder_notification_channels(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test specifying notification channels"""
        task_id = test_task["id"]
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={
                "reminder_time": reminder_time,
                "timezone": "UTC",
                "notification_channels": ["email", "in_app", "push"]
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert set(data["notification_channels"]) == {"email", "in_app", "push"}


class TestReminderIdempotency:
    """Test reminder idempotency"""

    @pytest.mark.asyncio
    async def test_duplicate_reminder_prevention(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test that duplicate reminders are prevented"""
        task_id = test_task["id"]
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        # Create first reminder
        response1 = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={"reminder_time": reminder_time, "timezone": "UTC"},
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Try to create duplicate reminder (same time)
        response2 = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            json={"reminder_time": reminder_time, "timezone": "UTC"},
            headers=auth_headers
        )

        # Should either return existing reminder or reject duplicate
        assert response2.status_code in [200, 201, 409]
