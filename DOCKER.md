# Docker Compose Guide for Doctor-AI

## Quick Start

### Using Docker Compose v2 (Recommended)

Modern Docker installations include Compose v2, which uses the command `docker compose` (without hyphen):

```bash
# Start database services only (recommended for development)
docker compose up -d

# Or use the Makefile
make docker-up

# Start all services including the API
docker compose --profile full up -d
# Or
make docker-up-all
```

### Using Docker Compose v1 (Legacy)

If you have the standalone `docker-compose` installed:

```bash
# Start database services
docker-compose up -d

# Start all services
docker-compose --profile full up -d
```

**Note:** The Makefile automatically detects which version you have and uses the correct command.

## What Was Fixed

### 1. **Removed Deprecated Version Field**
- The `version: '3.8'` field is deprecated in newer Docker Compose specifications
- Modern compose files don't require a version field

### 2. **Added Health Checks**
All services now have proper health checks:
- **Qdrant**: HTTP check on port 6333
- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping`

This ensures containers are fully ready before dependent services start.

### 3. **Added Service Dependencies with Health Conditions**
The API service now waits for all databases to be healthy:
```yaml
depends_on:
  qdrant:
    condition: service_healthy
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

### 4. **Created .dockerignore File**
Optimizes Docker builds by excluding:
- Development files (.vscode, .idea)
- Python cache (__pycache__, *.pyc)
- Documentation files
- Test files
- Large dataset files

This reduces build context size and speeds up builds significantly.

### 5. **Added Explicit Network**
All services now use a dedicated `doctor-ai-network` bridge network for better isolation and DNS resolution.

### 6. **Fixed Environment Variables**
- Updated `.env.example` to match docker-compose.yml credentials
- PostgreSQL: `doctor_ai` / `doctor_ai_pass`
- Added comments for local vs. Docker development

### 7. **Added Service Profiles**
The API service uses the `full` profile, allowing you to:
- Run databases only: `docker compose up -d` (default)
- Run everything: `docker compose --profile full up -d`

### 8. **Improved Environment Variable Syntax**
Changed from list format to map format for better readability:
```yaml
# Old
environment:
  - POSTGRES_USER=doctor_ai

# New
environment:
  POSTGRES_USER: doctor_ai
```

## Available Services

### Default Services (always started)
- **qdrant** - Vector database (ports 6333, 6334)
- **postgres** - Relational database (port 5432)
- **redis** - Cache (port 6379)

### Optional Services (with --profile full)
- **api** - FastAPI application (port 8000)

## Usage Commands

### Basic Operations

```bash
# Start database services
make docker-up

# Start all services including API
make docker-up-all

# Stop services
make docker-down

# Restart services
make docker-restart

# View logs
make docker-logs

# Check running containers
make docker-ps

# Check health status
make docker-health
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f qdrant
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f api
```

### Rebuild Services

```bash
# Rebuild and start
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build api
```

### Clean Up

```bash
# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (CAUTION: deletes data)
docker compose down -v

# Stop and remove containers + volumes + images
make docker-clean
```

## Development Workflows

### Workflow 1: Databases in Docker, API Locally (Recommended)

This is the fastest development workflow:

```bash
# 1. Start databases
make docker-up

# 2. Copy and configure .env
cp .env.example .env
# Edit .env to use localhost for database connections

# 3. Run API locally
python -m uvicorn src.main:app --reload
```

**Benefits:**
- Fast code reloading
- Easy debugging
- Direct access to Python debugger

### Workflow 2: Everything in Docker

Run the entire stack in Docker:

```bash
# Start all services
make docker-up-all

# View API logs
docker compose logs -f api
```

**Benefits:**
- Production-like environment
- Easier deployment testing
- Isolated from local system

## Troubleshooting

### Issue: "Error getting credentials" when pulling images

If you encounter an error like `error getting credentials - err: exit status 1, out: ''` when pulling Docker images (especially Qdrant):

**QUICK FIX (Recommended):**
```bash
./fix-docker-credentials.sh
```

This automated script will:
- Backup your Docker config
- Remove the problematic credential helper
- Clear cached credentials
- Pre-pull all required images

For detailed manual steps, see [DOCKER_CREDENTIAL_FIX.md](DOCKER_CREDENTIAL_FIX.md)

**Solution 1: Clear Docker credential helpers (Manual)**
```bash
# Edit or create ~/.docker/config.json
# Remove or comment out the "credsStore" line
nano ~/.docker/config.json

# Change from:
# {
#   "credsStore": "desktop"
# }

# To:
# {
# }
```

**Solution 2: Login to Docker Hub**
```bash
# Logout first
docker logout

# Login again (optional - public images don't require login)
docker login
```

**Solution 3: Pull the image manually**
```bash
# Pull the specific image first
docker pull qdrant/qdrant:v1.7.4

# Then start services
docker compose up -d
```

**What was fixed:**
- Changed from `qdrant/qdrant:latest` to `qdrant/qdrant:v1.7.4` (specific version)
- Added `pull_policy: missing` to avoid unnecessary pull attempts
- Using specific tags helps avoid credential helper issues

