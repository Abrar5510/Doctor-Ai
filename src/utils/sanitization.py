"""
Input sanitization utilities for LLM and user inputs.

This module provides protection against prompt injection attacks
and other input-based vulnerabilities.
"""

import re
from typing import List, Optional
from fastapi import HTTPException, status


class PromptInjectionDetector:
    """
    Detects and prevents prompt injection attacks.

    Prompt injection occurs when an attacker manipulates LLM behavior
    by injecting malicious instructions into user inputs.
    """

    def __init__(self):
        """Initialize with detection patterns."""
        # Patterns that indicate potential prompt injection
        self.suspicious_patterns = [
            # Direct instruction attempts
            r"(?i)(ignore|disregard|forget)\s+(previous|all|above|prior)\s+(instructions|prompts?|rules?|commands?)",
            r"(?i)system\s*(prompt|message|instruction)",
            r"(?i)(you are|act as|pretend to be|roleplay as)\s+(?!a\s+patient)",
            r"(?i)(new|different)\s+(instructions|prompt|role|personality|character)",
            # Jailbreak attempts
            r"(?i)(DAN|developer mode|admin mode|god mode|unrestricted mode)",
            r"(?i)jailbreak",
            # Encoding/obfuscation attempts
            r"(?i)base64\s*:",
            r"(?i)rot13",
            r"(?i)hex\s*:",
            # System command attempts
            r"(?i)(execute|run|eval|exec|system|shell|subprocess)",
            # Prompt leaking
            r"(?i)(show|reveal|display|tell me)\s+(your\s+)?(system\s+)?(prompt|instructions|rules)",
            # Code injection
            r"(?i)<\s*script",
            r"(?i)javascript\s*:",
            r"(?i)on(load|error|click|mouseover)\s*=",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern) for pattern in self.suspicious_patterns
        ]

        # Suspicious keywords that should trigger additional scrutiny
        self.suspicious_keywords = {
            "ignore",
            "disregard",
            "forget",
            "override",
            "bypass",
            "jailbreak",
            "dan",
            "roleplay",
            "pretend",
            "admin",
            "system",
            "execute",
            "eval",
            "script",
        }

    def detect(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Detect potential prompt injection in text.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (is_suspicious, reason)
        """
        if not text:
            return False, None

        # Check against patterns
        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                return True, f"Suspicious pattern detected: {match.group()}"

        # Check for excessive special characters (potential encoding)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        if special_char_ratio > 0.3:
            return True, "Excessive special characters detected"

        # Check for suspicious keyword density
        words = text.lower().split()
        suspicious_word_count = sum(1 for word in words if word in self.suspicious_keywords)
        if len(words) > 0 and suspicious_word_count / len(words) > 0.2:
            return True, "High density of suspicious keywords"

        # Check for multiple consecutive special instructions
        instruction_pattern = r"(?i)(\.|!|\?)\s*(ignore|disregard|forget|now)"
        if len(re.findall(instruction_pattern, text)) > 2:
            return True, "Multiple consecutive instructions detected"

        return False, None

    def sanitize(self, text: str, max_length: int = 5000) -> str:
        """
        Sanitize text by removing potentially dangerous content.

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed text length

        Returns:
            Sanitized text

        Raises:
            HTTPException: If text is too long or contains malicious content
        """
        if not text:
            return ""

        # Check length
        if len(text) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input text too long (max {max_length} characters)",
            )

        # Detect injection attempts
        is_suspicious, reason = self.detect(text)
        if is_suspicious:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potentially malicious input detected: {reason}",
            )

        # Remove HTML/script tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove null bytes
        text = text.replace("\x00", "")

        # Normalize whitespace
        text = " ".join(text.split())

        return text


class InputValidator:
    """General input validation for medical data."""

    @staticmethod
    def validate_symptom_text(text: str) -> str:
        """
        Validate and sanitize symptom descriptions.

        Args:
            text: Symptom description

        Returns:
            Sanitized text

        Raises:
            HTTPException: If input is invalid
        """
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symptom description cannot be empty",
            )

        # Remove leading/trailing whitespace
        text = text.strip()

        # Check length
        if len(text) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symptom description too short (minimum 3 characters)",
            )

        if len(text) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symptom description too long (maximum 1000 characters)",
            )

        # Sanitize
        detector = PromptInjectionDetector()
        return detector.sanitize(text, max_length=1000)

    @staticmethod
    def validate_patient_age(age: int) -> int:
        """
        Validate patient age.

        Args:
            age: Patient age in years

        Returns:
            Validated age

        Raises:
            HTTPException: If age is invalid
        """
        if age < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age cannot be negative",
            )

        if age > 150:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age value unrealistic (maximum 150)",
            )

        return age

    @staticmethod
    def validate_condition_name(name: str) -> str:
        """
        Validate medical condition name.

        Args:
            name: Condition name

        Returns:
            Validated name

        Raises:
            HTTPException: If name is invalid
        """
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condition name cannot be empty",
            )

        name = name.strip()

        # Allow only alphanumeric, spaces, hyphens, apostrophes, and parentheses
        if not re.match(r"^[a-zA-Z0-9\s\-'()]+$", name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condition name contains invalid characters",
            )

        if len(name) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condition name too long (maximum 200 characters)",
            )

        return name


# Global instances
prompt_injection_detector = PromptInjectionDetector()
input_validator = InputValidator()


def sanitize_for_llm(text: str, context: str = "user input") -> str:
    """
    Sanitize text before passing to LLM.

    Args:
        text: Text to sanitize
        context: Context description for error messages

    Returns:
        Sanitized text safe for LLM

    Raises:
        HTTPException: If input is malicious
    """
    try:
        return prompt_injection_detector.sanitize(text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error sanitizing {context}: {str(e)}",
        )
