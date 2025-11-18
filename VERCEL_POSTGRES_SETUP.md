# Vercel Postgres Complete Setup Guide

This is the **complete step-by-step guide** for deploying Doctor-AI with Vercel Postgres.

## 🎯 Quick Overview

You'll set up:
1. ✅ Vercel Postgres database
2. ✅ Environment variables
3. ✅ Deploy the application
4. ✅ Initialize database tables
5. ✅ Verify everything works

**Total time:** ~10 minutes

---

## Step 1: Create Vercel Postgres Database

### Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Click **"Storage"** in the top navigation
3. Click **"Create Database"**
4. Select **"Postgres"**
5. Configure:
   - **Database Name:** `doctor-ai-db` (or any name)
   - **Region:** Select closest to your users
     - `iad1` - US East (Virginia)
     - `sfo1` - US West (San Francisco)
     - `fra1` - Europe (Frankfurt)
   - **Plan:** Hobby (free) or Pro
6. Click **"Create"**
7. Wait ~30 seconds for provisioning

### Via Vercel CLI

```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Login
vercel login

# Create database
vercel storage create postgres doctor-ai-db --region iad1
```

---

## Step 2: Connect Database to Your Project

### Option A: During Project Creation

If you haven't deployed yet:
1. In your database dashboard, click **"Connect Project"**
2. Click **"Create New Project"**
3. Import your Doctor-AI GitHub repository
4. Database environment variables are auto-added

### Option B: Add to Existing Project

If you already have a Vercel project:
1. Go to your database in **Storage** tab
2. Click **"Connect Project"**
3. Select your Doctor-AI project
4. Click **"Connect"**

This automatically adds these variables to your project:
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`
- `POSTGRES_USER`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

---

## Step 3: Add Required Environment Variables

Your app needs `DATABASE_URL` (it references `POSTGRES_URL`).

### Via Vercel Dashboard

1. Go to your project: https://vercel.com/dashboard
2. Click **Settings** → **Environment Variables**
3. Add each variable below:

#### Required Variables

| Key | Value | Environments |
|-----|-------|--------------|
| `DATABASE_URL` | Reference `POSTGRES_URL` or paste the full connection string | Production, Preview, Development |
| `SECRET_KEY` | Generate: `openssl rand -base64 32` | Production, Preview, Development |
| `OPENAI_API_KEY` | Your OpenAI API key (from https://platform.openai.com/api-keys) | Production, Preview, Development |

**How to reference POSTGRES_URL:**
- In the Value field, you can type: `$POSTGRES_URL` (if supported)
- OR copy the actual connection string from POSTGRES_URL and paste it

#### Optional Variables (for enhanced features)

| Key | Value | Default |
|-----|-------|---------|
| `REDIS_ENABLED` | `false` | `false` |
| `QDRANT_HOST` | Your Qdrant host | `localhost` |
| `QDRANT_API_KEY` | Your Qdrant API key | - |

### Via Vercel CLI

```bash
# Add DATABASE_URL
vercel env add DATABASE_URL production
# Paste your POSTGRES_URL value when prompted

vercel env add DATABASE_URL preview
# Paste the same value

vercel env add DATABASE_URL development
# Paste the same value

# Add SECRET_KEY (generate it first)
openssl rand -base64 32
# Copy the output

vercel env add SECRET_KEY production
# Paste the generated secret

vercel env add SECRET_KEY preview
# Paste the same secret

vercel env add SECRET_KEY development
# Paste the same secret

# Add OPENAI_API_KEY
vercel env add OPENAI_API_KEY production
# Paste your OpenAI key (sk-...)

vercel env add OPENAI_API_KEY preview
vercel env add OPENAI_API_KEY development
```

---

## Step 4: Deploy Your Application

### Via Vercel CLI

```bash
# From your project root
cd /path/to/Doctor-Ai

