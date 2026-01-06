"""JWT authentication middleware."""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import verify_token

security = HTTPBearer()


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Verify JWT token from Authorization header and return user_id."""
    token = credentials.credentials
    print(f"🔍 Received token (first 50 chars): {token[:50]}...")

    user_id = verify_token(token)

    if not user_id:
        print(f"❌ Token verification failed - no user_id returned")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"✅ Token verified successfully for user: {user_id}")
    return user_id
