"""
API routes for diagnostic services
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from loguru import logger

from ..models.schemas import (
    PatientCase,
    DiagnosticResult,
    MedicalCondition,
)
from ..services.diagnostic import DiagnosticService
from ..services.embedding import EmbeddingService
from ..services.vector_store import VectorStoreService
from ..utils.audit import AuditLogger
from ..config import get_settings

# Create router
router = APIRouter()

# Global service instances (will be initialized on startup)
diagnostic_service: Optional[DiagnosticService] = None
audit_logger: Optional[AuditLogger] = None


def get_diagnostic_service() -> DiagnosticService:
    """Dependency to get diagnostic service"""
    global diagnostic_service
    if diagnostic_service is None:
        diagnostic_service = DiagnosticService()
        diagnostic_service.initialize()
    return diagnostic_service


def get_audit_logger() -> AuditLogger:
    """Dependency to get audit logger"""
    global audit_logger
    if audit_logger is None:
        audit_logger = AuditLogger()
    return audit_logger


@router.post(
    "/analyze",
    response_model=DiagnosticResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze patient symptoms and generate differential diagnosis",
    description="Main diagnostic endpoint that analyzes patient symptoms and returns ranked differential diagnoses",
)
async def analyze_patient_case(
    patient_case: PatientCase,
    user_id: Optional[str] = None,
    user_role: Optional[str] = "physician",
    service: DiagnosticService = Depends(get_diagnostic_service),
    audit: AuditLogger = Depends(get_audit_logger),
):
    """
    Analyze patient case and generate differential diagnosis

    **Input**: PatientCase with symptoms, demographics, and medical history
    **Output**: DiagnosticResult with ranked differential diagnoses, confidence scores, and recommendations

    **Review Tiers**:
    - Tier 1 (>85% confidence): Automated assessment
    - Tier 2 (60-85%): Primary care physician review
    - Tier 3 (40-60%): Specialist consultation
    - Tier 4 (<40%): Multi-disciplinary team

    **Safety**: Red flag symptoms trigger emergency alerts
    """
    try:
        logger.info(f"Received diagnostic request for case: {patient_case.case_id}")

        # Perform diagnostic analysis
        result = service.analyze_patient_case(patient_case)

        # Log to audit trail
        audit.log_diagnostic_analysis(
            case=patient_case,
            result=result,
            user_id=user_id,
            user_role=user_role,
        )

        return result

    except Exception as e:
        logger.error(f"Diagnostic analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostic analysis failed: {str(e)}"
        )


@router.get(
    "/condition/{condition_id}",
    response_model=MedicalCondition,
    status_code=status.HTTP_200_OK,
    summary="Get medical condition details by ID",
)
async def get_condition(
    condition_id: str,
    service: DiagnosticService = Depends(get_diagnostic_service),
):
    """
    Retrieve detailed information about a specific medical condition

    **Input**: Condition ID
    **Output**: Complete MedicalCondition object with all metadata
    """
    try:
        condition = service.vector_store.get_condition_by_id(condition_id)

        if condition is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Condition not found: {condition_id}"
            )

        return condition

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve condition: {str(e)}"
        )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
)
async def get_system_stats(
    service: DiagnosticService = Depends(get_diagnostic_service),
):
    """
    Get statistics about the vector database and system

    **Output**: Collection statistics, total conditions, etc.
    """
    try:
        stats = service.vector_store.get_collection_stats()
        return {
            "status": "operational",
            "vector_database": stats,
        }

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
async def health_check():
    """
    Simple health check endpoint

    **Output**: Service status
    """
    return {
        "status": "healthy",
        "service": "Medical Symptom Constellation Mapper",
        "version": "0.1.0"
    }
