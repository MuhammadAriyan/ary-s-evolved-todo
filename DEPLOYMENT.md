# Deployment Guide

This guide covers deploying the full-stack todo application to production environments.

## Table of Contents

1. [Quick Start Deployment](#quick-start-deployment)
2. [Prerequisites](#prerequisites)
3. [Database Setup (Neon)](#database-setup-neon)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment](#post-deployment)

## Quick Start Deployment

**Optimized for Vercel (Frontend) + HuggingFace Spaces (Backend)**

### 1. Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel --prod

# Set environment variables
vercel env add BETTER_AUTH_URL
vercel env add BETTER_AUTH_SECRET
vercel env add DATABASE_URL
vercel env add GOOGLE_CLIENT_ID
vercel env add GOOGLE_CLIENT_SECRET
vercel env add NEXT_PUBLIC_API_URL

# Redeploy with environment variables
vercel --prod
```

### 2. Deploy Backend to HuggingFace Spaces

```bash
# Create new Space at https://huggingface.co/spaces
# Choose: Docker SDK, CPU basic (free)

# Add repository secrets in Space settings:
# - DATABASE_URL
# - CORS_ORIGINS (your Vercel domain)
# - BETTER_AUTH_URL (your Vercel domain)
# - JWT_SECRET_KEY
# - AI_API_KEY (optional, for chatbot)

# Push to HuggingFace
cd backend
git init
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
git add .
git commit -m "Deploy backend"
git push hf main
```

### 3. Verify Deployment

```bash
# Check backend health (basic liveness)
curl https://YOUR_USERNAME-SPACE_NAME.hf.space/health
# Expected: {"status": "healthy"}

# Check backend readiness (database + OpenAI API)
curl https://YOUR_USERNAME-SPACE_NAME.hf.space/health/ready
# Expected: {"status": "ready", "checks": {...}}

# Check frontend
open https://your-app.vercel.app

# Test CORS
# Open browser DevTools → Network tab
# Send a message in chat
# Verify no CORS errors
```

### 4. Update Frontend API URL

After backend is deployed, update the frontend's `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR_USERNAME-SPACE_NAME.hf.space/api/:path*"
    }
  ]
}
```

Then redeploy:
```bash
cd frontend
vercel --prod
```

**Note**: HuggingFace Spaces free tier sleeps after 15 minutes of inactivity. First request after sleep takes 30-60 seconds.

## Prerequisites

- Neon PostgreSQL account
- Vercel account (for frontend)
- Railway/Render account (for backend)
- Google OAuth credentials (optional)
- Domain name (optional)

## Database Setup (Neon)

### 1. Create Neon Project

1. Go to [Neon Console](https://console.neon.tech/)
2. Click "New Project"
3. Choose a name: `ary-todo-app`
4. Select region closest to your users
5. Copy the connection string

### 2. Configure Database

```sql
-- Neon automatically creates a database
-- Connection string format:
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 3. Run Migrations

```bash
cd backend
export DATABASE_URL="your-neon-connection-string"
alembic upgrade head
```

## Backend Deployment

### Option 1: Hugging Face Spaces (Recommended - Free)

**Best for**: Hobby projects, demos, free hosting with no billing required.

1. **Create New Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Configure:
     - **Space name**: `ary-todo-backend`
     - **SDK**: `Docker`
     - **Hardware**: `CPU basic` (free)
     - **Visibility**: Public

2. **Add Secrets**
   Go to Settings → Repository secrets:
   ```
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
   CORS_ORIGINS=https://your-app.vercel.app
   BETTER_AUTH_URL=https://your-app.vercel.app
   APP_ENV=production
   JWT_SECRET_KEY=your-production-jwt-secret
   ```

3. **Push Backend Code**
   ```bash
   cd backend
   git init
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/ary-todo-backend
   git add .
   git commit -m "Deploy backend"
   git push hf main
   ```

4. **Verify Deployment**
   ```bash
   # Health check (wait 2-5 min for build)
   curl https://YOUR_USERNAME-ary-todo-backend.hf.space/health

   # API docs
   open https://YOUR_USERNAME-ary-todo-backend.hf.space/docs
   ```

**Note**: Free tier sleeps after ~15 min inactivity. First request after sleep takes 30-60 seconds.

### Option 2: Google Cloud Run (Pay-per-use)

**Best for**: Production apps needing auto-scaling and custom domains.

1. **Setup gcloud CLI**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Build and Deploy**
   ```bash
   cd backend

   # Build and push image
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/todo-backend

   # Deploy to Cloud Run
   gcloud run deploy todo-backend \
     --image gcr.io/YOUR_PROJECT_ID/todo-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "DATABASE_URL=postgresql://...,CORS_ORIGINS=https://your-app.vercel.app,BETTER_AUTH_URL=https://your-app.vercel.app,APP_ENV=production" \
     --port 8000 \
     --memory 512Mi
   ```

**Cost**: Free tier includes 2M requests/month, then ~$0.40/million requests.

### Option 3: Railway

