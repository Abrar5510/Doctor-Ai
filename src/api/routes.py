"""
Enhanced API routes with AI reasoning assistant
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from loguru import logger

from ..models.schemas import (
    PatientCase,
    DiagnosticResult,
    MedicalCondition,
)
from ..models.database import User
from ..services.diagnostic import DiagnosticService
from ..services.ai_assistant import AIReasoningAssistant, ReportType
from ..services.auth import get_current_user
from ..utils.audit import AuditLogger
from ..utils.sanitization import input_validator, sanitize_for_llm
from ..dependencies import (
    get_diagnostic_service,
    get_ai_assistant,
    get_audit_logger,
)

# Create router
router = APIRouter()


@router.post(
    "/analyze",
    response_model=DiagnosticResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze patient symptoms and generate differential diagnosis",
    description="Main diagnostic endpoint that analyzes patient symptoms and returns ranked differential diagnoses",
)
async def analyze_patient_case(
    patient_case: PatientCase,
    current_user: User = Depends(get_current_user),
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
            user_id=str(current_user.id),
            user_role=current_user.role.value,
        )

        return result

    except Exception as e:
        logger.error(f"Diagnostic analysis failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Diagnostic analysis failed. Please try again or contact support."
        )


@router.get(
    "/condition/{condition_id}",
    response_model=MedicalCondition,
    status_code=status.HTTP_200_OK,
    summary="Get medical condition details by ID",
)
async def get_condition(
    condition_id: str,
    current_user: User = Depends(get_current_user),
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
        logger.error(f"Failed to retrieve condition {condition_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve condition. Please try again or contact support."
        )


@router.post(
    "/analyze/enhanced",
    status_code=status.HTTP_200_OK,
    summary="🤖 Enhanced analysis with AI reasoning assistant",
    description="Full diagnostic analysis PLUS AI-generated explanations and follow-up questions",
)
async def analyze_with_ai_enhancement(
    patient_case: PatientCase,
    include_explanation: bool = True,
    include_questions: bool = True,
    include_report: bool = False,
    report_type: ReportType = ReportType.PHYSICIAN_SUMMARY,
    current_user: User = Depends(get_current_user),
    service: DiagnosticService = Depends(get_diagnostic_service),
    ai: AIReasoningAssistant = Depends(get_ai_assistant),
    audit: AuditLogger = Depends(get_audit_logger),
):
    """
    🚀 **Enhanced Diagnostic Analysis with AI Assistant**

    This endpoint provides everything from standard analysis PLUS:
    - 🗣️ Natural language explanations of diagnostic reasoning
    - ❓ Intelligent follow-up questions to refine diagnosis
    - 📋 Comprehensive medical reports (optional)

    **Parameters:**
    - `include_explanation`: Get detailed AI explanation of diagnosis
    - `include_questions`: Get follow-up questions to ask patient
    - `include_report`: Generate full medical report
    - `report_type`: Type of report (physician_summary, patient_friendly, detailed_clinical)
    """
    try:
        # Standard diagnostic analysis
        result = service.analyze_patient_case(patient_case)

        # Build enhanced response
        enhanced_result = {
            "diagnostic_result": result.model_dump(),
            "ai_enhancements": {}
        }

        # Generate AI explanation if requested
        if include_explanation and result.differential_diagnoses:
            logger.info("Generating AI explanation...")
            explanation = await ai.generate_detailed_explanation(patient_case, result)
            enhanced_result["ai_enhancements"]["detailed_explanation"] = explanation

        # Generate follow-up questions if requested
        if include_questions and result.differential_diagnoses:
            logger.info("Generating follow-up questions...")
            questions = await ai.generate_follow_up_questions(patient_case, result, num_questions=5)
            enhanced_result["ai_enhancements"]["follow_up_questions"] = questions

        # Generate medical report if requested
        if include_report and result.differential_diagnoses:
            logger.info(f"Generating {report_type} report...")
            report = await ai.generate_medical_report(patient_case, result, report_type)
            enhanced_result["ai_enhancements"]["medical_report"] = {
                "type": report_type,
                "content": report
            }

        # Log to audit
        audit.log_diagnostic_analysis(
            case=patient_case,
            result=result,
            user_id=str(current_user.id),
            user_role=current_user.role.value,
        )

        return enhanced_result

    except Exception as e:
        logger.error(f"Enhanced analysis failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enhanced analysis failed. Please try again or contact support."
        )


@router.post(
    "/explain",
    status_code=status.HTTP_200_OK,
    summary="🎓 Explain diagnosis in simple terms",
    description="Convert medical diagnosis into patient-friendly language",
)
async def explain_in_simple_terms(
    condition_name: str,
    technical_explanation: str,
    current_user: User = Depends(get_current_user),
    ai: AIReasoningAssistant = Depends(get_ai_assistant),
):
    """
    Convert medical jargon into patient-friendly language

    Perfect for:
    - Patient education materials
    - Explaining test results
    - Simplifying complex medical concepts
    """
    try:
        # Validate and sanitize inputs
        condition_name = input_validator.validate_condition_name(condition_name)
        technical_explanation = sanitize_for_llm(technical_explanation, "technical explanation")

        simple_explanation = await ai.explain_in_simple_terms(
            condition_name,
            technical_explanation
        )

        return {
            "condition": condition_name,
            "simple_explanation": simple_explanation,
            "reading_level": "Grade 6-8 (Patient-friendly)"
        }

    except Exception as e:
        logger.error(f"Explanation failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Explanation generation failed. Please try again or contact support."
        )


@router.post(
    "/treatment-recommendations",
    status_code=status.HTTP_200_OK,
    summary="💊 Get AI treatment recommendations",
    description="Generate evidence-based treatment recommendations for a diagnosis",
)
async def get_treatment_recommendations(
    case_id: str,
    diagnosis_name: str,
    patient_age: int,
    patient_sex: str,
    confidence_score: float,
    current_user: User = Depends(get_current_user),
    ai: AIReasoningAssistant = Depends(get_ai_assistant),
):
    """
    Generate treatment recommendations using AI

    Returns:
    - Immediate actions
    - Diagnostic workup
    - Initial treatment options
    - Specialist referrals
    - Patient counseling points
    - Red flags to watch for
    """
    try:
        # Validate inputs
        diagnosis_name = input_validator.validate_condition_name(diagnosis_name)
        patient_age = input_validator.validate_patient_age(patient_age)

        # Create minimal diagnosis object
        from ..models.schemas import DifferentialDiagnosis, UrgencyLevel
        diagnosis = DifferentialDiagnosis(
            condition_id=f"cond_{diagnosis_name.lower().replace(' ', '_')}",
            condition_name=diagnosis_name,
            similarity_score=confidence_score,
            confidence_score=confidence_score,
            probability=confidence_score,
            urgency_level=UrgencyLevel.ROUTINE
        )

        # Create minimal patient case
        from ..models.schemas import PatientCase, Sex
        patient_case = PatientCase(
            case_id=case_id,
            age=patient_age,
            sex=Sex(patient_sex.lower()),
            chief_complaint="",
            symptoms=[]
        )

        recommendations = await ai.generate_treatment_recommendations(diagnosis, patient_case)

        return recommendations

    except Exception as e:
        logger.error(f"Treatment recommendations failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Treatment recommendations generation failed. Please try again or contact support."
        )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
)
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    service: DiagnosticService = Depends(get_diagnostic_service),
):
    """
    Get statistics about the vector database and system
    """
    try:
        stats = service.vector_store.get_collection_stats()
        return {
            "status": "operational",
            "vector_database": stats,
            "ai_assistant": "enabled",
            "features": {
                "vector_search": True,
                "ai_explanations": True,
                "follow_up_questions": True,
                "medical_reports": True,
                "treatment_recommendations": True
            }
        }

    except Exception as e:
        logger.error(f"Failed to get stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics. Please try again or contact support."
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
async def health_check(
    service: DiagnosticService = Depends(get_diagnostic_service),
):
    """
    Health check endpoint that verifies service connectivity
    """
    health_status = {
        "status": "healthy",
        "service": "Medical Symptom Constellation Mapper",
        "version": "0.2.0",
        "checks": {}
    }

    try:
        # Check vector database connectivity
        try:
            stats = service.vector_store.get_collection_stats()
            health_status["checks"]["vector_database"] = "healthy"
        except Exception as e:
            logger.warning(f"Vector database health check failed: {e}")
            health_status["checks"]["vector_database"] = "unhealthy"
            health_status["status"] = "degraded"

        # Check if diagnostic service is initialized
        if service.vector_store is not None:
            health_status["checks"]["diagnostic_service"] = "healthy"
        else:
            health_status["checks"]["diagnostic_service"] = "unhealthy"
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )
