"""API v1 router setup."""
from fastapi import APIRouter
from app.api.v1.endpoints import tasks

router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
