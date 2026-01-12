---
name: deployment
description: Battle-tested deployment patterns for Vercel frontend and HuggingFace Spaces backend. Use when deploying applications, setting up CI/CD, or troubleshooting deployment errors.
---

# Deployment Skill

Comprehensive deployment guide for full-stack applications.

## Included Guides

1. **00-overview.md** - Deployment architecture overview
2. **01-vercel-frontend.md** - Vercel deployment for Next.js
3. **02-hf-spaces-backend.md** - HuggingFace Spaces for FastAPI
4. **03-environment-variables.md** - Environment configuration
5. **04-common-errors.md** - Error catalog and solutions
6. **05-cicd-setup.md** - GitHub Actions workflows
7. **06-checklist.md** - Pre-deployment checklist

## Quick Reference

### Frontend (Vercel)
- Framework: Next.js 15+
- Build: `npm run build`
- Environment: NEXT_PUBLIC_* for client-side

### Backend (HuggingFace Spaces)
- Framework: FastAPI
- Port: 7860 (required)
- Dockerfile required

### Common Issues
- ERR_101: Port must be 7860 on HF Spaces
- ERR_102: CORS origins must include production URLs
- ERR_103: Database URL must be set in Secrets
