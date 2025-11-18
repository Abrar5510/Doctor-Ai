# Render Deployment Guide for Doctor AI

This guide will help you deploy the Doctor AI application to Render.

## Prerequisites

- A Render account (sign up at https://render.com)
- Git repository connected to Render
- OpenAI API key (optional, for AI assistant features)

## Deployment Options

### Option 1: One-Click Deploy (Recommended)

We've included a `render.yaml` file that allows you to deploy the entire stack with one click:

1. **Fork or push this repository to GitHub**

2. **Connect to Render:**
   - Go to https://render.com/dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the `Doctor-Ai` repository

3. **Configure environment variables:**
   - The deployment will automatically create:
     - Backend API service
     - Frontend static site
     - PostgreSQL database

4. **Required manual configuration:**
   - Add your `OPENAI_API_KEY` if you want AI assistant features
   - Update `CORS_ORIGINS` to include your frontend URL

5. **Click "Apply"** and wait for deployment to complete

### Option 2: Manual Deployment

#### 1. Deploy PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `doctor-ai-db`
3. Database Name: `doctor_ai`
4. User: `doctor_ai_user`
5. Region: Oregon (or your preferred region)
6. Plan: Starter ($7/month)
7. Click "Create Database"
8. **Save the Internal Database URL** - you'll need it for the backend

#### 2. Deploy Backend API

1. Go to Render Dashboard → New → Web Service
2. Connect your repository
3. Configure:
   - **Name:** `doctor-ai-backend`
   - **Region:** Oregon (same as database)
   - **Branch:** main
   - **Root Directory:** (leave blank)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Starter ($7/month)

4. **Environment Variables:** Add the following:

```bash
# Application
APP_NAME=Medical Symptom Constellation Mapper
APP_VERSION=0.2.0
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PREFIX=/api/v1

# Security (Auto-generate in Render)
SECRET_KEY=<auto-generate-32-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Update after frontend is deployed)
CORS_ORIGINS=https://doctor-ai-frontend.onrender.com,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Database (Use Internal Database URL from step 1)
DATABASE_URL=<your-postgresql-internal-url>
DATABASE_ECHO=false

# Qdrant (Not available on free tier - disable for now)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=medical_conditions

# Redis (Not available on free tier - disable caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# ML Models
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
EMBEDDING_DIMENSION=768
MAX_SEQUENCE_LENGTH=512

# AI Assistant (Add your OpenAI key)
OPENAI_API_KEY=<your-openai-api-key>
USE_LOCAL_LLM=false

# Medical Ontology
USE_SNOMED_CT=true
USE_ICD10=true
USE_HPO=true

# Confidence Thresholds
TIER1_CONFIDENCE_THRESHOLD=0.85
TIER2_CONFIDENCE_THRESHOLD=0.60
TIER3_CONFIDENCE_THRESHOLD=0.40

# Search Parameters
TOP_K_CANDIDATES=50
FINAL_RESULTS_LIMIT=10

# HIPAA Compliance
ENABLE_AUDIT_LOGGING=true
ENABLE_DATA_ANONYMIZATION=true
AUDIT_LOG_PATH=./logs/audit/

# Feature Flags
ENABLE_RARE_DISEASE_DETECTION=true
ENABLE_RED_FLAG_ALERTS=true
ENABLE_TEMPORAL_ANALYSIS=true
ENABLE_AI_ASSISTANT=true
```

5. **Health Check Path:** `/api/v1/monitoring/health`
6. Click "Create Web Service"
7. **Save the backend URL** (e.g., `https://doctor-ai-backend.onrender.com`)

#### 3. Deploy Frontend

1. Go to Render Dashboard → New → Static Site
2. Connect your repository
3. Configure:
   - **Name:** `doctor-ai-frontend`
   - **Branch:** main
   - **Root Directory:** (leave blank)
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`

4. **Environment Variables:**
```bash
VITE_API_URL=https://doctor-ai-backend.onrender.com
```

5. **Rewrite Rules:** Add this to handle React Router:
   - Source: `/*`
   - Destination: `/index.html`
   - Action: Rewrite

6. Click "Create Static Site"

#### 4. Update CORS Origins

After frontend is deployed:
1. Go to your backend service settings
2. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   https://doctor-ai-frontend.onrender.com,http://localhost:3000
   ```
3. Save and redeploy

## Post-Deployment Setup

### 1. Database Initialization

The application will automatically create tables on first run. However, you need to seed the vector database with medical condition data:

**Note:** Qdrant is not available on Render's free tier. For production deployment:
- Consider upgrading to a paid plan and running Qdrant as a private service
- Or use Qdrant Cloud (https://cloud.qdrant.io/)
- Or temporarily disable vector search features for demo

### 2. Testing the Deployment

1. **Backend Health Check:**
   ```bash
   curl https://doctor-ai-backend.onrender.com/api/v1/monitoring/health
   ```

2. **Dashboard API:**
   ```bash
   curl https://doctor-ai-backend.onrender.com/api/v1/dashboard/overview
   ```

3. **Frontend:** Visit your frontend URL and test:
   - Landing page at `/`
   - Dashboard at `/dashboard`
   - Diagnosis tool at `/diagnose`

## Important Notes

### Free Tier Limitations

1. **Services spin down after 15 minutes of inactivity**
   - First request may take 30-60 seconds to wake up
   - Consider upgrading to paid plan for production

2. **No Qdrant or Redis on free tier**
   - Vector search features will be limited
   - No caching available
   - Consider using Qdrant Cloud or upgrading plan

3. **Database storage limited to 1GB**
   - Should be sufficient for demo purposes
   - Monitor usage in Render dashboard

### Performance Optimization

1. **ML Model Loading:**
   - First request will be slow as BioBERT downloads (~420MB)
   - Subsequent requests will be faster
   - Consider pre-downloading models during build

2. **Memory Usage:**
   - ML models require ~2GB RAM
   - Starter plan has 512MB - upgrade to Standard ($25/mo) for better performance

3. **Startup Time:**
   - Initial startup takes 1-2 minutes
   - Health check should account for this

## Cost Estimate

### Minimal Setup (Demo)
- PostgreSQL Starter: $7/month
- Backend Starter: $7/month
- Frontend Static: FREE
- **Total: ~$14/month**

### Production Setup
- PostgreSQL Standard: $20/month
- Backend Standard (2GB RAM): $25/month
- Frontend Pro: $3/month
- Qdrant Cloud Starter: $25/month
- **Total: ~$73/month**

## Monitoring

1. **Application Logs:** Available in Render dashboard
2. **Health Endpoint:** `/api/v1/monitoring/health`
3. **Metrics Endpoint:** `/api/v1/monitoring/metrics`
4. **Dashboard:** View system analytics at `/dashboard`

## Troubleshooting

### Backend Won't Start
- Check environment variables are set correctly
- Verify DATABASE_URL is using the internal URL
- Check logs for specific errors

### Frontend Can't Connect to Backend
- Verify VITE_API_URL is set correctly
- Check CORS_ORIGINS includes frontend URL
- Test backend health endpoint directly

### Database Connection Issues
- Use internal database URL, not external
- Verify database service is running
- Check database credentials

### ML Model Errors
- Ensure sufficient memory (upgrade to Standard plan)
- Check internet connectivity for model download
- Verify transformers library is installed

## Security Considerations

1. **SECRET_KEY:** Use Render's auto-generate feature
2. **OPENAI_API_KEY:** Store as environment variable, never commit
3. **DATABASE_URL:** Automatically secured by Render
4. **HTTPS:** Enabled by default on all Render services

## Scaling

For production use:
1. Upgrade to Standard or Pro plans for better performance
2. Add Qdrant Cloud for vector search
3. Add Redis Cloud for caching
4. Enable auto-scaling if traffic is variable
5. Consider CDN for frontend assets

## Support

For issues specific to Render deployment:
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

For Doctor AI application issues:
- Check application logs
- Review API documentation at `/docs`
- Test individual endpoints

## Next Steps

After deployment:
1. ✅ Test all endpoints
2. ✅ Verify dashboard displays data
3. ✅ Test diagnosis tool with sample data
4. ✅ Monitor performance and logs
5. ✅ Set up custom domain (optional)
6. ✅ Configure alerts and monitoring
