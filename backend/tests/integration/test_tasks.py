"""
Integration tests for task endpoints.

Tests the complete task CRUD flow with database and event publishing.
"""

import pytest
from httpx import AsyncClient
from app.main import app
from app.database import engine
from sqlalchemy import text
import asyncio


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers():
    """Mock authentication headers"""
    # In real tests, you would generate a valid JWT token
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture(autouse=True)
async def setup_database():
    """Setup and teardown database for each test"""
    # Setup: Create test data if needed
    yield
    # Teardown: Clean up test data
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM tasks WHERE title LIKE 'Test%'"))


class TestTaskCRUD:
    """Test task CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient, auth_headers: dict):
        """Test task creation"""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "priority": "medium",
                "status": "pending"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_task_validation(self, client: AsyncClient, auth_headers: dict):
        """Test task creation with invalid data"""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "",  # Empty title should fail
                "description": "Test Description"
            },
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_tasks(self, client: AsyncClient, auth_headers: dict):
        """Test task listing"""
        # Create a task first
        await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task 1", "description": "Description 1"},
            headers=auth_headers
        )

        # List tasks
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_task(self, client: AsyncClient, auth_headers: dict):
        """Test getting a specific task"""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "description": "Test Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Get the task
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, client: AsyncClient, auth_headers: dict):
        """Test getting a task that doesn't exist"""
        response = await client.get(
            "/api/v1/tasks/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, auth_headers: dict):
        """Test task update"""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "description": "Original Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "description": "Updated Description",
                "status": "completed"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated Description"
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, auth_headers: dict):
        """Test task deletion"""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task to Delete", "description": "Will be deleted"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestTaskFiltering:
    """Test task filtering and querying"""

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client: AsyncClient, auth_headers: dict):
        """Test filtering tasks by status"""
        # Create tasks with different statuses
        await client.post(
            "/api/v1/tasks",
            json={"title": "Test Pending", "status": "pending"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Test Completed", "status": "completed"},
            headers=auth_headers
        )

        # Filter by pending
        response = await client.get(
            "/api/v1/tasks?status=pending",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "pending" for task in data)

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client: AsyncClient, auth_headers: dict):
        """Test filtering tasks by priority"""
        # Create tasks with different priorities
        await client.post(
            "/api/v1/tasks",
            json={"title": "Test High Priority", "priority": "high"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Test Low Priority", "priority": "low"},
            headers=auth_headers
        )

        # Filter by high priority
        response = await client.get(
            "/api/v1/tasks?priority=high",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data)


class TestTaskAuthentication:
    """Test authentication and authorization"""

    @pytest.mark.asyncio
    async def test_create_task_without_auth(self, client: AsyncClient):
        """Test that creating a task without auth fails"""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "description": "Test Description"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_tasks_without_auth(self, client: AsyncClient):
        """Test that listing tasks without auth fails"""
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 401


class TestTaskEventPublishing:
    """Test event publishing for task operations"""

    @pytest.mark.asyncio
    async def test_task_created_event_published(self, client: AsyncClient, auth_headers: dict):
        """Test that task creation publishes an event"""
        # This would require mocking the Dapr client or using a test event store
        # For now, we just verify the task is created successfully
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Event Task", "description": "Test Description"},
            headers=auth_headers
        )

        assert response.status_code == 201
        # In a real test, you would verify the event was published to Kafka

    @pytest.mark.asyncio
    async def test_task_updated_event_published(self, client: AsyncClient, auth_headers: dict):
        """Test that task update publishes an event"""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "description": "Original"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"description": "Updated"},
            headers=auth_headers
        )

        assert response.status_code == 200
        # In a real test, you would verify the event was published


class TestTaskPerformance:
    """Test task endpoint performance"""

    @pytest.mark.asyncio
    async def test_list_tasks_performance(self, client: AsyncClient, auth_headers: dict):
        """Test that listing tasks is fast"""
        import time

        start_time = time.time()
        response = await client.get("/api/v1/tasks", headers=auth_headers)
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in less than 1 second

    @pytest.mark.asyncio
    async def test_create_task_performance(self, client: AsyncClient, auth_headers: dict):
        """Test that creating a task is fast"""
        import time

        start_time = time.time()
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Performance Test Task", "description": "Test"},
            headers=auth_headers
        )
        duration = time.time() - start_time

        assert response.status_code == 201
        assert duration < 0.5  # Should respond in less than 500ms
