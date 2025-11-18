# Vercel Environment Variables Setup

This guide explains how to configure environment variables for your Doctor-AI deployment on Vercel.

## Important: No Secrets in vercel.json

The `vercel.json` file does NOT contain secret references (no `@secret_name` syntax). All environment variables must be set in the **Vercel Dashboard**.

## Automatic Environment Variables (Vercel Postgres)

When you connect Vercel Postgres to your project, these variables are **automatically provided**:

- `POSTGRES_URL` - Pooled connection string
- `POSTGRES_URL_NON_POOLING` - Direct connection string (recommended for migrations)
- `POSTGRES_PRISMA_URL` - Prisma-compatible URL
- `POSTGRES_USER` - Database username
- `POSTGRES_HOST` - Database host
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DATABASE` - Database name

**You don't need to set these manually!** The application automatically uses `POSTGRES_URL_NON_POOLING` for database connections.

## Required Environment Variables

Set these in **Vercel Dashboard** → **Project Settings** → **Environment Variables**:

### 1. SECRET_KEY (Required)

Generate a secure secret key:

```bash
openssl rand -base64 32
```

Then add it to Vercel:
- **Key:** `SECRET_KEY`
- **Value:** (paste the generated value)
- **Environments:** Production, Preview, Development

### 2. OPENAI_API_KEY (Required for AI features)

Get your API key from https://platform.openai.com/api-keys

- **Key:** `OPENAI_API_KEY`
- **Value:** `sk-...` (your OpenAI API key)
- **Environments:** Production, Preview, Development

## Optional Environment Variables

### Redis (Caching - Optional)

If you want to enable Redis caching:

- **REDIS_ENABLED:** `true`
- **REDIS_HOST:** Your Redis host
- **REDIS_PORT:** `6379`
- **REDIS_PASSWORD:** Your Redis password (if required)

### Qdrant (Vector Database - Optional)

If you want to use Qdrant for vector search:

- **QDRANT_HOST:** Your Qdrant host
- **QDRANT_PORT:** `6333`
- **QDRANT_API_KEY:** Your Qdrant API key

## How to Set Environment Variables in Vercel

### Method 1: Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Select your project
3. Click **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter **Key** and **Value**
6. Select environments (Production, Preview, Development)
7. Click **Save**
8. Redeploy your application

### Method 2: Vercel CLI

```bash
# Add a variable for production
vercel env add SECRET_KEY production

# Add for preview
vercel env add SECRET_KEY preview

# Add for development
vercel env add SECRET_KEY development

# Pull variables locally for testing
vercel env pull .env.local
```

## Deployment Checklist

Before deploying, ensure:

- [ ] Vercel Postgres database is connected to your project
- [ ] `SECRET_KEY` is set (at least 32 characters)
- [ ] `OPENAI_API_KEY` is set (if using AI features)
- [ ] Optional services (Redis, Qdrant) are configured if needed
- [ ] All environment variables are set for all environments (Production, Preview, Development)

## Verifying Configuration

After deployment, check:

1. **Health endpoint:** `https://your-app.vercel.app/api/v1/health`
   - Should return `{"status": "healthy", ...}`

2. **Database connection:** Visit `/api/init_database` once to initialize tables
   - Should create tables and admin user

3. **Frontend:** `https://your-app.vercel.app`
   - Should load without errors

## Troubleshooting

### Error: "SECRET_KEY must be set"
- Generate a key: `openssl rand -base64 32`
- Add it to Vercel environment variables
- Redeploy

### Error: "Database URL not configured"
- Ensure Vercel Postgres is connected to your project
- Check that `POSTGRES_URL` or `POSTGRES_URL_NON_POOLING` exists
- Or manually set `DATABASE_URL` in Vercel dashboard

### Error: "SECRET_KEY must be at least 32 characters"
- Your SECRET_KEY is too short
- Generate a new one with `openssl rand -base64 32`
- Update in Vercel dashboard

## Need Help?

- [Vercel Environment Variables Docs](https://vercel.com/docs/projects/environment-variables)
- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
- [Full Deployment Guide](./VERCEL_POSTGRES_SETUP.md)
