# Deployment Checklist

## Pre-Deployment

### Code Ready
- [ ] All changes committed and pushed
- [ ] No hardcoded localhost URLs
- [ ] Environment variables use `process.env.*`
- [ ] Build passes locally

### Frontend Checklist
- [ ] `NEXT_PUBLIC_APP_URL` configured
- [ ] `NEXT_PUBLIC_API_URL` points to backend
- [ ] `DATABASE_URL` set (if using DB)
- [ ] Auth secrets configured
- [ ] Root directory set correctly in Vercel

### Backend Checklist
- [ ] Dockerfile uses port 7860
- [ ] `requirements.txt` complete (includes AI dependencies)
- [ ] `CORS_ORIGINS` includes frontend URL
- [ ] `BETTER_AUTH_URL` points to frontend
- [ ] `DATABASE_URL` set
- [ ] `AI_API_KEY` set (OpenAI-compatible key)
- [ ] `AI_BASE_URL` set (provider endpoint)
- [ ] `AI_MODEL` set (e.g., gpt-4o-mini)
- [ ] Health endpoint exists at `/health`

## Post-Deployment

### Frontend Verification
- [ ] Site loads without errors
- [ ] No localhost in Network tab
- [ ] Auth flow works
- [ ] API calls succeed

### Backend Verification
- [ ] Health check returns 200
- [ ] Space status is RUNNING
- [ ] CORS allows frontend
- [ ] JWT verification works
- [ ] Database queries work

## Rollback Plan

### Frontend (Vercel)
```
1. Go to Deployments tab
2. Find last working deployment
3. Click "..." → "Promote to Production"
```

### Backend (HF Spaces)
```
1. Go to Space Files tab
2. Click History
3. Revert to previous commit
```
