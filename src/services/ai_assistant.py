"""
AI-powered diagnostic reasoning assistant using LLM
Provides natural language explanations, follow-up questions, and detailed reports
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import json
from loguru import logger

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

from ..models.schemas import (
    PatientCase,
    DiagnosticResult,
    DifferentialDiagnosis,
    ReviewTier,
)
from ..config import get_settings


class ReportType(str, Enum):
    """Types of medical reports to generate"""
    PHYSICIAN_SUMMARY = "physician_summary"
    PATIENT_FRIENDLY = "patient_friendly"
    DETAILED_CLINICAL = "detailed_clinical"
    DIFFERENTIAL_ANALYSIS = "differential_analysis"


class AIReasoningAssistant:
    """
    Advanced LLM-based diagnostic reasoning assistant
    Provides natural language explanations and interactive capabilities
    """

    def __init__(self, api_key: Optional[str] = None, use_local: bool = False):
        """
        Initialize the AI reasoning assistant

        Args:
            api_key: OpenAI or OpenRouter API key (if using cloud LLM)
            use_local: Use local LLM (Ollama) instead of cloud API
        """
        self.settings = get_settings()
        self.use_local = use_local

        if not use_local and OPENAI_AVAILABLE:
            # Check if using OpenRouter
            if self.settings.use_openrouter and self.settings.openrouter_api_key:
                self.client = AsyncOpenAI(
                    api_key=self.settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                self.model = self.settings.openrouter_model
                logger.info(f"AI Assistant initialized with OpenRouter using model: {self.model}")
            elif api_key:
                # Use direct OpenAI API
                self.client = AsyncOpenAI(api_key=api_key)
                self.model = "gpt-4-turbo-preview"
                logger.info("AI Assistant initialized with OpenAI GPT-4")
            else:
                self.client = None
                logger.error("AI Assistant not initialized: No API key provided")
                raise ValueError(
                    "AI Assistant requires an API key. "
                    "Set OPENAI_API_KEY or configure OpenRouter with USE_OPENROUTER=True and OPENROUTER_API_KEY."
                )
        elif use_local:
            # For local LLM using Ollama
            self.model = "llama2"
            logger.info("AI Assistant initialized with local Llama2")
        else:
            self.client = None
            logger.error("AI Assistant not initialized: OpenAI library not available")
            raise ValueError(
                "AI Assistant requires the OpenAI library. Install with: pip install openai"
            )

    async def generate_detailed_explanation(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult
    ) -> str:
        """
        Generate a detailed, natural language explanation of the diagnosis

        Args:
            patient_case: Patient case information
            diagnostic_result: Diagnostic analysis result

        Returns:
            Detailed explanation in natural language
        """
        if not diagnostic_result.differential_diagnoses:
            return "Unable to generate explanation: No diagnoses found."

        top_diagnosis = diagnostic_result.differential_diagnoses[0]

        prompt = self._build_explanation_prompt(patient_case, diagnostic_result, top_diagnosis)

        response = await self._call_llm(prompt)
        return response

    async def generate_follow_up_questions(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult,
        num_questions: int = 5
    ) -> List[str]:
        """
        Generate intelligent follow-up questions to refine diagnosis

        Args:
            patient_case: Current patient information
            diagnostic_result: Current diagnostic analysis
            num_questions: Number of questions to generate

        Returns:
            List of follow-up questions
        """
        prompt = f"""Based on the following patient case and diagnostic findings, generate {num_questions} critical follow-up questions that would help narrow down the diagnosis and rule out competing conditions.

Patient Information:
- Age: {patient_case.age}, Sex: {patient_case.sex}
- Chief Complaint: {patient_case.chief_complaint}
- Symptoms: {', '.join([s.description for s in patient_case.symptoms])}

Top Differential Diagnoses:
{self._format_diagnoses(diagnostic_result.differential_diagnoses[:3])}

Generate specific, clinically relevant questions that:
1. Help distinguish between the top differential diagnoses
2. Check for red flag symptoms
3. Gather important temporal or contextual information
4. Assess severity and functional impact

