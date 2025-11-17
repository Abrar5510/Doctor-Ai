"""
Resilience utilities for error handling, circuit breakers, and retry logic.

This module provides fault tolerance patterns to make the application
more resilient to transient failures and service disruptions.
"""

import time
import asyncio
from typing import Callable, Optional, Any, TypeVar, List
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta

from loguru import logger


T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by failing fast when a service is down.
    Automatically recovers when service becomes available again.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exceptions: tuple = (Exception,)
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exceptions: Tuple of exceptions that trigger the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def _record_success(self):
        """Record a successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.info(f"Circuit breaker '{self.name}' closed (service recovered)")

    def _record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker '{self.name}' opened "
                f"(failures: {self.failure_count}/{self.failure_threshold})"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.state != CircuitState.OPEN:
            return False

        if self.last_failure_time is None:
            return True

        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from the function
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' half-open (testing recovery)")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Service unavailable. Retry in {self.recovery_timeout}s."
                )

        try:
            result = func(*args, **kwargs)

            # Success - close circuit if it was half-open
            if self.state == CircuitState.HALF_OPEN:
                self._record_success()

            return result

        except self.expected_exceptions as e:
            self._record_failure()
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure "
                f"({self.failure_count}/{self.failure_threshold}): {e}"
            )
            raise

    async def call_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Async version of call method"""
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' half-open (testing recovery)")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Service unavailable. Retry in {self.recovery_timeout}s."
                )

        try:
            result = await func(*args, **kwargs)

            # Success - close circuit if it was half-open
            if self.state == CircuitState.HALF_OPEN:
                self._record_success()

            return result

        except self.expected_exceptions as e:
            self._record_failure()
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure "
                f"({self.failure_count}/{self.failure_threshold}): {e}"
            )
            raise


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying functions with exponential backoff.

    Usage:
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def my_function():
            # Code that might fail
            pass

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )

                    logger.warning(
                        f"Function '{func.__name__}' attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    await asyncio.sleep(delay)

            # This shouldn't be reached, but just in case
            if last_exception:
                raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )

                    logger.warning(
                        f"Function '{func.__name__}' attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)

            # This shouldn't be reached, but just in case
            if last_exception:
                raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class FallbackHandler:
    """
    Provides fallback responses when primary service fails.

    Useful for graceful degradation when services are unavailable.
    """

    @staticmethod
    def get_diagnostic_fallback():
        """Fallback response for diagnostic service failure"""
        return {
            "status": "degraded",
            "message": "Diagnostic service is temporarily unavailable. Please try again later.",
            "differential_diagnoses": [],
            "review_tier": 4,
            "requires_manual_review": True,
        }

    @staticmethod
    def get_ai_assistant_fallback():
        """Fallback response for AI assistant failure"""
        return {
            "status": "degraded",
            "message": "AI assistant is temporarily unavailable.",
            "explanation": "Unable to generate detailed explanation at this time. "
                          "Please consult with a healthcare professional.",
        }

    @staticmethod
    def get_embedding_fallback(text: str) -> List[float]:
        """Fallback for embedding service failure (returns zero vector)"""
        logger.warning("Using fallback zero vector for embedding")
        # Return a zero vector of standard dimension (768 for PubMedBERT)
        return [0.0] * 768


# Global circuit breakers for critical services
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60
) -> CircuitBreaker:
    """
    Get or create a circuit breaker instance.

    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        recovery_timeout: Seconds before attempting recovery

    Returns:
        CircuitBreaker instance
    """
    global _circuit_breakers

    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

    return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict[str, CircuitBreaker]:
    """Get all circuit breaker instances for monitoring"""
    return _circuit_breakers.copy()


def get_circuit_breaker_status() -> dict[str, Any]:
    """Get status of all circuit breakers"""
    return {
        name: {
            "state": breaker.state.value,
            "failure_count": breaker.failure_count,
            "last_failure": breaker.last_failure_time.isoformat()
            if breaker.last_failure_time else None,
        }
        for name, breaker in _circuit_breakers.items()
    }
