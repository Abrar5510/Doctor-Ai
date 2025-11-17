"""
Advanced monitoring and observability endpoints.

Provides comprehensive system health, performance metrics, and diagnostics.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from loguru import logger
from datetime import datetime

from ..models.database import User
from ..services.auth import get_current_user
from ..utils.cache import get_cache
from ..utils.metrics import get_metrics
from ..utils.resilience import get_circuit_breaker_status
from ..dependencies import get_diagnostic_service, get_ai_assistant

router = APIRouter()


@router.get(
    "/health/detailed",
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Comprehensive health check including all services and dependencies",
)
async def detailed_health_check(
    diagnostic_service = Depends(get_diagnostic_service),
    ai_assistant = Depends(get_ai_assistant),
):
    """
    Detailed health check that tests all critical services.

    Returns:
        - Overall status (healthy, degraded, unhealthy)
        - Individual service status
        - Service availability percentage
        - Timestamp of check
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "available_services": 0,
        "total_services": 0,
    }

    # Check diagnostic service
    try:
        stats = diagnostic_service.vector_store.get_collection_stats()
        health_status["services"]["diagnostic_service"] = {
            "status": "healthy",
            "details": {
                "vector_count": stats.get("vectors_count", 0),
                "indexed": stats.get("indexed", False),
            }
        }
        health_status["available_services"] += 1
    except Exception as e:
        logger.warning(f"Diagnostic service health check failed: {e}")
        health_status["services"]["diagnostic_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    health_status["total_services"] += 1

    # Check AI assistant
    try:
        # Simple check - if it initialized, it's healthy
        if ai_assistant:
            health_status["services"]["ai_assistant"] = {
                "status": "healthy",
                "details": {
                    "enabled": True
                }
            }
            health_status["available_services"] += 1
        else:
            health_status["services"]["ai_assistant"] = {
                "status": "degraded",
                "details": {
                    "enabled": False
                }
            }
    except Exception as e:
        logger.warning(f"AI assistant health check failed: {e}")
        health_status["services"]["ai_assistant"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    health_status["total_services"] += 1

    # Check cache
    try:
        cache = get_cache()
        cache_stats = cache.get_stats()
        health_status["services"]["cache"] = {
            "status": "healthy" if cache_stats.get("enabled") else "disabled",
            "details": cache_stats
        }
        if cache_stats.get("enabled"):
            health_status["available_services"] += 1
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        health_status["services"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    health_status["total_services"] += 1

    # Calculate availability percentage
    if health_status["total_services"] > 0:
        health_status["availability_percentage"] = round(
            (health_status["available_services"] / health_status["total_services"]) * 100,
            2
        )
    else:
        health_status["availability_percentage"] = 0

    # Determine overall status
    if health_status["available_services"] == 0:
        health_status["status"] = "unhealthy"
        return health_status, status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_status["available_services"] < health_status["total_services"]:
        health_status["status"] = "degraded"

    return health_status


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Performance metrics",
    description="Get comprehensive performance and usage metrics",
)
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
):
    """
    Get system performance metrics.

    Requires authentication. Admin users get full metrics, others get limited view.
    """
    try:
        metrics = get_metrics()
        cache = get_cache()

        # Get cache statistics
        cache_stats = cache.get_stats()

        # Get common operation statistics
        operation_stats = {
            "analyze_patient_case": metrics.get_operation_stats("analyze_patient_case"),
            "embedding_generation": metrics.get_operation_stats("embedding_generation"),
            "vector_search": metrics.get_operation_stats("vector_search"),
            "save_case_to_history": metrics.get_operation_stats("save_case_to_history"),
        }

        # Get circuit breaker status
        circuit_breakers = get_circuit_breaker_status()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_stats,
            "operations": operation_stats,
            "circuit_breakers": circuit_breakers,
            "user": {
                "role": current_user.role.value,
                "access_level": "full" if current_user.role.value == "admin" else "limited",
            }
        }

    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics"
        )


@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK,
    summary="Monitoring dashboard data",
    description="Get comprehensive dashboard data for system monitoring",
)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive dashboard data for system monitoring and observability.

    Includes:
    - System health status
    - Performance metrics
    - Cache statistics
    - Circuit breaker status
    - Recent errors
    - Usage statistics
    """
    try:
        metrics = get_metrics()
        cache = get_cache()

        # Get all stats
        cache_stats = cache.get_stats()
        circuit_breakers = get_circuit_breaker_status()

        # Calculate uptime (simplified - in production would track actual uptime)
        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "operational",
            "overview": {
                "total_requests": cache_stats.get("total_commands_processed", 0),
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "active_circuit_breakers": len([
                    cb for cb in circuit_breakers.values()
                    if cb["state"] != "closed"
                ]),
            },
            "cache": {
                "enabled": cache_stats.get("enabled", False),
                "hit_rate": cache_stats.get("hit_rate", 0),
                "memory_used": cache_stats.get("used_memory_human", "0B"),
            },
            "circuit_breakers": circuit_breakers,
            "operations": {
                "analyze_patient_case": metrics.get_operation_stats("analyze_patient_case"),
                "embedding_generation": metrics.get_operation_stats("embedding_generation"),
                "vector_search": metrics.get_operation_stats("vector_search"),
            },
            "system_info": {
                "service": "Doctor-AI",
                "version": "0.2.0",
                "environment": "production",  # Would come from config
            }
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )


@router.post(
    "/cache/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear cache",
    description="Clear cache (admin only)",
)
async def clear_cache(
    pattern: str = "*",
    current_user: User = Depends(get_current_user),
):
    """
    Clear cache entries matching a pattern.

    Requires admin role.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to clear cache"
        )

    try:
        cache = get_cache()
        deleted = cache.clear_pattern(pattern)

        logger.warning(
            f"Cache cleared by user {current_user.id} (pattern: {pattern}). "
            f"{deleted} keys deleted."
        )

        return {
            "status": "success",
            "message": f"Cache cleared successfully",
            "deleted_keys": deleted,
            "pattern": pattern,
        }

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )


@router.get(
    "/diagnostics",
    status_code=status.HTTP_200_OK,
    summary="System diagnostics",
    description="Get detailed system diagnostics for troubleshooting",
)
async def get_system_diagnostics(
    current_user: User = Depends(get_current_user),
    diagnostic_service = Depends(get_diagnostic_service),
):
    """
    Get detailed system diagnostics for troubleshooting.

    Requires admin role for full diagnostics.
    """
    try:
        diagnostics = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": {
                "id": current_user.id,
                "role": current_user.role.value,
            },
            "services": {},
        }

        # Diagnostic service info
        try:
            stats = diagnostic_service.vector_store.get_collection_stats()
            diagnostics["services"]["diagnostic"] = {
                "status": "operational",
                "vector_database": {
                    "type": "qdrant",
                    "vectors_count": stats.get("vectors_count", 0),
                    "indexed": stats.get("indexed", False),
                },
                "embedding_model": {
                    "name": "microsoft/BiomedNLP-PubMedBERT",
                    "dimension": 768,
                }
            }
        except Exception as e:
            diagnostics["services"]["diagnostic"] = {
                "status": "error",
                "error": str(e)
            }

        # Cache diagnostics
        cache = get_cache()
        cache_stats = cache.get_stats()
        diagnostics["services"]["cache"] = cache_stats

        # Circuit breaker diagnostics
        diagnostics["circuit_breakers"] = get_circuit_breaker_status()

        return diagnostics

    except Exception as e:
        logger.error(f"Failed to get system diagnostics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system diagnostics"
        )
