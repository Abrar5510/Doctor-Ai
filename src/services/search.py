"""
Keyword-based search service for medical conditions (ML-free).

This replaces the ML-based embedding service for medical professional use.
Uses simple keyword matching suitable for proper medical terminology.
"""

from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from loguru import logger
import json

from ..models.database import MedicalCondition as DBMedicalCondition
from ..models.schemas import MedicalCondition


class SearchService:
    """
    Lightweight search service using keyword matching.
    Designed for medical professionals who use proper terminology.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def search_conditions(
        self,
        symptoms: List[str],
        db: Session,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Tuple[MedicalCondition, float]]:
        """
        Search for medical conditions using keyword matching.

        Args:
            symptoms: List of symptom keywords (e.g., ["fatigue", "weight gain"])
            db: Database session
            limit: Maximum number of results
            filters: Optional filters (e.g., {"is_rare_disease": True})

        Returns:
            List of (MedicalCondition, match_score) tuples
        """
        # Normalize symptoms to lowercase
        normalized_symptoms = [s.lower().strip() for s in symptoms]

        # Start with base query
        query = db.query(DBMedicalCondition)

        # Apply filters
        if filters:
            if "is_rare_disease" in filters:
                query = query.filter(DBMedicalCondition.is_rare_disease == filters["is_rare_disease"])
            if "urgency_level" in filters:
                query = query.filter(DBMedicalCondition.urgency_level == filters["urgency_level"])

        # Get all conditions (we'll score them in Python for simplicity)
        all_conditions = query.all()

        # Score each condition
        scored_conditions = []
        for db_condition in all_conditions:
            score = self._calculate_match_score(normalized_symptoms, db_condition)
            if score > 0:  # Only include conditions with some match
                # Convert to Pydantic model
                condition = self._db_to_pydantic(db_condition)
                scored_conditions.append((condition, score))

        # Sort by score (descending)
        scored_conditions.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        return scored_conditions[:limit]

    def _calculate_match_score(
        self,
        patient_symptoms: List[str],
        db_condition: DBMedicalCondition
    ) -> float:
        """
        Calculate match score between patient symptoms and condition.

        Uses weighted keyword matching:
        - Exact match in typical symptoms: 1.0 point
        - Partial match in typical symptoms: 0.5 points
        - Match in rare symptoms: 1.5 points (higher weight)
        - Red flag match: 2.0 points (highest weight)

        Args:
            patient_symptoms: Normalized patient symptom list
            db_condition: Database condition record

        Returns:
            Match score (higher is better)
        """
        score = 0.0

        # Parse JSON arrays
        typical_symptoms = json.loads(db_condition.typical_symptoms_json) if db_condition.typical_symptoms_json else []
        rare_symptoms = json.loads(db_condition.rare_symptoms_json) if db_condition.rare_symptoms_json else []
        red_flag_symptoms = json.loads(db_condition.red_flag_symptoms_json) if db_condition.red_flag_symptoms_json else []

        # Normalize condition symptoms
        typical_symptoms = [s.lower().strip() for s in typical_symptoms]
        rare_symptoms = [s.lower().strip() for s in rare_symptoms]
        red_flag_symptoms = [s.lower().strip() for s in red_flag_symptoms]

        # Check each patient symptom
        for patient_symptom in patient_symptoms:
            # Check red flags first (highest priority)
            for red_flag in red_flag_symptoms:
                if patient_symptom in red_flag or red_flag in patient_symptom:
                    score += 2.0
                    break

            # Check rare symptoms (high weight for diagnostic value)
            for rare_symptom in rare_symptoms:
                if patient_symptom == rare_symptom:  # Exact match
                    score += 1.5
                elif patient_symptom in rare_symptom or rare_symptom in patient_symptom:  # Partial
                    score += 1.0

            # Check typical symptoms
            for typical_symptom in typical_symptoms:
                if patient_symptom == typical_symptom:  # Exact match
                    score += 1.0
                elif patient_symptom in typical_symptom or typical_symptom in patient_symptom:  # Partial
                    score += 0.5

        # Adjust for prevalence (common things are common)
        # More common conditions get a slight boost
        if db_condition.prevalence:
            prevalence_boost = min(0.2, db_condition.prevalence / 1000000 * 2)
            score += score * prevalence_boost

        # Normalize score by number of typical symptoms (prevents conditions with
        # many symptoms from dominating)
        if typical_symptoms:
            score = score / (len(typical_symptoms) ** 0.5)

        return score

    def _db_to_pydantic(self, db_condition: DBMedicalCondition) -> MedicalCondition:
        """Convert database model to Pydantic schema."""
        from ..models.schemas import UrgencyLevel

        return MedicalCondition(
            condition_id=db_condition.condition_id,
            condition_name=db_condition.condition_name,
            icd_codes=json.loads(db_condition.icd_codes_json) if db_condition.icd_codes_json else [],
            snomed_codes=json.loads(db_condition.snomed_codes_json) if db_condition.snomed_codes_json else [],
            prevalence=db_condition.prevalence / 1000000 if db_condition.prevalence else 0.0,
            is_rare_disease=db_condition.is_rare_disease,
            typical_symptoms=json.loads(db_condition.typical_symptoms_json) if db_condition.typical_symptoms_json else [],
            rare_symptoms=json.loads(db_condition.rare_symptoms_json) if db_condition.rare_symptoms_json else [],
            red_flag_symptoms=json.loads(db_condition.red_flag_symptoms_json) if db_condition.red_flag_symptoms_json else [],
            temporal_pattern=db_condition.temporal_pattern,
            diagnostic_criteria=json.loads(db_condition.diagnostic_criteria_json) if db_condition.diagnostic_criteria_json else [],
            differential_diagnoses=json.loads(db_condition.differential_diagnoses_json) if db_condition.differential_diagnoses_json else [],
            urgency_level=UrgencyLevel(db_condition.urgency_level),
            recommended_tests=json.loads(db_condition.recommended_tests_json) if db_condition.recommended_tests_json else [],
            specialist_referral=db_condition.specialist_referral,
            distinguishing_features=json.loads(db_condition.distinguishing_features_json) if db_condition.distinguishing_features_json else [],
            evidence_sources=json.loads(db_condition.evidence_sources_json) if db_condition.evidence_sources_json else [],
            typical_age_range=db_condition.typical_age_range,
            sex_predilection=db_condition.sex_predilection,
        )

    def get_condition_by_id(self, condition_id: str, db: Session) -> Optional[MedicalCondition]:
        """
        Retrieve a specific condition by ID.

        Args:
            condition_id: Condition identifier
            db: Database session

        Returns:
            MedicalCondition if found, None otherwise
        """
        db_condition = db.query(DBMedicalCondition).filter(
            DBMedicalCondition.condition_id == condition_id
        ).first()

        if db_condition:
            return self._db_to_pydantic(db_condition)
        return None

    def get_stats(self, db: Session) -> Dict:
        """
        Get statistics about the medical conditions database.

        Returns:
            Dictionary with statistics
        """
        total_conditions = db.query(DBMedicalCondition).count()
        rare_diseases = db.query(DBMedicalCondition).filter(
            DBMedicalCondition.is_rare_disease == True
        ).count()

        return {
            "total_conditions": total_conditions,
            "rare_diseases": rare_diseases,
            "common_diseases": total_conditions - rare_diseases,
        }
