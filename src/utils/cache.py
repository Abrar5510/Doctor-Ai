"""
Redis caching utilities for embeddings, query results, and performance optimization.

This module provides a comprehensive caching layer using Redis to reduce
computation time for expensive operations like embedding generation and
vector similarity searches.
"""

import json
import hashlib
from typing import Optional, List, Any, Dict
from datetime import timedelta
import redis
from loguru import logger

from ..config import get_settings


class RedisCache:
    """
    Redis cache manager for Doctor-AI application.

    Provides caching for:
    - Vector embeddings (most expensive operation)
    - Query results
    - User sessions
    - Rate limiting data
    """

    def __init__(self):
        """Initialize Redis connection"""
        settings = get_settings()
        self.enabled = settings.redis_enabled

        if not self.enabled:
            logger.warning("Redis caching is disabled")
            self.client = None
            return

        try:
            self.client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password if settings.redis_password else None,
                db=settings.redis_db,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=50,
            )

            # Test connection
            self.client.ping()
            logger.success(f"Redis cache connected: {settings.redis_host}:{settings.redis_port}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Continuing without Redis cache")
            self.client = None
            self.enabled = False

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key with namespace prefix"""
        return f"doctor_ai:{prefix}:{identifier}"

    def _hash_text(self, text: str) -> str:
        """Generate SHA-256 hash of text for cache key"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def get_embedding(self, text: str, model: str) -> Optional[List[float]]:
        """
        Retrieve cached embedding for text.

        Args:
            text: The text that was embedded
            model: The embedding model used

        Returns:
            List of floats (embedding vector) or None if not cached
        """
        if not self.enabled or not self.client:
            return None

        try:
            text_hash = self._hash_text(text)
            key = self._generate_key("embedding", f"{model}:{text_hash}")

            cached = self.client.get(key)
            if cached:
                logger.debug(f"Embedding cache HIT for text hash {text_hash[:8]}")
                return json.loads(cached.decode('utf-8'))

            logger.debug(f"Embedding cache MISS for text hash {text_hash[:8]}")
            return None

        except Exception as e:
            logger.warning(f"Failed to get embedding from cache: {e}")
            return None

    def set_embedding(
        self,
        text: str,
        model: str,
        embedding: List[float],
        ttl: int = 86400 * 30  # 30 days default
    ) -> bool:
        """
        Cache an embedding vector.

        Args:
            text: The text that was embedded
            model: The embedding model used
            embedding: The embedding vector
            ttl: Time-to-live in seconds (default 30 days)

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            text_hash = self._hash_text(text)
            key = self._generate_key("embedding", f"{model}:{text_hash}")

            value = json.dumps(embedding)
            self.client.setex(key, ttl, value)

            logger.debug(f"Cached embedding for text hash {text_hash[:8]}")
            return True

        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
            return False

    def get_query_result(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached diagnostic query result.

        Args:
            query_hash: Hash of the query parameters

        Returns:
            Cached result dictionary or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            key = self._generate_key("query", query_hash)
            cached = self.client.get(key)

            if cached:
                logger.info(f"Query cache HIT for {query_hash[:8]}")
                return json.loads(cached.decode('utf-8'))

            logger.debug(f"Query cache MISS for {query_hash[:8]}")
            return None

        except Exception as e:
            logger.warning(f"Failed to get query from cache: {e}")
            return None

    def set_query_result(
        self,
        query_hash: str,
        result: Dict[str, Any],
        ttl: int = 3600  # 1 hour default
    ) -> bool:
        """
        Cache a diagnostic query result.

        Args:
            query_hash: Hash of the query parameters
            result: The diagnostic result to cache
            ttl: Time-to-live in seconds (default 1 hour)

        Returns:
            True if successfully cached
        """
        if not self.enabled or not self.client:
            return False

        try:
            key = self._generate_key("query", query_hash)
            value = json.dumps(result)
            self.client.setex(key, ttl, value)

            logger.debug(f"Cached query result for {query_hash[:8]}")
            return True

        except Exception as e:
            logger.warning(f"Failed to cache query result: {e}")
            return False

    def increment_metric(self, metric_name: str, amount: int = 1) -> Optional[int]:
        """
        Increment a metric counter.

        Args:
            metric_name: Name of the metric
            amount: Amount to increment (default 1)

        Returns:
            New value or None if failed
        """
        if not self.enabled or not self.client:
            return None

        try:
            key = self._generate_key("metric", metric_name)
            new_value = self.client.incrby(key, amount)
            return new_value

        except Exception as e:
            logger.warning(f"Failed to increment metric {metric_name}: {e}")
            return None

    def get_metric(self, metric_name: str) -> Optional[int]:
        """Get current value of a metric counter"""
        if not self.enabled or not self.client:
            return None

        try:
            key = self._generate_key("metric", metric_name)
            value = self.client.get(key)
            return int(value) if value else 0

        except Exception as e:
            logger.warning(f"Failed to get metric {metric_name}: {e}")
            return None

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "embedding:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            full_pattern = self._generate_key("*", pattern)
            keys = self.client.keys(full_pattern)

            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.client:
            return {"enabled": False}

        try:
            info = self.client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_connections_received": info.get("total_connections_received", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": False, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate as percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create the global Redis cache instance"""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = RedisCache()

    return _cache_instance
