"""Health check endpoint for monitoring service status."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
from datetime import datetime

from sqlmodel import Session, select
from app.database import engine
from app.services.dapr_state import get_dapr_state_store
from dapr.clients import DaprClient

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""
    status: str
    timestamp: str
    checks: Dict[str, Any]


class ComponentHealth(BaseModel):
    """Individual component health status."""
    status: str
    message: str
    latency_ms: float


async def check_database() -> ComponentHealth:
    """Check PostgreSQL database connectivity."""
    start_time = datetime.utcnow()
    try:
        with Session(engine) as session:
            # Simple query to verify connection
            session.exec(select(1))

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        return ComponentHealth(
            status="healthy",
            message="Database connection successful",
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Database health check failed: {str(e)}")
        return ComponentHealth(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            latency_ms=round(latency, 2)
        )


async def check_redis() -> ComponentHealth:
    """Check Redis state store connectivity via Dapr."""
    start_time = datetime.utcnow()
    try:
        state_store = get_dapr_state_store()
        test_key = "health_check_test"
        test_value = {"timestamp": datetime.utcnow().isoformat()}

        # Test write and read
        await state_store.set(test_key, test_value, ttl_seconds=10)
        result = await state_store.get(test_key)

        if result:
            await state_store.delete(test_key)
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            return ComponentHealth(
                status="healthy",
                message="Redis state store operational",
                latency_ms=round(latency, 2)
            )
        else:
            raise Exception("Failed to read test value")

    except Exception as e:
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Redis health check failed: {str(e)}")
        return ComponentHealth(
            status="unhealthy",
            message=f"Redis state store failed: {str(e)}",
            latency_ms=round(latency, 2)
        )


async def check_dapr() -> ComponentHealth:
    """Check Dapr sidecar connectivity."""
    start_time = datetime.utcnow()
    try:
        with DaprClient() as client:
            # Check if Dapr sidecar is responding
            metadata = client.get_metadata()
            # Access app_id from metadata (Dapr SDK uses app_id, not id)
            app_id = getattr(metadata, 'app_id', 'unknown')

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        return ComponentHealth(
            status="healthy",
            message=f"Dapr sidecar operational (app_id: {app_id})",
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Dapr health check failed: {str(e)}")
        return ComponentHealth(
            status="unhealthy",
            message=f"Dapr sidecar failed: {str(e)}",
            latency_ms=round(latency, 2)
        )


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        HealthStatus with status of all dependencies
    """
    # Run all health checks
    db_health = await check_database()
    redis_health = await check_redis()
    dapr_health = await check_dapr()

    # Determine overall status
    all_healthy = all([
        db_health.status == "healthy",
        redis_health.status == "healthy",
        dapr_health.status == "healthy"
    ])

    overall_status = "healthy" if all_healthy else "degraded"

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        checks={
            "database": db_health.dict(),
            "redis": redis_health.dict(),
            "dapr": dapr_health.dict()
        }
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.

    Returns:
        Simple OK response if service is alive
    """
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.

    Returns:
        OK if service is ready to accept traffic

    Raises:
        HTTPException: If service is not ready
    """
    # Check critical dependencies
    db_health = await check_database()

    if db_health.status != "healthy":
        raise HTTPException(
            status_code=503,
            detail="Service not ready: database unavailable"
        )

    return {"status": "ready"}
