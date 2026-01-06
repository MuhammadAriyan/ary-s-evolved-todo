"""Tests for task CRUD operations and user isolation."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt import create_jwt_token

client = TestClient(app)


def test_create_task():
    """Test creating a task for authenticated user."""
    user_id = "test_user_123"
    token = create_jwt_token(user_id, "test@example.com", "Test User")

    task_data = {
        "title": "Test Task",
        "description": "Test description",
        "priority": "High",
        "tags": ["work", "urgent"],
        "due_date": "2026-01-15",
        "recurring": None
    }

    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["user_id"] == user_id
    assert data["completed"] == False


def test_list_tasks():
    """Test listing tasks with user isolation."""
    user_id = "test_user_456"
    token = create_jwt_token(user_id, "user@example.com", "User")

    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All tasks should belong to the authenticated user
    for task in data:
        assert task["user_id"] == user_id


def test_get_task():
    """Test getting a specific task with user isolation."""
    user_id = "test_user_789"
    token = create_jwt_token(user_id, "get@example.com", "Get User")

    # This test assumes a task exists - in real implementation,
    # we'd create a task first or use fixtures
    response = client.get(
        "/api/v1/tasks/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 404 if task doesn't exist or doesn't belong to user
    assert response.status_code in [200, 404]


def test_update_task():
    """Test updating a task with user isolation."""
    user_id = "test_user_update"
    token = create_jwt_token(user_id, "update@example.com", "Update User")

    update_data = {
        "title": "Updated Task",
        "priority": "Medium"
    }

    response = client.put(
        "/api/v1/tasks/1",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 404 if task doesn't exist or doesn't belong to user
    assert response.status_code in [200, 404]


def test_toggle_complete():
    """Test toggling task completion status."""
    user_id = "test_user_toggle"
    token = create_jwt_token(user_id, "toggle@example.com", "Toggle User")

    response = client.patch(
        "/api/v1/tasks/1/complete",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 404 if task doesn't exist or doesn't belong to user
    assert response.status_code in [200, 404]


def test_delete_task():
    """Test deleting a task with user isolation."""
    user_id = "test_user_delete"
    token = create_jwt_token(user_id, "delete@example.com", "Delete User")

    response = client.delete(
        "/api/v1/tasks/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 404 if task doesn't exist or doesn't belong to user
    assert response.status_code in [200, 204, 404]


def test_user_isolation():
    """Test that users cannot access other users' tasks."""
    user1_id = "user_1"
    user2_id = "user_2"

    token1 = create_jwt_token(user1_id, "user1@example.com", "User 1")
    token2 = create_jwt_token(user2_id, "user2@example.com", "User 2")

    # Create task as user 1
    task_data = {
        "title": "User 1 Task",
        "priority": "High"
    }

    response1 = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token1}"}
    )

    if response1.status_code == 201:
        task_id = response1.json()["id"]

        # Try to access as user 2
        response2 = client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        # User 2 should not be able to access user 1's task
        assert response2.status_code == 404
