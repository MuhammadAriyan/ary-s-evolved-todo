"""
Rate limiting middleware using Redis state store via Dapr.

Implements token bucket algorithm for distributed rate limiting.
"""

from fastapi import Request, HTTPException
from dapr.clients import DaprClient
from datetime import datetime
import logging
from typing import Optional
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting using Redis state store via Dapr for distributed rate limiting"""

    def __init__(self, store_name: str = "redis-state", max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            store_name: Dapr state store name (default: redis-state)
            max_requests: Maximum requests allowed per window (default: 100)
            window_seconds: Time window in seconds (default: 60)
        """
        self.store_name = store_name
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check_rate_limit(
        self,
        user_id: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None
    ) -> tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier
            limit: Maximum requests per window (uses instance default if None)
            window_seconds: Time window in seconds (uses instance default if None)

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        limit = limit or self.max_requests
        window_seconds = window_seconds or self.window_seconds

        try:
            async with DaprClient() as client:
                # Use minute-based key for rate limiting
                current_minute = datetime.utcnow().strftime('%Y%m%d%H%M')
                key = f"rate_limit:{user_id}:{current_minute}"

                # Get current count
                state = await client.get_state(
                    store_name=self.store_name,
                    key=key
                )

                count = int(state.data.decode('utf-8')) if state.data else 0

                if count >= limit:
                    logger.warning(
                        f"Rate limit exceeded for user {user_id}",
                        extra={"user_id": user_id, "count": count, "limit": limit}
                    )
                    # Calculate seconds until reset
                    reset_time = window_seconds - (datetime.utcnow().second)
                    return False, 0, reset_time

                # Increment count
                new_count = count + 1
                await client.save_state(
                    store_name=self.store_name,
                    key=key,
                    value=str(new_count),
                    state_metadata={"ttlInSeconds": str(window_seconds)}
                )

                remaining = limit - new_count
                reset_time = window_seconds - (datetime.utcnow().second)

                return True, remaining, reset_time

        except Exception as e:
            logger.error(
                f"Rate limit check failed: {e}",
                extra={"user_id": user_id},
                exc_info=True
            )
            # Fail open - allow request if rate limiter is down
            return True, limit, window_seconds

    def is_allowed(self, user_id: str) -> bool:
        """Legacy sync method for backward compatibility - not recommended for async code"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            allowed, _, _ = loop.run_until_complete(
                self.check_rate_limit(user_id, self.max_requests, self.window_seconds)
            )
            return allowed
        except Exception:
            return True

    def get_remaining(self, user_id: str) -> int:
        """Legacy sync method for backward compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            _, remaining, _ = loop.run_until_complete(
                self.check_rate_limit(user_id, self.max_requests, self.window_seconds)
            )
            return remaining
        except Exception:
            return self.max_requests

    def get_reset_time(self, user_id: str) -> float:
        """Legacy sync method for backward compatibility"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            _, _, reset_time = loop.run_until_complete(
                self.check_rate_limit(user_id, self.max_requests, self.window_seconds)
            )
            return float(reset_time)
        except Exception:
            return 0.0


# Global rate limiter instance for chat messages (5 per minute)
chat_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


def rate_limit(limiter: RateLimiter = chat_rate_limiter):
    """Decorator to apply rate limiting to an endpoint.

    Args:
        limiter: RateLimiter instance to use

    Returns:
        Decorator function

    Usage:
        @router.post("/messages")
        @rate_limit()
        async def send_message(request: Request, user_id: str = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs (set by dependency injection)
            user_id = kwargs.get("current_user_id") or kwargs.get("user_id")

            if not user_id:
                # Try to get from request state if available
                request = kwargs.get("request")
                if request and hasattr(request, "state") and hasattr(request.state, "user_id"):
                    user_id = request.state.user_id

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="User identification required for rate limiting"
                )

            if not limiter.is_allowed(user_id):
                reset_time = limiter.get_reset_time(user_id)
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {int(reset_time)} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(limiter.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)),
                    }
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_rate_limit(user_id: str, limiter: RateLimiter = chat_rate_limiter) -> None:
    """Check rate limit and raise exception if exceeded.

    Alternative to decorator for more control.

    Args:
        user_id: The user identifier
        limiter: RateLimiter instance to use

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not limiter.is_allowed(user_id):
        reset_time = limiter.get_reset_time(user_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {int(reset_time)} seconds.",
            headers={
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time)),
            }
        )
