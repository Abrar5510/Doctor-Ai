"""
Password validation and security utilities.

This module provides robust password validation with configurable requirements
to prevent weak passwords and enforce security best practices.
"""

import re
from typing import List, Tuple
from passlib.context import CryptContext


class PasswordValidator:
    """Validates password strength and enforces security requirements."""

    def __init__(
        self,
        min_length: int = 12,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        min_uppercase: int = 1,
        min_lowercase: int = 1,
        min_digits: int = 1,
        min_special: int = 1,
    ):
        """
        Initialize password validator with configurable requirements.

        Args:
            min_length: Minimum password length (default: 12)
            require_uppercase: Require uppercase letters
            require_lowercase: Require lowercase letters
            require_digits: Require digits
            require_special: Require special characters
            min_uppercase: Minimum number of uppercase letters
            min_lowercase: Minimum number of lowercase letters
            min_digits: Minimum number of digits
            min_special: Minimum number of special characters
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special

        # Common weak passwords to reject
        self.weak_passwords = {
            "password",
            "password123",
            "12345678",
            "qwerty",
            "abc123",
            "monkey",
            "letmein",
            "trustno1",
            "dragon",
            "baseball",
            "iloveyou",
            "master",
            "sunshine",
            "ashley",
            "bailey",
            "passw0rd",
            "shadow",
            "123123",
            "654321",
            "superman",
            "qazwsx",
            "michael",
            "football",
            "welcome",
            "admin",
            "administrator",
        }

    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against all requirements.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check minimum length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")

        # Check for common weak passwords
        if password.lower() in self.weak_passwords:
            errors.append("Password is too common and easily guessable")

        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append("Password contains sequential characters (e.g., 'abc', '123')")

        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append("Password contains too many repeated characters")

        # Count character types
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_count = sum(1 for c in password if not c.isalnum())

        # Check uppercase requirement
        if self.require_uppercase and uppercase_count < self.min_uppercase:
            errors.append(
                f"Password must contain at least {self.min_uppercase} uppercase letter(s)"
            )

        # Check lowercase requirement
        if self.require_lowercase and lowercase_count < self.min_lowercase:
            errors.append(
                f"Password must contain at least {self.min_lowercase} lowercase letter(s)"
            )

        # Check digit requirement
        if self.require_digits and digit_count < self.min_digits:
            errors.append(f"Password must contain at least {self.min_digits} digit(s)")

        # Check special character requirement
        if self.require_special and special_count < self.min_special:
            errors.append(
                f"Password must contain at least {self.min_special} special character(s)"
            )

        # Check for username/email patterns (if applicable)
        if self._contains_dictionary_words(password):
            errors.append("Password should not contain common dictionary words")

        return len(errors) == 0, errors

    def _has_sequential_chars(self, password: str, max_sequential: int = 3) -> bool:
        """Check if password contains sequential characters."""
        password_lower = password.lower()

        # Check for sequential letters
        for i in range(len(password_lower) - max_sequential + 1):
            chars = password_lower[i : i + max_sequential]
            if all(
                ord(chars[j]) == ord(chars[j - 1]) + 1 for j in range(1, len(chars))
            ):
                return True

        # Check for sequential digits
        for i in range(len(password) - max_sequential + 1):
            chars = password[i : i + max_sequential]
            if chars.isdigit() and all(
                int(chars[j]) == int(chars[j - 1]) + 1 for j in range(1, len(chars))
            ):
                return True

        return False

    def _has_repeated_chars(self, password: str, max_repeats: int = 3) -> bool:
        """Check if password contains too many repeated characters."""
        for i in range(len(password) - max_repeats + 1):
            if len(set(password[i : i + max_repeats])) == 1:
                return True
        return False

    def _contains_dictionary_words(self, password: str) -> bool:
        """Check if password contains common dictionary words."""
        # Simple check for common patterns
        common_words = [
            "password",
            "admin",
            "user",
            "login",
            "welcome",
            "doctor",
            "medical",
            "health",
        ]
        password_lower = password.lower()
        return any(word in password_lower for word in common_words)

    def get_password_strength(self, password: str) -> str:
        """
        Calculate password strength.

        Args:
            password: Password to evaluate

        Returns:
            Strength rating: 'weak', 'medium', 'strong', or 'very_strong'
        """
        score = 0

        # Length score
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        # Character diversity score
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        score += sum([has_upper, has_lower, has_digit, has_special])

        # Check for weak patterns
        is_valid, errors = self.validate(password)
        if not is_valid:
            return "weak"

        # Rate based on score
        if score >= 7:
            return "very_strong"
        elif score >= 5:
            return "strong"
        elif score >= 3:
            return "medium"
        else:
            return "weak"


# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# Default validator instance
default_validator = PasswordValidator(
    min_length=12,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    min_uppercase=1,
    min_lowercase=1,
    min_digits=1,
    min_special=1,
)
