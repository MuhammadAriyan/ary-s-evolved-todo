"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router as api_v1_router
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.services.ai.config import initialize_ai_client, is_ai_configured
import logging
import time

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    start_scheduler()

    # Initialize AI client if configured
    if is_ai_configured():
        try:
            initialize_ai_client()
            logger.info("AI client initialized successfully")
        except Exception as e:
            logger.warning(f"AI client initialization failed: {e}")
    else:
        logger.info("AI client not configured (AI_API_KEY not set)")

    yield
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()


app = FastAPI(
    title="Todo API",
    description="Full-stack todo application API with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with headers for debugging."""
    start_time = time.time()

    # Log request details
    print(f"\n{'='*60}")
    print(f"📥 Incoming Request: {request.method} {request.url.path}")
    print(f"Headers:")
    for header, value in request.headers.items():
        if header.lower() == "authorization":
            print(f"  🔑 {header}: {value[:50]}..." if len(value) > 50 else f"  🔑 {header}: {value}")
        else:
            print(f"  {header}: {value}")

    response = await call_next(request)

    process_time = time.time() - start_time
    print(f"✅ Response: {response.status_code} (took {process_time:.3f}s)")
    print(f"{'='*60}\n")

    return response

# CORS configuration
# Allow Vercel domains and local development
# In production, set CORS_ORIGINS env var to include your Vercel domain
# Example: CORS_ORIGINS="https://your-app.vercel.app,http://localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,  # Required for cookies and auth headers
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow frontend to read response headers
)

# Include API routers
app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    """
    Basic liveness check endpoint.
    Returns immediately without checking dependencies.
    Target response time: <10ms
    """
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    Verifies database connection and OpenAI API availability.
    Returns detailed status for each dependency.
    """
    from app.database import engine
    from app.services.ai.config import is_ai_configured, get_ai_client
    from sqlalchemy import text

    status = {
        "status": "ready",
        "checks": {
            "database": {"status": "unknown"},
            "openai_api": {"status": "unknown"}
        }
    }

    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        status["status"] = "not_ready"

    # Check OpenAI API availability
    if is_ai_configured():
        try:
            client = get_ai_client()
            # Simple check - just verify client is initialized
            if client:
                status["checks"]["openai_api"] = {"status": "healthy"}
            else:
                status["checks"]["openai_api"] = {
                    "status": "unhealthy",
                    "error": "Client not initialized"
                }
                status["status"] = "not_ready"
        except Exception as e:
            status["checks"]["openai_api"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            status["status"] = "not_ready"
    else:
        status["checks"]["openai_api"] = {
            "status": "not_configured",
            "message": "AI_API_KEY not set"
        }

    return status

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
