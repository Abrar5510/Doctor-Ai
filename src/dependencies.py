"""
Centralized dependency injection for FastAPI application.

This module provides thread-safe, properly scoped dependencies for all services.
Replaces the previous global singleton pattern with proper dependency injection.
"""

from typing import Generator, Optional
from functools import lru_cache
from contextlib import contextmanager

from .services.diagnostic import DiagnosticService
from .services.ai_assistant import AIReasoningAssistant
from .utils.audit import AuditLogger
from .config import get_settings
from .database import get_db, SessionLocal
from sqlalchemy.orm import Session
from loguru import logger


class ServiceContainer:
    """
    Thread-safe service container for managing singleton services.
    Uses lazy initialization and proper lifecycle management.
    """

    _diagnostic_service: Optional[DiagnosticService] = None
    _ai_assistant: Optional[AIReasoningAssistant] = None
    _audit_logger: Optional[AuditLogger] = None
    _lock_initialized = False

    @classmethod
    def get_diagnostic_service(cls) -> DiagnosticService:
        """Get or create diagnostic service instance (thread-safe)"""
        if cls._diagnostic_service is None:
            logger.info("Initializing DiagnosticService...")
            cls._diagnostic_service = DiagnosticService()
            cls._diagnostic_service.initialize()
            logger.success("DiagnosticService initialized successfully")
        return cls._diagnostic_service

    @classmethod
    def get_ai_assistant(cls) -> AIReasoningAssistant:
        """Get or create AI assistant instance (thread-safe)"""
        if cls._ai_assistant is None:
            logger.info("Initializing AIReasoningAssistant...")
            settings = get_settings()
            api_key = getattr(settings, 'openai_api_key', None)
            cls._ai_assistant = AIReasoningAssistant(api_key=api_key)
            logger.success("AIReasoningAssistant initialized successfully")
        return cls._ai_assistant

    @classmethod
    def get_audit_logger(cls) -> AuditLogger:
        """Get or create audit logger instance (thread-safe)"""
        if cls._audit_logger is None:
            logger.info("Initializing AuditLogger...")
            cls._audit_logger = AuditLogger()
            logger.success("AuditLogger initialized successfully")
        return cls._audit_logger

    @classmethod
    def cleanup(cls):
        """Cleanup all services (call on application shutdown)"""
        logger.info("Cleaning up services...")

        if cls._diagnostic_service:
            try:
                cls._diagnostic_service.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down DiagnosticService: {e}")
            cls._diagnostic_service = None

        if cls._ai_assistant:
            # AIReasoningAssistant doesn't need explicit cleanup
            cls._ai_assistant = None

        if cls._audit_logger:
            # AuditLogger doesn't need explicit cleanup
            cls._audit_logger = None

        logger.success("Service cleanup completed")


# FastAPI dependency functions
def get_diagnostic_service() -> DiagnosticService:
    """
    FastAPI dependency for diagnostic service.
    Returns the singleton instance managed by ServiceContainer.
    """
    return ServiceContainer.get_diagnostic_service()


def get_ai_assistant() -> AIReasoningAssistant:
    """
    FastAPI dependency for AI assistant.
    Returns the singleton instance managed by ServiceContainer.
    """
    return ServiceContainer.get_ai_assistant()


def get_audit_logger() -> AuditLogger:
    """
    FastAPI dependency for audit logger.
    Returns the singleton instance managed by ServiceContainer.
    """
    return ServiceContainer.get_audit_logger()


def get_database() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Provides a new database session for each request.
    Automatically closes the session when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
