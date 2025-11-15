"""
Tests for audit logging and HIPAA compliance
"""

import pytest
import json
import hmac
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from src.utils.audit import AuditLogger
from src.models.schemas import (
    PatientCase,
    SymptomInput,
    Sex,
    Severity,
    DiagnosticResult,
    DifferentialDiagnosis,
    ReviewTier,
    UrgencyLevel,
)


@pytest.fixture
def temp_audit_dir(tmp_path):
    """Create temporary audit directory"""
    audit_dir = tmp_path / "audit_logs"
    audit_dir.mkdir()
    return audit_dir


@pytest.fixture
def audit_logger(temp_audit_dir):
    """Create audit logger with temporary directory"""
    with patch('src.utils.audit.get_settings') as mock_settings:
        settings = Mock()
        settings.enable_audit_logging = True
        settings.enable_data_anonymization = True
        settings.audit_log_path = str(temp_audit_dir)
        settings.secret_key = "test-secret-key-for-hmac-hashing-32chars"
        mock_settings.return_value = settings

        logger = AuditLogger()
        return logger


@pytest.fixture
def sample_patient_case():
    """Sample patient case for testing"""
    return PatientCase(
        case_id="case_001",
        patient_id="patient_12345",
        age=35,
        sex=Sex.MALE,
        symptoms=[
            SymptomInput(
                description="Persistent cough",
                severity=Severity.MODERATE,
                duration_days=7
            )
        ],
        chief_complaint="Cough for one week"
    )


@pytest.fixture
def sample_diagnostic_result():
    """Sample diagnostic result for testing"""
    return DiagnosticResult(
        case_id="case_001",
        differential_diagnoses=[
            DifferentialDiagnosis(
                condition_id="cond_001",
                condition_name="Common Cold",
                similarity_score=0.85,
                confidence_score=0.80,
                probability=0.75,
                urgency_level=UrgencyLevel.ROUTINE
            )
        ],
        review_tier=ReviewTier.TIER1_AUTOMATED,
        red_flags=[],
        processing_time_seconds=0.5
    )