# Deploy to production
vercel --prod
```

### Via GitHub Integration

1. Push your code to GitHub:
   ```bash
   git push origin main
   ```
2. Vercel auto-deploys (if connected to GitHub)
3. Check deployment status in Vercel dashboard

### Deployment URL

After deployment completes, you'll get a URL like:
```
https://doctor-ai-xyz123.vercel.app
```

---

## Step 5: Initialize Database Tables

⚠️ **IMPORTANT:** Your database is empty! You need to create tables.

### Method 1: Using the One-Time Init Endpoint (Easiest)

1. Visit the initialization endpoint:
   ```
   https://your-app.vercel.app/api/init_database
   ```

2. You should see a success response:
   ```json
   {
     "status": "success",
     "message": "Database initialized successfully!",
     "admin_credentials": {
       "username": "admin",
       "password": "ChangeMe123!@#",
       "warning": "⚠️ CHANGE THIS PASSWORD IMMEDIATELY!"
     },
     "next_steps": [
       "1. Change the admin password immediately",
       "2. DELETE this api/init_database.py file",
       "3. Redeploy your application"
     ]
   }
   ```

3. **SECURITY:** Delete the init file and redeploy:
   ```bash
   rm api/init_database.py
   git add api/init_database.py
   git commit -m "Remove database init endpoint for security"
   git push origin main
   ```

### Method 2: Using Local Script (Alternative)

```bash
# 1. Pull environment variables locally
vercel env pull .env.local

# 2. Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run initialization script
python scripts/init_db.py

# You should see:
# ✅ Database tables created successfully
# ✅ Admin user created successfully
# ⚠️ Default admin password is 'ChangeMe123!@#' - CHANGE IT IMMEDIATELY!
```

---

## Step 6: Verify Your Deployment

### 1. Check Frontend

Visit your app:
```
https://your-app.vercel.app
```

You should see the Doctor-AI landing page.

### 2. Check Backend Health

Visit the health endpoint:
```
https://your-app.vercel.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Medical Symptom Constellation Mapper",
  "version": "0.1.0",
  "ai_features": "enabled"
}
```

### 3. Test Database Connection

Try logging in:
1. Click "Login" on the frontend
2. Username: `admin`
3. Password: `ChangeMe123!@#`

If successful, database is working! ✅

**⚠️ CHANGE THE ADMIN PASSWORD IMMEDIATELY**

### 4. Test a Diagnosis

1. Click "Start Diagnosis"
2. Fill in sample symptoms
3. Submit

If you get results, everything is working! 🎉

---

## Step 7: Post-Deployment Checklist

- [ ] Change admin password from default
- [ ] Delete `api/init_database.py` file (if using Method 1)
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts
- [ ] Set up database backups
- [ ] Test all features
- [ ] Review Vercel usage/limits

---

## 🔧 Troubleshooting

### Issue: "SECRET_KEY must be set"

**Solution:**
```bash
# Generate a key
openssl rand -base64 32

# Add it to Vercel environment variables
vercel env add SECRET_KEY production
# Paste the generated key
```

### Issue: Database connection fails

**Check:**
1. Is `DATABASE_URL` set in Vercel environment variables?
2. Is the database active (not paused)?
3. Try viewing the connection string:
   ```bash
   vercel env pull .env.local
   cat .env.local | grep POSTGRES_URL
   ```

### Issue: Frontend shows but API calls fail

**Check:**
1. Visit `/api/v1/health` - does it work?
2. Check browser console for errors
3. Verify CORS is configured (should work automatically with same-domain)

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue: Build fails on Vercel

**Check:**
1. Build logs in Vercel dashboard
2. Python version (should be 3.11+)
3. Node.js version (should be 18+)
4. Check `runtime.txt` exists with `python-3.11`

---

## 📊 Vercel Limits (Hobby Plan)

- **Bandwidth:** 100 GB/month
- **Serverless execution:** 100 hours/month
- **Database:** 256 MB storage (Hobby Postgres)
- **Functions:** 10-second timeout

**Need more?** Upgrade to Pro plan

---

## 🎓 Next Steps

### Set Up Custom Domain

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS records
4. SSL is automatic

### Enable Monitoring

1. Go to Project → Analytics
2. Enable Web Analytics
3. Monitor traffic and performance

### Set Up CI/CD

Already done if using GitHub! Every push auto-deploys.

### Database Backups

Vercel Postgres includes:
- Automatic daily backups (7-day retention on Hobby)
- Point-in-time recovery (Pro plan)

---

## 📚 Resources

- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Doctor-AI Documentation](./README.md)
- [Deployment Guide](./VERCEL_UNIFIED_DEPLOYMENT.md)

---

## ✅ Summary

You've successfully:
1. ✅ Created a Vercel Postgres database
2. ✅ Connected it to your project
3. ✅ Configured environment variables
4. ✅ Deployed the application
5. ✅ Initialized database tables
6. ✅ Verified everything works

Your Doctor-AI app is now live! 🎉

**Deployment URL:** `https://your-app.vercel.app`

Questions? Check the [main README](./README.md) or open an issue on GitHub.
