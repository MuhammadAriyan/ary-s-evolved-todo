"""
Search Indexer Microservice
Subscribes to search-index-updates topic and updates search vectors
"""

from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
import asyncpg
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Indexer Service")
dapr_app = DaprApp(app)

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/todo_db")

@dapr_app.subscribe(pubsub="pubsub", topic="search-index-updates")
async def update_search_index(event_data: dict):
    """Update search vectors when tasks are modified"""
    task_id = event_data.get("task_id")
    event_type = event_data.get("event_type")

    logger.info(f"Received search index update for task {task_id}, event: {event_type}")

    try:
        conn = await asyncpg.connect(DB_URL)
        try:
            # Update search vector using PostgreSQL trigger
            # The trigger automatically updates search_vector on task update
            await conn.execute("""
                UPDATE tasks
                SET updated_at = NOW()
                WHERE id = $1
            """, task_id)

            logger.info(f"Successfully updated search index for task {task_id}")
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Failed to update search index for task {task_id}: {e}")
        raise

    return {"status": "indexed", "task_id": task_id}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "search-indexer"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "search-indexer",
        "version": "1.0.0",
        "description": "Search indexing microservice for task search optimization"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
