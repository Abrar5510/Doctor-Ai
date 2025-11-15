"""
Tests for configuration validation and settings
"""

import pytest
import os
from unittest.mock import patch

from src.config import Settings, get_settings


class TestConfigValidation:
    """Test configuration validation"""

    def test_default_settings_in_debug_mode(self):
        """Test that default settings work in debug mode"""
        with patch.dict(os.environ, {"DEBUG": "true"}, clear=True):
            settings = Settings()
            assert settings.debug is True

    def test_secret_key_validation_in_production(self):
        """Test that production requires a strong secret key"""
        with patch.dict(os.environ, {"DEBUG": "false", "SECRET_KEY": "short"}, clear=True):
            with pytest.raises(ValueError, match="SECRET_KEY must be set"):
                Settings()

    def test_secret_key_valid_in_production(self):
        """Test that valid secret key passes validation in production"""
        valid_key = "a" * 32  # 32 character key
        with patch.dict(os.environ, {"DEBUG": "false", "SECRET_KEY": valid_key}, clear=True):
            settings = Settings()
            assert settings.secret_key == valid_key

    def test_cors_origins_from_string(self):
        """Test parsing CORS origins from comma-separated string"""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "http://localhost:3000,http://example.com,https://app.example.com"
        }, clear=True):
            settings = Settings()
            assert len(settings.cors_origins) == 3
            assert "http://localhost:3000" in settings.cors_origins
            assert "http://example.com" in settings.cors_origins
            assert "https://app.example.com" in settings.cors_origins

    def test_cors_origins_default(self):
        """Test default CORS origins"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert isinstance(settings.cors_origins, list)
            assert len(settings.cors_origins) > 0

    def test_rate_limiting_enabled_by_default(self):
        """Test that rate limiting is enabled by default"""
        settings = Settings()
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute > 0

    def test_max_request_size_configured(self):
        """Test that max request size is configured"""
        settings = Settings()
        assert settings.max_request_size_mb > 0
        assert settings.max_request_size_mb <= 100  # Reasonable limit

    def test_confidence_thresholds_valid(self):
        """Test that confidence thresholds are properly ordered"""
        settings = Settings()
        assert settings.tier1_confidence_threshold > settings.tier2_confidence_threshold
        assert settings.tier2_confidence_threshold > settings.tier3_confidence_threshold
        assert 0.0 <= settings.tier3_confidence_threshold <= 1.0
        assert 0.0 <= settings.tier1_confidence_threshold <= 1.0

    def test_embedding_dimension_positive(self):
        """Test that embedding dimension is positive"""
        settings = Settings()
        assert settings.embedding_dimension > 0
        assert settings.embedding_dimension % 64 == 0  # Usually multiples of 64

    def test_top_k_candidates_reasonable(self):
        """Test that top_k_candidates is reasonable"""
        settings = Settings()
        assert settings.top_k_candidates > 0
        assert settings.top_k_candidates >= settings.final_results_limit

    def test_audit_logging_enabled_by_default(self):
        """Test that audit logging is enabled by default"""
        settings = Settings()
        assert settings.enable_audit_logging is True

    def test_settings_singleton_pattern(self):
        """Test that get_settings returns same instance"""
        # Clear cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2  # Should be same object

    @patch.dict(os.environ, {"APP_NAME": "Custom Medical App"})
    def test_custom_app_name(self):
        """Test custom app name from environment"""
        settings = Settings()
        assert settings.app_name == "Custom Medical App"

    @patch.dict(os.environ, {"API_PORT": "9000"})
    def test_custom_api_port(self):
        """Test custom API port from environment"""
        settings = Settings()
        assert settings.api_port == 9000

    def test_database_url_format(self):
        """Test database URL format"""
        settings = Settings()
        assert settings.database_url.startswith("postgresql://")

    def test_qdrant_configuration(self):
        """Test Qdrant configuration"""
        settings = Settings()
        assert settings.qdrant_host is not None
        assert settings.qdrant_port > 0
        assert settings.qdrant_collection_name is not None
        assert len(settings.qdrant_collection_name) > 0

    def test_redis_configuration(self):
        """Test Redis configuration"""
        settings = Settings()
        assert settings.redis_host is not None
        assert settings.redis_port > 0
        assert 0 <= settings.redis_db <= 15  # Redis DB index range

    def test_feature_flags(self):
        """Test feature flags are boolean"""
        settings = Settings()
        assert isinstance(settings.enable_rare_disease_detection, bool)
        assert isinstance(settings.enable_red_flag_alerts, bool)
        assert isinstance(settings.enable_temporal_analysis, bool)

    @patch.dict(os.environ, {"ENABLE_RARE_DISEASE_DETECTION": "false"})
    def test_feature_flag_override(self):
        """Test feature flag can be overridden"""
        settings = Settings()
        assert settings.enable_rare_disease_detection is False

    def test_log_level_valid(self):
        """Test log level is valid"""
        settings = Settings()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert settings.log_level.upper() in valid_levels


class TestEnvironmentSpecificSettings:
    """Test environment-specific configurations"""

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_development_mode(self):
        """Test development mode configuration"""
        settings = Settings()
        assert settings.debug is True

    @patch.dict(os.environ, {
        "DEBUG": "false",
        "SECRET_KEY": "production-secret-key-with-sufficient-length-32chars"
    })
    def test_production_mode(self):
        """Test production mode configuration"""
        settings = Settings()
        assert settings.debug is False
        assert len(settings.secret_key) >= 32
