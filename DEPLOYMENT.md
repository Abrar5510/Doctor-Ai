# Deployment Guide

This guide covers deploying Doctor-AI in different environments.

## Deployment Options

| Environment | Use Case | Complexity |
|-------------|----------|------------|
| Local Development | Development, Testing | Low |
| Docker | Production deployments | Low |
| Vercel | Serverless (frontend only) | Medium |
| Cloud Platforms | Production at scale | Medium |

## Local Development

See [SETUP.md](./SETUP.md) for local development setup.

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/Abrar5510/Doctor-Ai.git
cd Doctor-Ai

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker compose up -d

# Initialize database
python scripts/seed_data.py
```

### Access the Application

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Qdrant Dashboard: http://localhost:6333/dashboard

### Docker Services

The `docker-compose.yml` includes:
- **Qdrant**: Vector database (port 6333)
- **PostgreSQL**: Relational database (port 5432)
- **Redis**: Cache layer (port 6379)

### Stopping Services

```bash
# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v
```

## Vercel Deployment

**Note**: Vercel is best suited for the frontend only. The backend requires a container platform.

### Frontend Deployment

1. **Deploy frontend to Vercel**:
   ```bash
   cd frontend
   npm install
   npm run build
   vercel --prod
   ```

2. **Set environment variable**:
   In Vercel dashboard, add:
   ```
   VITE_API_URL=https://your-backend-url.com
   ```

### Backend Options

Deploy the backend to a container platform:
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io
- **AWS/GCP/Azure**: Container services

## Cloud Platforms

### Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Add environment variables in Railway dashboard

### Render

1. Create `render.yaml` (already included in repo)

2. Connect repository to Render dashboard

3. Configure environment variables

### Fly.io

1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Deploy:
   ```bash
   fly launch
   fly deploy
   ```

## Environment Variables

### Required Variables

```bash
# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ML Model
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Optional Variables

```bash
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Confidence Thresholds
TIER1_CONFIDENCE_THRESHOLD=0.85
TIER2_CONFIDENCE_THRESHOLD=0.60
TIER3_CONFIDENCE_THRESHOLD=0.40

# Features
ENABLE_RARE_DISEASE_DETECTION=true
ENABLE_RED_FLAG_ALERTS=true
```

## Production Considerations

### Security

- Use strong passwords for databases
- Enable HTTPS/TLS encryption
- Configure CORS properly
- Set secure environment variables
- Enable authentication

### Performance

- Use Redis for caching
- Configure connection pooling
- Monitor query performance
- Scale horizontally as needed

### Monitoring

```bash
# View Docker logs
docker compose logs -f

# Check service status
docker compose ps

# Monitor resource usage
docker stats
```

## Troubleshooting

### Docker Issues

**Port already in use**:
```bash
# Change ports in docker-compose.yml
# Then restart services
docker compose down
docker compose up -d
```

**Out of memory**:
- Increase Docker memory limit
- Close other applications
- System requires minimum 8GB RAM

**Container won't start**:
```bash
# Check logs
docker compose logs [service-name]

# Rebuild container
docker compose build --no-cache
docker compose up -d
```

### Database Issues

**Connection failed**:
```bash
# Check if services are running
docker compose ps

# Restart database
docker compose restart postgres

# Verify connection settings in .env
```

**Data persistence**:
```bash
# Volumes are defined in docker-compose.yml
# Data persists across container restarts
# To reset data:
docker compose down -v  # WARNING: deletes all data
```

## Scaling

### Horizontal Scaling

1. **FastAPI backend**: Deploy multiple instances behind load balancer
2. **Qdrant**: Use Qdrant Cloud or cluster mode
3. **PostgreSQL**: Use read replicas
4. **Redis**: Use Redis cluster

### Vertical Scaling

- Increase container memory limits
- Allocate more CPU cores
- Use GPU for ML models

## Health Checks

The API includes health check endpoints:

```bash
# Check API health
curl http://localhost:8000/health

# Check Qdrant connection
curl http://localhost:8000/api/v1/health/qdrant

# Check database connection
curl http://localhost:8000/api/v1/health/db
```

## Backup and Recovery

### Backup Data

```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U user dbname > backup.sql

# Backup Qdrant
# Use Qdrant's snapshot feature via API
curl -X POST "http://localhost:6333/collections/medical_conditions/snapshots"
```

### Restore Data

```bash
# Restore PostgreSQL
docker compose exec -T postgres psql -U user dbname < backup.sql

# Restore Qdrant
# Upload snapshot via Qdrant API
```

## Additional Resources

- **Setup Guide**: [SETUP.md](./SETUP.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Main README**: [README.md](./README.md)

---

For issues or questions, visit: https://github.com/Abrar5510/Doctor-Ai/issues
