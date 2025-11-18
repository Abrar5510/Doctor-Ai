# Vercel Deployment Guide for Doctor AI

This guide explains how to deploy the Doctor AI application using Vercel for the frontend and an external service for the backend.

## Architecture Overview

**Important**: Vercel is designed for frontend applications and serverless functions. Due to the nature of this application (large ML models, FastAPI backend, stateful services), we use a **hybrid deployment approach**:

- **Frontend**: Deployed on Vercel (React + Vite)
- **Backend**: Deployed on Render, Railway, Fly.io, or similar platform (FastAPI + ML models)

This approach provides:
- ✅ Fast, global CDN for frontend (Vercel)
- ✅ Optimal performance for ML models (dedicated backend service)
- ✅ No cold start issues
- ✅ Cost-effective deployment

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Backend Deployment**: Your backend should be deployed and accessible via URL
   - Render (recommended - see `RENDER_DEPLOYMENT.md`)
   - Railway: https://railway.app
   - Fly.io: https://fly.io
   - Any other platform supporting Python/FastAPI
3. **Git Repository**: Code pushed to GitHub, GitLab, or Bitbucket

## Deployment Options

### Option 1: Deploy via Vercel Dashboard (Recommended)

#### Step 1: Prepare Backend

1. **Deploy your backend** to Render, Railway, or similar platform (see `RENDER_DEPLOYMENT.md`)
2. **Note your backend URL**, e.g., `https://doctor-ai-backend.onrender.com`
3. **Ensure CORS is configured** on the backend to allow your Vercel domain

#### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Click "Add New Project"**

3. **Import Git Repository**:
   - Select your Git provider (GitHub, GitLab, Bitbucket)
   - Choose the `Doctor-Ai` repository
   - Click "Import"

