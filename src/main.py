"""
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from .config import get_settings
from .api.routes import router

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG",
)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
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

# Configure CORS with secure defaults
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API routes
app.include_router(
    router,
    prefix=settings.api_prefix,
    tags=["diagnostic"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_prefix}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


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
