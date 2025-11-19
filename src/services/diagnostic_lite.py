"""
Lightweight diagnostic reasoning service (ML-free).

This version uses keyword matching instead of ML embeddings.
Designed for medical professionals who use proper terminology.
"""

from typing import List, Dict, Any, Tuple
import time
from uuid import uuid4
from sqlalchemy.orm import Session
from loguru import logger

from ..models.schemas import (
    PatientCase,
    MedicalCondition,
    DiagnosticResult,
    DifferentialDiagnosis,
    ReviewTier,
    UrgencyLevel,
    Severity,
)
from ..config import get_settings
from .search import SearchService


class DiagnosticServiceLite:
    """
    Lightweight diagnostic engine using keyword matching.
    No ML dependencies required.
    """

    def __init__(self):
        self.settings = get_settings()
        self.search_service = SearchService()

        # Red flag symptoms requiring immediate attention
        self.red_flag_keywords = {
            "chest pain", "severe headache", "difficulty breathing", "shortness of breath",
            "loss of consciousness", "seizure", "stroke", "paralysis", "severe bleeding",
            "severe abdominal pain", "sudden vision loss", "confusion", "altered mental status",
            "severe trauma", "choking", "anaphylaxis", "suicide", "severe burn"
        }

    def analyze_patient_case(
        self,
        patient_case: PatientCase,
        db: Session
    ) -> DiagnosticResult:
        """
        Main diagnostic analysis pipeline.

        Args:
            patient_case: Complete patient case information
            db: Database session

        Returns:
            DiagnosticResult with differential diagnoses and recommendations
        """
        start_time = time.time()

        logger.info(f"Analyzing case: {patient_case.case_id}")

        # Step 1: Check for red flags
        red_flags = self._detect_red_flags(patient_case)
        requires_emergency = len(red_flags) > 0

        if requires_emergency:
            logger.warning(f"Red flags detected: {red_flags}")

        # Step 2: Extract symptoms
        symptom_keywords = self._extract_symptom_keywords(patient_case)

        # Step 3: Search for common conditions
        common_candidates = self.search_service.search_conditions(
            symptoms=symptom_keywords,
            db=db,
            limit=self.settings.top_k_candidates,
            filters={"is_rare_disease": False}
        )

        # Step 4: Search for rare diseases if enabled
        rare_candidates = []
        if self.settings.enable_rare_disease_detection:
            rare_candidates = self.search_service.search_conditions(
                symptoms=symptom_keywords,
                db=db,
                limit=20,
                filters={"is_rare_disease": True}
            )

        # Step 5: Combine and create differential diagnoses
        all_candidates = common_candidates + rare_candidates
        ranked_diagnoses = self._create_differential_diagnoses(
            all_candidates,
            patient_case,
            symptom_keywords
        )

        # Step 6: Determine review tier
        overall_confidence = ranked_diagnoses[0].confidence_score if ranked_diagnoses else 0.0
        review_tier = self._determine_review_tier(overall_confidence, requires_emergency)

        # Step 7: Generate recommendations
        recommended_specialists, recommended_tests = self._generate_recommendations(
            ranked_diagnoses
        )

        # Step 8: Build reasoning explanation
        reasoning_summary = self._generate_reasoning_summary(
            patient_case,
            ranked_diagnoses,
            symptom_keywords
        )

        # Step 9: Calculate feature importance
        feature_importance = self._calculate_feature_importance(
            symptom_keywords,
            ranked_diagnoses
        )

        # Separate rare diseases
        rare_diseases = [d for d in ranked_diagnoses if d.condition_id in [
            rc[0].condition_id for rc in rare_candidates
        ]]

        # Get primary diagnosis if confidence is high
        primary_diagnosis = None
        if ranked_diagnoses and overall_confidence >= self.settings.tier1_confidence_threshold:
            primary_diagnosis = ranked_diagnoses[0]

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Build result
        result = DiagnosticResult(
            result_id=f"result_{uuid4().hex[:12]}",
            case_id=patient_case.case_id,
            differential_diagnoses=ranked_diagnoses[:self.settings.final_results_limit],
            primary_diagnosis=primary_diagnosis,
            review_tier=review_tier,
            overall_confidence=overall_confidence,
            red_flags_detected=red_flags,
            requires_emergency_care=requires_emergency,
            rare_diseases_considered=rare_diseases[:5],
            recommended_specialists=recommended_specialists,
            recommended_tests=recommended_tests,
            reasoning_summary=reasoning_summary,
            feature_importance=feature_importance,
            processing_time_ms=processing_time,
        )

        logger.info(
            f"Analysis complete: {len(ranked_diagnoses)} diagnoses, "
            f"confidence: {overall_confidence:.2f}, tier: {review_tier}, "
            f"time: {processing_time:.2f}ms"
        )

        return result

    def _detect_red_flags(self, patient_case: PatientCase) -> List[str]:
        """Detect life-threatening symptoms requiring immediate attention."""
        red_flags = []

        # Check chief complaint
        chief_complaint_lower = patient_case.chief_complaint.lower()
        for red_flag in self.red_flag_keywords:
            if red_flag in chief_complaint_lower:
                red_flags.append(red_flag)

        # Check individual symptoms
        for symptom in patient_case.symptoms:
            symptom_desc_lower = symptom.description.lower()
            for red_flag in self.red_flag_keywords:
                if red_flag in symptom_desc_lower:
                    if red_flag not in red_flags:
                        red_flags.append(red_flag)

            # Check severity
            if symptom.severity == Severity.CRITICAL:
                red_flags.append(f"Critical severity: {symptom.description}")

        return red_flags

    def _extract_symptom_keywords(self, patient_case: PatientCase) -> List[str]:
        """Extract symptom keywords from patient case."""
        keywords = []

        # Add chief complaint
        keywords.append(patient_case.chief_complaint.lower().strip())

        # Add individual symptoms
        for symptom in patient_case.symptoms:
            keywords.append(symptom.description.lower().strip())

        return keywords

    def _create_differential_diagnoses(
        self,
        candidates: List[Tuple[MedicalCondition, float]],
        patient_case: PatientCase,
        symptom_keywords: List[str]
    ) -> List[DifferentialDiagnosis]:
        """Create differential diagnosis objects from search results."""
        diagnoses = []

        for condition, match_score in candidates:
            # Convert match score to confidence (0-1 range)
            confidence_score = min(1.0, match_score / 10.0)  # Normalize

            # Calculate probability (simplified Bayesian)
            probability = self._calculate_probability(condition, confidence_score)

            # Identify matching and missing symptoms
            matching_symptoms, missing_symptoms = self._compare_symptoms(
                symptom_keywords,
                condition.typical_symptoms,
                condition.rare_symptoms
            )

            # Generate supporting evidence
            supporting_evidence = [
                f"Keyword match score: {match_score:.2f}",
                f"Prevalence: {condition.prevalence:.6f}"
            ]
            if condition.evidence_sources:
                supporting_evidence.extend(condition.evidence_sources[:2])

            # Build differential diagnosis
            diagnosis = DifferentialDiagnosis(
                condition_id=condition.condition_id,
                condition_name=condition.condition_name,
                icd_codes=condition.icd_codes,
                similarity_score=confidence_score,  # Using confidence as similarity
                confidence_score=confidence_score,
                probability=probability,
                matching_symptoms=matching_symptoms,
                missing_symptoms=missing_symptoms,
                supporting_evidence=supporting_evidence,
                diagnostic_criteria_met=condition.diagnostic_criteria[:3],
                recommended_next_steps=condition.recommended_tests[:3],
                urgency_level=condition.urgency_level,
                distinguishing_features=condition.distinguishing_features
            )

            diagnoses.append(diagnosis)

        # Sort by confidence score
        diagnoses.sort(key=lambda d: d.confidence_score, reverse=True)

        return diagnoses

    def _calculate_probability(
        self,
        condition: MedicalCondition,
        confidence_score: float
    ) -> float:
        """Calculate Bayesian probability for a diagnosis."""
        prior = condition.prevalence
        likelihood = confidence_score

        # Simple Bayesian-inspired calculation
        probability = (prior * likelihood) / (prior * likelihood + (1 - prior) * (1 - likelihood))

        return probability

    def _compare_symptoms(
        self,
        patient_symptoms: List[str],
        typical_symptoms: List[str],
        rare_symptoms: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Compare patient symptoms with condition symptoms."""
        all_condition_symptoms = typical_symptoms + rare_symptoms

        # Simple substring matching
        matching = []
        for cond_symptom in all_condition_symptoms:
            for patient_symptom in patient_symptoms:
                if cond_symptom.lower() in patient_symptom or \
                   patient_symptom in cond_symptom.lower():
                    if cond_symptom not in matching:
                        matching.append(cond_symptom)
                    break

        # Missing symptoms
        missing = [s for s in typical_symptoms if s not in matching]

        return matching[:5], missing[:3]

    def _determine_review_tier(
        self,
        confidence: float,
        requires_emergency: bool
    ) -> ReviewTier:
        """Determine which review tier this case should go to."""
        if requires_emergency:
            return ReviewTier.TIER1_AUTOMATED

        if confidence >= self.settings.tier1_confidence_threshold:
            return ReviewTier.TIER1_AUTOMATED
        elif confidence >= self.settings.tier2_confidence_threshold:
            return ReviewTier.TIER2_PRIMARY_CARE
        elif confidence >= self.settings.tier3_confidence_threshold:
            return ReviewTier.TIER3_SPECIALIST
        else:
            return ReviewTier.TIER4_MULTIDISCIPLINARY

    def _generate_recommendations(
        self,
        diagnoses: List[DifferentialDiagnosis]
    ) -> Tuple[List[str], List[str]]:
        """Generate specialist and test recommendations."""
        specialists = set()
        tests = set()

        for diagnosis in diagnoses[:3]:  # Top 3 diagnoses
            # Add recommended tests
            tests.update(diagnosis.recommended_next_steps)

        return list(specialists), list(tests)[:5]

    def _generate_reasoning_summary(
        self,
        patient_case: PatientCase,
        diagnoses: List[DifferentialDiagnosis],
        symptoms: List[str]
    ) -> str:
        """Generate human-readable explanation of diagnostic reasoning."""
        summary_parts = []

        summary_parts.append(
            f"Patient presents with {patient_case.chief_complaint}."
        )

        summary_parts.append(
            f"Analysis of {len(symptoms)} reported symptoms reveals:"
        )

        if diagnoses:
            top = diagnoses[0]
            summary_parts.append(
                f"Most likely diagnosis is {top.condition_name} "
                f"with {top.confidence_score:.1%} confidence, "
                f"based on keyword matching of reported symptoms."
            )

            if len(diagnoses) > 1:
                other_names = [d.condition_name for d in diagnoses[1:4]]
                summary_parts.append(
                    f"Differential diagnoses to consider: {', '.join(other_names)}."
                )
        else:
            summary_parts.append(
                "Unable to identify a high-confidence diagnosis. "
                "Recommend specialist consultation."
            )

        return " ".join(summary_parts)

    def _calculate_feature_importance(
        self,
        symptoms: List[str],
        diagnoses: List[DifferentialDiagnosis]
    ) -> Dict[str, float]:
        """Calculate which symptoms were most important for diagnosis."""
        importance = {}

        for symptom in symptoms:
            importance[symptom[:50]] = 1.0 / len(symptoms)

        return importance
