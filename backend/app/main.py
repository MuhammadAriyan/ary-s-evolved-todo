"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router as api_v1_router
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.services.ai.config import initialize_ai_client, is_ai_configured
from app.services.event_publisher import get_event_publisher
from app.services.dapr_state import get_dapr_state_store
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

    # Initialize Dapr components (Phase V)
    try:
        # Initialize EventPublisher (Dapr Pub/Sub)
        event_publisher = get_event_publisher()
        logger.info("Dapr EventPublisher initialized successfully")

        # Initialize DaprStateStore (Redis)
        state_store = get_dapr_state_store()
        logger.info("Dapr StateStore initialized successfully")

        logger.info("Phase V: Event-driven microservices components initialized")
    except Exception as e:
        logger.warning(f"Dapr components initialization failed: {e}")
        logger.warning("Application will continue without event-driven features")

    yield
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()


app = FastAPI(
    title="Evolved Todo API",
    description="""
    ## Event-Driven Task Management API

    A production-ready, event-driven task management system with real-time synchronization,
    intelligent reminders, and comprehensive audit trails.

    ### Features

    * **Real-Time Sync**: WebSocket-based real-time task synchronization across devices
    * **Smart Reminders**: Precise time-based notifications with timezone support
    * **Recurring Tasks**: Advanced cron-based recurring task patterns
    * **Full-Text Search**: PostgreSQL-powered search with fuzzy matching
    * **Audit Trail**: Complete change history for all task operations
    * **Event-Driven**: Kafka-based event streaming for microservices
    * **Cloud-Native**: Deployed on Oracle OKE with Dapr runtime

    ### Authentication

    All endpoints (except health checks) require JWT authentication via Better Auth.
    Include the JWT token in the `Authorization` header:

    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ### Rate Limiting

    API requests are rate-limited per user:
    - Default: 100 requests per minute
    - Search: 30 requests per minute
    - Auth: 10 requests per minute

    Rate limit headers are included in responses:
    - `X-RateLimit-Limit`: Maximum requests per window
    - `X-RateLimit-Remaining`: Remaining requests
    - `X-RateLimit-Reset`: Seconds until reset

    ### Distributed Tracing

    All requests include correlation IDs for distributed tracing:
    - Request header: `X-Correlation-ID`
    - Response header: `X-Correlation-ID`

    ### Support

    For issues and questions, visit our [GitHub repository](https://github.com/your-org/evolved-todo).
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Evolved Todo Team",
        "url": "https://github.com/your-org/evolved-todo",
        "email": "support@evolved-todo.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Task CRUD operations and management"
        },
        {
            "name": "reminders",
            "description": "Task reminder scheduling and notifications"
        },
        {
            "name": "search",
            "description": "Full-text search with fuzzy matching"
        },
        {
            "name": "audit",
            "description": "Audit trail and change history"
        },
        {
            "name": "health",
            "description": "Health checks and service status"
        },
        {
            "name": "metrics",
            "description": "Prometheus metrics and monitoring"
        }
    ]
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

# Include Phase V API routers
from app.api.health import router as health_router
from app.api.metrics import router as metrics_router

app.include_router(health_router, tags=["health"])
app.include_router(metrics_router, tags=["metrics"])

@app.get("/health/basic")
async def basic_health_check():
    """
    Basic liveness check endpoint.
    Returns immediately without checking dependencies.
    Target response time: <10ms
    """
    return {"status": "healthy"}

@app.get("/health/legacy")
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
