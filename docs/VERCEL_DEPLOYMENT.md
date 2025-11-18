# Vercel Deployment Guide

Complete guide for deploying Doctor-AI to Vercel.

## Overview

Doctor-AI can be deployed to Vercel in multiple configurations:

1. **Separate Deployments** (Recommended): Frontend and backend as separate Vercel projects
2. **Hybrid Deployment**: Frontend on Vercel, backend self-hosted
3. **Unified Deployment**: Both frontend and backend in one Vercel project (experimental)

## Quick Start

### Prerequisites

- Vercel account: https://vercel.com
- External services for production:
  - PostgreSQL (Railway, Supabase, or Neon)
  - Redis (Upstash)
  - Qdrant Cloud (optional, for vector search)

### 1. Separate Deployments (Recommended)

Deploy frontend and backend as independent Vercel projects.

#### Deploy Backend

```bash
# Via CLI
vercel login
cp .vercelignore.backend .vercelignore
vercel --prod --name doctor-ai-backend
```

**Required Environment Variables**:
```
ENVIRONMENT=production
SECRET_KEY=<generate-random-secret>
CORS_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://user:pass@host:5432/db
```

#### Deploy Frontend

```bash
# Via CLI
cp .vercelignore.frontend .vercelignore
vercel --prod --name doctor-ai-frontend
```

**Required Environment Variable**:
```
VITE_API_URL=https://doctor-ai-backend.vercel.app
```

#### Link Them Together

1. Get backend URL after deployment
2. Update frontend's `VITE_API_URL` to backend URL
3. Update backend's `CORS_ORIGINS` to include frontend URL
4. Redeploy both projects

### 2. Hybrid Deployment

Deploy frontend to Vercel, host backend elsewhere (Docker, Railway, Fly.io, etc.)

#### Deploy Frontend

```bash
vercel --prod
```

**Environment Variable**:
```
VITE_API_URL=https://your-backend-url.com
```

#### Configure Backend CORS

Update your backend `.env`:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

This approach is ideal for:
- ML models requiring more resources
- Avoiding serverless function limitations
- Full control over backend infrastructure

## Environment Variables

### Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL (no trailing slash) | `https://api.example.com` |

### Backend Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Random secret for JWT (min 32 chars) |
| `CORS_ORIGINS` | ✅ | Comma-separated frontend URLs |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | Optional | Redis connection string |
| `QDRANT_URL` | Optional | Qdrant vector database URL |
| `OPENAI_API_KEY` | Optional | For AI assistant features |

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## External Services Setup

### PostgreSQL Database

**Option 1: Railway** (Easiest)
1. Go to https://railway.app
2. Create new project → Add PostgreSQL
3. Copy `DATABASE_URL` connection string
4. Add to Vercel environment variables

**Option 2: Supabase** (Free tier)
1. Go to https://supabase.com
2. Create new project
3. Get connection string from Settings → Database
4. Format: `postgresql://postgres:[password]@[host]:5432/postgres`

**Option 3: Neon** (Serverless)
1. Go to https://neon.tech
2. Create new project
3. Copy connection string
4. Add to Vercel

### Redis (Optional)

**Upstash** (Serverless, recommended)
1. Go to https://upstash.com
2. Create Redis database
3. Copy `REDIS_URL`
4. Add to Vercel environment variables

### Qdrant Vector Database (Optional)

**Qdrant Cloud**
1. Go to https://cloud.qdrant.io
2. Create cluster (free tier available)
3. Get cluster URL and API key
4. Add `QDRANT_URL` to Vercel

## Vercel Dashboard Setup

### Deploy via Dashboard

1. **Import Repository**
   - Go to https://vercel.com/new
   - Import your `Doctor-Ai` repository
   - Select framework: Vite (frontend) or Other (backend)

2. **Configure Build Settings**

   **For Frontend**:
   - Framework: Vite
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `cd frontend && npm install`

   **For Backend**:
   - Framework: Other
   - Use `vercel-backend.json` configuration
   - Root Directory: `./`

3. **Add Environment Variables**
   - Go to Settings → Environment Variables
   - Add all required variables
   - Select Production, Preview, and Development environments
   - Click Save

4. **Deploy**
   - Click Deploy
   - Wait for build to complete
   - Get deployment URL

## Vercel Configuration Files

### vercel-frontend.json

```json
{
  "version": 2,
  "name": "doctor-ai-frontend",
  "framework": "vite",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "routes": [
    {
      "src": "/assets/(.*)",
      "dest": "/assets/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### vercel-backend.json

```json
{
  "version": 2,
  "name": "doctor-ai-backend",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "ENVIRONMENT": "production"
  }
}
```

## Testing Deployment

### Test Backend

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

### Test Frontend

1. Visit: `https://doctor-ai-frontend.vercel.app`
2. Check browser console for errors
3. Navigate to diagnosis page
4. Submit test diagnosis
5. Verify API calls succeed in Network tab

## Custom Domain Setup

### Add Custom Domain

1. Go to Project Settings → Domains
2. Click "Add"
3. Enter your domain (e.g., `app.example.com`)
4. Follow DNS configuration instructions

### Configure DNS

Add one of the following:
- **CNAME**: `cname.vercel-dns.com`
- **A Record**: Point to Vercel's IP

### Update CORS

