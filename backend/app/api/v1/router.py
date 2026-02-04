"""API v1 router setup."""
from fastapi import APIRouter
from app.api.v1.endpoints import tasks, chat, reminders, search, audit

router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(reminders.router, tags=["reminders"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(audit.router, prefix="/audit", tags=["audit"])
