# Vercel Unified Deployment Guide

This guide explains how to deploy Doctor-AI as a **single unified deployment** on Vercel with both frontend and backend integrated.

## Overview

The unified deployment configuration:
- **Frontend**: Deployed as static files (Vite build)
- **Backend**: Deployed as serverless functions
- **URL Structure**:
  - Frontend: `https://your-app.vercel.app/*`
  - Backend API: `https://your-app.vercel.app/api/v1/*`
- **Database**: Connected via environment variables

## Prerequisites

1. A Vercel account
2. A PostgreSQL database (e.g., from Neon, Supabase, or Vercel Postgres)
3. An OpenAI API key (for AI assistant features)
4. (Optional) Qdrant Cloud instance for vector search
5. (Optional) Redis instance for caching

## Step 1: Prepare Your Database

### Option A: Vercel Postgres (Recommended)

1. Go to your Vercel dashboard
2. Navigate to Storage → Create Database → Postgres
3. Copy the `DATABASE_URL` connection string

### Option B: External PostgreSQL

Use any PostgreSQL provider (Neon, Supabase, Railway, etc.)
Ensure you have a connection string in this format:
```
postgresql://username:password@host:port/database
```

## Step 2: Set Up Vercel Project

### Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel
vercel
```

### Using Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Vercel will auto-detect the `vercel.json` configuration

## Step 3: Configure Environment Variables

In your Vercel project settings, add the following environment secrets:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Generate with: `openssl rand -base64 32` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant server host | `localhost` (uses local file storage) |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `QDRANT_API_KEY` | Qdrant API key | (none) |
| `REDIS_ENABLED` | Enable Redis caching | `false` |
| `REDIS_HOST` | Redis server host | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_PASSWORD` | Redis password | (none) |

### How to Add Environment Variables in Vercel

1. Go to your project in Vercel dashboard
2. Click on **Settings** → **Environment Variables**
3. For each variable:
   - Click **Add New**
   - Enter the **Key** (e.g., `DATABASE_URL`)
   - Enter the **Value**
   - Select **Production**, **Preview**, and **Development** environments
   - Click **Save**

**Important:** For sensitive values like `DATABASE_URL` and `SECRET_KEY`, use Vercel's secret reference format `@secret_name` in `vercel.json`, but set the actual value in the Vercel dashboard.

## Step 4: Deploy

Once environment variables are configured:

```bash
# Deploy to production
vercel --prod
```

Or push to your main branch if you've connected GitHub to Vercel (auto-deploys).

## Step 5: Verify Deployment

1. Visit your deployment URL: `https://your-app.vercel.app`
2. You should see the Doctor-AI frontend
3. Test the API by visiting: `https://your-app.vercel.app/api/v1/health`
4. Should return:
   ```json
   {
     "status": "healthy",
     "service": "Medical Symptom Constellation Mapper",
     "version": "0.1.0",
     "ai_features": "enabled"
   }
   ```

## Architecture

```
User Request
    ↓
Vercel Edge Network
    ↓
    ├─→ /api/* ──→ Python Serverless Functions (Backend)
    │                    ↓
    │              PostgreSQL Database
    │                    ↓
    │              (Optional: Qdrant, Redis)
    │
    └─→ /* ──────→ Static Files (Frontend)
```

## Local Development

For local development, use separate frontend and backend:

```bash
# Terminal 1 - Backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python -m uvicorn src.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
cp .env.example .env
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## Troubleshooting

### Frontend shows but API calls fail

Check:
1. API routes are prefixed with `/api/v1/` (e.g., `/api/v1/analyze`)
2. CORS is properly configured (same-origin should work automatically)
3. Environment variables are set in Vercel dashboard

### "SECRET_KEY must be set" error

Generate a strong secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Add it to Vercel environment variables as `SECRET_KEY`.

### Database connection fails

Verify:
1. `DATABASE_URL` format is correct: `postgresql://user:pass@host:port/database`
2. Database allows connections from Vercel's IP addresses
3. Database is not paused (some providers auto-pause on free tier)

### Build fails

Check:
1. Node.js version compatibility (requires >= 18.0.0)
2. Python version compatibility (requires 3.11+)
3. Build logs in Vercel dashboard for specific errors

## Cost Optimization

### Vercel Limits
- **Hobby Plan**: 100GB bandwidth, 100 hours serverless execution
- **Pro Plan**: 1TB bandwidth, 1000 hours serverless execution

### Recommendations
1. Enable Redis caching to reduce database queries
2. Use Qdrant Cloud free tier for vector storage (1GB free)
3. Monitor serverless execution time
4. Consider upgrading for production workloads

## Next Steps

1. Set up a custom domain in Vercel settings
2. Configure monitoring and alerts
3. Set up CI/CD pipelines for automated testing
4. Enable preview deployments for pull requests
5. Configure backup strategy for your database

## Support

For issues or questions:
- Check the [main README](./README.md)
- Review [DEPLOYMENT.md](./DEPLOYMENT.md) for general deployment info
- Open an issue on GitHub
