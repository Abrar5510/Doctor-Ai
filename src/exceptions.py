"""
Custom exceptions for the Medical Symptom Constellation Mapper

This module defines specific exception types for better error handling
and debugging throughout the application.
"""


class DoctorAIException(Exception):
    """Base exception for all Doctor AI errors"""
    pass


class ConfigurationError(DoctorAIException):
    """Raised when there's a configuration error"""
    pass


class ServiceInitializationError(DoctorAIException):
    """Raised when a service fails to initialize"""
    pass


class ModelLoadError(ServiceInitializationError):
    """Raised when an ML model fails to load"""
    pass


class VectorStoreError(DoctorAIException):
    """Base exception for vector store errors"""
    pass


class VectorStoreConnectionError(VectorStoreError):
    """Raised when unable to connect to vector database"""
    pass


class VectorStoreQueryError(VectorStoreError):
    """Raised when a vector store query fails"""
    pass


class EmbeddingError(DoctorAIException):
    """Raised when embedding generation fails"""
    pass


class DiagnosticError(DoctorAIException):
    """Base exception for diagnostic errors"""
    pass


class InvalidSymptomError(DiagnosticError):
    """Raised when symptom data is invalid"""
    pass


class ConfidenceCalculationError(DiagnosticError):
    """Raised when confidence score calculation fails"""
    pass


class AIAssistantError(DoctorAIException):
    """Base exception for AI assistant errors"""
    pass


class AIAPIError(AIAssistantError):
    """Raised when AI API calls fail"""
    pass


class AuditError(DoctorAIException):
    """Raised when audit logging fails"""
    pass


class ValidationError(DoctorAIException):
    """Raised when input validation fails"""
    pass


class RateLimitError(DoctorAIException):
    """Raised when rate limit is exceeded"""
    pass