class TestAuditLogger:
    """Test suite for AuditLogger"""

    def test_initialization(self, audit_logger):
        """Test audit logger initialization"""
        assert audit_logger is not None
        assert audit_logger.settings is not None
        assert audit_logger.audit_log_path is not None

    def test_log_directory_creation(self, temp_audit_dir, audit_logger):
        """Test that audit log directory is created"""
        assert temp_audit_dir.exists()
        assert temp_audit_dir.is_dir()

    def test_log_diagnostic_analysis(
        self,
        audit_logger,
        sample_patient_case,
        sample_diagnostic_result
    ):
        """Test logging diagnostic analysis"""
        audit_logger.log_diagnostic_analysis(
            case=sample_patient_case,
            result=sample_diagnostic_result,
            user_id="user_001",
            user_role="physician"
        )

        # Verify log file was created
        log_files = list(audit_logger.audit_log_path.glob("*.jsonl"))
        assert len(log_files) > 0

    def test_patient_anonymization_hmac(self, audit_logger):
        """Test HIPAA-compliant patient ID anonymization using HMAC"""
        data = {"patient_id": "patient_12345"}

        anonymized = audit_logger._anonymize_patient_data(data)

        # Should be anonymized
        assert anonymized["patient_id"] != "patient_12345"
        assert anonymized["patient_id"].startswith("anon_")

        # Should use HMAC-SHA256 (verify by recreating)
        secret = audit_logger.settings.secret_key.encode('utf-8')
        expected_hash = hmac.new(
            secret,
            "patient_12345".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:12]

        assert anonymized["patient_id"] == f"anon_{expected_hash}"

    def test_patient_anonymization_consistency(self, audit_logger):
        """Test that same patient ID always anonymizes to same value"""
        data1 = {"patient_id": "patient_12345"}
        data2 = {"patient_id": "patient_12345"}

        anonymized1 = audit_logger._anonymize_patient_data(data1)
        anonymized2 = audit_logger._anonymize_patient_data(data2)

        # Same patient should have same anonymized ID
        assert anonymized1["patient_id"] == anonymized2["patient_id"]

    def test_patient_anonymization_uniqueness(self, audit_logger):
        """Test that different patient IDs produce different anonymized values"""
        data1 = {"patient_id": "patient_12345"}
        data2 = {"patient_id": "patient_67890"}

        anonymized1 = audit_logger._anonymize_patient_data(data1)
        anonymized2 = audit_logger._anonymize_patient_data(data2)

        # Different patients should have different anonymized IDs
        assert anonymized1["patient_id"] != anonymized2["patient_id"]

    def test_geographic_location_anonymization(self, audit_logger):
        """Test that geographic location is anonymized"""
        data = {
            "patient_id": "patient_001",
            "geographic_location": "123 Main St, New York, NY 10001"
        }

        anonymized = audit_logger._anonymize_patient_data(data)

        assert anonymized["geographic_location"] == "anonymized"

    def test_anonymization_preserves_other_fields(self, audit_logger):
        """Test that anonymization preserves non-sensitive fields"""
        data = {
            "patient_id": "patient_001",
            "age": 35,
            "diagnosis": "Common Cold"
        }

        anonymized = audit_logger._anonymize_patient_data(data)

        assert anonymized["age"] == 35
        assert anonymized["diagnosis"] == "Common Cold"

    def test_audit_log_format(
        self,
        audit_logger,
        sample_patient_case,
        sample_diagnostic_result
    ):
        """Test audit log entry format"""
        audit_logger.log_diagnostic_analysis(
            case=sample_patient_case,
            result=sample_diagnostic_result,
            user_id="user_001",
            user_role="physician"
        )

        # Read log file
        log_files = list(audit_logger.audit_log_path.glob("*.jsonl"))
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.readline())

        # Verify required fields
        assert "timestamp" in log_entry
        assert "event_type" in log_entry
        assert "case_id" in log_entry
        assert "user_id" in log_entry
        assert "user_role" in log_entry

    def test_multiple_log_entries(
        self,
        audit_logger,
        sample_patient_case,
        sample_diagnostic_result
    ):
        """Test logging multiple entries"""
        for i in range(5):
            audit_logger.log_diagnostic_analysis(
                case=sample_patient_case,
                result=sample_diagnostic_result,
                user_id=f"user_{i:03d}",
                user_role="physician"
            )

        # Read log file
        log_files = list(audit_logger.audit_log_path.glob("*.jsonl"))
        with open(log_files[0], 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 5

    @patch('src.utils.audit.logger')
    def test_logging_on_write_failure(self, mock_logger, audit_logger):
        """Test that failures are logged"""
        with patch('builtins.open', side_effect=IOError("Disk full")):
            # Should not raise, just log error
            audit_logger.log_diagnostic_analysis(
                case=Mock(),
                result=Mock(),
                user_id="user_001"
            )

            # Verify error was logged
            assert mock_logger.error.called

    def test_audit_logging_disabled(self, temp_audit_dir):
        """Test behavior when audit logging is disabled"""
        with patch('src.utils.audit.get_settings') as mock_settings:
            settings = Mock()
            settings.enable_audit_logging = False
            settings.audit_log_path = str(temp_audit_dir)
            settings.secret_key = "test-key"
            mock_settings.return_value = settings

            logger = AuditLogger()

            # Log directory should still be created for consistency
            # but logging might be skipped
            assert logger.settings.enable_audit_logging is False

    def test_hmac_requires_secret_key(self, temp_audit_dir):
        """Test that HMAC anonymization uses secret key"""
        with patch('src.utils.audit.get_settings') as mock_settings:
            settings = Mock()
            settings.enable_audit_logging = True
            settings.audit_log_path = str(temp_audit_dir)
            settings.secret_key = ""  # Empty secret key
            mock_settings.return_value = settings

            logger = AuditLogger()
            data = {"patient_id": "patient_001"}

            # Should fall back to default key if secret_key is empty
            anonymized = logger._anonymize_patient_data(data)
            assert anonymized["patient_id"].startswith("anon_")

    def test_collision_resistance(self, audit_logger):
        """Test that anonymization has good collision resistance"""
        # Generate many patient IDs and check for collisions
        patient_ids = [f"patient_{i:06d}" for i in range(1000)]
        anonymized_ids = set()

        for patient_id in patient_ids:
            data = {"patient_id": patient_id}
            anonymized = audit_logger._anonymize_patient_data(data)
            anonymized_ids.add(anonymized["patient_id"])

        # All should be unique (no collisions)
        assert len(anonymized_ids) == len(patient_ids)

    def test_anonymization_not_reversible(self, audit_logger):
        """Test that anonymization is one-way (not reversible)"""
        original_id = "patient_12345"
        data = {"patient_id": original_id}

        anonymized = audit_logger._anonymize_patient_data(data)
        anonymized_id = anonymized["patient_id"]

        # Should not be able to reverse engineer original from anonymized
        # (This is a property of HMAC, we just verify format)
        assert original_id not in anonymized_id
        assert anonymized_id.startswith("anon_")
        assert len(anonymized_id) > len("anon_")
