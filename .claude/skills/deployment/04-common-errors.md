# Common Deployment Errors Catalog

## Frontend Errors (Vercel/Next.js)

### ERR_001: No Next.js Version Detected
```
Error: No Next.js version detected. Make sure your package.json has "next"
```
**Cause:** Wrong root directory in Vercel settings
**Fix:** Set Root Directory to folder containing package.json (e.g., `frontend`)

---

### ERR_002: Module Not Found During Build
```
Module not found: Can't resolve '@/components/ui/canvas'
```
**Cause:** File missing from repository or not committed
**Fix:**
1. Check if file exists locally
2. `git status` to see if it's untracked
3. `git add` and push the missing file

---

### ERR_003: localhost Connection Refused
```
POST http://localhost:3004/api/auth/sign-up/email net::ERR_CONNECTION_REFUSED
```
**Cause:** Hardcoded localhost URL or missing env var
**Fix:**
1. Find hardcoded URLs: `grep -r "localhost" --include="*.ts" --include="*.tsx"`
2. Replace with `process.env.NEXT_PUBLIC_*`
3. Add env var to Vercel
4. REDEPLOY (env vars are build-time)

---

### ERR_004: GitHub Actions Deprecated
```
This request has been automatically failed because it uses a deprecated version of actions/upload-artifact: v3
```
**Cause:** Using old GitHub Action versions
**Fix:** Update to v4:
```yaml
# OLD
uses: actions/upload-artifact@v3

# NEW
uses: actions/upload-artifact@v4
```

---

## Backend Errors (HF Spaces)

### ERR_101: Space Returns 503
```
curl returns 503 Service Unavailable
```
**Cause:** Space still building OR crashed
**Fix:**
1. Check status: `curl https://huggingface.co/api/spaces/user/space/runtime`
2. If BUILDING, wait
3. If RUNTIME_ERROR, check error message in response

---

### ERR_102: Pydantic Settings Parse Error
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins"
```
**Cause:** Using `List[str]` type for env var
**Fix:** Use `str` type and parse manually:
```python
cors_origins: str = "http://localhost:3000"

def get_cors_origins_list(self) -> list[str]:
    return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
```

---

### ERR_103: Port 7860 Required
```
Space builds but never becomes healthy
```
**Cause:** Using wrong port (not 7860)
**Fix:** HF Spaces REQUIRES port 7860:
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

### ERR_104: Alembic Migration Fails
```
alembic.util.exc.CommandError: Can't locate revision
```
**Cause:** Missing migration files or wrong alembic config
**Fix:**
1. Ensure `alembic/` folder is uploaded
2. Check `alembic.ini` has correct `script_location`
3. Verify DATABASE_URL is set in secrets

---

## Auth Errors

### ERR_201: 401 Unauthorized on API Calls
```
GET /api/v1/tasks returns 401
```
**Cause:** JWT verification failing
**Fix:**
1. Check BETTER_AUTH_URL on backend points to frontend
2. Verify frontend is sending Authorization header
3. Check browser console for JWT token logs

---

### ERR_202: CORS Error
```
Access to fetch blocked by CORS policy
```
**Cause:** Backend doesn't allow frontend origin
**Fix:** Add frontend URL to CORS_ORIGINS on backend:
```
CORS_ORIGINS = https://your-frontend.vercel.app
```

---

### ERR_203: JWKS Fetch Failed
```
JWT decode error: Unable to fetch JWKS
```
**Cause:** Backend can't reach frontend's JWKS endpoint
**Fix:**
1. Verify BETTER_AUTH_URL is correct
2. Check frontend is deployed and accessible
3. Test: `curl https://frontend.vercel.app/api/auth/jwks`

---

## Database Errors

### ERR_301: Connection Refused
```
psycopg2.OperationalError: could not connect to server
```
**Cause:** Wrong DATABASE_URL or network issues
**Fix:**
1. Verify DATABASE_URL format: `postgresql://user:pass@host/db?sslmode=require`
2. Check Neon dashboard for correct connection string
3. Ensure `?sslmode=require` is included

---

### ERR_302: Relation Does Not Exist
```
relation "users" does not exist
```
**Cause:** Migrations not run
**Fix:**
1. Run migrations: `alembic upgrade head`
2. For HF Spaces, add to Dockerfile CMD:
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 7860"]
```

---

## Quick Diagnosis Commands

```bash
# Check HF Space status
curl -s https://huggingface.co/api/spaces/USER/SPACE/runtime | python3 -c "import sys,json; d=json.load(sys.stdin); print('Stage:', d.get('stage')); print('Error:', d.get('errorMessage','None')[:200] if d.get('errorMessage') else 'None')"

# Check backend health
curl https://USER-SPACE.hf.space/health

# Check frontend
curl -I https://app.vercel.app

# Find hardcoded URLs
grep -r "localhost" --include="*.ts" --include="*.tsx" --include="*.py"
```
