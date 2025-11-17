"""
Database models for Doctor-AI application.

This module defines SQLAlchemy models for user management, authentication,
and audit logging in PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    API_USER = "api_user"


class UserStatus(str, enum.Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Role and status
    role = Column(Enum(UserRole), default=UserRole.API_USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)

    # Security fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Password management
    password_changed_at = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Verification
    verification_token = Column(String(255), nullable=True)
    verification_expires = Column(DateTime, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class UserSession(Base):
    """User session model for tracking active sessions and JWT tokens."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID

    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    device_info = Column(String(255), nullable=True)

    # Session lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"


class AuditLog(Base):
    """Audit log model for HIPAA compliance and security tracking."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), nullable=False)  # success, failure, error

    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_path = Column(String(500), nullable=True)

    # Additional context
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    error_message = Column(Text, nullable=True)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', status='{self.status}')>"


class APIKey(Base):
    """API key model for service-to-service authentication."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Key details
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Permissions and limits
    scopes = Column(Text, nullable=True)  # JSON array of allowed scopes
    rate_limit = Column(Integer, nullable=True)  # Requests per minute
    is_active = Column(Boolean, default=True, nullable=False)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    # Usage tracking
    total_requests = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_api_key_name"),
    )

    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.name}', active={self.is_active})>"


class PatientCaseRecord(Base):
    """Patient case record model for storing diagnostic cases."""

    __tablename__ = "patient_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Patient demographics
    patient_age = Column(Integer, nullable=False)
    patient_sex = Column(String(20), nullable=False)
    patient_ethnicity = Column(String(100), nullable=True)
    patient_location = Column(String(255), nullable=True)

    # Chief complaint
    chief_complaint = Column(Text, nullable=False)

    # Symptoms data (stored as JSON)
    symptoms_json = Column(Text, nullable=False)  # JSON array of symptoms
    medical_history_json = Column(Text, nullable=True)  # JSON array of medical history
    family_history_json = Column(Text, nullable=True)  # JSON array of family history
    medications_json = Column(Text, nullable=True)  # JSON array of current medications
    allergies_json = Column(Text, nullable=True)  # JSON array of allergies

    # Diagnostic results
    top_diagnosis = Column(String(255), nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    review_tier = Column(Integer, nullable=True)  # 1-4
    has_red_flags = Column(Boolean, default=False, nullable=False)
    red_flags_json = Column(Text, nullable=True)  # JSON array of red flags detected

    # Case metadata
    status = Column(String(50), default="pending_review", nullable=False)  # pending_review, reviewed, confirmed, rejected
    priority = Column(String(50), default="routine", nullable=False)  # routine, urgent, emergency
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    diagnoses = relationship("DiagnosisRecord", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PatientCaseRecord(id={self.id}, case_id='{self.case_id}', status='{self.status}')>"


class DiagnosisRecord(Base):
    """Individual diagnosis record for each differential diagnosis."""

    __tablename__ = "diagnosis_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("patient_cases.id"), nullable=False)

    # Diagnosis details
    condition_id = Column(String(255), nullable=False, index=True)
    condition_name = Column(String(500), nullable=False)
    icd10_code = Column(String(20), nullable=True)
    snomed_code = Column(String(50), nullable=True)

    # Scores
    similarity_score = Column(Integer, nullable=False)  # 0-100
    confidence_score = Column(Integer, nullable=False)  # 0-100
    probability = Column(Integer, nullable=False)  # 0-100
    rank = Column(Integer, nullable=False)  # Position in differential (1-N)

    # Classification
    is_rare_disease = Column(Boolean, default=False, nullable=False)
    urgency_level = Column(String(50), nullable=False)  # routine, urgent, emergency
    specialty = Column(String(100), nullable=True)

    # Evidence
    matching_symptoms_json = Column(Text, nullable=True)  # JSON array
    supporting_evidence_json = Column(Text, nullable=True)  # JSON array
    distinguishing_features_json = Column(Text, nullable=True)  # JSON array

    # Clinical metadata
    typical_age_range = Column(String(50), nullable=True)
    sex_predilection = Column(String(20), nullable=True)
    prevalence = Column(String(50), nullable=True)

    # Physician review
    physician_confirmed = Column(Boolean, nullable=True)
    physician_notes = Column(Text, nullable=True)
    physician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("PatientCaseRecord", back_populates="diagnoses")

    def __repr__(self):
        return f"<DiagnosisRecord(id={self.id}, condition='{self.condition_name}', rank={self.rank})>"


class SystemMetrics(Base):
    """System performance and usage metrics."""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Metric details
    metric_type = Column(String(100), nullable=False, index=True)  # query_latency, embedding_time, cache_hit_rate, etc.
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Integer, nullable=False)  # Store as integer (milliseconds, count, percentage * 100)
    metric_unit = Column(String(50), nullable=False)  # ms, count, percentage, etc.

    # Context
    endpoint = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_id = Column(String(100), nullable=True)

    # Additional metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, type='{self.metric_type}', value={self.metric_value})>"


class CachedEmbedding(Base):
    """Cache for vector embeddings to reduce computation."""

    __tablename__ = "cached_embeddings"

    id = Column(Integer, primary_key=True, index=True)

    # Text that was embedded
    text_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256 hash
    text_content = Column(Text, nullable=False)

    # Embedding data
    embedding_json = Column(Text, nullable=False)  # JSON array of floats
    embedding_model = Column(String(255), nullable=False)
    vector_dimension = Column(Integer, nullable=False)

    # Cache metadata
    access_count = Column(Integer, default=1, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CachedEmbedding(id={self.id}, model='{self.embedding_model}', accesses={self.access_count})>"
