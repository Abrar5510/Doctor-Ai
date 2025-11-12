# Qdrant Setup Guide for Doctor-AI

This guide helps you set up Qdrant vector database for the Doctor-AI Medical Symptom Constellation Mapper.

## Quick Setup

Run the automated setup script:

```bash
chmod +x scripts/setup_qdrant.sh
./scripts/setup_qdrant.sh
```

## Manual Setup Options

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Compose](https://docs.docker.com/compose/install/))

**Steps:**

1. **Install qdrant-client Python package:**
   ```bash
   pip install qdrant-client==1.7.0
   ```

2. **Start Qdrant with Docker Compose:**
   ```bash
   docker-compose up -d qdrant
   ```

3. **Verify Qdrant is running:**
   ```bash
   docker ps | grep qdrant
   ```

   You should see:
   ```
   doctor-ai-qdrant   Up   0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
   ```

4. **Access Qdrant Web UI:**
   Open [http://localhost:6333/dashboard](http://localhost:6333/dashboard) in your browser

5. **Test connection:**
   ```bash
   python -c "from qdrant_client import QdrantClient; client = QdrantClient('localhost', port=6333); print('Connected:', client.get_collections())"
   ```

---

### Option 2: Docker without Docker Compose

If you only have Docker installed:

```bash
# Install Python client
pip install qdrant-client==1.7.0

# Run Qdrant container
docker run -d \
  --name doctor-ai-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

---

### Option 3: Qdrant Binary (No Docker)

**For Linux/macOS:**

1. **Download Qdrant:**
   ```bash
   # Linux
   wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-musl.tar.gz
   tar -xzf qdrant-x86_64-unknown-linux-musl.tar.gz

   # macOS
   wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-apple-darwin.tar.gz
   tar -xzf qdrant-x86_64-apple-darwin.tar.gz
   ```

2. **Run Qdrant:**
   ```bash
   ./qdrant
   ```

3. **Install Python client:**
   ```bash
   pip install qdrant-client==1.7.0
   ```

**For Windows:**

Download the Windows binary from [Qdrant Releases](https://github.com/qdrant/qdrant/releases) and run `qdrant.exe`

---

### Option 4: Qdrant Cloud (Recommended for Production)

1. **Sign up for Qdrant Cloud:**
   - Go to [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
   - Create a free account (1GB cluster included)
   - Create a new cluster

2. **Get your credentials:**
   - Cluster URL: `your-cluster-name.cloud.qdrant.io`
   - API Key: Generated in the dashboard

3. **Install Python client:**
   ```bash
   pip install qdrant-client==1.7.0
   ```

4. **Update your `.env` file:**
   ```env
   QDRANT_HOST=your-cluster-name.cloud.qdrant.io
   QDRANT_PORT=6333
   QDRANT_API_KEY=your-api-key-here
   ```

---

### Option 5: Embedded Qdrant (Development/Testing Only)

For quick testing without running a separate Qdrant server:

1. **Install qdrant-client:**
   ```bash
   pip install qdrant-client==1.7.0
   ```

2. **Use in-memory or local storage:**
   ```python
   from qdrant_client import QdrantClient

   # In-memory (data lost on restart)
   client = QdrantClient(":memory:")

   # Local storage (persists data)
   client = QdrantClient(path="./qdrant_data")
   ```

**Note:** Not recommended for production use.

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'qdrant_client'"

**Solution:**
```bash
pip install qdrant-client==1.7.0
```

### Error: "docker: command not found"

**Solution:**
Install Docker from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

Or use one of the non-Docker options above.

### Error: "Connection refused" when connecting to Qdrant

**Possible causes:**

1. **Qdrant is not running**
   - Check with: `docker ps` (for Docker)
   - Start with: `docker-compose up -d qdrant`

2. **Port 6333 is already in use**
   - Check with: `lsof -i :6333` (Linux/macOS) or `netstat -ano | findstr :6333` (Windows)
   - Stop the conflicting service or change Qdrant port

3. **Firewall blocking connection**
   - Allow port 6333 in your firewall
   - For cloud deployments, check security group settings

4. **Wrong host/port configuration**
   - Verify `.env` settings:
     ```env
     QDRANT_HOST=localhost
     QDRANT_PORT=6333
     ```

### Error: "grpcio" installation fails on macOS M1/M2

**Solution:**
```bash
# Install with Homebrew dependencies
brew install grpc

# Or install from source
pip install grpcio --no-binary :all:
```

### Docker container keeps restarting

**Check logs:**
```bash
docker logs doctor-ai-qdrant
```

**Common issues:**
- Insufficient memory: Increase Docker memory limit (Preferences → Resources)
- Port conflict: Change ports in `docker-compose.yml`
- Corrupted storage: Remove volume and restart
  ```bash
  docker-compose down -v
  docker-compose up -d qdrant
  ```

---

## Configuration

### Environment Variables

Update your `.env` file with Qdrant settings:

```env
# Qdrant Vector Database
QDRANT_HOST=localhost          # Use "localhost" for local, or your cloud URL
QDRANT_PORT=6333              # Default HTTP port
QDRANT_API_KEY=               # Leave empty for local, required for cloud
QDRANT_COLLECTION_NAME=medical_conditions
```

### Testing Your Setup

1. **Check Qdrant is accessible:**
   ```bash
   curl http://localhost:6333/
   ```

   Expected response:
   ```json
   {
     "title": "qdrant - vector search engine",
     "version": "..."
   }
   ```

2. **Test with Python:**
   ```python
   from qdrant_client import QdrantClient

   client = QdrantClient(host="localhost", port=6333)
   print("Collections:", client.get_collections())
   ```

3. **Initialize the database:**
   ```bash
   # Create collection and seed data
   python scripts/seed_data.py
   ```

---

## Next Steps

After Qdrant is running:

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your settings**

3. **Seed the database:**
   ```bash
   python scripts/seed_data.py
   ```

4. **Start the API:**
   ```bash
   python -m uvicorn src.main:app --reload
   ```

5. **Access the API:**
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Qdrant Dashboard: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Docker Documentation](https://docs.docker.com/)
- [Doctor-AI GitHub Repository](https://github.com/Abrar5510/Doctor-Ai)

---

## Support

If you encounter any issues not covered here:

1. Check [Qdrant GitHub Issues](https://github.com/qdrant/qdrant/issues)
2. Review [Doctor-AI Issues](https://github.com/Abrar5510/Doctor-Ai/issues)
3. Create a new issue with:
   - Your setup method (Docker/Binary/Cloud)
   - Error messages
   - Operating system
   - Python version
