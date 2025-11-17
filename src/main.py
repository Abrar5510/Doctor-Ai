"""
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from contextlib import asynccontextmanager

from .config import get_settings
from .api.routes import router
from .api.auth_routes import router as auth_router
from .api.case_history_routes import router as case_history_router
from .api.monitoring_routes import router as monitoring_router
from .api.export_routes import router as export_router
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware

# Get settings first for log level configuration
settings = get_settings()

# Configure logging with environment-dependent log level
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level=settings.log_level,  # Use configured log level, not DEBUG
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_prefix}")

    # Initialize services on startup
    from .dependencies import ServiceContainer
    logger.info("Pre-initializing services...")
    ServiceContainer.get_diagnostic_service()
    ServiceContainer.get_ai_assistant()
    ServiceContainer.get_audit_logger()
    logger.success("All services pre-initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down application")
    ServiceContainer.cleanup()
    logger.success("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Medical Symptom Constellation Mapper

    AI-powered diagnostic support system that maps patient symptoms to potential
    medical conditions using advanced pattern matching and vector similarity search.

    ### Key Features
    - **Vector Similarity Search**: Semantic understanding of symptom relationships
    - **Rare Disease Detection**: Comprehensive orphan disease coverage
    - **Multi-tier Review System**: Confidence-based routing to appropriate care level
    - **Red Flag Detection**: Immediate alerts for life-threatening symptoms
    - **Explainable AI**: Complete transparency in diagnostic reasoning
    - **HIPAA Compliant**: Full audit trail and data anonymization

    ### Review Tiers
    - **Tier 1** (>85% confidence): Automated assessment
    - **Tier 2** (60-85%): Primary care physician review
    - **Tier 3** (40-60%): Specialist consultation
    - **Tier 4** (<40%): Multi-disciplinary team

    ### Important Notice
    This system is a **Clinical Decision Support** tool and does not replace
    physician judgment. All diagnoses require human review and confirmation.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_requests,
    )
    logger.info(
        f"Rate limiting enabled: {settings.rate_limit_requests} requests per minute"
    )

# Configure CORS with proper origin restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)
logger.info(f"CORS origins configured: {settings.get_cors_origins()}")

# Include authentication routes (no auth required)
app.include_router(
    auth_router,
    prefix=settings.api_prefix,
    tags=["authentication"],
)

# Include API routes (diagnostic endpoints)
app.include_router(
    router,
    prefix=settings.api_prefix,
    tags=["diagnostic"],
)

# Include case history routes
app.include_router(
    case_history_router,
    prefix=f"{settings.api_prefix}/history",
    tags=["case-history"],
)

# Include monitoring routes
app.include_router(
    monitoring_router,
    prefix=f"{settings.api_prefix}/monitoring",
    tags=["monitoring"],
)

# Include export routes
app.include_router(
    export_router,
    prefix=f"{settings.api_prefix}/export",
    tags=["export"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
