# Quick Start: Deploy to Vercel (Separate Projects)

Fast guide to deploy Doctor AI with separate frontend and backend on Vercel.

## TL;DR

```bash
# 1. Deploy Backend
vercel --prod --name doctor-ai-backend
# Set environment variables via Vercel dashboard

# 2. Deploy Frontend
vercel --prod --name doctor-ai-frontend
# Set VITE_API_URL=https://doctor-ai-backend.vercel.app

# 3. Update backend CORS to include frontend URL
# Done! 🎉
```

## Step-by-Step

### 1️⃣ Deploy Backend First

**Via Vercel Dashboard**:
1. Go to https://vercel.com/dashboard
2. New Project → Import `Doctor-Ai` repo
3. Configure:
   - Name: `doctor-ai-backend`
   - Framework: Other
   - Config: Use `vercel-backend.json`
4. Add environment variables (see below)
5. Deploy

**Via CLI**:
```bash
vercel login
cp .vercelignore.backend .vercelignore
vercel --prod --name doctor-ai-backend
```

**Required Environment Variables**:
```
ENVIRONMENT=production
SECRET_KEY=your-random-secret-key
CORS_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
QDRANT_URL=http://qdrant-host:6333
```

**Get Backend URL**: `https://doctor-ai-backend.vercel.app`

### 2️⃣ Deploy Frontend Second

**Via Vercel Dashboard**:
1. Go to https://vercel.com/dashboard
2. New Project → Import `Doctor-Ai` repo (again)
3. Configure:
   - Name: `doctor-ai-frontend`
   - Framework: Vite
   - Config: Use `vercel-frontend.json`
4. Add environment variable:
   ```
   VITE_API_URL=https://doctor-ai-backend.vercel.app
   ```
5. Deploy

**Via CLI**:
```bash
cp .vercelignore.frontend .vercelignore
vercel --prod --name doctor-ai-frontend
vercel env add VITE_API_URL
# Enter: https://doctor-ai-backend.vercel.app
```

**Get Frontend URL**: `https://doctor-ai-frontend.vercel.app`

### 3️⃣ Link Them Together

**Update Backend CORS**:
1. Go to Backend project → Settings → Environment Variables
2. Update `CORS_ORIGINS`:
   ```
   https://doctor-ai-frontend.vercel.app,http://localhost:3000
   ```
3. Redeploy backend (Deployments → Redeploy)

### 4️⃣ Test

```bash
# Test backend
curl https://doctor-ai-backend.vercel.app/health

# Test frontend
open https://doctor-ai-frontend.vercel.app
```

## External Services Needed

Since Vercel is serverless, you need external services for:

### Database (PostgreSQL)
- **Railway**: https://railway.app (Easiest)
- **Supabase**: https://supabase.com (Free tier)
- **Neon**: https://neon.tech (Serverless)

### Redis
- **Upstash**: https://upstash.com (Serverless, free tier)

### Qdrant (Vector DB)
- **Qdrant Cloud**: https://cloud.qdrant.io (Free tier available)

## Project Structure

```
Doctor-Ai/
├── frontend/                    # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── api/                         # Vercel serverless wrapper
│   ├── index.py                 # Backend entry point
│   └── requirements.txt         # Backend dependencies
├── src/                         # FastAPI backend source
│   ├── main.py
│   └── api/
├── vercel-frontend.json         # Frontend config
├── vercel-backend.json          # Backend config
├── .vercelignore.frontend       # Frontend ignore file
└── .vercelignore.backend        # Backend ignore file
```

## Configuration Files

### vercel-frontend.json
Deploys the React frontend from `frontend/` directory.

### vercel-backend.json
Deploys the FastAPI backend as serverless function.

### api/index.py
Wraps FastAPI app for Vercel:
```python
from src.main import app
handler = app
```

## Common Issues

### ❌ CORS Error
**Fix**: Add frontend URL to backend `CORS_ORIGINS`:
```
https://doctor-ai-frontend.vercel.app
```

### ❌ API Connection Failed
**Fix**: Check `VITE_API_URL` in frontend:
```
https://doctor-ai-backend.vercel.app  # ✅ No trailing slash!
```

### ❌ Backend Timeout
**Fix**:
- Upgrade to Vercel Pro (60s timeout)
- Or deploy backend to Railway/Fly.io instead

## Full Documentation

For complete guide, see:
- **[VERCEL_SEPARATE_DEPLOYMENTS.md](./VERCEL_SEPARATE_DEPLOYMENTS.md)** - Detailed guide
- **[VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)** - Original hybrid guide

## Architecture Diagram

```
┌─────────────────────────┐
│  Frontend (Vercel)      │
│  React + Vite           │
│  Global CDN             │
└───────────┬─────────────┘
            │
            │ HTTPS
            ▼
┌─────────────────────────┐
│  Backend (Vercel)       │
│  FastAPI Serverless     │
│  API Endpoints          │
└───────────┬─────────────┘
            │
            ├──► PostgreSQL (Railway/Neon)
            ├──► Redis (Upstash)
            └──► Qdrant (Qdrant Cloud)
```

## Next Steps

1. ✅ Deploy both projects
2. ✅ Set up external services
3. ✅ Configure environment variables
4. ✅ Test the deployment
5. ✅ Add custom domains (optional)
6. ✅ Set up monitoring

## Need Help?

- Check [VERCEL_SEPARATE_DEPLOYMENTS.md](./VERCEL_SEPARATE_DEPLOYMENTS.md) for detailed guide
- See Vercel docs: https://vercel.com/docs
- Open an issue on GitHub

---

**Happy Deploying! 🚀**
