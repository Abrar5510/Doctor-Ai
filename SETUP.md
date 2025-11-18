# Setup & Troubleshooting

Quick reference for common setup issues and solutions.

## Quick Setup

1. **Install Prerequisites**
   - Python 3.9+
   - Docker & Docker Compose
   - 8GB+ RAM

2. **Clone and Install**
   ```bash
   git clone https://github.com/Abrar5510/Doctor-Ai.git
   cd Doctor-Ai
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start Services**
   ```bash
   docker compose up -d
   python scripts/seed_data.py
   python -m src.main
   ```

## Common Issues

### Docker Credential Error

If you get `error getting credentials - err: exit status 1`:

```bash
# Quick fix
./fix-docker-credentials.sh

# Or manually
mkdir -p ~/.docker
echo '{"auths": {}}' > ~/.docker/config.json
docker compose up -d
```

### Port Already in Use

Change ports in `docker-compose.yml` if defaults are taken:
- Qdrant: 6333 → 6334
- PostgreSQL: 5432 → 5433
- Redis: 6379 → 6380

Update `.env` to match new ports.

### Out of Memory

- Close other applications
- System will automatically use CPU if GPU unavailable
- Requires minimum 8GB RAM

### Model Download Slow/Fails

First run downloads ~420MB model. This is normal and only happens once.

If download fails:
- Check internet connection
- Try again (downloads resume automatically)
- Model is cached at `~/.cache/huggingface/`

### Qdrant Connection Failed

```bash
# Check Qdrant is running
docker compose ps

# View logs
docker compose logs qdrant

# Restart Qdrant
docker compose restart qdrant

# Test connection
python scripts/test_qdrant_connection.py
```

## Verify Installation

```bash
# Check all services
docker compose ps

# Test API
python scripts/test_api.py

# Open browser
# http://localhost:8000/docs
# http://localhost:3000
```

## Clean Restart

```bash
# Stop everything
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Start fresh
docker compose up -d
python scripts/seed_data.py
python -m src.main
```

## Getting Help

- Check main README.md
- Review API docs: http://localhost:8000/docs
- Open issue: https://github.com/Abrar5510/Doctor-Ai/issues
