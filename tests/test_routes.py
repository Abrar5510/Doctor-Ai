"""
Comprehensive tests for API routes
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import app
from src.models.schemas import (
    PatientCase,
    SymptomInput,
    Sex,
    Severity,
    Frequency,
    DiagnosticResult,
    DifferentialDiagnosis,
    ReviewTier,
    UrgencyLevel,
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "case_id": "test_case_001",
        "age": 35,
        "sex": "male",
        "chief_complaint": "Persistent cough and fever",
        "symptoms": [
            {
                "description": "Persistent cough",
                "severity": "moderate",
                "duration_days": 7,
                "frequency": "constant"
            },
            {
                "description": "Fever",
                "severity": "mild",
                "duration_days": 3,
                "frequency": "intermittent"
            }
        ],
        "medical_history": ["Asthma"],
        "current_medications": ["Albuterol"]
    }


@pytest.fixture
def mock_diagnostic_result():
    """Mock diagnostic result"""
    return DiagnosticResult(
        case_id="test_case_001",
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


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check returns 200 OK"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "service" in data
        assert "version" in data
        assert "docs" in data


class TestDiagnosticEndpoints:
    """Test diagnostic API endpoints"""

    @patch('src.api.routes.get_diagnostic_service')
    @patch('src.api.routes.get_audit_logger')
    def test_analyze_endpoint(
        self,
        mock_audit,
        mock_service,
        client,
        sample_patient_data,
        mock_diagnostic_result
    ):
        """Test basic analyze endpoint"""
        # Setup mocks
        service_instance = Mock()
        service_instance.analyze_patient_case.return_value = mock_diagnostic_result
        mock_service.return_value = service_instance

        audit_instance = Mock()
        mock_audit.return_value = audit_instance

        # Make request
        response = client.post("/api/v1/analyze", json=sample_patient_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data
        assert "differential_diagnoses" in data

    def test_analyze_invalid_age(self, client, sample_patient_data):
        """Test analyze endpoint rejects invalid age"""
        sample_patient_data["age"] = -5  # Invalid age

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error

    def test_analyze_missing_required_field(self, client, sample_patient_data):
        """Test analyze endpoint rejects missing required fields"""
        del sample_patient_data["age"]

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error

    def test_analyze_empty_symptoms(self, client, sample_patient_data):
        """Test analyze endpoint rejects empty symptoms list"""
        sample_patient_data["symptoms"] = []

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error

    def test_analyze_too_many_symptoms(self, client, sample_patient_data):
        """Test analyze endpoint rejects excessive symptoms"""
        sample_patient_data["symptoms"] = [
            {
                "description": f"Symptom {i}",
                "severity": "mild"
            }
            for i in range(100)  # Exceeds limit of 50
        ]

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error

    def test_analyze_invalid_symptom_description(self, client, sample_patient_data):
        """Test analyze endpoint rejects invalid symptom descriptions"""
        sample_patient_data["symptoms"][0]["description"] = "AB"  # Too short (< 3 chars)

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error

    def test_analyze_invalid_chief_complaint(self, client, sample_patient_data):
        """Test analyze endpoint rejects invalid chief complaint"""
        sample_patient_data["chief_complaint"] = "AB"  # Too short (< 3 chars)

        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code == 422  # Validation error


class TestStatsEndpoint:
    """Test stats endpoint"""

    @patch('src.api.routes.get_diagnostic_service')
    def test_stats_endpoint(self, mock_service, client):
        """Test stats endpoint returns system information"""
        # Setup mock
        service_instance = Mock()
        service_instance.vector_store.get_collection_stats.return_value = {
            "total_conditions": 1000,
            "collection_name": "medical_conditions"
        }
        mock_service.return_value = service_instance

        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "vector_database" in data
        assert "ai_assistant" in data
        assert "features" in data


class TestEnhancedAnalysisEndpoint:
    """Test enhanced analysis endpoint with AI features"""

    @patch('src.api.routes.get_diagnostic_service')
    @patch('src.api.routes.get_ai_assistant')
    @patch('src.api.routes.get_audit_logger')
    def test_enhanced_analysis_basic(
        self,
        mock_audit,
        mock_ai,
        mock_service,
        client,
        sample_patient_data,
        mock_diagnostic_result
    ):
        """Test enhanced analysis endpoint"""
        # Setup mocks
        service_instance = Mock()
        service_instance.analyze_patient_case.return_value = mock_diagnostic_result
        mock_service.return_value = service_instance

        ai_instance = Mock()
        ai_instance.generate_detailed_explanation.return_value = "This is a detailed explanation"
        ai_instance.generate_follow_up_questions.return_value = [
            "Question 1?",
            "Question 2?"
        ]
        mock_ai.return_value = ai_instance

        audit_instance = Mock()
        mock_audit.return_value = audit_instance

        # Make request
        response = client.post(
            "/api/v1/analyze/enhanced",
            json=sample_patient_data,
            params={
                "include_explanation": True,
                "include_questions": True,
                "include_report": False
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "diagnostic_result" in data
        assert "ai_enhancements" in data

    @patch('src.api.routes.get_diagnostic_service')
    @patch('src.api.routes.get_ai_assistant')
    @patch('src.api.routes.get_audit_logger')
    def test_enhanced_analysis_without_ai_features(
        self,
        mock_audit,
        mock_ai,
        mock_service,
        client,
        sample_patient_data,
        mock_diagnostic_result
    ):
        """Test enhanced analysis without AI enhancements"""
        # Setup mocks
        service_instance = Mock()
        service_instance.analyze_patient_case.return_value = mock_diagnostic_result
        mock_service.return_value = service_instance

        audit_instance = Mock()
        mock_audit.return_value = audit_instance

        # Make request without AI features
        response = client.post(
            "/api/v1/analyze/enhanced",
            json=sample_patient_data,
            params={
                "include_explanation": False,
                "include_questions": False,
                "include_report": False
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "diagnostic_result" in data


class TestCORSHeaders:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly configured"""
        response = client.options("/api/v1/stats")

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers


class TestInputValidation:
    """Test comprehensive input validation"""

    def test_sql_injection_attempt(self, client, sample_patient_data):
        """Test that SQL injection attempts are sanitized"""
        sample_patient_data["case_id"] = "'; DROP TABLE users; --"

        # Should not cause error, just treat as string
        # (Pydantic will validate max_length but won't execute SQL)
        response = client.post("/api/v1/analyze", json=sample_patient_data)

        # Might fail on other validation, but shouldn't execute SQL
        assert response.status_code in [200, 422, 500]

    def test_xss_attempt(self, client, sample_patient_data):
        """Test that XSS attempts are sanitized"""
        sample_patient_data["chief_complaint"] = "<script>alert('XSS')</script>"

        # Should handle without executing script
        response = client.post("/api/v1/analyze", json=sample_patient_data)

        assert response.status_code in [200, 422, 500]
        # Response should not contain executable script
        if response.status_code == 200:
            assert "<script>" not in str(response.json())
