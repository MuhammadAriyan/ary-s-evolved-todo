"""Unit tests for rate limiter middleware."""
import pytest
import time
from unittest.mock import patch

from app.middleware.rate_limit import RateLimiter, chat_rate_limiter


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        user_id = "test-user-1"

        # Should allow 5 requests
        for i in range(5):
            assert limiter.is_allowed(user_id) is True

    def test_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        user_id = "test-user-2"

        # Allow first 3 requests
        for i in range(3):
            assert limiter.is_allowed(user_id) is True

        # Block 4th request
        assert limiter.is_allowed(user_id) is False

    def test_different_users_have_separate_limits(self):
        """Test that different users have independent rate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        # User 1 uses their limit
        assert limiter.is_allowed("user-1") is True
        assert limiter.is_allowed("user-1") is True
        assert limiter.is_allowed("user-1") is False

        # User 2 should still have their full limit
        assert limiter.is_allowed("user-2") is True
        assert limiter.is_allowed("user-2") is True
        assert limiter.is_allowed("user-2") is False

    def test_window_expiration_allows_new_requests(self):
        """Test that requests are allowed after window expires."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        user_id = "test-user-3"

        # Use up the limit
        assert limiter.is_allowed(user_id) is True
        assert limiter.is_allowed(user_id) is True
        assert limiter.is_allowed(user_id) is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should allow new requests
        assert limiter.is_allowed(user_id) is True

    def test_get_remaining_returns_correct_count(self):
        """Test that get_remaining returns correct remaining requests."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        user_id = "test-user-4"

        assert limiter.get_remaining(user_id) == 5

        limiter.is_allowed(user_id)
        assert limiter.get_remaining(user_id) == 4

        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)
        assert limiter.get_remaining(user_id) == 2

    def test_get_reset_time_returns_positive_value(self):
        """Test that get_reset_time returns time until reset."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user_id = "test-user-5"

        # No requests yet
        assert limiter.get_reset_time(user_id) == 0

        # Make a request
        limiter.is_allowed(user_id)

        # Reset time should be positive (close to window_seconds)
        reset_time = limiter.get_reset_time(user_id)
        assert 0 < reset_time <= 60

    def test_sliding_window_behavior(self):
        """Test that the sliding window correctly expires old requests."""
        limiter = RateLimiter(max_requests=3, window_seconds=2)
        user_id = "test-user-6"

        # Make 3 requests
        assert limiter.is_allowed(user_id) is True
        time.sleep(0.5)
        assert limiter.is_allowed(user_id) is True
        time.sleep(0.5)
        assert limiter.is_allowed(user_id) is True

        # Should be blocked
        assert limiter.is_allowed(user_id) is False

        # Wait for first request to expire (2 seconds from first request)
        time.sleep(1.1)

        # Should allow one more request (first one expired)
        assert limiter.is_allowed(user_id) is True


class TestChatRateLimiter:
    """Tests for the global chat rate limiter."""

    def test_chat_limiter_has_correct_config(self):
        """Test that chat_rate_limiter has correct configuration."""
        assert chat_rate_limiter.max_requests == 5
        assert chat_rate_limiter.window_seconds == 60
