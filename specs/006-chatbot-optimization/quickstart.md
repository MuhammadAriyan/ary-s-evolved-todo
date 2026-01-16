# Quickstart: Deploying AI Chatbot to Production

**Feature**: 006-chatbot-optimization
**Last Updated**: 2026-01-16

This guide walks through deploying the optimized AI chatbot to production using Vercel (frontend) and HuggingFace Spaces (backend).

## Prerequisites

- Node.js 18+ installed
- Python 3.12+ installed
- Git installed
- Vercel account (free tier)
- HuggingFace account (free tier)
- Neon PostgreSQL database (existing)

## Environment Variables

### Frontend (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.hf.space
BETTER_AUTH_URL=https://your-frontend-url.vercel.app
BETTER_AUTH_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Backend (HuggingFace Spaces)

```bash
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=your-openai-api-key
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

## Deployment Steps

### Step 1: Deploy Frontend to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

4. **Deploy to production**:
   ```bash
   vercel --prod
   ```

5. **Set environment variables** in Vercel dashboard:
   - Go to Project Settings → Environment Variables
   - Add all frontend environment variables
   - Redeploy: `vercel --prod`

6. **Verify deployment**:
   - Visit your Vercel URL
   - Check that all optimizations are applied (FCP < 1s, bundle < 5MB)
   - Test authentication flow

### Step 2: Deploy Backend to HuggingFace Spaces

1. **Create HuggingFace account**:
   - Visit https://huggingface.co/join
   - Verify email

2. **Create new Space**:
   - Go to https://huggingface.co/new-space
   - Name: `todo-chatbot-backend`
   - SDK: Docker
   - Visibility: Public or Private

3. **Clone Space repository**:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-chatbot-backend
   cd todo-chatbot-backend
   ```

4. **Copy backend files**:
   ```bash
   cp -r /path/to/backend/* .
   ```

5. **Ensure Dockerfile and README.md exist**:
   - `Dockerfile` should expose port 7860
   - `README.md` should have HF Spaces metadata

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push
   ```

7. **Set environment variables** in HF Spaces settings:
   - Go to Space Settings → Variables
   - Add all backend environment variables

8. **Wait for auto-deploy**:
   - HF Spaces will automatically build and deploy
   - Check logs for any errors

9. **Verify deployment**:
   - Visit your HF Spaces URL
   - Test health endpoint: `https://your-space.hf.space/health`
   - Test chat endpoint with authentication

### Step 3: Configure CORS

1. **Update Vercel configuration**:
   - Edit `frontend/vercel.json`
   - Update `rewrites` destination to your HF Spaces URL

2. **Update backend CORS**:
   - Ensure `CORS_ORIGINS` includes your Vercel URL
   - Restart HF Space if needed

3. **Test cross-origin requests**:
   - Open browser DevTools → Network tab
   - Send a chat message
   - Verify no CORS errors

### Step 4: Performance Validation

1. **Run Lighthouse audit**:
   ```bash
   npm install -g lighthouse
   lighthouse https://your-frontend-url.vercel.app --view
   ```

2. **Check Core Web Vitals**:
   - FCP should be < 1s
   - LCP should be < 2s
   - TTI should be < 2s
   - TBT should be < 400ms

3. **Verify bundle size**:
   ```bash
   cd frontend
   npm run analyze
   ```
   - Total bundle should be < 5MB

4. **Test compression**:
   - Open DevTools → Network tab
   - Check `Content-Encoding: gzip` header
   - Verify 70% size reduction

### Step 5: Functional Testing

1. **Test authentication**:
   - Sign up with Google OAuth
   - Verify session persists
   - Test logout

2. **Test chat functionality**:
   - Send a message
   - Verify streaming works smoothly
   - Check agent icons display correctly
   - Verify no scroll jank

3. **Test UI polish**:
   - Check custom scrollbar (purple theme)
   - Verify avatar colors (purple/magenta)
   - Check Google icon on login
   - Check ClipboardList icon in navbar

