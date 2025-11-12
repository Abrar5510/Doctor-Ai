"""
Pydantic schemas for data validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class Severity(str, Enum):
    """Symptom severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class Frequency(str, Enum):
    """Symptom frequency patterns"""
    CONSTANT = "constant"
    INTERMITTENT = "intermittent"
    EPISODIC = "episodic"
    PROGRESSIVE = "progressive"


class UrgencyLevel(str, Enum):
    """Medical urgency classification"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    NON_URGENT = "non_urgent"


class Sex(str, Enum):
    """Biological sex"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class ReviewTier(str, Enum):
    """Multi-tier review system"""
    TIER1_AUTOMATED = "tier1_automated"  # Confidence > 85%
    TIER2_PRIMARY_CARE = "tier2_primary_care"  # Confidence 60-85%
    TIER3_SPECIALIST = "tier3_specialist"  # Confidence 40-60%
    TIER4_MULTIDISCIPLINARY = "tier4_multidisciplinary"  # Confidence < 40%


# ============= Symptom Models =============

class SymptomInput(BaseModel):
    """Input model for patient-reported symptoms"""
    description: str = Field(..., description="Free-text symptom description")
    severity: Severity = Field(default=Severity.MODERATE, description="Symptom severity")
    duration_days: Optional[int] = Field(None, description="Duration in days", ge=0)
    frequency: Frequency = Field(default=Frequency.CONSTANT, description="Symptom frequency")
    onset_date: Optional[date] = Field(None, description="When symptom first appeared")
    location: Optional[str] = Field(None, description="Body location if applicable")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Persistent fatigue and weakness",
                "severity": "moderate",
                "duration_days": 30,
                "frequency": "constant",
                "onset_date": "2024-01-15",
                "location": "general"
            }
        }


class Symptom(BaseModel):
    """Standardized symptom representation"""
    symptom_id: str = Field(..., description="Unique symptom identifier")
    name: str = Field(..., description="Standardized symptom name")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code")
    description: str = Field(..., description="Detailed description")
    severity: Severity
    duration_days: Optional[int] = None
    frequency: Frequency
    onset_date: Optional[date] = None
    location: Optional[str] = None
    temporal_pattern: Optional[str] = Field(None, description="Temporal progression pattern")
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


# ============= Medical Condition Models =============

class MedicalCondition(BaseModel):
    """Comprehensive medical condition/disease representation"""
    condition_id: str = Field(..., description="Unique condition identifier")
    condition_name: str = Field(..., description="Disease/condition name")
    icd_codes: List[str] = Field(default_factory=list, description="ICD-10/11 codes")
    snomed_codes: List[str] = Field(default_factory=list, description="SNOMED CT codes")

    # Prevalence & Demographics
    prevalence: float = Field(..., description="Disease prevalence (0-1)", ge=0.0, le=1.0)
    is_rare_disease: bool = Field(default=False, description="Orphan/rare disease status")
    age_distribution: Dict[str, float] = Field(
        default_factory=dict,
        description="Age group distribution"
    )
    sex_distribution: Dict[str, float] = Field(
        default_factory=dict,
        description="Sex distribution"
    )

    # Symptoms
    typical_symptoms: List[str] = Field(
        default_factory=list,
        description="Common symptoms"
    )
    rare_symptoms: List[str] = Field(
        default_factory=list,
        description="Rare but diagnostic symptoms"
    )
    red_flag_symptoms: List[str] = Field(
        default_factory=list,
        description="Dangerous symptoms requiring immediate attention"
    )

    # Clinical Characteristics
    temporal_pattern: Optional[str] = Field(
        None,
        description="Typical disease progression pattern"
    )
    severity_profile: Dict[str, Any] = Field(
        default_factory=dict,
        description="Disease severity characteristics"
    )
    diagnostic_criteria: List[str] = Field(
        default_factory=list,
        description="Clinical diagnostic criteria"
    )

    # Differential Diagnosis
    differential_diagnoses: List[str] = Field(
        default_factory=list,
        description="Common differential diagnoses"
    )
    distinguishing_features: Dict[str, str] = Field(
        default_factory=dict,
        description="Features that distinguish from similar conditions"
    )

    # Clinical Decision Support
    urgency_level: UrgencyLevel = Field(
        default=UrgencyLevel.ROUTINE,
        description="Typical urgency level"
    )
    recommended_tests: List[str] = Field(
        default_factory=list,
        description="Recommended diagnostic tests"
    )
    specialist_referral: Optional[str] = Field(
        None,
        description="Recommended specialist type"
    )

    # Evidence & Sources
    evidence_sources: List[str] = Field(
        default_factory=list,
        description="Literature and guideline references"
    )

    # Vector Embedding (stored separately in Qdrant)
    embedding_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata about vector embedding"
    )


# ============= Patient Models =============

class PatientCase(BaseModel):
    """Patient case information (de-identified for HIPAA compliance)"""
    case_id: str = Field(..., description="Unique case identifier")
    patient_id: Optional[str] = Field(None, description="De-identified patient ID")

    # Demographics
    age: int = Field(..., description="Patient age", ge=0, le=150)
    sex: Sex = Field(..., description="Biological sex")
    ethnicity: Optional[str] = Field(None, description="Ethnicity")

    # Symptoms
    symptoms: List[SymptomInput] = Field(..., description="Patient symptoms")
    chief_complaint: str = Field(..., description="Primary complaint")

    # Medical History
    medical_history: List[str] = Field(
        default_factory=list,
        description="Past medical conditions"
    )
    family_history: List[str] = Field(
        default_factory=list,
        description="Family medical history"
    )
    current_medications: List[str] = Field(
        default_factory=list,
        description="Current medications"
    )

    # Lab & Test Results
    lab_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Laboratory test results"
    )
    imaging_reports: List[str] = Field(
        default_factory=list,
        description="Imaging report summaries"
    )

    # Context
    geographic_location: Optional[str] = Field(
        None,
        description="Geographic location for prevalence context"
    )
    travel_history: List[str] = Field(
        default_factory=list,
        description="Recent travel history"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case_12345",
                "age": 35,
                "sex": "female",
                "symptoms": [
                    {
                        "description": "Persistent fatigue",
                        "severity": "moderate",
                        "duration_days": 60,
                        "frequency": "constant"
                    }
                ],
                "chief_complaint": "Unexplained fatigue and weight gain"
            }
        }