Format each question on a new line, numbered 1-{num_questions}."""

        response = await self._call_llm(prompt)

        # Parse questions from response
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                question = line.lstrip('0123456789.-•) ').strip()
                if question and '?' in question:
                    questions.append(question)

        return questions[:num_questions]

    async def generate_medical_report(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult,
        report_type: ReportType = ReportType.PHYSICIAN_SUMMARY
    ) -> str:
        """
        Generate a comprehensive medical report

        Args:
            patient_case: Patient case information
            diagnostic_result: Diagnostic result
            report_type: Type of report to generate

        Returns:
            Formatted medical report
        """
        if report_type == ReportType.PHYSICIAN_SUMMARY:
            return await self._generate_physician_summary(patient_case, diagnostic_result)
        elif report_type == ReportType.PATIENT_FRIENDLY:
            return await self._generate_patient_friendly_report(patient_case, diagnostic_result)
        elif report_type == ReportType.DETAILED_CLINICAL:
            return await self._generate_detailed_clinical_report(patient_case, diagnostic_result)
        elif report_type == ReportType.DIFFERENTIAL_ANALYSIS:
            return await self._generate_differential_analysis(patient_case, diagnostic_result)

        return "Invalid report type"

    async def explain_in_simple_terms(
        self,
        medical_condition: str,
        technical_explanation: str
    ) -> str:
        """
        Convert medical jargon into patient-friendly language

        Args:
            medical_condition: Name of the condition
            technical_explanation: Technical medical explanation

        Returns:
            Simple, patient-friendly explanation
        """
        prompt = f"""Explain the following medical condition and information in simple, patient-friendly language that a 12-year-old could understand. Avoid medical jargon and use everyday analogies where helpful.

Medical Condition: {medical_condition}

Technical Explanation:
{technical_explanation}

Provide a clear, compassionate explanation that:
1. Uses simple words (avoid medical terms or explain them)
2. Uses analogies to everyday situations
3. Is encouraging and not alarming
4. Explains what the condition means for daily life
5. Is no more than 3-4 short paragraphs"""

        response = await self._call_llm(prompt)
        return response

    async def generate_treatment_recommendations(
        self,
        diagnosis: DifferentialDiagnosis,
        patient_case: PatientCase
    ) -> Dict[str, Any]:
        """
        Generate evidence-based treatment recommendations

        Args:
            diagnosis: The diagnosis to generate recommendations for
            patient_case: Patient information

        Returns:
            Dictionary with treatment recommendations
        """
        prompt = f"""As a medical AI assistant, provide evidence-based treatment recommendations for the following diagnosis. Focus on initial management and next steps.

Diagnosis: {diagnosis.condition_name}
Patient: {patient_case.age}-year-old {patient_case.sex}
Confidence: {diagnosis.confidence_score:.1%}

Provide recommendations for:

1. IMMEDIATE ACTIONS (next 24-48 hours)
2. DIAGNOSTIC WORKUP (tests and imaging)
3. INITIAL TREATMENT (if appropriate)
4. SPECIALIST REFERRALS (if needed)
5. PATIENT COUNSELING (lifestyle, expectations)
6. RED FLAGS (warning signs to watch for)

Format as structured sections. Be specific but acknowledge this is AI-assisted guidance that requires physician oversight."""

        response = await self._call_llm(prompt)

        return {
            "diagnosis": diagnosis.condition_name,
            "recommendations": response,
            "confidence": diagnosis.confidence_score,
            "disclaimer": "These recommendations are AI-generated and must be reviewed by a qualified healthcare professional before implementation."
        }

    def _build_explanation_prompt(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult,
        top_diagnosis: DifferentialDiagnosis
    ) -> str:
        """Build prompt for diagnostic explanation"""

        symptoms_text = "\n".join([
            f"- {s.description} ({s.severity.value}, {s.duration_days} days)"
            for s in patient_case.symptoms
        ])

        return f"""You are an expert medical AI assistant. Provide a detailed, clinically sound explanation of the following diagnostic analysis.

PATIENT PRESENTATION:
Age: {patient_case.age}
Sex: {patient_case.sex}
Chief Complaint: {patient_case.chief_complaint}

Symptoms:
{symptoms_text}

DIAGNOSTIC ANALYSIS:
Primary Diagnosis: {top_diagnosis.condition_name}
Confidence: {top_diagnosis.confidence_score:.1%}
Vector Similarity: {top_diagnosis.similarity_score:.1%}

Matching Symptoms: {', '.join(top_diagnosis.matching_symptoms)}
Missing Expected Symptoms: {', '.join(top_diagnosis.missing_symptoms) if top_diagnosis.missing_symptoms else 'None'}

Differential Diagnoses:
{self._format_diagnoses(diagnostic_result.differential_diagnoses[1:4])}

TASK:
Provide a comprehensive explanation that:

1. CLINICAL REASONING: Explain why this diagnosis fits the symptom pattern
2. PATTERN MATCHING: Describe how the symptoms align with typical presentation
3. DIFFERENTIAL CONSIDERATION: Explain why alternatives were considered but ranked lower
4. DIAGNOSTIC CERTAINTY: Discuss the confidence level and what factors contribute to it
5. NEXT STEPS: Recommend specific diagnostic tests to confirm

