"""
WebSocket performance benchmark using websockets library.

Tests concurrent WebSocket connections and message throughput.
"""

import asyncio
import websockets
import time
import json
from typing import List
import statistics


async def connect_websocket(url: str, token: str, duration: int = 10) -> dict:
    """
    Connect to WebSocket and measure performance.

    Args:
        url: WebSocket URL
        token: Authentication token
        duration: Test duration in seconds

    Returns:
        Performance metrics
    """
    messages_received = 0
    latencies = []

    try:
        async with websockets.connect(
            url,
            extra_headers={"Authorization": f"Bearer {token}"}
        ) as websocket:
            start_time = time.time()

            while time.time() - start_time < duration:
                try:
                    # Send ping
                    ping_time = time.time()
                    await websocket.send(json.dumps({"type": "ping"}))

                    # Wait for response
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5.0
                    )

                    # Calculate latency
                    latency = (time.time() - ping_time) * 1000  # Convert to ms
                    latencies.append(latency)
                    messages_received += 1

                    await asyncio.sleep(0.1)  # Small delay between messages

                except asyncio.TimeoutError:
                    print("WebSocket timeout")
                    break

            return {
                "success": True,
                "messages_received": messages_received,
                "avg_latency": statistics.mean(latencies) if latencies else 0,
                "min_latency": min(latencies) if latencies else 0,
                "max_latency": max(latencies) if latencies else 0,
                "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "messages_received": messages_received
        }


async def benchmark_concurrent_connections(
    url: str,
    token: str,
    num_connections: int = 100,
    duration: int = 10
) -> dict:
    """
    Benchmark concurrent WebSocket connections.

    Args:
        url: WebSocket URL
        token: Authentication token
        num_connections: Number of concurrent connections
        duration: Test duration in seconds

    Returns:
        Aggregated performance metrics
    """
    print(f"\nStarting WebSocket benchmark:")
    print(f"  Connections: {num_connections}")
    print(f"  Duration: {duration}s")
    print(f"  Target: Support 100+ concurrent connections")
    print()

    # Create concurrent connections
    tasks = [
        connect_websocket(url, token, duration)
        for _ in range(num_connections)
    ]

    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    # Aggregate results
    successful = sum(1 for r in results if r.get("success"))
    total_messages = sum(r.get("messages_received", 0) for r in results)

    all_latencies = []
    for r in results:
        if r.get("success") and r.get("avg_latency"):
            all_latencies.append(r["avg_latency"])

    return {
        "total_connections": num_connections,
        "successful_connections": successful,
        "failed_connections": num_connections - successful,
        "total_messages": total_messages,
        "total_time": total_time,
        "messages_per_second": total_messages / total_time if total_time > 0 else 0,
        "avg_latency": statistics.mean(all_latencies) if all_latencies else 0,
        "min_latency": min(all_latencies) if all_latencies else 0,
        "max_latency": max(all_latencies) if all_latencies else 0,
    }


async def main():
    """Run WebSocket benchmarks"""
    # Configuration
    WS_URL = "ws://localhost:8000/ws"
    TOKEN = "test-token"  # Replace with valid token

    # Test scenarios
    scenarios = [
        {"connections": 10, "duration": 10},
        {"connections": 50, "duration": 10},
        {"connections": 100, "duration": 10},
        {"connections": 200, "duration": 10},
    ]

    print("=" * 60)
    print("WebSocket Performance Benchmark")
    print("=" * 60)

    for scenario in scenarios:
        results = await benchmark_concurrent_connections(
            WS_URL,
            TOKEN,
            num_connections=scenario["connections"],
            duration=scenario["duration"]
        )

        print(f"\nScenario: {scenario['connections']} concurrent connections")
        print("-" * 60)
        print(f"Successful connections: {results['successful_connections']}/{results['total_connections']}")
        print(f"Failed connections: {results['failed_connections']}")
        print(f"Total messages: {results['total_messages']}")
        print(f"Messages per second: {results['messages_per_second']:.2f}")
        print(f"Average latency: {results['avg_latency']:.2f}ms")
        print(f"Min latency: {results['min_latency']:.2f}ms")
        print(f"Max latency: {results['max_latency']:.2f}ms")

        # Check if target met
        if results['successful_connections'] >= scenario['connections'] * 0.95:
            print("✓ Target met: 95%+ connections successful")
        else:
            print("✗ Target not met: <95% connections successful")

        print()

        # Wait between scenarios
        await asyncio.sleep(2)

    print("=" * 60)
    print("WebSocket benchmark complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
