"""
Performance benchmarks for search, WebSocket, and event processing.

Uses locust for load testing and performance benchmarking.
"""

from locust import HttpUser, task, between, events
import time
import json
from typing import Optional


class SearchBenchmark(HttpUser):
    """
    Performance benchmark for search endpoints.

    Target: <1 second response time for search queries
    """

    wait_time = between(1, 2)
    host = "http://localhost:8000"

    def on_start(self):
        """Setup: Login and get auth token"""
        # In real tests, you would authenticate and get a token
        self.token = "test-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(3)
    def search_simple_query(self):
        """Benchmark simple search query"""
        start_time = time.time()

        with self.client.get(
            "/api/v1/search/tasks?q=meeting",
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 1.0:
                    response.success()
                else:
                    response.failure(f"Search took {duration:.2f}s (expected <1s)")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def search_with_filters(self):
        """Benchmark search with filters"""
        start_time = time.time()

        with self.client.get(
            "/api/v1/search/tasks?q=client&status=pending&priority=high",
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 1.0:
                    response.success()
                else:
                    response.failure(f"Filtered search took {duration:.2f}s (expected <1s)")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def search_fuzzy_query(self):
        """Benchmark fuzzy search"""
        start_time = time.time()

        with self.client.get(
            "/api/v1/search/tasks?q=meetng",  # Typo for fuzzy matching
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 1.5:  # Fuzzy search may be slightly slower
                    response.success()
                else:
                    response.failure(f"Fuzzy search took {duration:.2f}s (expected <1.5s)")
            else:
                response.failure(f"Got status code {response.status_code}")


class TaskCRUDBenchmark(HttpUser):
    """
    Performance benchmark for task CRUD operations.

    Target: <500ms for create/update, <200ms for read
    """

    wait_time = between(0.5, 1.5)
    host = "http://localhost:8000"

    def on_start(self):
        """Setup: Login and get auth token"""
        self.token = "test-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.task_ids = []

    @task(5)
    def create_task(self):
        """Benchmark task creation"""
        start_time = time.time()

        with self.client.post(
            "/api/v1/tasks",
            json={
                "title": f"Benchmark Task {time.time()}",
                "description": "Performance test task",
                "priority": "medium"
            },
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 201:
                if duration < 0.5:
                    response.success()
                    # Store task ID for later operations
                    data = response.json()
                    self.task_ids.append(data["id"])
                else:
                    response.failure(f"Task creation took {duration:.2f}s (expected <500ms)")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(10)
    def list_tasks(self):
        """Benchmark task listing"""
        start_time = time.time()

        with self.client.get(
            "/api/v1/tasks",
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 0.2:
                    response.success()
                else:
                    response.failure(f"Task listing took {duration:.2f}s (expected <200ms)")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(3)
    def update_task(self):
        """Benchmark task update"""
        if not self.task_ids:
            return

        task_id = self.task_ids[-1]
        start_time = time.time()

        with self.client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"description": f"Updated at {time.time()}"},
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 0.5:
                    response.success()
                else:
                    response.failure(f"Task update took {duration:.2f}s (expected <500ms)")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(8)
    def get_task(self):
        """Benchmark getting a single task"""
        if not self.task_ids:
            return

        task_id = self.task_ids[-1]
        start_time = time.time()

        with self.client.get(
            f"/api/v1/tasks/{task_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                if duration < 0.2:
                    response.success()
                else:
                    response.failure(f"Task get took {duration:.2f}s (expected <200ms)")
            else:
                response.failure(f"Got status code {response.status_code}")


class WebSocketBenchmark(HttpUser):
    """
    Performance benchmark for WebSocket connections.

    Target: Support 100+ concurrent connections
    """

    wait_time = between(2, 5)
    host = "http://localhost:8000"

    def on_start(self):
        """Setup: Establish WebSocket connection"""
        self.token = "test-token"
        # Note: Locust doesn't natively support WebSocket
        # For real WebSocket testing, use a specialized tool like Artillery or custom script

    @task
    def simulate_websocket_message(self):
        """Simulate WebSocket message handling"""
        # This is a placeholder - real WebSocket testing requires different tools
        pass


class EventProcessingBenchmark(HttpUser):
    """
    Performance benchmark for event processing.

    Target: Process events within 100ms
    """

    wait_time = between(0.5, 1)
    host = "http://localhost:8000"

    def on_start(self):
        """Setup: Login and get auth token"""
        self.token = "test-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task
    def trigger_event_processing(self):
        """Trigger event that requires processing"""
        start_time = time.time()

        # Create a task (which publishes an event)
        with self.client.post(
            "/api/v1/tasks",
            json={
                "title": f"Event Test {time.time()}",
                "description": "Test event processing"
            },
            headers=self.headers,
            catch_response=True
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 201:
                # Event should be published quickly
                if duration < 0.1:
                    response.success()
                else:
                    response.failure(f"Event processing took {duration:.2f}s (expected <100ms)")
            else:
                response.failure(f"Got status code {response.status_code}")


# Custom event handlers for detailed metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log detailed request metrics"""
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response_time > 1000:  # Log slow requests (>1s)
        print(f"Slow request: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test"""
    print("Starting performance benchmarks...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary after test"""
    print("\nPerformance Benchmark Summary:")
    print("=" * 60)

    stats = environment.stats

    print(f"\nTotal requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")

    print("\nPercentiles:")
    print(f"  50th: {stats.total.get_response_time_percentile(0.5):.2f}ms")
    print(f"  75th: {stats.total.get_response_time_percentile(0.75):.2f}ms")
    print(f"  90th: {stats.total.get_response_time_percentile(0.90):.2f}ms")
    print(f"  95th: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  99th: {stats.total.get_response_time_percentile(0.99):.2f}ms")

    print("\n" + "=" * 60)

    # Check if performance targets were met
    avg_time = stats.total.avg_response_time
    p95_time = stats.total.get_response_time_percentile(0.95)

    print("\nPerformance Target Assessment:")
    if avg_time < 500:
        print(f"✓ Average response time: {avg_time:.2f}ms (target: <500ms)")
    else:
        print(f"✗ Average response time: {avg_time:.2f}ms (target: <500ms)")

    if p95_time < 1000:
        print(f"✓ 95th percentile: {p95_time:.2f}ms (target: <1000ms)")
    else:
        print(f"✗ 95th percentile: {p95_time:.2f}ms (target: <1000ms)")

    if stats.total.num_failures == 0:
        print("✓ No failures")
    else:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"✗ Failure rate: {failure_rate:.2f}%")
