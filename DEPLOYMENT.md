# Deployment Guide

This guide covers deploying Doctor-AI in various environments from development to production.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Scaling](#scaling)

## Deployment Options

### Quick Comparison

| Environment | Use Case | Complexity | Cost |
|-------------|----------|------------|------|
| Local Development | Development, Testing | Low | Free |
| Docker Compose | Small deployments, Demos | Low | Low |
| Docker Swarm | Medium deployments | Medium | Medium |
| Kubernetes | Production, Scale | High | Variable |
| Cloud (Managed) | Production | Medium | Variable |

## Local Development

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- 8GB+ RAM
- 10GB+ disk space

### Setup Steps

1. **Clone Repository**

   ```bash
   git clone https://github.com/Abrar5510/Doctor-Ai.git
   cd Doctor-Ai
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start Services**

   ```bash
   docker-compose up -d
   ```

6. **Initialize Database**

   ```bash
   python scripts/seed_data.py
   ```

7. **Run Application**

   ```bash
   python -m src.main
   # Or: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Verify**

   Visit http://localhost:8000/docs

## Docker Deployment

### Using Docker Compose

#### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - QDRANT_HOST=qdrant
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:password@postgres:5432/doctor_ai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - qdrant
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - doctor-ai-network
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped
    networks:
      - doctor-ai-network

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=doctor_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - doctor-ai-network

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - doctor-ai-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - doctor-ai-network

volumes:
  qdrant_storage:
  postgres_data:
  redis_data:

networks:
  doctor-ai-network:
    driver: bridge
```

#### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
        limit_req zone=api_limit burst=20 nodelay;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint (no rate limit)
        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

#### Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Stop services
docker-compose -f docker-compose.prod.yml down

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Dockerfile Optimization

Create optimized `Dockerfile`:

```dockerfile
# Multi-stage build
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production image
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Push Docker Image to ECR**

   ```bash
   # Authenticate with ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag image
   docker build -t doctor-ai .
   docker tag doctor-ai:latest <account>.dkr.ecr.us-east-1.amazonaws.com/doctor-ai:latest

   # Push image
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/doctor-ai:latest
   ```

2. **Create ECS Task Definition**

   ```json
   {
     "family": "doctor-ai",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "api",
         "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/doctor-ai:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "QDRANT_HOST",
             "value": "qdrant.service.local"
           }
         ],
         "secrets": [
           {
             "name": "OPENAI_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/doctor-ai",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "api"
           }
         },
         "healthCheck": {
           "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
           "interval": 30,
           "timeout": 5,
           "retries": 3
         }
       }
     ]
   }
   ```

3. **Create ECS Service**

   ```bash
   aws ecs create-service \
     --cluster doctor-ai-cluster \
     --service-name doctor-ai-service \
     --task-definition doctor-ai \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
     --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/doctor-ai-tg,containerName=api,containerPort=8000"
   ```

#### Using AWS Managed Services

- **Qdrant**: Self-hosted on EC2 or use Qdrant Cloud
- **PostgreSQL**: Amazon RDS
- **Redis**: Amazon ElastiCache
- **Secrets**: AWS Secrets Manager
- **Load Balancer**: Application Load Balancer
- **Monitoring**: CloudWatch

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/doctor-ai
gcloud run deploy doctor-ai \
  --image gcr.io/PROJECT_ID/doctor-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars QDRANT_HOST=qdrant.service.local
```

### Azure

#### Using Azure Container Instances

```bash
az container create \
  --resource-group doctor-ai-rg \
  --name doctor-ai \
  --image <registry>.azurecr.io/doctor-ai:latest \
  --dns-name-label doctor-ai \
  --ports 8000 \
  --environment-variables \
    QDRANT_HOST=qdrant.service.local
```

## Production Considerations

### Security Checklist

- [ ] HTTPS/TLS enabled with valid certificates
- [ ] API authentication implemented
- [ ] Secrets stored in secure secret manager
- [ ] Database passwords rotated regularly
- [ ] Network security groups configured
- [ ] CORS policy restricted
- [ ] Rate limiting enabled
- [ ] Firewall rules configured
- [ ] Regular security updates applied
- [ ] Audit logging enabled

### Environment Variables

**Production `.env`:**

```bash
# Application
APP_NAME=Doctor-AI
DEBUG=False
LOG_LEVEL=WARNING

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security (use strong random values)
SECRET_KEY=<generate-strong-secret>
API_KEY=<generate-api-key>

# Databases (use managed services)
QDRANT_HOST=qdrant-cluster.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=<qdrant-api-key>

DATABASE_URL=postgresql://user:pass@rds-instance.amazonaws.com:5432/doctor_ai
REDIS_HOST=redis-cluster.cache.amazonaws.com
REDIS_PASSWORD=<redis-password>

# AI (use production API key)
OPENAI_API_KEY=<openai-api-key>

# Features
ENABLE_AUDIT_LOGGING=True
ENABLE_RATE_LIMITING=True
```

### Performance Optimization

1. **Enable Caching**
   - Redis for API responses
   - Embedding cache
   - Query result cache

2. **Connection Pooling**
   ```python
   # PostgreSQL connection pool
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=10
   ```

3. **Async Workers**
   ```bash
   # Gunicorn with uvicorn workers
   gunicorn src.main:app \
     -w 4 \
     -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

4. **Resource Limits**
   ```yaml
   # Docker resource limits
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
       reservations:
         cpus: '1'
         memory: 2G
   ```

### High Availability

#### Multi-Region Deployment

```
Region 1 (Primary)          Region 2 (Backup)
┌─────────────────┐         ┌─────────────────┐
│  Load Balancer  │         │  Load Balancer  │
│        │        │         │        │        │
│     API (x3)    │◄───────►│     API (x3)    │
│        │        │         │        │        │
│   Qdrant (HA)   │◄───────►│   Qdrant (HA)   │
│        │        │         │        │        │
│   PostgreSQL    │◄───────►│   PostgreSQL    │
│    (Primary)    │  Sync   │    (Replica)    │
└─────────────────┘         └─────────────────┘
```

#### Backup Strategy

```bash
# Automated daily backups
# Qdrant
0 2 * * * /scripts/backup_qdrant.sh

# PostgreSQL
0 3 * * * pg_dump doctor_ai | gzip > /backups/doctor_ai_$(date +%Y%m%d).sql.gz

# Retention: 30 days
find /backups -name "*.sql.gz" -mtime +30 -delete
```

## Monitoring & Maintenance

### Logging

**Structured Logging:**

```python
import logging
import json

logger = logging.getLogger(__name__)

# JSON structured logging
logger.info(json.dumps({
    "event": "diagnosis_completed",
    "case_id": case_id,
    "confidence": confidence,
    "processing_time_ms": duration
}))
```

**Log Aggregation:**

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Cloud provider logging (CloudWatch, Stackdriver)
- Third-party (Datadog, Splunk)

### Metrics

**Key Metrics to Monitor:**

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- Cache hit rate
- Vector search latency
- Embedding generation time
- Queue depth
- CPU/Memory usage

**Prometheus Metrics:**

```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@request_duration.time()
async def analyze_symptoms(request):
    request_count.inc()
    # ... processing
```

### Health Checks

```python
from fastapi import status

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    checks = {
        "api": "healthy",
        "qdrant": await check_qdrant(),
        "postgres": await check_postgres(),
        "redis": await check_redis()
    }

    all_healthy = all(v == "healthy" for v in checks.values())

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks
    }
```

### Alerting

**Alert Rules:**

```yaml
# Prometheus alert rules
groups:
  - name: doctor-ai
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.05
        annotations:
          summary: "High error rate detected"

      - alert: SlowResponse
        expr: histogram_quantile(0.95, api_request_duration_seconds) > 2
        annotations:
          summary: "95th percentile response time > 2s"

      - alert: ServiceDown
        expr: up{job="doctor-ai"} == 0
        annotations:
          summary: "Service is down"
```

### Maintenance Windows

```bash
# Graceful shutdown for updates
# 1. Stop accepting new requests
# 2. Wait for active requests to complete
# 3. Shutdown

# Example systemd service
[Unit]
Description=Doctor-AI API
After=network.target

[Service]
Type=notify
ExecStart=/usr/local/bin/gunicorn src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Verify network connectivity
docker network inspect doctor-ai-network

# Test database connections
docker-compose exec api python -c "from src.config import settings; print(settings.DATABASE_URL)"
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Reduce worker processes
# In .env: WORKERS=2

# Enable memory limits
# In docker-compose.yml:
# mem_limit: 2g
# mem_reservation: 1g
```

#### Slow Queries

```bash
# Enable query logging
# PostgreSQL: log_min_duration_statement = 1000

# Analyze slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Optimize Qdrant
# Increase HNSW index parameters
```

## Scaling

### Horizontal Scaling

**Scale API Servers:**

```bash
# Docker Compose
docker-compose up -d --scale api=3

# Kubernetes
kubectl scale deployment doctor-ai --replicas=5
```

**Load Balancing:**

- Round-robin
- Least connections
- IP hash (for session affinity)

### Vertical Scaling

**Increase Resources:**

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### Database Scaling

**Qdrant:**
- Sharding across multiple nodes
- Replication for high availability

**PostgreSQL:**
- Read replicas
- Connection pooling (PgBouncer)

**Redis:**
- Redis Cluster
- Redis Sentinel for HA

### Auto-Scaling

**Kubernetes HPA:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: doctor-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: doctor-ai
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

**Last Updated**: 2025-11-14
