"""JWT utility functions for token verification using Better Auth JWKS."""
import jwt
from jwt import PyJWKClient
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import lru_cache
from app.config import settings


@lru_cache(maxsize=1)
def _get_cached_jwk_client() -> PyJWKClient:
    """Get cached JWKS client to fetch public keys from Better Auth."""
    # Better Auth JWKS endpoint
    jwks_url = f"{settings.better_auth_url}/api/auth/jwks"
    return PyJWKClient(jwks_url)


def decode_jwt(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token using Better Auth JWKS.

    Better Auth uses EdDSA (Ed25519) for signing tokens.
    The public key is fetched from the JWKS endpoint.
    """
    try:
        # Get JWKS client and fetch signing key
        jwk_client = _get_cached_jwk_client()
        signing_key = jwk_client.get_signing_key_from_jwt(token)

        # Verify signature and decode payload
        # Better Auth uses EdDSA (Ed25519) or RS256
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256"],
            options={"verify_aud": False}  # Better Auth doesn't use audience claim
        )

        print(f"✅ JWT decoded successfully. User ID: {payload.get('sub')}")
        return payload
    except jwt.InvalidTokenError as e:
        print(f"❌ JWT InvalidTokenError: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ JWT decode error: {type(e).__name__}: {str(e)}")
        return None


def verify_token(token: str) -> Optional[str]:
    """
    Verify token and return user_id if valid.

    Returns:
        user_id (str) if token is valid, None otherwise
    """
    payload = decode_jwt(token)
    if payload:
        # Better Auth uses 'sub' claim for user_id
        return payload.get("sub")
    return None


def get_user_info_from_token(token: str) -> Optional[Dict[str, str]]:
    """
    Extract user information from JWT token.

    Returns:
        dict with user_id and email if valid, None otherwise
    """
    payload = decode_jwt(token)
    if payload:
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email", ""),
        }
    return None


# Legacy function for backward compatibility (not used with Better Auth)
def create_jwt_token(user_id: str, email: str, name: Optional[str] = None) -> str:
    """
    Create a JWT token for a user.

    NOTE: This is not used with Better Auth. Better Auth generates its own tokens.
    This function is kept for backward compatibility only.
    """
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