After adding custom domain, update backend `CORS_ORIGINS`:
```
CORS_ORIGINS=https://app.example.com,https://doctor-ai-frontend.vercel.app
```

## Troubleshooting

### Build Fails

**Error: Cannot find module**
- Ensure `buildCommand` includes `npm install`
- Verify `package.json` exists in correct directory

**Error: Build exceeded time limit**
- Upgrade to Vercel Pro (longer build times)
- Optimize dependencies

### CORS Errors

**Error: Access blocked by CORS policy**
- Verify `CORS_ORIGINS` includes your Vercel domain
- Check for trailing slashes (shouldn't have them)
- Ensure backend is deployed and accessible

### API Connection Failed

**Error: Network Error or Failed to fetch**
- Check `VITE_API_URL` is correct (no trailing slash)
- Verify backend is running and accessible
- Test backend health endpoint directly
- Check browser console for specific error

### Environment Variables Not Working

**Error: undefined when accessing env vars**
- Frontend vars must start with `VITE_` prefix
- Redeploy after adding/changing environment variables
- Check variable is set in correct environment (Production/Preview/Development)

## Limitations & Considerations

### Vercel Free Tier

- **Bandwidth**: 100 GB/month
- **Build Time**: 100 hours/month
- **Function Execution**: 100 GB-hours
- **Function Timeout**: 10 seconds (Hobby), 60 seconds (Pro)
- **Function Size**: 50 MB max

### Backend Considerations

⚠️ **For ML Models**: Vercel serverless functions may have limitations:
- Cold start delays
- 10-second timeout (Hobby tier)
- Memory constraints
- Large model size issues

**Recommended for production ML workloads**:
- Deploy backend to Railway, Fly.io, or Google Cloud Run
- Use Vercel only for frontend
- Self-host with Docker for full control

## Architecture Diagrams

### Separate Deployments

```
┌─────────────────────────┐
│  Frontend (Vercel)      │
│  - React + Vite         │
│  - Global CDN           │
│  - Static Assets        │
└───────────┬─────────────┘
            │
            │ HTTPS API Calls
            ▼
┌─────────────────────────┐
│  Backend (Vercel)       │
│  - FastAPI Serverless   │
│  - API Endpoints        │
└───────────┬─────────────┘
            │
            ├──► PostgreSQL (External)
            ├──► Redis (External)
            └──► Qdrant (External)
```

### Hybrid Deployment

```
┌─────────────────────────┐
│  Frontend (Vercel)      │
│  - React + Vite         │
│  - Global CDN           │
└───────────┬─────────────┘
            │
            │ HTTPS API Calls
            ▼
┌─────────────────────────┐
│  Backend (Self-Hosted)  │
│  - Docker Container     │
│  - FastAPI + ML Models  │
│  - PostgreSQL           │
│  - Redis                │
│  - Qdrant               │
└─────────────────────────┘
```

## Cost Estimate

### Free Tier

**Frontend Only** (Hybrid):
- Vercel: $0/month (free tier)
- Backend: Self-hosted (variable)
- **Total**: $0-20/month depending on hosting

**Separate Deployments**:
- Vercel Frontend: $0/month
- Vercel Backend: $0/month (light usage)
- PostgreSQL (Railway): $5/month
- Redis (Upstash): $0/month (free tier)
- Qdrant Cloud: $0/month (free tier)
- **Total**: ~$5/month

### Pro Tier ($20/month)

- Better for production workloads
- 60-second function timeout
- Enhanced analytics
- Team features

## Security Best Practices

### Environment Variables

- ✅ Never commit `.env` files
- ✅ Use Vercel dashboard to set secrets
- ✅ Frontend env vars are public (start with `VITE_`)
- ❌ Never store API keys in frontend code

### CORS Configuration

- ✅ Only allow specific origins
- ❌ Never use `*` in production
- ✅ Include all your domains (production + preview)

### HTTPS

- ✅ Automatically enabled by Vercel
- ✅ SSL certificates provided free
- ✅ Enforce HTTPS (automatic)

## Monitoring & Logs

### View Logs

```bash
# View deployment logs
vercel logs <deployment-url>

# Follow in real-time
vercel logs <deployment-url> --follow
```

### Vercel Dashboard

- **Deployments**: View all deployments and status
- **Analytics**: Traffic and performance metrics
- **Speed Insights**: Performance monitoring
- **Runtime Logs**: Function execution logs

## Deployment Workflow

### Automatic Deployments

**Production** (main branch):
- Push to `main` branch
- Vercel auto-deploys
- Updates production URL

**Preview** (feature branches):
- Push to any branch
- Vercel creates preview deployment
- Unique URL for testing

### Manual Deployments

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Rollback
vercel rollback
```

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Set up custom domain (optional)
3. ✅ Enable Vercel Analytics
4. ✅ Configure monitoring and alerts
5. ✅ Set up database backups
6. ✅ Document deployment URLs
7. ✅ Share with users

## Additional Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel CLI Reference**: https://vercel.com/docs/cli
- **Doctor-AI Main README**: See root `README.md`
- **Architecture Details**: See `ARCHITECTURE.md`

## Support

For issues or questions:
- Check this guide first
- Review Vercel documentation
- Check deployment logs
- Open an issue on GitHub

---

**Last Updated**: 2025-11-18
