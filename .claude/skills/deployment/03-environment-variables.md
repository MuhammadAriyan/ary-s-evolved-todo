# Environment Variables Configuration

## The Golden Rules

### Rule 1: NEXT_PUBLIC_* is Build-Time Only
```
Frontend (Next.js):
- NEXT_PUBLIC_* vars are embedded INTO the JavaScript bundle at BUILD time
- Changing them in Vercel dashboard requires a REDEPLOY
- They are visible in browser (don't put secrets here!)

Backend:
- All env vars are runtime - changes apply on restart
```

### Rule 2: Match Names Exactly
```
Code says: process.env.NEXT_PUBLIC_APP_URL
Dashboard must have: NEXT_PUBLIC_APP_URL (not NEXT_PUBLIC_API_URL)

One typo = hours of debugging
```

### Rule 3: No Quotes in Dashboard Values
```
WRONG: "https://example.com"
RIGHT: https://example.com

Quotes become part of the value!
```

## Environment Variable Map

### Frontend (Vercel)
| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_APP_URL` | Frontend URL (for auth client) | `https://app.vercel.app` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://backend.hf.space` |
| `DATABASE_URL` | Neon/Postgres connection | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Auth encryption key | `openssl rand -base64 32` |
| `BETTER_AUTH_URL` | Same as APP_URL | `https://app.vercel.app` |
| `GOOGLE_CLIENT_ID` | OAuth (if used) | From Google Console |
| `GOOGLE_CLIENT_SECRET` | OAuth (if used) | From Google Console |

### Backend (HF Spaces)
| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | Same DB as frontend | `postgresql://...` |
| `CORS_ORIGINS` | Allowed frontend URLs | `https://app.vercel.app` |
| `BETTER_AUTH_URL` | Frontend URL (for JWKS) | `https://app.vercel.app` |
| `JWT_SECRET_KEY` | Fallback JWT signing | `openssl rand -base64 32` |
| `AI_API_KEY` | OpenAI-compatible API key | `sk-...` or provider key |
| `AI_BASE_URL` | AI provider endpoint | `https://api.openai.com/v1` |
| `AI_MODEL` | Model to use | `gpt-4o-mini` |

## Generating Secrets
```bash
# Generate a secure random secret
openssl rand -base64 32

# Example output: JMvSe2tp1vVXIL/pOkO538t55RwflC33n+I6tRrV7hY=
```

## Common Patterns

### Pattern 1: Shared Database
```
Frontend and Backend use SAME DATABASE_URL
- Frontend: Better Auth stores users/sessions
- Backend: Stores application data (tasks, etc.)
- Both connect to same Neon PostgreSQL
```

### Pattern 2: Auth Flow
```
1. User logs in on Frontend (Better Auth)
2. Frontend gets JWT from Better Auth
3. Frontend sends JWT to Backend API
4. Backend verifies JWT via JWKS from Frontend
5. Backend trusts the user

BETTER_AUTH_URL on backend = Frontend URL (where JWKS lives)
```

### Pattern 3: CORS Configuration
```
Backend must allow Frontend origin:
CORS_ORIGINS = https://your-frontend.vercel.app

Multiple origins (comma-separated):
CORS_ORIGINS = https://app.vercel.app,https://staging.vercel.app
```

## Debugging Env Vars

### Check if var is set (Frontend)
```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
// If undefined, var not set or not prefixed with NEXT_PUBLIC_
```

### Check if var is set (Backend)
```python
from app.config import settings
print(f"CORS: {settings.cors_origins}")
print(f"Auth URL: {settings.better_auth_url}")
```

### Verify in Network Tab
```
1. Open Browser DevTools → Network
2. Look at request URLs
3. If going to localhost, env var not applied
4. Redeploy if you just added the var
```