4. **Configure Project**:
   - **Framework Preset**: Select "Vite"
   - **Root Directory**: Leave as `.` (root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

5. **Add Environment Variables**:
   ```
   VITE_API_URL = https://your-backend-url.onrender.com
   ```
   Replace with your actual backend URL (without trailing slash)

6. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (2-5 minutes)
   - Vercel will provide you with a URL like `https://doctor-ai-xyz.vercel.app`

#### Step 3: Update Backend CORS

1. **Go to your backend service** (e.g., Render dashboard)

2. **Update CORS_ORIGINS environment variable**:
   ```
   CORS_ORIGINS=https://doctor-ai-xyz.vercel.app,http://localhost:3000
   ```
   Include your Vercel URL (the one provided after deployment)

3. **Redeploy backend** service to apply changes

4. **Test the connection**:
   - Visit your Vercel URL
   - Check browser console for any CORS errors
   - Test the diagnosis feature

### Option 2: Deploy via Vercel CLI

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

#### Step 3: Configure Project

1. **Set environment variables**:
   ```bash
   vercel env add VITE_API_URL
   ```
   Enter your backend URL when prompted: `https://your-backend-url.onrender.com`

2. **Deploy**:
   ```bash
   # For production
   vercel --prod

   # For preview
   vercel
   ```

3. **Follow prompts**:
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No (first time) or Yes (subsequent deploys)
   - Project name: doctor-ai
   - Directory: ./
   - Override settings: Yes
   - Build command: `cd frontend && npm install && npm run build`
   - Output directory: `frontend/dist`
   - Development command: `cd frontend && npm run dev`

#### Step 4: Update Backend CORS

Same as Option 1, Step 3.

## Custom Domain Setup (Optional)

1. **In Vercel Dashboard**:
   - Go to your project → Settings → Domains
   - Click "Add"
   - Enter your domain name

2. **Configure DNS**:
   - Add CNAME record pointing to `cname.vercel-dns.com`
   - Or add A record pointing to Vercel's IP
   - Follow Vercel's instructions for your DNS provider

3. **Update Backend CORS**:
   - Add your custom domain to `CORS_ORIGINS`
   - Redeploy backend

## Environment Variables

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://doctor-ai-backend.onrender.com` |

**Important**:
- No trailing slash in `VITE_API_URL`
- Must be accessible from browser (public URL)
- Must have CORS configured

### Backend (Render/Railway/Fly.io)

Add your Vercel domain(s) to `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com,http://localhost:3000
```

## Vercel Configuration Files

### vercel.json

The `vercel.json` file configures the deployment:

```json
{
  "version": 2,
  "name": "doctor-ai",
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

Key settings:
- **buildCommand**: Builds the Vite app
- **outputDirectory**: Where built files are located
- **routes**: Handles React Router (SPA routing)

### .vercelignore

Excludes backend code and unnecessary files from deployment:
- Python backend code
- Docker files
- Environment files
- Documentation

## Deployment Workflow

### Automatic Deployments

Vercel automatically deploys when you push to your repository:

1. **Production Deployments** (main branch):
   - Push to `main` branch
   - Vercel builds and deploys automatically
   - Updates production URL

2. **Preview Deployments** (feature branches):
   - Push to any other branch
   - Vercel creates preview deployment
   - Provides unique URL for testing
   - Perfect for pull request reviews

### Manual Deployments

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Rollback to previous deployment
vercel rollback
```

## Monitoring and Logs

### Vercel Dashboard

1. **Deployments**: View all deployments and their status
2. **Analytics**: Traffic, performance metrics
3. **Logs**: Build logs and runtime logs (functions)
4. **Speed Insights**: Performance monitoring

### Access Logs

```bash
# View recent logs
vercel logs <deployment-url>

# Follow logs in real-time
vercel logs <deployment-url> --follow
```

## Performance Optimization

### Vercel Edge Network

Vercel automatically:
- ✅ Distributes your app globally via CDN
- ✅ Enables HTTP/2 and HTTP/3
- ✅ Compresses assets (gzip/brotli)
- ✅ Optimizes images (if using Next.js Image)
- ✅ Provides SSL/TLS certificates

### Build Optimization

1. **Enable Build Cache**:
   - Automatically enabled by Vercel
   - Speeds up subsequent builds

2. **Optimize Dependencies**:
   ```bash
   # In frontend directory
   npm prune --production
   ```

3. **Code Splitting**:
   - Vite handles this automatically
   - Reduces initial bundle size

## Cost Estimate

### Free Tier (Hobby)
- **Deployment**: Unlimited
- **Bandwidth**: 100 GB/month
- **Build Time**: 100 hours/month
- **Serverless Functions**: Not needed (frontend only)
- **Custom Domains**: Included
- **SSL Certificates**: Free
- **Total**: **$0/month** ✨

Perfect for:
- Personal projects
- Demos and prototypes
- Small applications

### Pro Tier ($20/month)
- **Deployment**: Unlimited
- **Bandwidth**: 1 TB/month
- **Build Time**: 400 hours/month
- **Analytics**: Enhanced
- **Team Features**: Included
- **Total**: **$20/month**

### With Backend (Render)
- **Vercel Frontend**: $0/month (free tier)
- **Render Backend**: $0-25/month (free or starter plan)
- **Render Database**: $0-7/month (external free DB or paid)
- **Total**: **$0-52/month**

## Troubleshooting

### Build Fails

**Error**: `Cannot find module 'vite'`
- **Solution**: Ensure `buildCommand` includes `npm install`
- Check `package.json` exists in `frontend/` directory

**Error**: `Build exceeded time limit`
- **Solution**:
  - Upgrade to Pro plan for longer build times
  - Optimize dependencies
  - Remove unnecessary dev dependencies

### Frontend Can't Connect to Backend

**Error**: `Network Error` or `CORS Error`
- **Solution**:
  1. Verify `VITE_API_URL` is set correctly
  2. Check backend URL is accessible
  3. Ensure CORS_ORIGINS includes your Vercel domain
  4. Test backend health: `curl https://your-backend.com/health`

**Error**: `Failed to fetch`
- **Solution**:
  1. Check backend is deployed and running
  2. Verify environment variable has no trailing slash
  3. Test API in browser: `https://your-backend.com/api/v1/monitoring/health`

### Routing Issues

**Error**: 404 on refresh or direct URL access
- **Solution**: Ensure routes are configured in `vercel.json`:
  ```json
  {
    "routes": [
      { "src": "/(.*)", "dest": "/index.html" }
    ]
  }
  ```

### Environment Variables Not Working

**Error**: `undefined` when accessing `import.meta.env.VITE_API_URL`
- **Solution**:
  1. Ensure variable starts with `VITE_` prefix
  2. Redeploy after adding environment variable
  3. Check variable is added in Vercel dashboard
  4. Rebuild the app

## Security Best Practices

### Frontend Security

1. **Environment Variables**:
   - ✅ Use `VITE_` prefix for public variables
   - ❌ Never store API keys or secrets in frontend
   - ✅ All frontend env vars are public

2. **HTTPS**:
   - ✅ Automatically enabled by Vercel
   - ✅ Enforced on all domains

3. **Headers**:
   - Configure security headers in `vercel.json`
   - Add Content Security Policy (CSP)

### Backend Security

1. **CORS**:
   - ✅ Only allow specific origins (your Vercel domains)
   - ❌ Never use `*` for production

2. **API Keys**:
   - ✅ Store in backend environment variables
   - ❌ Never expose in frontend code

3. **Rate Limiting**:
   - ✅ Already implemented in backend
   - Monitor and adjust as needed

## Advanced Configuration

### Custom Headers

Add to `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Redirects

Add to `vercel.json`:

```json
{
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ]
}
```

### Preview Deployments

Configure preview branch deployments:

1. **In Vercel Dashboard**:
   - Go to Settings → Git
   - Configure which branches trigger deployments
   - Set production branch (usually `main`)

2. **Environment Variables**:
   - Set different values for preview/production
   - Use preview backend URL for testing

## Testing the Deployment

### 1. Backend Health Check

```bash
curl https://your-backend.onrender.com/api/v1/monitoring/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Medical Symptom Constellation Mapper",
  "version": "0.2.0"
}
```

### 2. Frontend Deployment

Visit your Vercel URL: `https://your-app.vercel.app`

