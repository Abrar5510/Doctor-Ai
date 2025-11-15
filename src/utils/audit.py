"""
Audit logging for HIPAA compliance and regulatory requirements
"""

import json
import hmac
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
from loguru import logger

from ..models.schemas import AuditLog, PatientCase, DiagnosticResult
from ..config import get_settings


class AuditLogger:
    """
    Comprehensive audit logging system for medical compliance
    """

    def __init__(self):
        self.settings = get_settings()
        self.audit_log_path = Path(self.settings.audit_log_path)
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Create audit log directory if it doesn't exist"""
        if self.settings.enable_audit_logging:
            self.audit_log_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Audit logging enabled: {self.audit_log_path}")

    def log_diagnostic_analysis(
        self,
        case: PatientCase,
        result: DiagnosticResult,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        vector_search_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a diagnostic analysis event

        Args:
            case: Patient case data
            result: Diagnostic result
            user_id: De-identified user ID
            user_role: User role (physician, specialist, etc.)
            vector_search_params: Parameters used for vector search

        Returns:
            Audit log ID
        """
        if not self.settings.enable_audit_logging:
            return ""

        # Anonymize patient data if required
        input_data = case.model_dump()
        if self.settings.enable_data_anonymization:
            input_data = self._anonymize_patient_data(input_data)

        # Create audit log entry
        audit_log = AuditLog(
            audit_id=f"audit_{uuid4().hex[:16]}",
            case_id=case.case_id,
            result_id=result.result_id,
            action_type="diagnostic_analysis",
            user_id=user_id,
            user_role=user_role,
            input_data=input_data,
            output_data={
                "review_tier": result.review_tier,
                "overall_confidence": result.overall_confidence,
                "primary_diagnosis": result.primary_diagnosis.condition_name if result.primary_diagnosis else None,
                "num_differential_diagnoses": len(result.differential_diagnoses),
                "red_flags_detected": result.red_flags_detected,
                "requires_emergency_care": result.requires_emergency_care,
            },
            vector_search_params=vector_search_params,
            similarity_scores=[d.similarity_score for d in result.differential_diagnoses],
            filters_applied=[],
            hipaa_compliant=True,
            data_anonymized=self.settings.enable_data_anonymization,
            timestamp=datetime.utcnow(),
        )

        # Write to file
        self._write_audit_log(audit_log)

        logger.info(f"Audit log created: {audit_log.audit_id}")

        return audit_log.audit_id

    def log_human_review(
        self,
        case_id: str,
        result_id: str,
        user_id: str,
        user_role: str,
        review_decision: str,
        override_rationale: Optional[str] = None
    ) -> str:
        """
        Log a human review event

        Args:
            case_id: Case identifier
            result_id: Result identifier
            user_id: Reviewer ID
            user_role: Reviewer role
            review_decision: Review decision
            override_rationale: Rationale if AI was overridden

        Returns:
            Audit log ID
        """
        if not self.settings.enable_audit_logging:
            return ""

        audit_log = AuditLog(
            audit_id=f"audit_{uuid4().hex[:16]}",
            case_id=case_id,
            result_id=result_id,
            action_type="human_review",
            user_id=user_id,
            user_role=user_role,
            input_data={},
            output_data={
                "review_decision": review_decision,
            },
            human_review_performed=True,
            review_decision=review_decision,
            override_rationale=override_rationale,
            hipaa_compliant=True,
            data_anonymized=True,
            timestamp=datetime.utcnow(),
        )

        self._write_audit_log(audit_log)

        logger.info(f"Human review logged: {audit_log.audit_id}")

        return audit_log.audit_id

    def log_outcome(
        self,
        case_id: str,
        final_diagnosis: str,
        outcome: str,
        accuracy_validated: bool = True
    ) -> str:
        """
        Log patient outcome for quality assurance

        Args:
            case_id: Case identifier
            final_diagnosis: Confirmed final diagnosis
            outcome: Patient outcome
            accuracy_validated: Whether diagnosis accuracy was validated

        Returns:
            Audit log ID
        """
        if not self.settings.enable_audit_logging:
            return ""

        audit_log = AuditLog(
            audit_id=f"audit_{uuid4().hex[:16]}",
            case_id=case_id,
            action_type="outcome_tracking",
            input_data={},
            output_data={
                "final_diagnosis": final_diagnosis,
                "outcome": outcome,
            },
            final_diagnosis=final_diagnosis,
            outcome=outcome,
            accuracy_validated=accuracy_validated,
            hipaa_compliant=True,
            data_anonymized=True,
            timestamp=datetime.utcnow(),
        )

        self._write_audit_log(audit_log)

        logger.info(f"Outcome logged: {audit_log.audit_id}")

        return audit_log.audit_id

    def _write_audit_log(self, audit_log: AuditLog):
        """Write audit log to file"""
        try:
            # Organize by date
            date_str = audit_log.timestamp.strftime("%Y-%m-%d")
            log_file = self.audit_log_path / f"audit_{date_str}.jsonl"

            # Write as JSON Lines format
            with open(log_file, "a") as f:
                f.write(audit_log.model_dump_json() + "\n")

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def _anonymize_patient_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize patient data for HIPAA compliance using HMAC-SHA256

        Uses cryptographically secure HMAC-SHA256 for one-way hashing of
        patient identifiers, ensuring HIPAA compliance while maintaining
        the ability to track the same patient across sessions.

        Args:
            data: Patient data dictionary

        Returns:
            Anonymized data with HIPAA-compliant hashing
        """
        anonymized = data.copy()

        # Use HMAC-SHA256 for secure, one-way hashing of patient identifiers
        if "patient_id" in anonymized:
            patient_id = str(anonymized['patient_id'])
            # Use secret key from settings for HMAC
            secret = self.settings.secret_key.encode('utf-8') if self.settings.secret_key else b'default-audit-key'
            hashed = hmac.new(
                secret,
                patient_id.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            # Take first 12 characters for readability while maintaining uniqueness
            anonymized["patient_id"] = f"anon_{hashed[:12]}"

        # Keep only necessary demographic information
        # Remove specific locations if present
        if "geographic_location" in anonymized:
            anonymized["geographic_location"] = "anonymized"

        return anonymized

    def get_audit_logs(
        self,
        case_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[AuditLog]:
        """
        Retrieve audit logs with filters

        Args:
            case_id: Filter by case ID
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of audit logs
        """
        logs = []

        # Read all log files
        for log_file in sorted(self.audit_log_path.glob("audit_*.jsonl")):
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        log_data = json.loads(line)
                        audit_log = AuditLog(**log_data)

                        # Apply filters
                        if case_id and audit_log.case_id != case_id:
                            continue

                        if start_date and audit_log.timestamp < start_date:
                            continue

                        if end_date and audit_log.timestamp > end_date:
                            continue

                        logs.append(audit_log)

                    except Exception as e:
                        logger.warning(f"Failed to parse audit log line: {e}")

        return logs