### Issue: "docker compose: command not found"

**Solution 1:** You have Docker Compose v1, use `docker-compose` instead:
```bash
docker-compose up -d
```

**Solution 2:** Update to Docker Compose v2:
- **Linux:** `sudo apt-get update && sudo apt-get install docker-compose-plugin`
- **macOS/Windows:** Update Docker Desktop to the latest version

### Issue: Containers keep restarting

**Check logs:**
```bash
docker compose logs qdrant
docker compose logs postgres
docker compose logs redis
```

**Common causes:**
1. **Port conflicts** - Another service is using ports 6333, 5432, or 6379
   ```bash
   # Check what's using a port
   lsof -i :6333
   lsof -i :5432
   lsof -i :6379
   ```

2. **Insufficient memory** - Increase Docker memory limit
   - Docker Desktop: Settings → Resources → Memory (increase to 4GB+)

3. **Corrupted volumes** - Remove and recreate
   ```bash
   docker compose down -v
   docker compose up -d
   ```

### Issue: "Connection refused" errors

**Check if services are healthy:**
```bash
make docker-health
# Or
docker ps
```

Look for "healthy" status. If status is "starting", wait a bit longer.

**Verify connectivity:**
```bash
# Qdrant
curl http://localhost:6333/

# PostgreSQL
pg_isready -h localhost -U doctor_ai

# Redis
redis-cli -h localhost ping
```

### Issue: Slow builds

**Use .dockerignore:**
The project now includes a `.dockerignore` file that excludes unnecessary files.

**Clear build cache:**
```bash
docker compose build --no-cache
```

### Issue: Permission errors on volumes

**Linux users may need to fix volume permissions:**
```bash
# Stop services
docker compose down

# Fix ownership (replace 1000:1000 with your user:group)
sudo chown -R 1000:1000 ./logs
sudo chown -R 1000:1000 ./qdrant_storage

# Restart
docker compose up -d
```

### Issue: API can't connect to databases

**If API is running locally:**
- Use `localhost` in `.env`:
  ```
  DATABASE_URL=postgresql://doctor_ai:doctor_ai_pass@localhost:5432/doctor_ai
  QDRANT_HOST=localhost
  REDIS_HOST=localhost
  ```

**If API is running in Docker:**
- Use service names in `.env`:
  ```
  DATABASE_URL=postgresql://doctor_ai:doctor_ai_pass@postgres:5432/doctor_ai
  QDRANT_HOST=qdrant
  REDIS_HOST=redis
  ```

## Health Check Details

### Qdrant
- **Check:** HTTP GET to `http://localhost:6333/`
- **Interval:** Every 10 seconds
- **Start period:** 30 seconds (gives time to initialize)

### PostgreSQL
- **Check:** `pg_isready` command
- **Interval:** Every 10 seconds
- **Start period:** 10 seconds

### Redis
- **Check:** `redis-cli ping`
- **Interval:** Every 10 seconds
- **Start period:** 10 seconds

### API
- **Check:** HTTP GET to `http://localhost:8000/health`
- **Interval:** Every 30 seconds
- **Start period:** 40 seconds (waits for dependencies)

**Note:** The API health check requires a `/health` endpoint. If this doesn't exist, the health check will fail but the service will still run.

## Best Practices

1. **Use profiles for optional services**
   - Keep default setup lightweight (databases only)
   - Use `--profile full` when you need the API in Docker

2. **Always use health checks**
   - Prevents race conditions
   - Ensures services are ready before use

3. **Use service names for inter-container communication**
   - Inside Docker: use `postgres`, `qdrant`, `redis`
   - From host: use `localhost`

4. **Mount volumes for data persistence**
   - Database data is stored in named volumes
   - Survives container restarts
   - Can be backed up with `docker volume` commands

5. **Use .dockerignore**
   - Speeds up builds
   - Reduces image size
   - Prevents sensitive files from being copied

6. **Monitor logs**
   - Regularly check `docker compose logs`
   - Use `make docker-health` to verify status

## Advanced Usage

### Custom Network Configuration

The compose file creates a bridge network. To customize:

```yaml
networks:
  doctor-ai-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Resource Limits

Add resource constraints to prevent services from consuming too much:

```yaml
services:
  qdrant:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

### Production Considerations

For production deployments:

1. **Use specific image tags** (not `latest`)
2. **Enable restart policies** (already configured)
3. **Set up backups** for volumes
4. **Use secrets** for passwords instead of environment variables
5. **Enable SSL/TLS** for database connections
6. **Set up monitoring** (Prometheus, Grafana)
7. **Configure log rotation**

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Compose v2 Migration](https://docs.docker.com/compose/migrate/)
- [Qdrant Docker Guide](https://qdrant.tech/documentation/quick-start/)
- [PostgreSQL Docker Guide](https://hub.docker.com/_/postgres)
- [Redis Docker Guide](https://hub.docker.com/_/redis)
