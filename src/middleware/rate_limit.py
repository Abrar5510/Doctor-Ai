"""
Rate limiting middleware for API protection.

This module provides rate limiting capabilities to prevent API abuse
and DoS attacks.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta, timezone
import asyncio
from collections import defaultdict

from src.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using in-memory storage.

    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(self, app, requests_per_minute: int = 100):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests allowed per minute
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client.

        Args:
            request: FastAPI request object

        Returns:
            Client identifier (IP address or user ID)
        """
        # Try to get authenticated user first
        # In production, extract from JWT token
        client_ip = request.client.host if request.client else "unknown"

        # Get forwarded IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return client_ip

    def _cleanup_old_requests(self, identifier: str):
        """
        Remove requests older than 1 minute.

        Args:
            identifier: Client identifier
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)

        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if req_time > cutoff
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response or rate limit error
        """
        settings = get_settings()

        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for health checks and docs
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client identifier
        identifier = self._get_client_identifier(request)

        async with self.lock:
            # Cleanup old requests
            self._cleanup_old_requests(identifier)

            # Check rate limit
            request_count = len(self.requests[identifier])

            if request_count >= self.requests_per_minute:
                # Calculate retry after time
                if self.requests[identifier]:
                    oldest_request = min(self.requests[identifier])
                    retry_after = int((oldest_request + timedelta(minutes=1) - datetime.now(timezone.utc)).total_seconds())
                else:
                    retry_after = 60

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

            # Record this request
            self.requests[identifier].append(datetime.now(timezone.utc))

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        async with self.lock:
            remaining = self.requests_per_minute - len(self.requests[identifier])

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(
            int((datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp())
        )

        return response


class IPWhitelist:
    """IP whitelist for rate limit exemptions."""

    def __init__(self):
        """Initialize with default whitelisted IPs."""
        self.whitelist = {
            "127.0.0.1",  # Localhost
            "::1",  # IPv6 localhost
        }

    def add(self, ip: str):
        """Add IP to whitelist."""
        self.whitelist.add(ip)

    def remove(self, ip: str):
        """Remove IP from whitelist."""
        self.whitelist.discard(ip)

    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        return ip in self.whitelist
