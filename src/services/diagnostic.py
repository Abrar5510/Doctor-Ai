"""
Diagnostic reasoning service - core AI diagnostic engine
"""

from typing import List, Dict, Any, Optional, Tuple
import time
from uuid import uuid4
from datetime import datetime
import numpy as np
from loguru import logger

from ..models.schemas import (
    PatientCase,
    SymptomInput,
    Symptom,
    MedicalCondition,
    DiagnosticResult,
    DifferentialDiagnosis,
    ReviewTier,
    UrgencyLevel,
    Severity,
)
from ..config import get_settings
from .embedding import EmbeddingService
from .vector_store import VectorStoreService


class DiagnosticService:
    """
    Core diagnostic reasoning engine that analyzes patient symptoms
    and generates differential diagnoses
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None
    ):
        self.settings = get_settings()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()

        # Red flag symptoms requiring immediate attention
        self.red_flag_keywords = {
            "chest pain", "severe headache", "difficulty breathing", "shortness of breath",
            "loss of consciousness", "seizure", "stroke", "paralysis", "severe bleeding",
            "severe abdominal pain", "sudden vision loss", "confusion", "altered mental status",
            "severe trauma", "choking", "anaphylaxis", "suicide", "severe burn"
        }

    def initialize(self):
        """Initialize all services"""
        logger.info("Initializing diagnostic service")
        self.embedding_service.initialize()
        self.vector_store.initialize()
        logger.info("Diagnostic service initialized")

    def analyze_patient_case(
        self,
        patient_case: PatientCase
    ) -> DiagnosticResult:
        """
        Main diagnostic analysis pipeline

        Args:
            patient_case: Complete patient case information

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

        # Step 2: Extract and standardize symptoms
        standardized_symptoms = self._extract_symptoms(patient_case)

        # Step 3: Generate symptom constellation embedding
        symptom_weights = self._calculate_symptom_weights(standardized_symptoms)
        query_embedding = self._generate_query_embedding(
            standardized_symptoms,
            symptom_weights
        )

        # Step 4: Multi-stage search
        # Stage 1: Broad search for common conditions
        common_candidates = self._search_common_conditions(
            query_embedding,
            patient_case
        )

        # Stage 2: Rare disease search if enabled
        rare_candidates = []
        if self.settings.enable_rare_disease_detection:
            rare_candidates = self._search_rare_diseases(
                query_embedding,
                patient_case
            )

        # Step 5: Combine and rank all candidates
        all_candidates = common_candidates + rare_candidates
        ranked_diagnoses = self._rank_and_score_diagnoses(
            all_candidates,
            patient_case,
            standardized_symptoms,
            symptom_weights
        )

        # Step 6: Determine review tier based on confidence
        overall_confidence = ranked_diagnoses[0].confidence_score if ranked_diagnoses else 0.0
        review_tier = self._determine_review_tier(overall_confidence, requires_emergency)

        # Step 7: Generate clinical recommendations
        recommended_specialists, recommended_tests = self._generate_recommendations(
            ranked_diagnoses
        )

        # Step 8: Build reasoning explanation
        reasoning_summary = self._generate_reasoning_summary(
            patient_case,
            ranked_diagnoses,
            standardized_symptoms
        )

        # Step 9: Calculate feature importance
        feature_importance = self._calculate_feature_importance(
            standardized_symptoms,
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
            rare_diseases_considered=rare_diseases[:5],  # Top 5 rare diseases
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
        """Detect life-threatening symptoms requiring immediate attention"""
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

    def _extract_symptoms(self, patient_case: PatientCase) -> List[str]:
        """Extract and standardize symptom descriptions"""
        symptoms = []

        # Add chief complaint
        symptoms.append(patient_case.chief_complaint)

        # Add individual symptoms
        for symptom in patient_case.symptoms:
            # Build detailed description
            desc = symptom.description

            if symptom.severity:
                desc += f" ({symptom.severity.value} severity)"

            if symptom.duration_days:
                desc += f" for {symptom.duration_days} days"

            if symptom.location:
                desc += f" in {symptom.location}"

            symptoms.append(desc)

        return symptoms

    def _calculate_symptom_weights(self, symptoms: List[str]) -> List[float]:
        """
        Calculate importance weights for symptoms
        (Rare symptoms should have higher weight)
        """
        # For MVP, use equal weights
        # In production, this would use symptom rarity from database
        return [1.0] * len(symptoms)

    def _generate_query_embedding(
        self,
        symptoms: List[str],
        weights: List[float]
    ) -> np.ndarray:
        """Generate weighted embedding for symptom constellation"""
        return self.embedding_service.encode_symptom_constellation(
            symptoms,
            weights
        )

    def _search_common_conditions(
        self,
        query_embedding: np.ndarray,
        patient_case: PatientCase
    ) -> List[Tuple[MedicalCondition, float]]:
        """Search for common medical conditions"""
        # Build filters based on patient demographics
        filters = self._build_demographic_filters(patient_case)

        # Search for common conditions (prevalence > 0.001)
        filters["min_prevalence"] = 0.001

        results = self.vector_store.search(
            query_vector=query_embedding,
            limit=self.settings.top_k_candidates,
            score_threshold=0.5,  # Minimum similarity
            filters=filters
        )

        logger.debug(f"Found {len(results)} common condition candidates")
        return results

    def _search_rare_diseases(
        self,
        query_embedding: np.ndarray,
        patient_case: PatientCase
    ) -> List[Tuple[MedicalCondition, float]]:
        """Search for rare diseases"""
        results = self.vector_store.search_rare_diseases(
            query_vector=query_embedding,
            limit=20,  # More candidates for rare diseases
            score_threshold=0.6  # Higher threshold for rare diseases
        )

        logger.debug(f"Found {len(results)} rare disease candidates")
        return results

    def _build_demographic_filters(self, patient_case: PatientCase) -> Dict[str, Any]:
        """Build search filters based on patient demographics"""
        filters = {}

        # Add age and sex filtering logic here in production
        # For MVP, return empty filters

        return filters

    def _rank_and_score_diagnoses(
        self,
        candidates: List[Tuple[MedicalCondition, float]],
        patient_case: PatientCase,
        symptoms: List[str],
        symptom_weights: List[float]
    ) -> List[DifferentialDiagnosis]:
        """
        Rank and score all candidate diagnoses using multiple factors
        """
        diagnoses = []

        for condition, similarity_score in candidates:
            # Calculate confidence score (combining multiple factors)
            confidence_score = self._calculate_confidence(
                condition,
                similarity_score,
                patient_case
            )

            # Calculate Bayesian probability
            probability = self._calculate_probability(
                condition,
                similarity_score,
                confidence_score
            )

            # Identify matching and missing symptoms
            matching_symptoms, missing_symptoms = self._compare_symptoms(
                symptoms,
                condition.typical_symptoms,
                condition.rare_symptoms
            )

            # Generate supporting evidence
            supporting_evidence = self._generate_evidence(condition, similarity_score)

            # Build differential diagnosis
            diagnosis = DifferentialDiagnosis(
                condition_id=condition.condition_id,
                condition_name=condition.condition_name,
                icd_codes=condition.icd_codes,
                similarity_score=similarity_score,
                confidence_score=confidence_score,
                probability=probability,
                matching_symptoms=matching_symptoms,
                missing_symptoms=missing_symptoms,
                supporting_evidence=supporting_evidence,
                diagnostic_criteria_met=condition.diagnostic_criteria[:3],  # Top 3
                recommended_next_steps=condition.recommended_tests[:3],  # Top 3
                urgency_level=condition.urgency_level,
                distinguishing_features=condition.distinguishing_features
            )

            diagnoses.append(diagnosis)

        # Sort by confidence score
        diagnoses.sort(key=lambda d: d.confidence_score, reverse=True)

        return diagnoses

    def _calculate_confidence(
        self,
        condition: MedicalCondition,
        similarity_score: float,
        patient_case: PatientCase
    ) -> float:
        """
        Calculate overall confidence score for a diagnosis
        """
        # Base confidence from similarity
        confidence = similarity_score

        # Adjust for prevalence (common things are common)
        # More common = slight confidence boost
        prevalence_factor = min(1.0, condition.prevalence * 10)
        confidence = confidence * (0.9 + 0.1 * prevalence_factor)

        # Rare diseases need higher similarity to be confident
        if condition.is_rare_disease:
            confidence *= 0.9

        # Cap confidence
        confidence = min(1.0, confidence)

        return confidence

    def _calculate_probability(
        self,
        condition: MedicalCondition,
        similarity_score: float,
        confidence_score: float
    ) -> float:
        """
        Calculate Bayesian probability for a diagnosis
        (Simplified version for MVP)
        """
        # In production, this would use proper Bayesian inference
        # For MVP, use a weighted combination
        prior = condition.prevalence
        likelihood = similarity_score

        # Simple Bayesian-inspired calculation
        probability = (prior * likelihood) / (prior * likelihood + (1 - prior) * (1 - likelihood))

        return probability

    def _compare_symptoms(
        self,
        patient_symptoms: List[str],
        typical_symptoms: List[str],
        rare_symptoms: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Compare patient symptoms with condition symptoms"""
        all_condition_symptoms = typical_symptoms + rare_symptoms

        # For MVP, use simple substring matching
        # In production, use semantic similarity
        matching = []
        for cond_symptom in all_condition_symptoms:
            for patient_symptom in patient_symptoms:
                if cond_symptom.lower() in patient_symptom.lower() or \
                   patient_symptom.lower() in cond_symptom.lower():
                    if cond_symptom not in matching:
                        matching.append(cond_symptom)
                    break

        # Missing symptoms
        missing = [s for s in all_condition_symptoms if s not in matching]

        return matching[:5], missing[:3]  # Limit for readability

    def _generate_evidence(
        self,
        condition: MedicalCondition,
        similarity_score: float
    ) -> List[str]:
        """Generate supporting evidence for a diagnosis"""
        evidence = []

        evidence.append(f"Vector similarity score: {similarity_score:.2f}")
        evidence.append(f"Prevalence: {condition.prevalence:.6f}")

        if condition.evidence_sources:
            evidence.extend(condition.evidence_sources[:2])

        return evidence

    def _determine_review_tier(
        self,
        confidence: float,
        requires_emergency: bool
    ) -> ReviewTier:
        """Determine which review tier this case should go to"""
        if requires_emergency:
            return ReviewTier.TIER1_AUTOMATED  # Emergency escalation

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
        """Generate specialist and test recommendations"""
        specialists = set()
        tests = set()

        for diagnosis in diagnoses[:3]:  # Top 3 diagnoses
            # Get specialist from vector store
            condition = self.vector_store.get_condition_by_id(diagnosis.condition_id)
            if condition and condition.specialist_referral:
                specialists.add(condition.specialist_referral)

            # Add recommended tests
            tests.update(diagnosis.recommended_next_steps)

        return list(specialists), list(tests)[:5]  # Top 5 tests

    def _generate_reasoning_summary(
        self,
        patient_case: PatientCase,
        diagnoses: List[DifferentialDiagnosis],
        symptoms: List[str]
    ) -> str:
        """Generate human-readable explanation of diagnostic reasoning"""
        summary_parts = []

        # Patient presentation
        summary_parts.append(
            f"Patient presents with {patient_case.chief_complaint}."
        )

        # Key symptoms
        summary_parts.append(
            f"Analysis of {len(symptoms)} reported symptoms reveals:"
        )

        # Top diagnosis
        if diagnoses:
            top = diagnoses[0]
            summary_parts.append(
                f"Most likely diagnosis is {top.condition_name} "
                f"with {top.confidence_score:.1%} confidence, "
                f"based on symptom pattern matching and clinical presentation."
            )

            # Differential
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
        """Calculate which symptoms were most important for diagnosis"""
        importance = {}

        # For MVP, assign equal importance
        # In production, use SHAP or similar techniques
        for symptom in symptoms:
            importance[symptom[:50]] = 1.0 / len(symptoms)  # Truncate for readability

        return importance

    def shutdown(self):
        """Clean up resources"""
        self.embedding_service.shutdown()
        self.vector_store.shutdown()
        logger.info("Diagnostic service shut down")
