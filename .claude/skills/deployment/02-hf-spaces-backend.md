# Hugging Face Spaces Backend Deployment

## Prerequisites
- HF account with write token
- Docker-based backend (FastAPI, Flask, etc.)
- `Dockerfile` in backend directory

## Deployment Steps

### 1. Create HF Space
```
1. Go to https://huggingface.co/new-space
2. Choose:
   - Owner: your-username
   - Space name: your-backend-name
   - SDK: Docker
   - Hardware: CPU Basic (free)
   - Visibility: Public (or Private with Pro)
3. Create Space
```

### 2. Prepare Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces REQUIRES port 7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 3. Deploy via CLI
```bash
# Install HF CLI
pip install huggingface_hub

# Login (or use token)
huggingface-cli login

# Upload backend folder to Space
huggingface-cli upload username/space-name ./backend . --repo-type space

# Or with pipx (no install needed)
pipx run --spec huggingface-hub hf upload username/space-name ./backend . --repo-type space
```

### 4. Configure Secrets
```
1. Go to https://huggingface.co/spaces/username/space-name/settings
2. Add Repository secrets:
   - DATABASE_URL
   - CORS_ORIGINS
   - BETTER_AUTH_URL
   - JWT_SECRET_KEY
   - Any other env vars
3. Space auto-rebuilds after adding secrets
```

### 5. Verify Deployment
```bash
# Check Space status
curl https://huggingface.co/api/spaces/username/space-name/runtime

# Health check
curl https://username-space-name.hf.space/health
```

## Mistakes Made & Fixes

### Mistake 1: Wrong Port
**Error:** Space builds but returns 503
**Cause:** Using port 8000 instead of 7860
**Fix:** HF Spaces REQUIRES port 7860
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Mistake 2: Pydantic List Type for Env Vars
**Error:**
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins" from source "EnvSettingsSource"
```
**Cause:** Pydantic Settings can't parse `List[str]` from env var string
**Fix:** Use `str` type and parse manually:
```python
# BAD - doesn't work with env vars
cors_origins: List[str] = ["http://localhost:3000"]

# GOOD - works with env vars
cors_origins: str = "http://localhost:3000"

def get_cors_origins_list(self) -> list[str]:
    return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
```

### Mistake 3: Missing Default Values
**Error:** Space crashes on startup - missing required env vars
**Cause:** Required fields without defaults fail if env var not set
**Fix:** Add sensible defaults:
```python
jwt_secret_key: str = "dev-secret-change-in-production"
database_url: str = ""
cors_origins: str = "http://localhost:3000"
```

### Mistake 4: CORS Not Configured
**Error:** Frontend gets CORS errors
**Cause:** Backend CORS_ORIGINS doesn't include frontend URL
**Fix:** Add frontend URL to HF Space secrets:
```
CORS_ORIGINS = https://your-frontend.vercel.app
```

### Mistake 5: JWT Verification Fails
**Error:** 401 Unauthorized on all API calls
**Cause:** Backend can't reach Better Auth JWKS endpoint
**Fix:** Set BETTER_AUTH_URL to frontend URL where Better Auth runs:
```
BETTER_AUTH_URL = https://your-frontend.vercel.app
```

## Space Status Codes
| Stage | Meaning |
|-------|---------|
| BUILDING | Docker image being built |
| RUNNING | Space is live |
| RUNTIME_ERROR | Crashed - check logs |
| SLEEPING | Inactive, will wake on request |

## Verification Checklist
- [ ] Space status is RUNNING
- [ ] Health endpoint returns 200
- [ ] CORS allows frontend origin
- [ ] JWT verification works
- [ ] Database connection works
