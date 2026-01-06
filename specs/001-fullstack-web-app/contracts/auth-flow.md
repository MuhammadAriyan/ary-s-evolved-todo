# Authentication Flow Contract

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-06
**Version**: 1.0.0

## Overview

This document defines the authentication flow between the Next.js frontend (Better Auth), FastAPI backend, and Neon PostgreSQL database. The system uses JWT tokens with a shared secret for stateless authentication.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

Frontend (Next.js)          Backend (FastAPI)         Database (Neon)
     │                            │                         │
     │                            │                         │
┌────▼────┐                 ┌─────▼─────┐           ┌──────▼──────┐
│ Better  │                 │    JWT    │           │   users     │
│  Auth   │                 │ Middleware│           │   table     │
└─────────┘                 └───────────┘           └─────────────┘
```

---

## Flow Steps

### 1. User Registration (Email/Password)

```
1. User visits /signup page
   ↓
2. User enters email, password, name
   ↓
3. Frontend validates input (client-side)
   ↓
4. Better Auth sends registration request to database
   ↓
5. Database creates user record in users table
   ↓
6. Better Auth generates JWT token:
   {
     "sub": "user_abc123",        # User ID
     "email": "user@example.com",
     "name": "John Doe",
     "iat": 1704537600,           # Issued at (Unix timestamp)
     "exp": 1704624000            # Expires in 24 hours
   }
   ↓
7. JWT signed with BETTER_AUTH_SECRET using HS256 algorithm
   ↓
8. Frontend stores JWT in httpOnly cookie (secure, not accessible via JS)
   ↓
9. User redirected to /todo dashboard
```

**Security Notes**:
- Password hashed with bcrypt before storage
- Email validation on both client and server
- Minimum password length: 8 characters
- httpOnly cookie prevents XSS attacks

---

### 2. User Registration (Google OAuth)

```
1. User visits /signup page
   ↓
2. User clicks "Sign up with Google"
   ↓
3. Frontend redirects to Google OAuth consent screen
   ↓
4. User approves permissions
   ↓
5. Google redirects back with authorization code
   ↓
6. Better Auth exchanges code for Google user info
   ↓
7. Better Auth checks if user exists by email
   ↓
8. If new user: Create user record in database
   If existing: Update last login timestamp
   ↓
9. Better Auth generates JWT token (same format as email/password)
   ↓
10. Frontend stores JWT in httpOnly cookie
   ↓
11. User redirected to /todo dashboard
```

**Security Notes**:
- Google OAuth uses PKCE (Proof Key for Code Exchange)
- State parameter prevents CSRF attacks
- Redirect URI must match registered URI in Google Console

---

### 3. User Login (Email/Password)

```
1. User visits /login page
   ↓
2. User enters email and password
   ↓
3. Frontend validates input (client-side)
   ↓
4. Better Auth queries database for user by email
   ↓
5. Better Auth verifies password hash
   ↓
6. If valid: Generate JWT token
   If invalid: Return 401 Unauthorized
   ↓
7. Frontend stores JWT in httpOnly cookie
   ↓
8. User redirected to /todo dashboard
```

---

### 4. Authenticated API Request

```
1. User navigates to /todo page
   ↓
2. Frontend makes API call: GET /api/v1/tasks
   ↓
3. API client extracts JWT from cookie
   ↓
4. API client adds JWT to Authorization header:
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ↓
5. Request reaches FastAPI backend
   ↓
6. JWT Verification Middleware intercepts request:
   - Extracts token from Authorization header
   - Verifies signature using JWT_SECRET_KEY (must match BETTER_AUTH_SECRET)
   - Checks expiration (exp claim)
   - Decodes payload to get user_id (sub claim)
   ↓
7. If valid:
   - Middleware attaches user object to request.state.user
   - Request proceeds to endpoint handler
   If invalid:
   - Return 401 Unauthorized
   - Frontend redirects to /login
   ↓
8. Endpoint handler uses dependency injection:
   current_user: User = Depends(get_current_user)
   ↓
9. Database query filters by user_id:
   tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
   ↓
10. Response sent back to frontend with only user's tasks
   ↓
11. Frontend displays tasks in UI
```

**Security Notes**:
- JWT signature verification prevents token tampering
- Expiration check prevents use of old tokens
- User isolation enforced at database query level

---

### 5. Token Refresh

```
1. Frontend detects token expiring soon (< 1 hour remaining)
   ↓
2. Frontend makes request to Better Auth refresh endpoint
   ↓
3. Better Auth validates current token
   ↓
4. Better Auth generates new JWT with extended expiration
   ↓
5. Frontend updates cookie with new token
   ↓
6. User continues session without interruption
```

**Note**: Token refresh happens automatically in the background.

---

### 6. User Logout

```
1. User clicks "Logout" button
   ↓