4. **Test production features**:
   - Simulate network failure (DevTools → Network → Offline)
   - Verify retry logic works
   - Check session caching (no redundant API calls)

## Monitoring

### Web Vitals

Web Vitals are logged in development mode. For production monitoring:

1. **Add analytics service** (optional):
   - Vercel Analytics (built-in)
   - Google Analytics
   - Custom monitoring

2. **Check metrics**:
   - FCP, LCP, TTI, TBT, CLS
   - Track over time
   - Alert on regressions

### Error Tracking

1. **Check Vercel logs**:
   - Go to Vercel dashboard → Logs
   - Monitor for errors

2. **Check HF Spaces logs**:
   - Go to HF Space → Logs
   - Monitor for errors

## Rollback Procedure

### Frontend Rollback

1. **Via Vercel dashboard**:
   - Go to Deployments
   - Find previous working deployment
   - Click "Promote to Production"

2. **Via CLI**:
   ```bash
   vercel rollback
   ```

### Backend Rollback

1. **Via Git**:
   ```bash
   git revert HEAD
   git push
   ```

2. **HF Spaces will auto-deploy** the reverted version

## Troubleshooting

### Frontend Issues

**Issue**: Bundle size still > 5MB
- **Solution**: Run `npm run analyze` and check for large dependencies
- Verify Three.js shader is lazy-loaded
- Check webpack config

**Issue**: Fonts not loading
- **Solution**: Verify `next/font` import in `layout.tsx`
- Check font fallbacks
- Clear browser cache

**Issue**: Scroll jank during streaming
- **Solution**: Verify debouncing logic in `MessageThread.tsx`
- Check scroll event count (should be ≤10)
- Test in different browsers

### Backend Issues

**Issue**: Port 7860 not accessible
- **Solution**: Verify Dockerfile exposes port 7860
- Check HF Spaces logs for errors
- Ensure `uvicorn` binds to `0.0.0.0`

**Issue**: CORS errors
- **Solution**: Verify `CORS_ORIGINS` includes Vercel URL
- Check backend CORS middleware
- Test with curl: `curl -H "Origin: https://your-vercel-url" https://your-hf-space/health`

### Integration Issues

**Issue**: Frontend can't reach backend
- **Solution**: Verify `vercel.json` rewrites
- Check `NEXT_PUBLIC_API_URL` environment variable
- Test backend URL directly

**Issue**: Authentication fails
- **Solution**: Verify `BETTER_AUTH_SECRET` matches on both sides
- Check `BETTER_AUTH_URL` points to Vercel URL
- Test Google OAuth credentials

## Performance Benchmarks

### Expected Metrics (After Optimization)

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| FCP | < 1s | 0.8-1.2s |
| LCP | < 2s | 1.5-2.0s |
| TTI | < 2s | 2-3s |
| TBT | < 400ms | 200-400ms |
| CLS | < 0.1 | 0.05-0.10 |
| Bundle Size | < 5MB | 3-5MB |
| Scroll Events | ≤ 10 | 5-10 per response |

### Baseline Metrics (Before Optimization)

| Metric | Baseline |
|--------|----------|
| FCP | 2.5-3.5s |
| LCP | 3.5-4.5s |
| TTI | 4-6s |
| TBT | 800-1200ms |
| CLS | 0.15-0.25 |
| Bundle Size | 38MB |
| Scroll Events | 100+ per response |

## Next Steps

After successful deployment:

1. **Monitor performance** for 24-48 hours
2. **Collect user feedback** on perceived performance
3. **Track Web Vitals** in production
4. **Iterate on optimizations** if needed
5. **Document lessons learned** in PHR

## Support

For issues or questions:
- Check HF Spaces logs: https://huggingface.co/spaces/YOUR_USERNAME/todo-chatbot-backend/logs
- Check Vercel logs: https://vercel.com/YOUR_USERNAME/YOUR_PROJECT/logs
- Review implementation plan: `specs/006-chatbot-optimization/plan.md`
- Review specification: `specs/006-chatbot-optimization/spec.md`