1. **Create New Project**
   - Go to [Railway](https://railway.app/)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Service**
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   ```
   DATABASE_URL=postgresql://...
   JWT_SECRET=your-production-jwt-secret
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   CORS_ORIGINS=https://yourdomain.com
   BETTER_AUTH_SECRET=your-production-auth-secret
   APP_ENV=production
   LOG_LEVEL=INFO
   ```

4. **Deploy**
   - Railway will automatically deploy
   - Note the public URL: `https://your-app.railway.app`

### Option 2: Render

1. **Create Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `ary-todo-backend`
   - Root directory: `backend`
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   - Add same variables as Railway option

4. **Deploy**
   - Click "Create Web Service"
   - Note the public URL: `https://your-app.onrender.com`

### Option 3: Docker (Self-hosted)

```bash
cd backend
docker build -t ary-todo-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET="your-secret" \
  ary-todo-backend
```

## Frontend Deployment

### Vercel (Recommended)

1. **Import Project**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New" → "Project"
   - Import your GitHub repository

2. **Configure Project**
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables**
   ```
   DATABASE_URL=postgresql://...
   BETTER_AUTH_SECRET=your-production-auth-secret
   BETTER_AUTH_URL=https://yourdomain.com
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   NODE_ENV=production
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Note the deployment URL

5. **Custom Domain (Optional)**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

### Netlify (Alternative)

1. **Import Project**
   - Go to [Netlify Dashboard](https://app.netlify.com/)
   - Click "Add new site" → "Import an existing project"

2. **Configure Build**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `.next`

3. **Environment Variables**
   - Add same variables as Vercel option

4. **Deploy**
   - Click "Deploy site"

## Environment Variables

### Backend Production Variables

```env
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT
JWT_SECRET=use-a-strong-random-secret-at-least-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Auth
BETTER_AUTH_SECRET=use-a-strong-random-secret-at-least-32-characters
BETTER_AUTH_URL=https://yourdomain.com

# App
APP_ENV=production
LOG_LEVEL=INFO

# Scheduler
SCHEDULER_TIMEZONE=UTC
```

### Frontend Production Variables

```env
# Database (for Better Auth)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Auth
BETTER_AUTH_SECRET=use-a-strong-random-secret-at-least-32-characters
BETTER_AUTH_URL=https://yourdomain.com

# API
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# App
NODE_ENV=production
```

### Generating Secrets

```bash
# Generate random secrets
openssl rand -base64 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Post-Deployment

### 1. Verify Backend

```bash
# Health check
curl https://your-backend.railway.app/health

# API documentation
open https://your-backend.railway.app/docs
```

### 2. Verify Frontend

```bash
# Open in browser
open https://yourdomain.com

# Test authentication
# - Register new user
# - Login with email/password
# - Test Google OAuth (if configured)
```

### 3. Test Core Features

- [ ] User registration and login
- [ ] Create, read, update, delete tasks
- [ ] Tag filtering
- [ ] Calendar view
- [ ] Recurring task generation (wait 24h or trigger manually)

### 4. Monitor Logs

**Railway:**
```bash
railway logs
```

**Render:**
- View logs in Render dashboard

**Vercel:**
- View logs in Vercel dashboard

### 5. Set Up Monitoring

**Backend Monitoring:**
- Add Sentry for error tracking
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Configure log aggregation (Logtail, Papertrail)

**Frontend Monitoring:**
- Vercel Analytics (built-in)
- Google Analytics
- Sentry for frontend errors

### 6. Database Backups

**Neon:**
- Automatic backups included
- Configure backup retention in Neon console
- Test restore procedure

### 7. Security Checklist

- [ ] HTTPS enabled on all endpoints
- [ ] CORS configured correctly
- [ ] JWT secrets are strong and unique
- [ ] Database credentials are secure
- [ ] Environment variables are not committed to git
- [ ] Rate limiting configured (optional)
- [ ] SQL injection protection (SQLModel handles this)
- [ ] XSS protection (React handles this)

## Troubleshooting

### Backend Issues

**Database Connection Errors:**
```bash
# Verify connection string
psql "postgresql://user:password@host/db?sslmode=require"

# Check Neon status
# Visit https://neon.tech/status
```

**CORS Errors:**
```python
# Verify CORS_ORIGINS in backend/.env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Migration Errors:**
```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**API Connection Errors:**
```bash
# Verify NEXT_PUBLIC_API_URL
echo $NEXT_PUBLIC_API_URL

# Test backend health
curl $NEXT_PUBLIC_API_URL/health
```

**Authentication Errors:**
```bash
# Verify secrets match between frontend and backend
# BETTER_AUTH_SECRET must be identical
```

**Build Errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## Scaling Considerations

### Database

- Neon automatically scales
- Monitor connection pool usage
- Consider read replicas for high traffic

### Backend

- Railway/Render auto-scale with traffic
- Configure horizontal scaling if needed
- Add Redis for caching (optional)

### Frontend

- Vercel automatically scales globally
- CDN included by default
- No additional configuration needed

## Cost Estimates

### Development/Hobby Tier (Free)

- **Neon**: Free tier (0.5 GB storage, 1 compute unit)
- **Railway**: $5/month credit (enough for small apps)
- **Vercel**: Free tier (100 GB bandwidth)
- **Total**: ~$0-5/month

### Production Tier

- **Neon**: ~$20/month (Pro plan)
- **Railway**: ~$20/month (Pro plan)
- **Vercel**: ~$20/month (Pro plan)
- **Total**: ~$60/month

## Rollback Procedure

### Backend Rollback

**Railway:**
```bash
# Rollback to previous deployment
railway rollback
```

**Render:**
- Use Render dashboard to rollback

### Frontend Rollback

**Vercel:**
- Go to Deployments
- Find previous working deployment
- Click "Promote to Production"

### Database Rollback

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>
```

## Support

For deployment issues:
- Check logs first
- Review environment variables
- Verify database connectivity
- Test API endpoints manually
- Contact support: support@example.com

---

**Last Updated**: 2026-01-06