2. Frontend calls Better Auth logout endpoint
   ↓
3. Better Auth invalidates session in database
   ↓
4. Frontend deletes JWT cookie
   ↓
5. User redirected to /login page
   ↓
6. Subsequent API requests fail with 401 Unauthorized
```

---

## JWT Token Structure

### Token Payload

```json
{
  "sub": "user_abc123",           // Subject (user ID)
  "email": "user@example.com",    // User email
  "name": "John Doe",             // User name
  "iat": 1704537600,              // Issued at (Unix timestamp)
  "exp": 1704624000               // Expires at (Unix timestamp, 24 hours later)
}
```

### Token Header

```json
{
  "alg": "HS256",                 // Algorithm (HMAC SHA-256)
  "typ": "JWT"                    // Token type
}
```

### Complete Token Format

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyX2FiYzEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTcwNDUzNzYwMCwiZXhwIjoxNzA0NjI0MDAwfQ.signature
│                                  │                                                                                                                                                      │
│         Header (Base64)          │                                    Payload (Base64)                                                                                                  │  Signature
```

---

## Environment Configuration

### Frontend (.env.local)

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars-long
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@db.neon.tech/todo_db?sslmode=require

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)

```bash
# JWT Configuration (MUST match frontend BETTER_AUTH_SECRET)
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://user:pass@db.neon.tech/todo_db?sslmode=require

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

**CRITICAL**: `BETTER_AUTH_SECRET` (frontend) and `JWT_SECRET_KEY` (backend) MUST be identical for JWT verification to work.

---

## Security Best Practices

### 1. Secret Management
- Use strong secrets (32+ characters, random)
- Never commit secrets to version control
- Use environment variables for all secrets
- Rotate secrets periodically in production

### 2. Token Security
- Store JWT in httpOnly cookies (prevents XSS)
- Use secure flag in production (HTTPS only)
- Set appropriate expiration (24 hours)
- Implement token refresh for long sessions

### 3. Password Security
- Minimum 8 characters
- Hash with bcrypt (cost factor 10+)
- Never log or expose passwords
- Implement rate limiting on login attempts

### 4. OAuth Security
- Use PKCE for authorization code flow
- Validate state parameter (CSRF protection)
- Verify redirect URI matches registered URI
- Store OAuth tokens securely

### 5. API Security
- Verify JWT signature on every request
- Check token expiration
- Enforce user isolation at database level
- Use HTTPS in production
- Implement rate limiting

---

## Error Handling

### Authentication Errors

| Error | HTTP Status | Description | User Action |
|-------|-------------|-------------|-------------|
| Invalid credentials | 401 | Email/password incorrect | Re-enter credentials |
| Token expired | 401 | JWT token has expired | Redirect to login |
| Token invalid | 401 | JWT signature verification failed | Redirect to login |
| Email already exists | 409 | User tried to register with existing email | Use different email or login |
| OAuth error | 400 | Google OAuth flow failed | Retry OAuth flow |

### Frontend Error Handling

```typescript
// frontend/lib/api-client.ts
if (response.status === 401) {
  // Token expired or invalid - redirect to login
  window.location.href = "/login";
  throw new Error("Authentication required");
}
```

---

## Testing Authentication

### Manual Testing Checklist

- [ ] Register with email/password
- [ ] Register with Google OAuth
- [ ] Login with email/password
- [ ] Login with Google OAuth
- [ ] Access protected route without token (should redirect to login)
- [ ] Access protected route with valid token (should succeed)
- [ ] Access protected route with expired token (should redirect to login)
- [ ] Logout and verify token is cleared
- [ ] Try to access another user's tasks (should return 404)

### Automated Testing

```python
# backend/tests/test_auth.py
def test_jwt_verification():
    """Test JWT token verification."""
    # Create valid token
    token = create_jwt_token(user_id="test_user")

    # Verify token
    user_id = verify_token(token)
    assert user_id == "test_user"

    # Test expired token
    expired_token = create_jwt_token(user_id="test_user", expires_in=-1)
    assert verify_token(expired_token) is None

    # Test invalid signature
    invalid_token = token + "tampered"
    assert verify_token(invalid_token) is None
```

---

## Monitoring and Logging

### Authentication Events to Log

- User registration (success/failure)
- User login (success/failure)
- Token refresh
- Token expiration
- Invalid token attempts
- OAuth flow completion

### Example Log Format

```json
{
  "timestamp": "2026-01-06T10:00:00Z",
  "event": "user_login",
  "user_id": "user_abc123",
  "email": "user@example.com",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "status": "success"
}
```

---

**Authentication Flow Status**: ✅ Complete
**Version**: 1.0.0
**Last Updated**: 2026-01-06
