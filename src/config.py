"""
Configuration management for the Medical Symptom Constellation Mapper
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application Settings
    app_name: str = "Medical Symptom Constellation Mapper"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/doctor_ai"
    database_echo: bool = False

    # Qdrant Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "medical_conditions"

    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # ML Models
    embedding_model: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    embedding_dimension: int = 768
    max_sequence_length: int = 512

    # Medical Ontology
    use_snomed_ct: bool = True
    use_icd10: bool = True
    use_hpo: bool = True

    # Confidence Thresholds
    tier1_confidence_threshold: float = 0.85
    tier2_confidence_threshold: float = 0.60
    tier3_confidence_threshold: float = 0.40

    # Search Parameters
    top_k_candidates: int = 50
    final_results_limit: int = 10

    # HIPAA Compliance
    enable_audit_logging: bool = True
    enable_data_anonymization: bool = True
    audit_log_path: str = "./logs/audit/"

    # Feature Flags
    enable_rare_disease_detection: bool = True
    enable_red_flag_alerts: bool = True
    enable_temporal_analysis: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
