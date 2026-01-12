# Vercel Frontend Deployment

## Prerequisites
- GitHub repository with Next.js app
- Vercel account linked to GitHub

## Deployment Steps

### 1. Connect Repository to Vercel
```
1. Go to https://vercel.com/dashboard
2. Click "Add New → Project"
3. Import your GitHub repository
4. Configure:
   - Root Directory: `frontend` (if monorepo)
   - Framework: Next.js (auto-detected)
   - Project Name: your-app-name (becomes URL: your-app-name.vercel.app)
5. Add environment variables BEFORE first deploy
6. Click Deploy
```

### 2. Environment Variables (CRITICAL)
```
NEXT_PUBLIC_* vars are embedded at BUILD TIME, not runtime!

Required vars:
- NEXT_PUBLIC_APP_URL = https://your-app.vercel.app
- NEXT_PUBLIC_API_URL = https://your-backend-url
- DATABASE_URL = your-db-connection-string
- BETTER_AUTH_SECRET = your-auth-secret (if using Better Auth)
```

### 3. Custom Domain (Optional)
```
1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS as instructed
```

## Mistakes Made & Fixes

### Mistake 1: Root Directory Not Set
**Error:**
```
Error: No Next.js version detected. Make sure your package.json has "next"
```
**Cause:** Vercel tried to build from repo root instead of `frontend/` folder
**Fix:** Set Root Directory to `frontend` in Project Settings

### Mistake 2: Hardcoded localhost URLs
**Error:**
```
POST http://localhost:3004/api/auth/sign-up/email net::ERR_CONNECTION_REFUSED
```
**Cause:** Auth client had hardcoded `baseURL: "http://localhost:3004"`
**Fix:** Use environment variable:
```typescript
baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3004"
```

### Mistake 3: Env Vars Not Applied
**Symptom:** Still connecting to localhost after adding env vars
**Cause:** `NEXT_PUBLIC_*` vars are embedded at build time
**Fix:** Redeploy after adding/changing env vars - auto-deploy won't pick up new vars

### Mistake 4: Wrong Env Var Name
**Symptom:** API calls going to wrong URL
**Cause:** Code used `NEXT_PUBLIC_APP_URL` but Vercel had `NEXT_PUBLIC_API_URL`
**Fix:** Ensure env var names match exactly between code and Vercel dashboard

## Verification Checklist
- [ ] Site loads at https://your-app.vercel.app
- [ ] No localhost errors in browser console
- [ ] Auth flow works (signup/login)
- [ ] API calls go to correct backend URL
- [ ] GitHub pushes trigger auto-deploy
