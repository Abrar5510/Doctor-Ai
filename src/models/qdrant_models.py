"""
Qdrant Database Models for Doctor-AI Application.

This module provides model classes for interacting with Qdrant collections,
replacing the traditional SQLAlchemy ORM models.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserModel(BaseModel):
    """User model for authentication and authorization."""

    id: int
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    role: str = "api_user"  # admin, physician, nurse, researcher, api_user
    status: str = "pending_verification"  # active, inactive, suspended, pending_verification
    is_active: bool = True
    is_verified: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    verification_token: Optional[str] = None
    verification_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    created_by: Optional[int] = None


class UserSessionModel(BaseModel):
    """User session model for tracking active sessions and JWT tokens."""

    id: int
    user_id: int
    token_jti: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    is_active: bool = True


class AuditLogModel(BaseModel):
    """Audit log model for HIPAA compliance and security tracking."""

    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: str  # success, failure, error
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    description: Optional[str] = None
    metadata_json: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None


class APIKeyModel(BaseModel):
    """API key model for service-to-service authentication."""

    id: int
    user_id: int
    key_hash: str
    key_prefix: str
    name: str
    description: Optional[str] = None
    scopes: Optional[str] = None
    rate_limit: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    total_requests: int = 0


class PatientCaseModel(BaseModel):
    """Patient case record model for storing diagnostic cases."""

    id: int
    case_id: str
    user_id: int
    patient_age: int
    patient_sex: str
    patient_ethnicity: Optional[str] = None
    patient_location: Optional[str] = None
    chief_complaint: str
    symptoms_json: str  # JSON array of symptoms
    medical_history_json: Optional[str] = None
    family_history_json: Optional[str] = None
    medications_json: Optional[str] = None
    allergies_json: Optional[str] = None
    top_diagnosis: Optional[str] = None
    confidence_score: Optional[int] = None
    review_tier: Optional[int] = None
    has_red_flags: bool = False
    red_flags_json: Optional[str] = None
    status: str = "pending_review"
    priority: str = "routine"
    assigned_to_user_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None


class DiagnosisRecordModel(BaseModel):
    """Individual diagnosis record for each differential diagnosis."""

    id: int
    case_id: int
    condition_id: str
    condition_name: str
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    similarity_score: int
    confidence_score: int
    probability: int
    rank: int
    is_rare_disease: bool = False
    urgency_level: str
    specialty: Optional[str] = None
    matching_symptoms_json: Optional[str] = None
    supporting_evidence_json: Optional[str] = None
    distinguishing_features_json: Optional[str] = None
    typical_age_range: Optional[str] = None
    sex_predilection: Optional[str] = None
    prevalence: Optional[str] = None
    physician_confirmed: Optional[bool] = None
    physician_notes: Optional[str] = None
    physician_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SystemMetricsModel(BaseModel):
    """System performance and usage metrics."""

    id: int
    metric_type: str
    metric_name: str
    metric_value: int
    metric_unit: str
    endpoint: Optional[str] = None
    user_id: Optional[int] = None
    request_id: Optional[str] = None
    metadata_json: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MedicalConditionModel(BaseModel):
    """Medical condition model for diagnostic knowledge base."""

    id: int
    condition_id: str
    condition_name: str
    icd_codes_json: Optional[str] = None
    snomed_codes_json: Optional[str] = None
    typical_symptoms_json: str
    rare_symptoms_json: Optional[str] = None
    red_flag_symptoms_json: Optional[str] = None
    prevalence: Optional[int] = None
    is_rare_disease: bool = False
    urgency_level: str
    temporal_pattern: Optional[str] = None
    diagnostic_criteria_json: Optional[str] = None
    differential_diagnoses_json: Optional[str] = None
    recommended_tests_json: Optional[str] = None
    specialist_referral: Optional[str] = None
    distinguishing_features_json: Optional[str] = None
    evidence_sources_json: Optional[str] = None
    typical_age_range: Optional[str] = None
    sex_predilection: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Model mapping for collection names to model classes
COLLECTION_MODELS = {
    "users": UserModel,
    "user_sessions": UserSessionModel,
    "audit_logs": AuditLogModel,
    "api_keys": APIKeyModel,
    "patient_cases": PatientCaseModel,
    "diagnosis_records": DiagnosisRecordModel,
    "system_metrics": SystemMetricsModel,
    "medical_conditions": MedicalConditionModel,
}
