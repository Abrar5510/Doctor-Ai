"""
Performance metrics and structured logging utilities.

This module provides comprehensive performance tracking, structured logging,
and metrics collection for monitoring system health and performance.
"""

import time
import json
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime
from contextlib import contextmanager

from loguru import logger
from .cache import get_cache


class PerformanceMetrics:
    """
    Performance metrics tracker for Doctor-AI application.

    Tracks:
    - API request latency
    - Embedding generation time
    - Vector search time
    - Cache hit/miss rates
    - Error rates per endpoint
    """

    def __init__(self):
        """Initialize metrics tracker"""
        self.cache = get_cache()

    @contextmanager
    def measure(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager to measure operation duration.

        Usage:
            with metrics.measure("embedding_generation"):
                # Your code here
                pass
        """
        start_time = time.time()
        error_occurred = False
        error_type = None

        try:
            yield
        except Exception as e:
            error_occurred = True
            error_type = type(e).__name__
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)

            # Log with structured data
            log_data = {
                "operation": operation,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error_occurred,
            }

            if metadata:
                log_data.update(metadata)

            if error_occurred:
                log_data["error_type"] = error_type
                logger.warning(
                    f"Operation '{operation}' completed with error in {duration_ms}ms",
                    extra=log_data
                )
            else:
                logger.info(
                    f"Operation '{operation}' completed in {duration_ms}ms",
                    extra=log_data
                )

            # Store metrics in cache for aggregation
            self._store_metric(operation, duration_ms, error_occurred)

    def _store_metric(self, operation: str, duration_ms: int, error: bool):
        """Store metric in Redis for aggregation"""
        try:
            # Increment operation counter
            self.cache.increment_metric(f"count:{operation}")

            # Increment error counter if error occurred
            if error:
                self.cache.increment_metric(f"errors:{operation}")

            # Store duration (we'll use a simple counter for now)
            # In production, consider using Redis TimeSeries or similar
            self.cache.increment_metric(f"total_duration:{operation}", duration_ms)

        except Exception as e:
            logger.debug(f"Failed to store metric: {e}")

    def track_cache_hit(self, cache_type: str = "general"):
        """Track a cache hit"""
        self.cache.increment_metric(f"cache_hits:{cache_type}")

    def track_cache_miss(self, cache_type: str = "general"):
        """Track a cache miss"""
        self.cache.increment_metric(f"cache_misses:{cache_type}")

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        count = self.cache.get_metric(f"count:{operation}") or 0
        errors = self.cache.get_metric(f"errors:{operation}") or 0
        total_duration = self.cache.get_metric(f"total_duration:{operation}") or 0

        avg_duration = int(total_duration / count) if count > 0 else 0
        error_rate = (errors / count * 100) if count > 0 else 0

        return {
            "operation": operation,
            "total_requests": count,
            "total_errors": errors,
            "error_rate_percent": round(error_rate, 2),
            "average_duration_ms": avg_duration,
            "total_duration_ms": total_duration,
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all available metrics"""
        cache_stats = self.cache.get_stats()

        return {
            "cache": cache_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }


def track_performance(operation_name: str):
    """
    Decorator to track function performance.

    Usage:
        @track_performance("my_operation")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = PerformanceMetrics()
            with metrics.measure(operation_name):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = PerformanceMetrics()
            with metrics.measure(operation_name):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x00000080:
            # It's a coroutine
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Structured logging helpers
def log_request(
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
):
    """Log API request with structured data"""
    log_data = {
        "type": "api_request",
        "endpoint": endpoint,
        "method": method,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if user_id:
        log_data["user_id"] = user_id
    if request_id:
        log_data["request_id"] = request_id

    log_data.update(kwargs)

    logger.info(f"API Request: {method} {endpoint}", extra=log_data)


def log_response(
    endpoint: str,
    status_code: int,
    duration_ms: int,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
):
    """Log API response with structured data"""
    log_data = {
        "type": "api_response",
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if user_id:
        log_data["user_id"] = user_id
    if request_id:
        log_data["request_id"] = request_id

    log_data.update(kwargs)

    log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
    getattr(logger, log_level)(
        f"API Response: {status_code} in {duration_ms}ms",
        extra=log_data
    )


def log_error(
    error: Exception,
    context: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log error with structured data and context"""
    log_data = {
        "type": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if user_id:
        log_data["user_id"] = user_id

    log_data.update(kwargs)

    logger.error(f"Error in {context}: {error}", extra=log_data, exc_info=True)


# Global metrics instance
_metrics_instance: Optional[PerformanceMetrics] = None


def get_metrics() -> PerformanceMetrics:
    """Get or create the global metrics instance"""
    global _metrics_instance

    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()

    return _metrics_instance