Write in professional medical language appropriate for physician review. Be thorough but concise (3-4 paragraphs)."""

    async def _generate_physician_summary(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult
    ) -> str:
        """Generate physician-focused summary"""

        prompt = f"""Generate a concise clinical summary for physician review.

PATIENT: {patient_case.age}yo {patient_case.sex}
CC: {patient_case.chief_complaint}

HPI: Patient presents with {len(patient_case.symptoms)} symptoms:
{', '.join([s.description for s in patient_case.symptoms[:5]])}

AI DIAGNOSTIC ANALYSIS:
- Primary: {diagnostic_result.differential_diagnoses[0].condition_name} ({diagnostic_result.overall_confidence:.1%})
- Review Tier: {diagnostic_result.review_tier.value}
- Red Flags: {', '.join(diagnostic_result.red_flags_detected) if diagnostic_result.red_flags_detected else 'None'}

DDx: {', '.join([d.condition_name for d in diagnostic_result.differential_diagnoses[1:4]])}

Recommended Workup: {', '.join(diagnostic_result.recommended_tests[:5])}

Format as a standard clinical note (SOAP format if appropriate)."""

        return await self._call_llm(prompt)

    async def _generate_patient_friendly_report(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult
    ) -> str:
        """Generate patient-friendly report"""

        top_diagnosis = diagnostic_result.differential_diagnoses[0]

        prompt = f"""Create a patient-friendly medical report that explains the diagnostic findings in simple, compassionate language.

Patient Information:
- Your symptoms: {patient_case.chief_complaint}
- Analysis confidence: {diagnostic_result.overall_confidence:.1%}
- Most likely cause: {top_diagnosis.condition_name}

Create a report that:
1. Explains what we found in simple terms
2. Describes what this condition means
3. Outlines next steps in a reassuring way
4. Lists tests that may be needed
5. Provides hope and clear path forward

Use "you" and "your" language. Be warm and encouraging. Avoid scary medical jargon.
Length: 4-5 short paragraphs."""

        return await self._call_llm(prompt)

    async def _generate_detailed_clinical_report(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult
    ) -> str:
        """Generate detailed clinical report"""

        prompt = f"""Generate a comprehensive clinical diagnostic report suitable for medical records and specialist referral.

Include all standard sections:
- Patient Demographics
- Chief Complaint
- History of Present Illness
- Review of Systems
- Differential Diagnosis (detailed)
- Diagnostic Reasoning
- Recommended Workup
- Clinical Decision Support Notes
- AI Analysis Metadata

Patient Data:
{json.dumps(patient_case.model_dump(), indent=2, default=str)}

Diagnostic Results:
{json.dumps(diagnostic_result.model_dump(), indent=2, default=str)}

Create a formal, complete clinical report."""

        return await self._call_llm(prompt)

    async def _generate_differential_analysis(
        self,
        patient_case: PatientCase,
        diagnostic_result: DiagnosticResult
    ) -> str:
        """Generate differential diagnosis analysis"""

        prompt = f"""Create a detailed differential diagnosis analysis comparing the top diagnoses.

Top Differential Diagnoses:
{self._format_diagnoses(diagnostic_result.differential_diagnoses[:5])}

For each diagnosis, analyze:
1. Supporting Features (symptoms/findings that support it)
2. Refuting Features (what argues against it)
3. Distinguishing Tests (how to differentiate from others)
4. Clinical Probability

Create a comparison table or structured analysis."""

        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Call the LLM (OpenAI or local) with the given prompt

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature

        Returns:
            LLM response text
        """
        if self.client is None:
            raise RuntimeError(
                "AI Assistant client not initialized. "
                "This should not happen if initialization was successful."
            )

        try:
            if not self.use_local:
                # Use OpenAI
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert medical AI assistant specializing in diagnostic reasoning and clinical decision support. Provide accurate, evidence-based medical information while acknowledging the limitations of AI and the need for human physician oversight."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=2000,
                )
                return response.choices[0].message.content
            else:
                # Use local Ollama (would need ollama Python client)
                # This is a placeholder - implement based on local LLM choice
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=60.0
                    )
                    return response.json()["response"]

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError("AI service temporarily unavailable. Please try again later.")

    def _format_diagnoses(self, diagnoses: List[DifferentialDiagnosis]) -> str:
        """Format diagnoses for prompt"""
        formatted = []
        for i, dx in enumerate(diagnoses, 1):
            formatted.append(
                f"{i}. {dx.condition_name} (Confidence: {dx.confidence_score:.1%})"
            )
        return "\n".join(formatted)

    async def shutdown(self):
        """Clean up resources"""
        if self.client:
            await self.client.close()
        logger.info("AI Reasoning Assistant shut down")