Check:
- ✅ Landing page loads
- ✅ Navigation works
- ✅ No console errors

### 3. API Connection

1. Open browser console
2. Navigate to diagnosis page
3. Submit a test diagnosis
4. Verify API calls succeed (Network tab)

### 4. Full Flow Test

1. **Landing Page**: Visit `/`
2. **Dashboard**: Navigate to `/dashboard`
3. **Diagnosis**: Go to `/diagnose`
4. **Submit Test**: Enter symptoms and submit
5. **View Results**: Check diagnosis results display

## Comparison: Vercel vs Render

| Feature | Vercel (Frontend) | Render (Backend) |
|---------|-------------------|------------------|
| **Best For** | React, Vue, Next.js | Python, Node, Go APIs |
| **Free Tier** | 100GB bandwidth | 750 hours/month |
| **Build Time** | Fast (2-5 min) | Moderate (3-10 min) |
| **Cold Starts** | None (CDN) | Yes on free tier |
| **Custom Domains** | Free | Free |
| **SSL** | Automatic | Automatic |
| **Global CDN** | Yes | No (single region) |
| **ML Models** | Not suitable | ✅ Suitable |
| **Databases** | Not included | PostgreSQL available |

## Alternative Backend Options

### Railway
- **Pros**: Easy deployment, generous free tier
- **Cons**: Free tier limited, can be slow
- **Setup**: `railway up` from project root

### Fly.io
- **Pros**: Edge deployment, fast cold starts
- **Cons**: More complex setup
- **Setup**: Requires Dockerfile

### Google Cloud Run
- **Pros**: Scalable, pay-per-use
- **Cons**: Requires GCP setup
- **Setup**: Deploy container

### AWS App Runner
- **Pros**: AWS integration, scalable
- **Cons**: More expensive
- **Setup**: Container or source code

## Migration from Render to Vercel (Frontend Only)

If you're currently using Render for everything:

1. **Keep Backend on Render**: Don't change anything
2. **Deploy Frontend to Vercel**: Follow this guide
3. **Update CORS**: Add Vercel domain to backend
4. **Test**: Ensure everything works
5. **Update DNS** (if using custom domain): Point to Vercel
6. **Remove Frontend from Render**: Optional, can keep as backup

## Support and Resources

### Vercel Resources
- **Documentation**: https://vercel.com/docs
- **Community**: https://github.com/vercel/vercel/discussions
- **Status**: https://vercel-status.com

### Doctor AI Resources
- **Main README**: See `README.md`
- **Render Deployment**: See `RENDER_DEPLOYMENT.md`
- **API Documentation**: https://your-backend.com/docs

### Getting Help

1. **Build Issues**: Check Vercel deployment logs
2. **Runtime Issues**: Check browser console
3. **API Issues**: Check backend logs on Render
4. **CORS Issues**: Verify CORS_ORIGINS includes your domain

## Next Steps

After successful deployment:

1. ✅ **Test all features thoroughly**
2. ✅ **Set up custom domain** (optional)
3. ✅ **Enable analytics** in Vercel
4. ✅ **Monitor performance** (Vercel Speed Insights)
5. ✅ **Set up alerts** for backend (Render)
6. ✅ **Configure backups** for database
7. ✅ **Document** your deployment URLs
8. ✅ **Share** with users!

## Conclusion

This hybrid deployment approach gives you:
- ⚡ Lightning-fast frontend (Vercel CDN)
- 🧠 Powerful backend (Render/Railway/etc.)
- 💰 Cost-effective ($0-52/month)
- 🌍 Global performance
- 🔒 Secure and scalable

Your Doctor AI application is now deployed and ready to help diagnose symptoms worldwide! 🏥✨
