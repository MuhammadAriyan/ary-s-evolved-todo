"""
Event processing performance benchmark.

Tests event publishing and consumption latency.
"""

import asyncio
import time
from dapr.clients import DaprClient
import json
import statistics
from typing import List, Dict


async def benchmark_event_publishing(
    topic: str,
    num_events: int = 1000,
    batch_size: int = 10
) -> Dict:
    """
    Benchmark event publishing performance.

    Args:
        topic: Pub/Sub topic name
        num_events: Number of events to publish
        batch_size: Number of events to publish in parallel

    Returns:
        Performance metrics
    """
    print(f"\nBenchmarking event publishing:")
    print(f"  Topic: {topic}")
    print(f"  Events: {num_events}")
    print(f"  Batch size: {batch_size}")
    print(f"  Target: <100ms per event")
    print()

    latencies = []
    errors = 0

    async with DaprClient() as client:
        start_time = time.time()

        for i in range(0, num_events, batch_size):
            batch_start = time.time()

            # Publish batch of events
            tasks = []
            for j in range(min(batch_size, num_events - i)):
                event_data = {
                    "event_id": f"test-{i + j}",
                    "timestamp": time.time(),
                    "data": {"test": "data"}
                }

                task = client.publish_event(
                    pubsub_name="kafka-pubsub",
                    topic_name=topic,
                    data=json.dumps(event_data)
                )
                tasks.append(task)

            try:
                await asyncio.gather(*tasks)
                batch_latency = (time.time() - batch_start) * 1000 / batch_size
                latencies.append(batch_latency)
            except Exception as e:
                errors += batch_size
                print(f"Error publishing batch: {e}")

        total_time = time.time() - start_time

    return {
        "total_events": num_events,
        "successful_events": num_events - errors,
        "failed_events": errors,
        "total_time": total_time,
        "events_per_second": num_events / total_time if total_time > 0 else 0,
        "avg_latency": statistics.mean(latencies) if latencies else 0,
        "min_latency": min(latencies) if latencies else 0,
        "max_latency": max(latencies) if latencies else 0,
        "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0,
        "p99_latency": statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else 0
    }


async def benchmark_event_roundtrip(
    topic: str,
    num_events: int = 100
) -> Dict:
    """
    Benchmark event roundtrip time (publish + consume).

    Args:
        topic: Pub/Sub topic name
        num_events: Number of events to test

    Returns:
        Performance metrics
    """
    print(f"\nBenchmarking event roundtrip:")
    print(f"  Topic: {topic}")
    print(f"  Events: {num_events}")
    print(f"  Target: <200ms roundtrip")
    print()

    # This would require setting up a consumer and measuring end-to-end latency
    # For now, we'll simulate with publishing metrics

    return {
        "note": "Roundtrip testing requires consumer setup",
        "recommendation": "Use distributed tracing (Jaeger/Zipkin) for production monitoring"
    }


async def main():
    """Run event processing benchmarks"""
    print("=" * 60)
    print("Event Processing Performance Benchmark")
    print("=" * 60)

    # Test scenarios
    scenarios = [
        {"topic": "task-events", "num_events": 100, "batch_size": 10},
        {"topic": "task-events", "num_events": 1000, "batch_size": 50},
        {"topic": "task-updates", "num_events": 500, "batch_size": 25},
    ]

    for scenario in scenarios:
        try:
            results = await benchmark_event_publishing(
                topic=scenario["topic"],
                num_events=scenario["num_events"],
                batch_size=scenario["batch_size"]
            )

            print(f"\nResults:")
            print("-" * 60)
            print(f"Total events: {results['total_events']}")
            print(f"Successful: {results['successful_events']}")
            print(f"Failed: {results['failed_events']}")
            print(f"Total time: {results['total_time']:.2f}s")
            print(f"Events per second: {results['events_per_second']:.2f}")
            print(f"Average latency: {results['avg_latency']:.2f}ms")
            print(f"Min latency: {results['min_latency']:.2f}ms")
            print(f"Max latency: {results['max_latency']:.2f}ms")
            print(f"95th percentile: {results['p95_latency']:.2f}ms")
            print(f"99th percentile: {results['p99_latency']:.2f}ms")

            # Check if target met
            if results['avg_latency'] < 100:
                print("✓ Target met: Average latency <100ms")
            else:
                print("✗ Target not met: Average latency >=100ms")

            print()

        except Exception as e:
            print(f"Error in scenario: {e}")
            print("Note: Dapr must be running for event benchmarks")

        await asyncio.sleep(1)

    print("=" * 60)
    print("Event processing benchmark complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
