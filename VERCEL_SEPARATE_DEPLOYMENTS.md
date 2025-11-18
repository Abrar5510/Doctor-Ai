# Vercel Separate Deployments Guide

This guide explains how to deploy Doctor AI with **separate Vercel projects** for frontend and backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Frontend Vercel Project (doctor-ai-frontend)      │
│  ├── React App (Vite)                              │
│  ├── Static Assets                                 │
│  └── Global CDN                                    │
│                                                     │
│  URL: https://doctor-ai-frontend.vercel.app        │
│                                                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ API Calls
                  ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Backend Vercel Project (doctor-ai-backend)        │
│  ├── FastAPI Application                           │
│  ├── Serverless Functions                          │
│  └── API Endpoints                                 │
│                                                     │
│  URL: https://doctor-ai-backend.vercel.app         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Benefits of Separate Deployments

✅ **Independent Scaling**: Frontend and backend scale separately
✅ **Isolated Deployments**: Update one without affecting the other
✅ **Better Organization**: Clear separation of concerns
✅ **Flexible Versioning**: Different release cycles for frontend/backend
✅ **Multiple Frontends**: Connect different frontends to same backend
✅ **Custom Domains**: Separate domains (e.g., app.example.com & api.example.com)

## Important Limitations

⚠️ **Backend on Vercel Serverless**:
- **Execution Timeout**: 10 seconds (Hobby), 60 seconds (Pro)
- **Cold Starts**: First request after inactivity may be slow
- **Memory Limits**: 1 GB (Hobby), 3 GB (Pro)
- **ML Models**: May be too large or slow to initialize

**Recommended for Production**:
- Deploy frontend to Vercel (optimal for static sites)
- Deploy backend to Railway, Fly.io, or Google Cloud Run (better for ML models)

However, this guide shows how to deploy both to Vercel if needed.

## Prerequisites

1. **Vercel Account**: https://vercel.com
2. **Git Repository**: Code pushed to GitHub/GitLab/Bitbucket
3. **Node.js 18+**: For frontend development
4. **Python 3.11+**: For backend (if testing locally)

## Deployment Steps

### Step 1: Deploy Backend to Vercel

#### Option A: Via Vercel Dashboard

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Click "Add New Project"**

3. **Import Repository**:
   - Select your Git provider
   - Choose the `Doctor-Ai` repository
   - Click "Import"

