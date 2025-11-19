# Docker Deployment Guide for Doctor-AI

## Important Note About Vercel and Docker

**Vercel does not support direct Docker deployments** on their standard (Hobby/Pro) plans. Docker support is only available on Enterprise plans through custom configurations. The current `vercel.json` configuration uses Vercel's native builders (`@vercel/python` and `@vercel/static-build`) which are optimized for serverless deployments.

This guide provides instructions for deploying Doctor-AI using Docker on platforms that support containerized applications.

## Table of Contents

1. [Local Development with Docker](#local-development-with-docker)
2. [Production Deployment Options](#production-deployment-options)
3. [Platform-Specific Deployment Guides](#platform-specific-deployment-guides)
4. [Docker Image Details](#docker-image-details)

## Local Development with Docker

### Prerequisites

- Docker Engine 20.10+
- Docker Compose V2+
- 4GB+ available RAM

### Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure your environment variables (API keys, database credentials, etc.)

3. **Start all services (databases only)**
   ```bash
   docker-compose up -d
   ```

4. **Start all services including the API**
   ```bash
   docker-compose --profile full up -d
   ```

5. **View logs**
   ```bash
   docker-compose logs -f api
   ```

6. **Stop all services**
   ```bash
   docker-compose down
   ```

### Development Workflow

For development, you might want to run the databases in Docker but run the application locally:

```bash
# Start only databases
docker-compose up -d qdrant postgres redis

# Run the application locally
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment Options

Since Vercel doesn't support Docker, here are recommended platforms that do:

### Platform Comparison

| Platform | Free Tier | Docker Support | Database Hosting | Ease of Use |
|----------|-----------|----------------|------------------|-------------|
| **Railway** | Yes ($5 credit/mo) | Native | Yes (Postgres, Redis) | ⭐⭐⭐⭐⭐ |
| **Render** | Yes (limited) | Native | Yes (Postgres) | ⭐⭐⭐⭐ |
| **Fly.io** | Yes (limited) | Native | Yes (Postgres) | ⭐⭐⭐⭐ |
| **DigitalOcean App Platform** | No | Native | Add-on required | ⭐⭐⭐ |
| **AWS ECS/Fargate** | Limited | Native | Separate (RDS, ElastiCache) | ⭐⭐ |
| **Google Cloud Run** | Yes | Native | Separate (Cloud SQL) | ⭐⭐⭐ |

## Platform-Specific Deployment Guides

### 1. Railway (Recommended)

Railway is the easiest platform for deploying Docker applications with built-in database support.

#### Steps:

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway project**
   ```bash
   railway init
   ```

4. **Add databases**
   ```bash
   railway add postgresql
   railway add redis
   ```

5. **Set environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=your_key_here
   railway variables set SECRET_KEY=your_secret_here
   ```

6. **Deploy**
   ```bash
   railway up
   ```

7. **Get deployment URL**
   ```bash
   railway open
   ```

#### Railway Configuration

Create a `railway.json` in the project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Render

Render provides a simple Docker deployment experience.

#### Steps:

1. **Create a `render.yaml` in your project root**

```yaml
services:
  - type: web
    name: doctor-ai
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: doctor-ai-db
          property: connectionString
      - key: REDIS_URL
        fromDatabase:
          name: doctor-ai-redis
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health

databases:
  - name: doctor-ai-db
    databaseName: doctor_ai
    user: doctor_ai
  - name: doctor-ai-redis
    type: redis
```

2. **Connect your GitHub repository to Render**

3. **Configure environment variables in Render dashboard**

4. **Deploy automatically on git push**

### 3. Fly.io

Fly.io offers global deployment with edge computing capabilities.

#### Steps:

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch application**
   ```bash
   fly launch
   ```

4. **Create Postgres database**
   ```bash
   fly postgres create
   fly postgres attach <postgres-app-name>
   ```

5. **Set secrets**
   ```bash
   fly secrets set OPENAI_API_KEY=your_key_here
   fly secrets set SECRET_KEY=your_secret_here
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

### 4. Google Cloud Run

For production workloads with auto-scaling.

#### Steps:

1. **Build and push Docker image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/doctor-ai
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy doctor-ai \
     --image gcr.io/PROJECT_ID/doctor-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "OPENAI_API_KEY=your_key,SECRET_KEY=your_secret"
   ```

3. **Set up Cloud SQL (Postgres)**
   ```bash
   gcloud sql instances create doctor-ai-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

## Docker Image Details

### Multi-Stage Build

The Dockerfile uses a multi-stage build process:

1. **Stage 1: Frontend Builder**
   - Uses Node.js 18 to build the React frontend
   - Compiles Vite application to static files
   - Output: `frontend/dist/`

2. **Stage 2: Backend + Production**
   - Uses Python 3.11 slim image
   - Installs system dependencies (gcc, g++, curl)
   - Installs Python dependencies
   - Downloads spaCy model
   - Copies built frontend from Stage 1
   - Sets up non-root user for security
   - Configures health checks

### Image Size Optimization

The multi-stage build ensures:
- Frontend build dependencies are not included in final image
- Python dev dependencies are excluded
- APT cache is cleaned
- Total image size: ~1.5GB (primarily due to ML models)

### Security Features

- Runs as non-root user (`appuser`)
- Minimal base image (slim variant)
- No unnecessary packages
- Health checks enabled
- Isolated logs directory

### Environment Variables

Required environment variables:

```env
# API Keys
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true
```

## Building and Running Manually

### Build the image

```bash
docker build -t doctor-ai:latest .
```

### Run with environment variables

```bash
docker run -d \
  --name doctor-ai \
  -p 8000:8000 \
  --env-file .env \
  doctor-ai:latest
```

### View logs

```bash
docker logs -f doctor-ai
```

### Access the application

Open http://localhost:8000 in your browser

## Troubleshooting

### Issue: Frontend not found

**Solution**: Ensure the frontend is built during Docker build:
```bash
docker build --no-cache -t doctor-ai:latest .
```

### Issue: Database connection failed

**Solution**: Check that your database is accessible from the container:
```bash
docker exec -it doctor-ai python -c "from src.database import engine; print(engine.connect())"
```

### Issue: Out of memory

**Solution**: Increase Docker memory allocation to at least 4GB:
- Docker Desktop: Settings → Resources → Memory → 4GB+

### Issue: spaCy model download fails

**Solution**: Pre-download the model in Dockerfile (already done) or mount a volume:
```bash
docker run -v ~/.cache:/home/appuser/.cache doctor-ai:latest
```

## Migrating from Vercel

If you're currently deployed on Vercel and want to switch to Docker:

1. **Choose a platform** from the options above (Railway recommended)
2. **Set up databases** on the new platform
3. **Migrate environment variables**
4. **Update database connection strings**
5. **Deploy using Docker**
6. **Test thoroughly**
7. **Update DNS** to point to new deployment
8. **Monitor for issues**

## Keeping Vercel

If you prefer to stay on Vercel:

- The current `vercel.json` configuration is optimized for Vercel
- Vercel handles serverless deployments efficiently
- This Dockerfile is available for local development and testing
- You can use `docker-compose up` for local development while deploying to Vercel for production

## Support

For issues or questions:
- Check the project README
- Review platform-specific documentation
- Open an issue on GitHub

## License

This deployment guide is part of the Doctor-AI project and follows the same license.