# ============= Diagnostic Result Models =============

class DifferentialDiagnosis(BaseModel):
    """Individual diagnosis in differential list"""
    condition_id: str
    condition_name: str
    icd_codes: List[str] = Field(default_factory=list)

    # Scoring
    similarity_score: float = Field(..., description="Vector similarity score", ge=0.0, le=1.0)
    confidence_score: float = Field(..., description="Overall confidence", ge=0.0, le=1.0)
    probability: float = Field(..., description="Bayesian probability", ge=0.0, le=1.0)

    # Evidence
    matching_symptoms: List[str] = Field(
        default_factory=list,
        description="Symptoms that match this condition"
    )
    missing_symptoms: List[str] = Field(
        default_factory=list,
        description="Expected symptoms not present"
    )
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Supporting evidence from literature/cases"
    )

    # Clinical Guidance
    diagnostic_criteria_met: List[str] = Field(
        default_factory=list,
        description="Diagnostic criteria satisfied"
    )
    recommended_next_steps: List[str] = Field(
        default_factory=list,
        description="Suggested next steps"
    )
    urgency_level: UrgencyLevel

    # Distinguishing Features
    distinguishing_features: Dict[str, str] = Field(
        default_factory=dict,
        description="Features to distinguish from other diagnoses"
    )


class DiagnosticResult(BaseModel):
    """Complete diagnostic analysis result"""
    result_id: str = Field(..., description="Unique result identifier")
    case_id: str = Field(..., description="Associated case ID")

    # Differential Diagnosis List
    differential_diagnoses: List[DifferentialDiagnosis] = Field(
        ...,
        description="Ranked list of possible diagnoses"
    )

    # Primary Diagnosis
    primary_diagnosis: Optional[DifferentialDiagnosis] = Field(
        None,
        description="Most likely diagnosis if confidence is high"
    )

    # Review Tier Assignment
    review_tier: ReviewTier = Field(
        ...,
        description="Assigned review tier based on confidence"
    )
    overall_confidence: float = Field(..., ge=0.0, le=1.0)

    # Red Flags
    red_flags_detected: List[str] = Field(
        default_factory=list,
        description="Critical symptoms requiring immediate attention"
    )
    requires_emergency_care: bool = Field(
        default=False,
        description="Emergency care needed"
    )

    # Rare Disease Detection
    rare_diseases_considered: List[DifferentialDiagnosis] = Field(
        default_factory=list,
        description="Rare diseases in consideration"
    )

    # Clinical Decision Support
    recommended_specialists: List[str] = Field(
        default_factory=list,
        description="Recommended specialist consultations"
    )
    recommended_tests: List[str] = Field(
        default_factory=list,
        description="Suggested diagnostic tests"
    )

    # Explainability
    reasoning_summary: str = Field(
        ...,
        description="Human-readable explanation of diagnostic reasoning"
    )
    feature_importance: Dict[str, float] = Field(
        default_factory=dict,
        description="Which symptoms were most important"
    )

    # Metadata
    processing_time_ms: float = Field(..., description="Time taken for analysis")
    model_version: str = Field(default="0.1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============= Audit & Compliance Models =============

class AuditLog(BaseModel):
    """Comprehensive audit trail for regulatory compliance"""
    audit_id: str = Field(..., description="Unique audit log identifier")
    case_id: Optional[str] = Field(None, description="Associated case ID")
    result_id: Optional[str] = Field(None, description="Associated result ID")

    # Action Details
    action_type: str = Field(..., description="Type of action performed")
    user_id: Optional[str] = Field(None, description="De-identified user ID")
    user_role: Optional[str] = Field(None, description="User role (physician, specialist, etc.)")

    # Data Provenance
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for the action"
    )
    output_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Output/result data"
    )

    # Processing Details
    vector_search_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Vector search parameters used"
    )
    similarity_scores: Optional[List[float]] = Field(
        None,
        description="All similarity scores from search"
    )
    filters_applied: List[str] = Field(
        default_factory=list,
        description="Filters applied during processing"
    )

    # Human Review
    human_review_performed: bool = Field(default=False)
    review_decision: Optional[str] = Field(None, description="Human reviewer decision")
    override_rationale: Optional[str] = Field(
        None,
        description="Rationale if AI suggestion was overridden"
    )

    # Outcome Tracking
    final_diagnosis: Optional[str] = Field(None, description="Confirmed final diagnosis")
    outcome: Optional[str] = Field(None, description="Patient outcome")
    accuracy_validated: bool = Field(default=False)

    # Compliance
    hipaa_compliant: bool = Field(default=True)
    data_anonymized: bool = Field(default=True)

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "audit_67890",
                "case_id": "case_12345",
                "action_type": "diagnostic_analysis",
                "user_role": "primary_care_physician",
                "timestamp": "2024-11-12T10:30:00Z"
            }
        }
