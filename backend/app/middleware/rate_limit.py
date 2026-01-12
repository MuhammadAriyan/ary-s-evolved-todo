"""Rate limiting middleware for chat endpoints."""
import time
from collections import defaultdict
from functools import wraps
from typing import Callable
from fastapi import HTTPException, Request


class RateLimiter:
    """In-memory rate limiter using sliding window algorithm.

    Limits requests per user within a time window.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window (default: 5)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per user: {user_id: [timestamp1, timestamp2, ...]}
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup_old_requests(self, user_id: str, current_time: float) -> None:
        """Remove requests outside the current window.

        Args:
            user_id: The user identifier
            current_time: Current timestamp
        """
        cutoff = current_time - self.window_seconds
        self._requests[user_id] = [
            ts for ts in self._requests[user_id] if ts > cutoff
        ]

    def is_allowed(self, user_id: str) -> bool:
        """Check if a request is allowed for the user.

        Args:
            user_id: The user identifier

        Returns:
            bool: True if request is allowed, False if rate limited
        """
        current_time = time.time()
        self._cleanup_old_requests(user_id, current_time)

        if len(self._requests[user_id]) >= self.max_requests:
            return False

        self._requests[user_id].append(current_time)
        return True

    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for the user in current window.

        Args:
            user_id: The user identifier

        Returns:
            int: Number of remaining requests
        """
        current_time = time.time()
        self._cleanup_old_requests(user_id, current_time)
        return max(0, self.max_requests - len(self._requests[user_id]))

    def get_reset_time(self, user_id: str) -> float:
        """Get seconds until rate limit resets.

        Args:
            user_id: The user identifier

        Returns:
            float: Seconds until oldest request expires from window
        """
        if not self._requests[user_id]:
            return 0

        oldest = min(self._requests[user_id])
        reset_at = oldest + self.window_seconds
        return max(0, reset_at - time.time())


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
