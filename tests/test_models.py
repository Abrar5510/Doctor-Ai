"""
Tests for data models
"""

import pytest
from datetime import datetime, date
from src.models.schemas import (
    SymptomInput,
    Symptom,
    MedicalCondition,
    PatientCase,
    DiagnosticResult,
    DifferentialDiagnosis,
    Severity,
    Frequency,
    Sex,
    UrgencyLevel,
    ReviewTier,
)


def test_symptom_input_creation():
    """Test creating a symptom input"""
    symptom = SymptomInput(
        description="Persistent fatigue",
        severity=Severity.MODERATE,
        duration_days=30,
        frequency=Frequency.CONSTANT,
    )

    assert symptom.description == "Persistent fatigue"
    assert symptom.severity == Severity.MODERATE
    assert symptom.duration_days == 30


def test_patient_case_creation():
    """Test creating a patient case"""
    case = PatientCase(
        case_id="test_001",
        age=35,
        sex=Sex.FEMALE,
        chief_complaint="Fatigue and weight gain",
        symptoms=[
            SymptomInput(
                description="Fatigue",
                severity=Severity.MODERATE,
                duration_days=60
            )
        ]
    )

    assert case.case_id == "test_001"
    assert case.age == 35
    assert case.sex == Sex.FEMALE
    assert len(case.symptoms) == 1


def test_medical_condition_creation():
    """Test creating a medical condition"""
    condition = MedicalCondition(
        condition_id="cond_001",
        condition_name="Hypothyroidism",
        icd_codes=["E03.9"],
        prevalence=0.05,
        typical_symptoms=["fatigue", "weight gain", "cold intolerance"],
        urgency_level=UrgencyLevel.ROUTINE,
    )

    assert condition.condition_id == "cond_001"
    assert condition.condition_name == "Hypothyroidism"
    assert len(condition.typical_symptoms) == 3


def test_differential_diagnosis_creation():
    """Test creating a differential diagnosis"""
    diagnosis = DifferentialDiagnosis(
        condition_id="cond_001",
        condition_name="Hypothyroidism",
        icd_codes=["E03.9"],
        similarity_score=0.92,
        confidence_score=0.88,
        probability=0.75,
        matching_symptoms=["fatigue", "weight gain"],
        missing_symptoms=["constipation"],
        supporting_evidence=["High TSH correlation"],
        urgency_level=UrgencyLevel.ROUTINE,
    )

    assert diagnosis.confidence_score == 0.88
    assert diagnosis.similarity_score == 0.92
    assert len(diagnosis.matching_symptoms) == 2


def test_invalid_confidence_score():
    """Test that invalid confidence scores are rejected"""
    with pytest.raises(ValueError):
        DifferentialDiagnosis(
            condition_id="cond_001",
            condition_name="Test",
            similarity_score=1.5,  # Invalid: > 1.0
            confidence_score=0.9,
            probability=0.8,
            urgency_level=UrgencyLevel.ROUTINE,
        )
