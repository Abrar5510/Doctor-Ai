# Vercel Separate Deployments - Setup Summary

This document summarizes the changes made to enable separate Vercel deployments for frontend and backend.

## Files Created

### Configuration Files

1. **`vercel-frontend.json`**
   - Vercel configuration for frontend deployment
   - Builds React app from `frontend/` directory
   - Configures SPA routing
   - Sets `VITE_API_URL` environment variable

2. **`vercel-backend.json`**
   - Vercel configuration for backend deployment
   - Deploys FastAPI as serverless function
   - Entry point: `api/index.py`
   - Configures environment variables for backend

3. **`.vercelignore.frontend`**
   - Ignores backend files for frontend deployment
   - Excludes Python code, Docker files, etc.

4. **`.vercelignore.backend`**
   - Ignores frontend files for backend deployment
   - Excludes React app, node_modules, etc.

### Backend Wrapper

5. **`api/index.py`**
   - Vercel serverless function entry point
   - Wraps FastAPI app for Vercel compatibility
   - Handles ASGI server integration

6. **`api/requirements.txt`**
   - Python dependencies for backend
   - Includes FastAPI, ML libraries, database clients

### Documentation

7. **`VERCEL_SEPARATE_DEPLOYMENTS.md`**
   - Comprehensive guide for separate deployments
   - Architecture overview
   - Step-by-step instructions
   - Troubleshooting guide
   - Configuration examples

8. **`DEPLOYMENT_QUICK_START.md`**
   - Quick reference guide
   - TL;DR deployment steps
   - Common issues and fixes
   - External services setup

9. **`VERCEL_SETUP_SUMMARY.md`** (this file)
   - Summary of all changes
   - File descriptions
   - Usage instructions

### Modified Files

10. **`README.md`**
    - Added Vercel deployment section
    - Updated documentation links
    - Organized deployment guides

## How to Use

### Deploy Backend

```bash
# Copy backend ignore file
cp .vercelignore.backend .vercelignore

# Deploy
vercel --prod --name doctor-ai-backend
```

Or use `vercel-backend.json` configuration in Vercel dashboard.

### Deploy Frontend

```bash
# Copy frontend ignore file
cp .vercelignore.frontend .vercelignore

# Deploy
vercel --prod --name doctor-ai-frontend
```

Or use `vercel-frontend.json` configuration in Vercel dashboard.

### Link Them Together

1. Deploy backend first
2. Get backend URL: `https://doctor-ai-backend.vercel.app`
3. Deploy frontend with environment variable:
   ```
   VITE_API_URL=https://doctor-ai-backend.vercel.app
   ```
4. Update backend CORS to include frontend URL:
   ```
   CORS_ORIGINS=https://doctor-ai-frontend.vercel.app
   ```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Frontend Vercel Project                            │
│  ├── React App (Vite)                               │
│  ├── Static Assets                                  │
│  └── CDN Distribution                               │
│                                                      │
│  URL: https://doctor-ai-frontend.vercel.app         │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ API Calls (HTTPS)
                  │
┌─────────────────▼────────────────────────────────────┐
│  Backend Vercel Project                              │
│  ├── FastAPI Application                            │
│  ├── Serverless Functions                           │
│  ├── API Endpoints                                  │
│  └── ML Models (with limitations)                   │
│                                                      │
│  URL: https://doctor-ai-backend.vercel.app          │
└─────────────────┬────────────────────────────────────┘
                  │
                  ├──► PostgreSQL (External)
                  ├──► Redis (External)
                  └──► Qdrant (External)
```

## Key Features

✅ **Separate Deployments**: Independent frontend and backend
✅ **Scalable Architecture**: Each component scales independently
✅ **Easy Updates**: Deploy changes to one without affecting the other
✅ **Custom Domains**: Support for separate domains (app.example.com, api.example.com)
✅ **Environment Isolation**: Separate environment variables for each project

## Important Notes

### Backend Limitations on Vercel

⚠️ Vercel serverless functions have limitations:
- **Timeout**: 10 seconds (Hobby), 60 seconds (Pro)
- **Memory**: 1 GB (Hobby), 3 GB (Pro)
- **Cold Starts**: First request may be slow
- **ML Models**: May be too large or slow

### Recommended Production Setup

For production with ML models:
- **Frontend**: Vercel ✅ (optimal for static sites)
- **Backend**: Railway, Fly.io, or Google Cloud Run ✅ (better for ML)
- **Database**: Managed PostgreSQL (Railway, Supabase, Neon)
- **Redis**: Upstash (serverless)
- **Qdrant**: Qdrant Cloud

## Environment Variables

### Frontend

| Variable | Example | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `https://doctor-ai-backend.vercel.app` | Backend API URL |

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `ENVIRONMENT` | ✅ | `production` |
| `SECRET_KEY` | ✅ | Random secret for JWT |
| `CORS_ORIGINS` | ✅ | Frontend URL(s) |
| `DATABASE_URL` | ✅ | PostgreSQL connection |
| `REDIS_URL` | ✅ | Redis connection |
| `QDRANT_URL` | ✅ | Qdrant vector DB |

## Testing

### Test Backend

```bash
curl https://doctor-ai-backend.vercel.app/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "Medical Symptom Constellation Mapper",
  "version": "0.2.0"
}
```

### Test Frontend

1. Visit: `https://doctor-ai-frontend.vercel.app`
2. Check browser console for errors
3. Navigate to diagnosis page
4. Submit test diagnosis
5. Verify API calls succeed

## Documentation

- **Quick Start**: [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)
- **Detailed Guide**: [VERCEL_SEPARATE_DEPLOYMENTS.md](./VERCEL_SEPARATE_DEPLOYMENTS.md)
- **Original Guide**: [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)
- **Main README**: [README.md](./README.md)

## Next Steps

1. ✅ Review the configuration files
2. ✅ Set up external services (Database, Redis, Qdrant)
3. ✅ Deploy backend to Vercel
4. ✅ Deploy frontend to Vercel
5. ✅ Link them together via environment variables
6. ✅ Test the deployment
7. ✅ Set up custom domains (optional)

## Support

For issues or questions:
- See [VERCEL_SEPARATE_DEPLOYMENTS.md](./VERCEL_SEPARATE_DEPLOYMENTS.md) for troubleshooting
- Check Vercel documentation: https://vercel.com/docs
- Open an issue on GitHub

---

**Created**: 2025-11-18
**Purpose**: Enable separate Vercel deployments for Doctor AI frontend and backend
