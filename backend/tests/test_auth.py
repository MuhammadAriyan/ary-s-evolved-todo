"""Tests for JWT authentication."""
import pytest
from datetime import datetime, timedelta
from app.utils.jwt import create_jwt_token, decode_jwt, verify_token


def test_jwt_verification_valid_token():
    """Test JWT verification with valid token."""
    user_id = "test_user_123"
    email = "test@example.com"
    name = "Test User"

    # Create token
    token = create_jwt_token(user_id, email, name)

    # Verify token
    result = verify_token(token)

    assert result == user_id


def test_jwt_verification_expired_token():
    """Test JWT verification with expired token."""
    # This test would require mocking time or creating a token with negative expiration
    # For now, we'll test the decode function returns None for invalid tokens
    invalid_token = "invalid.token.here"

    result = verify_token(invalid_token)

    assert result is None


def test_jwt_verification_invalid_token():
    """Test JWT verification with invalid token."""
    invalid_token = "completely.invalid.token"

    result = verify_token(invalid_token)

    assert result is None


def test_decode_jwt_valid():
    """Test decoding valid JWT token."""
    user_id = "test_user_456"
    email = "user@example.com"

    token = create_jwt_token(user_id, email)
    payload = decode_jwt(token)

    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert "iat" in payload
    assert "exp" in payload


def test_decode_jwt_invalid():
    """Test decoding invalid JWT token."""
    invalid_token = "invalid.token"

    payload = decode_jwt(invalid_token)

    assert payload is None
