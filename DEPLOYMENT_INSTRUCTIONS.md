# Deployment Instructions - Chelsea Market Font Update

## ✅ Completed Steps

1. **Git Commit**: All Chelsea Market font changes committed
   - Commit: a2f431e
   - Branch: 006-chatbot-optimization
   
2. **GitHub Push**: Changes pushed to remote repository
   - Remote: https://github.com/MuhammadAriyan/ary-s-evolved-todo

3. **Vercel Auto-Deploy**: Frontend should be deploying automatically
   - Project: frontend
   - Dashboard: https://vercel.com/dashboard

## 🚀 Next Steps

### Step 1: Verify Vercel Deployment

1. Go to https://vercel.com/dashboard
2. Find your "frontend" project
3. Check the latest deployment status
4. Once deployed, test the Chelsea Market font at your Vercel URL

### Step 2: Deploy Backend to HuggingFace Spaces

**Option A: If you have an existing Space**

```bash
cd backend
./deploy-to-hf.sh YOUR_USERNAME/YOUR_SPACE_NAME
```

**Option B: Create a new Space first**

1. Go to https://huggingface.co/new-space
2. Configure:
   - Space name: `ary-todo-backend`
   - SDK: `Docker`
   - Hardware: `CPU Basic` (free)
   - Visibility: Public
3. Then deploy:
```bash
cd backend
./deploy-to-hf.sh YOUR_USERNAME/ary-todo-backend
```

### Step 3: Configure Backend Secrets

After deploying, add these secrets in HuggingFace Space settings:

1. Go to: https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/settings
2. Add Repository secrets:
   ```
   DATABASE_URL=postgresql://...
   CORS_ORIGINS=https://your-frontend.vercel.app
   BETTER_AUTH_URL=https://your-frontend.vercel.app
   JWT_SECRET_KEY=your-secret-key
   AI_API_KEY=your-openai-key (optional)
   AI_BASE_URL=https://api.openai.com/v1 (optional)
   AI_MODEL=gpt-4o-mini (optional)
   ```

### Step 4: Update Frontend API URL

Once backend is deployed, update `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/:path*"
    }
  ]
}
```

Then redeploy frontend:
```bash
cd frontend
git add vercel.json
git commit -m "Update backend API URL"
git push origin 006-chatbot-optimization
```

### Step 5: Verify Deployment

**Frontend:**
```bash
# Open your Vercel URL
open https://your-app.vercel.app

# Check for Chelsea Market font in:
# - Header "Ary's Evolved Todo"
# - Page titles
# - Chat messages
# - Todo task titles
```

**Backend:**
```bash
# Health check
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health

# Expected: {"status": "healthy"}
```

**Cross-Origin Requests:**
- Open browser DevTools → Network tab
- Send a chat message
- Verify no CORS errors

## 📝 Deployment Checklist

- [ ] Vercel deployment completed successfully
- [ ] Chelsea Market font visible on production
- [ ] HuggingFace Space created
- [ ] Backend deployed to HF Space
- [ ] Backend secrets configured
- [ ] Backend health check passes
- [ ] Frontend API URL updated
- [ ] CORS working correctly
- [ ] Chat functionality working
- [ ] Todo functionality working

## 🔧 Troubleshooting

**Vercel deployment failed:**
- Check build logs in Vercel dashboard
- Verify environment variables are set

**Backend 503 error:**
- Ensure port 7860 is used (required by HF Spaces)
- Check Space build logs

**CORS errors:**
- Verify CORS_ORIGINS includes your Vercel URL
- Check backend logs for CORS configuration

**Font not loading:**
- Check browser console for font loading errors
- Verify Google Fonts CSS link in layout.tsx

## 📞 Support

If you encounter issues:
1. Check the deployment logs
2. Review environment variables
3. Test health endpoints
4. Verify CORS configuration

---

**Created**: $(date)
**Branch**: 006-chatbot-optimization
**Commit**: a2f431e
