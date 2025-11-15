"""
Minimal FastAPI server to view the API documentation UI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create FastAPI app
app = FastAPI(
    title="Medical Symptom Constellation Mapper",
    version="0.2.0",
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

    ---

    **Note**: This is a minimal server for UI preview. Full ML functionality requires
    additional dependencies (PyTorch, transformers, etc.) to be installed via:
    ```
    pip install -r requirements.txt
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Medical Symptom Constellation Mapper",
        "version": "0.2.0",
        "status": "operational (minimal mode)",
        "docs": "/docs",
        "note": "This is a minimal server. Full functionality requires ML dependencies.",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "minimal",
        "ml_dependencies": "not installed",
    }


@app.get("/api/v1/stats")
async def stats():
    """System statistics endpoint (minimal mode)"""
    return {
        "mode": "minimal",
        "message": "Full statistics require ML dependencies to be installed",
        "install_command": "pip install -r requirements.txt",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Medical Symptom Constellation Mapper (Minimal Mode)")
    logger.info("Full functionality requires: pip install -r requirements.txt")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
