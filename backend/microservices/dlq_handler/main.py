"""
Dead Letter Queue Handler Microservice
Handles failed events with exponential backoff retry logic
"""

from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
import logging
import asyncio
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DLQ Handler Service")
dapr_app = DaprApp(app)

MAX_RETRIES = 3
PUBSUB_NAME = "pubsub"

@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic="dead-letter-queue")
async def handle_failed_event(event_data: dict):
    """Handle failed events with exponential backoff retry"""
    event_type = event_data.get("event_type")
    retry_count = event_data.get("retry_count", 0)
    original_topic = event_data.get("original_topic")
    original_payload = event_data.get("original_payload", {})
    error_message = event_data.get("error_message", "Unknown error")

    logger.error(
        f"DLQ: Failed event type={event_type} from topic={original_topic} "
        f"retry={retry_count} error={error_message}"
    )

    if retry_count < MAX_RETRIES:
        # Exponential backoff: 2^retry_count seconds
        backoff_seconds = 2 ** retry_count
        logger.info(f"DLQ: Retrying in {backoff_seconds} seconds (attempt {retry_count + 1}/{MAX_RETRIES})")

        await asyncio.sleep(backoff_seconds)

        # Republish to original topic with incremented retry count
        try:
            with DaprClient() as client:
                # Update retry count in payload
                retry_payload = {
                    **original_payload,
                    "retry_count": retry_count + 1,
                    "retry_timestamp": datetime.utcnow().isoformat(),
                }

                client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=original_topic,
                    data=json.dumps(retry_payload),
                    data_content_type="application/json",
                )

                logger.info(f"DLQ: Successfully republished to {original_topic}")
        except Exception as e:
            logger.error(f"DLQ: Failed to republish event: {e}")
            # If republish fails, it will come back to DLQ
    else:
        # Log to persistent storage for manual intervention
        logger.critical(
            f"DLQ: Event permanently failed after {MAX_RETRIES} retries\n"
            f"Event Type: {event_type}\n"
            f"Original Topic: {original_topic}\n"
            f"Payload: {json.dumps(original_payload, indent=2)}\n"
            f"Error: {error_message}"
        )

        # TODO: Store in database for manual review
        # await store_failed_event_in_db(event_data)

    return {"status": "processed", "retry_count": retry_count}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dlq-handler"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "dlq-handler",
        "version": "1.0.0",
        "description": "Dead Letter Queue handler with exponential backoff retry",
        "max_retries": MAX_RETRIES,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
