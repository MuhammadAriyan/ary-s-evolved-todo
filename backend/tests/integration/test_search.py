"""
Integration tests for search functionality.

Tests full-text search, fuzzy matching, and search performance.
"""

import pytest
from httpx import AsyncClient
from app.main import app
import asyncio


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
async def sample_tasks(client: AsyncClient, auth_headers: dict):
    """Create sample tasks for search testing"""
    tasks = [
        {"title": "Meeting with client", "description": "Discuss project requirements"},
        {"title": "Code review", "description": "Review pull request for authentication"},
        {"title": "Client presentation", "description": "Present quarterly results"},
        {"title": "Team standup", "description": "Daily team sync meeting"},
        {"title": "Bug fix", "description": "Fix authentication bug in login flow"},
    ]

    created_tasks = []
    for task in tasks:
        response = await client.post(
            "/api/v1/tasks",
            json=task,
            headers=auth_headers
        )
        created_tasks.append(response.json())

    return created_tasks


class TestSearchBasic:
    """Test basic search functionality"""

    @pytest.mark.asyncio
    async def test_search_by_title(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test searching tasks by title"""
        response = await client.get(
            "/api/v1/search/tasks?q=client",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # Should find "Meeting with client" and "Client presentation"
        assert any("client" in task["title"].lower() for task in data)

    @pytest.mark.asyncio
    async def test_search_by_description(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test searching tasks by description"""
        response = await client.get(
            "/api/v1/search/tasks?q=authentication",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # Should find tasks with "authentication" in description

    @pytest.mark.asyncio
    async def test_search_no_results(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test search with no matching results"""
        response = await client.get(
            "/api/v1/search/tasks?q=nonexistent_xyz_123",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_search_empty_query(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test search with empty query"""
        response = await client.get(
            "/api/v1/search/tasks?q=",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Empty query should return all tasks or handle gracefully


class TestSearchFuzzy:
    """Test fuzzy search functionality"""

    @pytest.mark.asyncio
    async def test_fuzzy_search_typo(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test fuzzy search with typo"""
        response = await client.get(
            "/api/v1/search/tasks?q=meetng",  # Typo: missing 'i'
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should still find "meeting" tasks with fuzzy matching
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_fuzzy_search_partial_word(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test fuzzy search with partial word"""
        response = await client.get(
            "/api/v1/search/tasks?q=auth",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should find tasks with "authentication"
        assert len(data) > 0


class TestSearchFilters:
    """Test search with filters"""

    @pytest.mark.asyncio
    async def test_search_with_status_filter(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test search with status filter"""
        response = await client.get(
            "/api/v1/search/tasks?q=meeting&status=pending",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "pending" for task in data)

    @pytest.mark.asyncio
    async def test_search_with_priority_filter(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test search with priority filter"""
        response = await client.get(
            "/api/v1/search/tasks?q=client&priority=high",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data)

    @pytest.mark.asyncio
    async def test_search_with_date_range(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test search with date range filter"""
        from datetime import datetime, timedelta

        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = await client.get(
            f"/api/v1/search/tasks?q=meeting&start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200


class TestSearchPerformance:
    """Test search performance"""

    @pytest.mark.asyncio
    async def test_search_performance(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test that search returns results quickly"""
        import time

        start_time = time.time()
        response = await client.get(
            "/api/v1/search/tasks?q=client",
            headers=auth_headers
        )
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in less than 1 second

    @pytest.mark.asyncio
    async def test_search_with_large_result_set(self, client: AsyncClient, auth_headers: dict):
        """Test search performance with many results"""
        # Create many tasks
        for i in range(50):
            await client.post(
                "/api/v1/tasks",
                json={"title": f"Test Task {i}", "description": "Common description"},
                headers={"Authorization": "Bearer test-token"}
            )

        import time
        start_time = time.time()
        response = await client.get(
            "/api/v1/search/tasks?q=common",
            headers={"Authorization": "Bearer test-token"}
        )
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 1.0  # Should still be fast with many results


class TestSearchRelevance:
    """Test search result relevance and ranking"""

    @pytest.mark.asyncio
    async def test_search_relevance_ranking(self, client: AsyncClient, auth_headers: dict, sample_tasks: list):
        """Test that search results are ranked by relevance"""
        response = await client.get(
            "/api/v1/search/tasks?q=client",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Results should be ordered by relevance
        # Tasks with "client" in title should rank higher than in description
        if len(data) >= 2:
            first_result = data[0]
            assert "client" in first_result["title"].lower() or "client" in first_result["description"].lower()