4. **Configure Backend Project**:
   - **Project Name**: `doctor-ai-backend`
   - **Framework Preset**: Other
   - **Root Directory**: `.` (root)
   - **Build Command**: Leave empty (Python doesn't need build)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

5. **Override Settings**:
   - Click "Override" next to Build and Output Settings
   - Use custom config: Upload or specify `vercel-backend.json`

6. **Add Environment Variables**:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your-secret-key-here
   CORS_ORIGINS=https://doctor-ai-frontend.vercel.app
   DATABASE_URL=your-database-url
   REDIS_URL=your-redis-url
   QDRANT_URL=your-qdrant-url
   QDRANT_API_KEY=your-qdrant-key
   ```

7. **Deploy**:
   - Click "Deploy"
   - Wait for build (2-5 minutes)
   - Note the URL: `https://doctor-ai-backend.vercel.app`

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to project
cd /path/to/Doctor-Ai

# Copy backend config
cp .vercelignore.backend .vercelignore

# Deploy backend
vercel --prod --name doctor-ai-backend

# Set environment variables
vercel env add ENVIRONMENT
vercel env add SECRET_KEY
vercel env add CORS_ORIGINS
vercel env add DATABASE_URL
vercel env add REDIS_URL
vercel env add QDRANT_URL
vercel env add QDRANT_API_KEY
```

### Step 2: Deploy Frontend to Vercel

#### Option A: Via Vercel Dashboard

1. **Create Another Project**:
   - Go to Vercel Dashboard
   - Click "Add New Project"
   - Import the same `Doctor-Ai` repository

2. **Configure Frontend Project**:
   - **Project Name**: `doctor-ai-frontend`
   - **Framework Preset**: Vite
   - **Root Directory**: `.` (root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

3. **Override Settings**:
   - Use custom config: Upload or specify `vercel-frontend.json`

4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://doctor-ai-backend.vercel.app
   ```
   **Note**: Replace with your actual backend URL from Step 1

5. **Deploy**:
   - Click "Deploy"
   - Wait for build (2-5 minutes)
   - Note the URL: `https://doctor-ai-frontend.vercel.app`

#### Option B: Via Vercel CLI

```bash
# Navigate to project
cd /path/to/Doctor-Ai

# Copy frontend config
cp .vercelignore.frontend .vercelignore

# Deploy frontend
vercel --prod --name doctor-ai-frontend

# Set environment variable
vercel env add VITE_API_URL
# When prompted, enter: https://doctor-ai-backend.vercel.app
```

### Step 3: Link Frontend to Backend

1. **Update Backend CORS**:
   - Go to Backend Vercel Project Settings
   - Navigate to Environment Variables
   - Update `CORS_ORIGINS` to include frontend URL:
     ```
     https://doctor-ai-frontend.vercel.app,http://localhost:3000
     ```

2. **Redeploy Backend**:
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment
   - Or push a new commit to trigger redeployment

3. **Verify Frontend API URL**:
   - Go to Frontend Vercel Project Settings
   - Check Environment Variables
   - Ensure `VITE_API_URL` points to backend:
     ```
     https://doctor-ai-backend.vercel.app
     ```

4. **Test Connection**:
   - Visit frontend URL
   - Open browser console
   - Navigate to diagnosis page
   - Check for CORS errors in Network tab

### Step 4: Test the Deployment

#### Backend Health Check

```bash
curl https://doctor-ai-backend.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Medical Symptom Constellation Mapper",
  "version": "0.2.0"
}
```

#### Frontend Test

1. Visit: `https://doctor-ai-frontend.vercel.app`
2. Check:
   - ✅ Page loads without errors
   - ✅ Navigation works
   - ✅ No CORS errors in console

#### Full Integration Test

1. Go to diagnosis page
2. Enter symptoms
3. Submit diagnosis request
4. Verify:
   - ✅ Request sent to backend
   - ✅ Response received
   - ✅ Results displayed

## Configuration Files

### vercel-frontend.json

Configures the frontend deployment:
- Builds Vite app from `frontend/` directory
- Serves static files
- Handles React Router (SPA routing)
- Sets `VITE_API_URL` environment variable

### vercel-backend.json

Configures the backend deployment:
- Deploys FastAPI as serverless function
- Entry point: `api/index.py`
- Sets backend environment variables
- Configures routes to API handler

### api/index.py

Wrapper for FastAPI app to work with Vercel serverless functions:
```python
from src.main import app
handler = app
```

## Environment Variables

### Frontend (doctor-ai-frontend)

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://doctor-ai-backend.vercel.app` | Backend API URL |

### Backend (doctor-ai-backend)

| Variable | Description | Required |
|----------|-------------|----------|
| `ENVIRONMENT` | `production` | Environment mode | ✅ |
| `SECRET_KEY` | Random secret key | For JWT tokens | ✅ |
| `CORS_ORIGINS` | Frontend URL(s) | CORS allowed origins | ✅ |
| `DATABASE_URL` | PostgreSQL URL | Database connection | ✅ |
| `REDIS_URL` | Redis URL | Caching | ✅ |
| `QDRANT_URL` | Qdrant URL | Vector database | ✅ |
| `QDRANT_API_KEY` | Qdrant key | Authentication | ❌ |

**For External Services**:
- **Database**: Use Railway, Supabase, or Neon PostgreSQL
- **Redis**: Use Upstash Redis (serverless)
- **Qdrant**: Use Qdrant Cloud

## Custom Domains

### Frontend Domain

1. In Frontend Vercel Project:
   - Settings → Domains
   - Add: `app.yourdomain.com`
   - Configure DNS CNAME to `cname.vercel-dns.com`

2. Update Backend CORS:
   ```
   CORS_ORIGINS=https://app.yourdomain.com,https://doctor-ai-frontend.vercel.app
   ```

### Backend Domain

1. In Backend Vercel Project:
   - Settings → Domains
   - Add: `api.yourdomain.com`
   - Configure DNS CNAME to `cname.vercel-dns.com`

2. Update Frontend Environment:
   ```
   VITE_API_URL=https://api.yourdomain.com
   ```

3. Redeploy frontend

## Automatic Deployments

### Git Integration

**Production Branch** (e.g., `main`):
- Push to `main` → Automatic production deployment
- Updates both projects if configured

**Feature Branches**:
- Push to feature branch → Preview deployment
- Unique URLs for testing
- Perfect for pull request reviews

### CI/CD Workflow

```yaml
# Example GitHub Actions workflow
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_BACKEND_PROJECT_ID }}
          vercel-args: '--prod'

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_FRONTEND_PROJECT_ID }}
          vercel-args: '--prod'
```

## Monitoring

### Vercel Dashboard

**Frontend Project**:
- Deployments: Build logs, deployment history
- Analytics: Page views, performance
- Speed Insights: Core Web Vitals

**Backend Project**:
- Deployments: Function logs
- Analytics: API request counts
- Logs: Runtime errors and warnings

### View Logs

```bash
# Frontend logs
vercel logs doctor-ai-frontend --follow

# Backend logs
vercel logs doctor-ai-backend --follow
```

## Troubleshooting

### Backend Errors

**Error**: `Function timeout (10s)`
- **Solution**:
  - Upgrade to Vercel Pro (60s timeout)
  - Optimize ML model loading
  - Consider external backend hosting

**Error**: `Module not found`
- **Solution**:
  - Check `api/requirements.txt` includes all dependencies
  - Verify `api/index.py` imports correctly
  - Redeploy

### Frontend Errors

**Error**: `CORS policy blocked`
- **Solution**:
  1. Check backend `CORS_ORIGINS` includes frontend URL
  2. Verify environment variable has correct frontend URL
  3. Redeploy backend

**Error**: `Failed to fetch`
- **Solution**:
  1. Verify `VITE_API_URL` is correct
  2. No trailing slash in URL
  3. Backend is deployed and accessible
  4. Test: `curl https://doctor-ai-backend.vercel.app/health`

### Build Errors

**Frontend build fails**:
- Check `package.json` exists in `frontend/`
- Verify Node version compatibility
- Check build logs for specific errors

**Backend build fails**:
- Check `api/requirements.txt` is valid
- Verify Python version (3.11+)
- Check for conflicting dependencies

## Performance Optimization

### Frontend

- **Code Splitting**: Vite handles automatically
- **Asset Optimization**: Vercel compresses assets
- **CDN**: Global edge network

### Backend

- **Cold Start Optimization**:
  - Minimize import time
  - Lazy load ML models
  - Use external model hosting (e.g., HuggingFace Inference)

- **Caching**:
  - Use Redis for frequently accessed data
  - Cache ML model results

- **Database Optimization**:
  - Use connection pooling
  - Optimize queries

## Cost Estimate

### Free Tier (Both Projects)

**Frontend**:
- Bandwidth: 100 GB/month
- Build time: 100 hours/month
- Deployments: Unlimited

**Backend**:
- Function executions: 100 GB-hours/month
- Function duration: 100 hours/month
- Requests: Unlimited

**Total**: **$0/month** ✨

### Pro Tier ($20/month per project)

**Frontend Pro**:
- Bandwidth: 1 TB/month
- Build time: 400 hours/month
- Analytics: Enhanced

**Backend Pro**:
- Function timeout: 60 seconds
- Function memory: 3 GB
- Execution time: Increased limits

**Total**: **$40/month** (both projects)

## Alternative Deployment Strategy

**Recommended for Production**:

```
Frontend: Vercel (Free/Pro)
         ↓
Backend: Railway/Fly.io/Cloud Run
         ↓
Database: Managed PostgreSQL
         ↓
Vector DB: Qdrant Cloud
         ↓
Cache: Upstash Redis
```

**Why?**:
- ✅ No serverless limitations for backend
- ✅ Better ML model support
- ✅ No cold starts
- ✅ More memory/CPU
- ✅ Longer execution times

## Next Steps

After successful deployment:

1. ✅ **Test all features** thoroughly
2. ✅ **Set up custom domains** (optional)
3. ✅ **Enable monitoring** and alerts
4. ✅ **Configure backups** for databases
5. ✅ **Set up CI/CD** for automatic deployments
6. ✅ **Document** your deployment URLs
7. ✅ **Monitor performance** and optimize

## Quick Reference

### Frontend URL Format
```
https://doctor-ai-frontend.vercel.app
https://your-frontend.vercel.app
https://app.yourdomain.com (custom)
```

### Backend URL Format
```
https://doctor-ai-backend.vercel.app
https://your-backend.vercel.app
https://api.yourdomain.com (custom)
```

### Health Check Endpoints
```bash
# Backend health
curl https://your-backend.vercel.app/health

# Backend API docs
https://your-backend.vercel.app/docs

# Frontend
https://your-frontend.vercel.app
```

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Vercel Community**: https://github.com/vercel/vercel/discussions
- **Project Issues**: See repository issues

## Summary

You now have:
- ✅ Separate Vercel projects for frontend and backend
- ✅ Independent deployment pipelines
- ✅ Proper CORS configuration
- ✅ Environment variables configured
- ✅ Custom domain support
- ✅ Automatic deployments from Git

Your Doctor AI application is deployed with a modern, scalable architecture! 🚀
