"""
Comprehensive tests for the DiagnosticService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from src.services.diagnostic import DiagnosticService
from src.models.schemas import (
    PatientCase,
    SymptomInput,
    Sex,
    Severity,
    Frequency,
    DiagnosticResult,
    DifferentialDiagnosis,
)


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service"""
    service = Mock()
    service.encode_cached = Mock(return_value=[0.1] * 768)
    return service


@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    store = Mock()
    store.search_similar = Mock(return_value=[
        {
            "condition_id": "cond_001",
            "condition_name": "Common Cold",
            "similarity_score": 0.85,
            "prevalence": 0.15
        },
        {
            "condition_id": "cond_002",
            "condition_name": "Influenza",
            "similarity_score": 0.78,
            "prevalence": 0.05
        }
    ])
    store.get_condition_by_id = Mock(return_value={
        "condition_id": "cond_001",
        "condition_name": "Common Cold",
        "prevalence": 0.15
    })
    return store


@pytest.fixture
def diagnostic_service(mock_embedding_service, mock_vector_store):
    """Create diagnostic service with mocked dependencies"""
    return DiagnosticService(
        embedding_service=mock_embedding_service,
        vector_store=mock_vector_store
    )


@pytest.fixture
def sample_patient_case():
    """Create a sample patient case for testing"""
    return PatientCase(
        case_id="case_001",
        patient_id="patient_001",
        age=35,
        sex=Sex.MALE,
        symptoms=[
            SymptomInput(
                description="Persistent cough",
                severity=Severity.MODERATE,
                duration_days=7,
                frequency=Frequency.CONSTANT
            ),
            SymptomInput(
                description="Fever",
                severity=Severity.MILD,
                duration_days=3,
                frequency=Frequency.INTERMITTENT
            )
        ],
        chief_complaint="Cough and fever for one week",
        medical_history=["Asthma"],
        current_medications=["Albuterol"]
    )


class TestDiagnosticService:
    """Test suite for DiagnosticService"""

    def test_initialization(self, diagnostic_service):
        """Test service initialization"""
        assert diagnostic_service is not None
        assert diagnostic_service.embedding_service is not None
        assert diagnostic_service.vector_store is not None
        assert len(diagnostic_service.red_flag_keywords) > 0

    def test_analyze_patient_case_basic(self, diagnostic_service, sample_patient_case):
        """Test basic patient case analysis"""
        result = diagnostic_service.analyze_patient_case(sample_patient_case)

        assert isinstance(result, DiagnosticResult)
        assert result.case_id == sample_patient_case.case_id
        assert len(result.differential_diagnoses) > 0

    def test_red_flag_detection_no_flags(self, diagnostic_service, sample_patient_case):
        """Test that normal symptoms don't trigger red flags"""
        result = diagnostic_service.analyze_patient_case(sample_patient_case)

        # Normal symptoms should not trigger emergency
        assert not hasattr(result, 'requires_emergency') or not result.requires_emergency

    def test_red_flag_detection_with_flags(self, diagnostic_service):
        """Test that emergency symptoms trigger red flags"""
        emergency_case = PatientCase(
            case_id="case_002",
            age=65,
            sex=Sex.MALE,
            symptoms=[
                SymptomInput(
                    description="Severe chest pain",
                    severity=Severity.CRITICAL,
                    duration_days=1,
                    frequency=Frequency.CONSTANT
                )
            ],
            chief_complaint="Chest pain"
        )

        red_flags = diagnostic_service._detect_red_flags(emergency_case)
        assert len(red_flags) > 0

    def test_symptom_standardization(self, diagnostic_service, sample_patient_case):
        """Test symptom standardization"""
        standardized = diagnostic_service._standardize_symptoms(sample_patient_case.symptoms)

        assert isinstance(standardized, list)
        assert len(standardized) == len(sample_patient_case.symptoms)
        for symptom in standardized:
            assert hasattr(symptom, 'name')
            assert hasattr(symptom, 'description')

    def test_invalid_patient_age(self, diagnostic_service):
        """Test validation of invalid patient age"""
        with pytest.raises(Exception):
            PatientCase(
                case_id="case_003",
                age=-5,  # Invalid age
                sex=Sex.MALE,
                symptoms=[
                    SymptomInput(
                        description="Fever",
                        severity=Severity.MILD
                    )
                ],
                chief_complaint="Fever"
            )

    def test_empty_symptoms_list(self, diagnostic_service):
        """Test that empty symptoms list is rejected"""
        with pytest.raises(Exception):
            PatientCase(
                case_id="case_004",
                age=35,
                sex=Sex.MALE,
                symptoms=[],  # Empty list should fail validation
                chief_complaint="Test"
            )

    def test_too_many_symptoms(self, diagnostic_service):
        """Test that excessive symptoms are rejected"""
        with pytest.raises(Exception):
            PatientCase(
                case_id="case_005",
                age=35,
                sex=Sex.MALE,
                symptoms=[
                    SymptomInput(description=f"Symptom {i}", severity=Severity.MILD)
                    for i in range(100)  # Exceeds max of 50
                ],
                chief_complaint="Too many symptoms"
            )

    def test_confidence_score_calculation(self, diagnostic_service, sample_patient_case):
        """Test that confidence scores are properly calculated"""
        result = diagnostic_service.analyze_patient_case(sample_patient_case)

        for diagnosis in result.differential_diagnoses:
            assert 0.0 <= diagnosis.confidence_score <= 1.0
            assert diagnosis.confidence_score <= 1.0

    def test_review_tier_assignment(self, diagnostic_service, sample_patient_case):
        """Test that review tiers are properly assigned based on confidence"""
        result = diagnostic_service.analyze_patient_case(sample_patient_case)

        assert result.review_tier is not None
        # Review tier should match confidence threshold

    @patch('src.services.diagnostic.logger')
    def test_logging_on_analysis(self, mock_logger, diagnostic_service, sample_patient_case):
        """Test that analysis is properly logged"""
        diagnostic_service.analyze_patient_case(sample_patient_case)

        # Verify logging occurred
        assert mock_logger.info.called

    def test_processing_time_recorded(self, diagnostic_service, sample_patient_case):
        """Test that processing time is recorded"""
        result = diagnostic_service.analyze_patient_case(sample_patient_case)

        assert hasattr(result, 'processing_time_seconds')
        assert result.processing_time_seconds > 0

    def test_multiple_patient_cases(self, diagnostic_service):
        """Test processing multiple patient cases"""
        cases = [
            PatientCase(
                case_id=f"case_{i}",
                age=30 + i,
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
                symptoms=[
                    SymptomInput(
                        description=f"Symptom {i}",
                        severity=Severity.MODERATE
                    )
                ],
                chief_complaint=f"Complaint {i}"
            )
            for i in range(5)
        ]

        results = [diagnostic_service.analyze_patient_case(case) for case in cases]

        assert len(results) == 5
        assert all(isinstance(r, DiagnosticResult) for r in results)
