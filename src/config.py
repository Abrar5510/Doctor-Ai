"""
Configuration management for the Medical Symptom Constellation Mapper
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from functools import lru_cache
from typing import Optional
import os


def get_database_url() -> str:
    """
    Get database URL with Vercel Postgres fallback.

    Priority:
    1. DATABASE_URL environment variable
    2. POSTGRES_URL_NON_POOLING (Vercel Postgres automatic variable)
    3. POSTGRES_URL (Vercel Postgres pooled connection)
    """
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    # Fallback to Vercel Postgres environment variables
    db_url = os.getenv('POSTGRES_URL_NON_POOLING') or os.getenv('POSTGRES_URL')
    if db_url:
        return db_url

    # If no database URL is found, return empty string
    # The validation will catch this and provide a helpful error
    return ""


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

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
    secret_key: str  # REQUIRED: Must be set via environment variable
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:8000"  # Comma-separated list
    cors_allow_credentials: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per minute
    rate_limit_period: int = 60  # seconds

    # Database Configuration
    # PRIMARY DATABASE: Set to "qdrant" to use Qdrant as main database, or "postgresql" for PostgreSQL
    primary_database: str = "qdrant"  # Options: "qdrant" or "postgresql"

    # PostgreSQL Database (Legacy/Optional)
    # Automatically uses POSTGRES_URL_NON_POOLING or POSTGRES_URL if DATABASE_URL not set
    database_url: str = Field(default_factory=get_database_url)
    database_echo: bool = False

    # Qdrant Vector Database (PRIMARY DATABASE)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "medical_conditions"

    # Redis Cache
    redis_enabled: bool = False  # Disabled by default, enable in production if Redis is available
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # ML Models
    embedding_model: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    embedding_dimension: int = 768
    max_sequence_length: int = 512

    # AI Assistant (OpenAI / OpenRouter)
    openai_api_key: Optional[str] = None
    use_openrouter: bool = False
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-4-turbo-preview"
    use_local_llm: bool = False
    local_llm_model: str = "llama2"

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
    enable_ai_assistant: bool = True

    def get_cors_origins(self) -> list:
        """Get CORS origins as a list. Never allows wildcard for security."""
        # SECURITY: Never allow wildcard origins, even in debug mode
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        if "*" in origins:
            raise ValueError(
                "Wildcard CORS origins (*) are not allowed for security reasons. "
                "Please specify exact origins."
            )
        return origins

    def validate_secret_key(self) -> bool:
        """Validate that secret key is strong enough for production."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set via environment variable")

        if len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security"
            )
        return True

    def validate_database_config(self) -> bool:
        """Validate database configuration based on primary_database setting."""
        if self.primary_database == "qdrant":
            # Qdrant is primary - ensure it's configured
            if not self.qdrant_host:
                raise ValueError("QDRANT_HOST must be set when using Qdrant as primary database")
        elif self.primary_database == "postgresql":
            # PostgreSQL is primary - ensure it's configured
            if not self.database_url:
                raise ValueError(
                    "Database URL not configured. Please set one of:\n"
                    "  - DATABASE_URL environment variable\n"
                    "  - Connect Vercel Postgres to your project (provides POSTGRES_URL automatically)"
                )
        else:
            raise ValueError(
                f"Invalid primary_database value: {self.primary_database}. "
                "Must be 'qdrant' or 'postgresql'"
            )
        return True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    settings.validate_secret_key()
    settings.validate_database_config()
    return settings
