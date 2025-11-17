"""
API routes for patient case history and tracking.

Provides endpoints for storing, retrieving, and managing diagnostic case history.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger
import json
from datetime import datetime

from ..models.database import User, PatientCaseRecord, DiagnosisRecord
from ..models.schemas import PatientCase, DiagnosticResult
from ..services.auth import get_current_user
from ..dependencies import get_database
from ..utils.metrics import get_metrics

router = APIRouter()


@router.post(
    "/cases",
    status_code=status.HTTP_201_CREATED,
    summary="Save a diagnostic case to history",
    description="Store a completed diagnostic case with results for future reference",
)
async def save_case_to_history(
    patient_case: PatientCase,
    diagnostic_result: DiagnosticResult,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    """
    Save a diagnostic case and its results to the database.

    This enables case tracking, historical analysis, and learning from outcomes.
    """
    try:
        metrics = get_metrics()

        with metrics.measure("save_case_to_history"):
            # Create patient case record
            case_record = PatientCaseRecord(
                case_id=patient_case.case_id,
                user_id=current_user.id,
                patient_age=patient_case.age,
                patient_sex=patient_case.sex.value,
                patient_ethnicity=patient_case.ethnicity if hasattr(patient_case, 'ethnicity') else None,
                patient_location=patient_case.location if hasattr(patient_case, 'location') else None,
                chief_complaint=patient_case.chief_complaint,
                symptoms_json=json.dumps([s.model_dump() for s in patient_case.symptoms]),
                medical_history_json=json.dumps(patient_case.medical_history) if patient_case.medical_history else None,
                family_history_json=json.dumps(patient_case.family_history) if patient_case.family_history else None,
                medications_json=json.dumps(patient_case.current_medications) if patient_case.current_medications else None,
                allergies_json=json.dumps(patient_case.allergies) if patient_case.allergies else None,
                top_diagnosis=diagnostic_result.differential_diagnoses[0].condition_name if diagnostic_result.differential_diagnoses else None,
                confidence_score=int(diagnostic_result.differential_diagnoses[0].confidence_score * 100) if diagnostic_result.differential_diagnoses else None,
                review_tier=diagnostic_result.review_tier,
                has_red_flags=len(diagnostic_result.red_flags) > 0 if diagnostic_result.red_flags else False,
                red_flags_json=json.dumps(diagnostic_result.red_flags) if diagnostic_result.red_flags else None,
                status="pending_review",
                priority="emergency" if diagnostic_result.red_flags else "routine",
            )

            db.add(case_record)
            db.flush()  # Get the ID

            # Create diagnosis records for each differential diagnosis
            for rank, diagnosis in enumerate(diagnostic_result.differential_diagnoses[:10], start=1):
                diagnosis_record = DiagnosisRecord(
                    case_id=case_record.id,
                    condition_id=diagnosis.condition_id,
                    condition_name=diagnosis.condition_name,
                    icd10_code=getattr(diagnosis, 'icd10_code', None),
                    snomed_code=getattr(diagnosis, 'snomed_code', None),
                    similarity_score=int(diagnosis.similarity_score * 100),
                    confidence_score=int(diagnosis.confidence_score * 100),
                    probability=int(diagnosis.probability * 100),
                    rank=rank,
                    is_rare_disease=getattr(diagnosis, 'is_rare_disease', False),
                    urgency_level=diagnosis.urgency_level.value,
                    specialty=getattr(diagnosis, 'specialty', None),
                    matching_symptoms_json=json.dumps(diagnosis.matching_symptoms) if hasattr(diagnosis, 'matching_symptoms') else None,
                    supporting_evidence_json=json.dumps(diagnosis.supporting_evidence) if diagnosis.supporting_evidence else None,
                    distinguishing_features_json=json.dumps(diagnosis.distinguishing_features) if diagnosis.distinguishing_features else None,
                )

                db.add(diagnosis_record)

            db.commit()

            logger.info(
                f"Case {patient_case.case_id} saved to history by user {current_user.id} "
                f"with {len(diagnostic_result.differential_diagnoses)} diagnoses"
            )

            return {
                "status": "success",
                "message": "Case saved to history",
                "case_id": patient_case.case_id,
                "database_id": case_record.id,
            }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save case to history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save case to history"
        )


@router.get(
    "/cases",
    status_code=status.HTTP_200_OK,
    summary="Get case history",
    description="Retrieve all diagnostic cases for the current user",
)
async def get_case_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    priority_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    """
    Get paginated case history for the authenticated user.

    Supports filtering by status and priority.
    """
    try:
        query = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.user_id == current_user.id
        )

        if status_filter:
            query = query.filter(PatientCaseRecord.status == status_filter)

        if priority_filter:
            query = query.filter(PatientCaseRecord.priority == priority_filter)

        total = query.count()
        cases = query.order_by(PatientCaseRecord.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "cases": [
                {
                    "id": case.id,
                    "case_id": case.case_id,
                    "patient_age": case.patient_age,
                    "patient_sex": case.patient_sex,
                    "chief_complaint": case.chief_complaint,
                    "top_diagnosis": case.top_diagnosis,
                    "confidence_score": case.confidence_score,
                    "review_tier": case.review_tier,
                    "has_red_flags": case.has_red_flags,
                    "status": case.status,
                    "priority": case.priority,
                    "created_at": case.created_at.isoformat(),
                    "reviewed_at": case.reviewed_at.isoformat() if case.reviewed_at else None,
                }
                for case in cases
            ]
        }

    except Exception as e:
        logger.error(f"Failed to retrieve case history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case history"
        )


@router.get(
    "/cases/{case_id}",
    status_code=status.HTTP_200_OK,
    summary="Get case details",
    description="Retrieve complete details of a specific case including all diagnoses",
)
async def get_case_details(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    """
    Get complete details of a specific case including all differential diagnoses.
    """
    try:
        case = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.case_id == case_id,
            PatientCaseRecord.user_id == current_user.id
        ).first()

        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case not found: {case_id}"
            )

        # Get all diagnoses for this case
        diagnoses = db.query(DiagnosisRecord).filter(
            DiagnosisRecord.case_id == case.id
        ).order_by(DiagnosisRecord.rank).all()

        return {
            "id": case.id,
            "case_id": case.case_id,
            "patient_age": case.patient_age,
            "patient_sex": case.patient_sex,
            "patient_ethnicity": case.patient_ethnicity,
            "patient_location": case.patient_location,
            "chief_complaint": case.chief_complaint,
            "symptoms": json.loads(case.symptoms_json),
            "medical_history": json.loads(case.medical_history_json) if case.medical_history_json else None,
            "family_history": json.loads(case.family_history_json) if case.family_history_json else None,
            "medications": json.loads(case.medications_json) if case.medications_json else None,
            "allergies": json.loads(case.allergies_json) if case.allergies_json else None,
            "top_diagnosis": case.top_diagnosis,
            "confidence_score": case.confidence_score,
            "review_tier": case.review_tier,
            "has_red_flags": case.has_red_flags,
            "red_flags": json.loads(case.red_flags_json) if case.red_flags_json else None,
            "status": case.status,
            "priority": case.priority,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
            "reviewed_at": case.reviewed_at.isoformat() if case.reviewed_at else None,
            "diagnoses": [
                {
                    "rank": diag.rank,
                    "condition_id": diag.condition_id,
                    "condition_name": diag.condition_name,
                    "icd10_code": diag.icd10_code,
                    "snomed_code": diag.snomed_code,
                    "similarity_score": diag.similarity_score,
                    "confidence_score": diag.confidence_score,
                    "probability": diag.probability,
                    "is_rare_disease": diag.is_rare_disease,
                    "urgency_level": diag.urgency_level,
                    "specialty": diag.specialty,
                    "matching_symptoms": json.loads(diag.matching_symptoms_json) if diag.matching_symptoms_json else None,
                    "supporting_evidence": json.loads(diag.supporting_evidence_json) if diag.supporting_evidence_json else None,
                    "distinguishing_features": json.loads(diag.distinguishing_features_json) if diag.distinguishing_features_json else None,
                    "physician_confirmed": diag.physician_confirmed,
                    "physician_notes": diag.physician_notes,
                    "reviewed_at": diag.reviewed_at.isoformat() if diag.reviewed_at else None,
                }
                for diag in diagnoses
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve case details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case details"
        )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get user statistics",
    description="Get statistics about the user's diagnostic cases",
)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    """
    Get statistics about the user's diagnostic activity.
    """
    try:
        total_cases = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.user_id == current_user.id
        ).count()

        pending_cases = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.user_id == current_user.id,
            PatientCaseRecord.status == "pending_review"
        ).count()

        emergency_cases = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.user_id == current_user.id,
            PatientCaseRecord.priority == "emergency"
        ).count()

        cases_with_red_flags = db.query(PatientCaseRecord).filter(
            PatientCaseRecord.user_id == current_user.id,
            PatientCaseRecord.has_red_flags == True
        ).count()

        return {
            "total_cases": total_cases,
            "pending_review": pending_cases,
            "emergency_cases": emergency_cases,
            "cases_with_red_flags": cases_with_red_flags,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
