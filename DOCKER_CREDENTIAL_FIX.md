# Fix Docker Credential Error

If you're getting this error when running `docker compose up`:
```
error getting credentials - err: exit status 1, out: ``
```

This guide will help you fix it.

## Quick Fix (Automated)

Run the automated fix script:

```bash
./fix-docker-credentials.sh
```

This script will:
1. Backup your current Docker config
2. Remove the problematic credential helper
3. Clear cached credentials
4. Pre-pull all required images
5. Verify everything works

## Manual Fix (Step-by-Step)

If you prefer to fix it manually:

### Step 1: Edit Docker Config

```bash
# Edit Docker config file
nano ~/.docker/config.json
```

**Change from:**
```json
{
  "credsStore": "desktop",
  "auths": {}
}
```

**To:**
```json
{
  "auths": {}
}
```

Or simply delete the file and recreate it:
```bash
# Backup first
cp ~/.docker/config.json ~/.docker/config.json.backup

# Create clean config
mkdir -p ~/.docker
echo '{"auths": {}}' > ~/.docker/config.json
```

### Step 2: Logout and Clear Credentials

```bash
docker logout
```

### Step 3: Pull Images Manually

```bash
# Pull Qdrant
docker pull qdrant/qdrant:v1.7.4

# Pull PostgreSQL
docker pull postgres:15-alpine

# Pull Redis
docker pull redis:7-alpine
```

### Step 4: Start Services

```bash
docker compose up -d
```

## Why This Happens

Docker uses "credential helpers" to store login credentials securely. Common helpers include:
- `docker-credential-desktop` (Docker Desktop)
- `docker-credential-secretservice` (Linux)
- `docker-credential-osxkeychain` (macOS)

The error occurs when:
1. The credential helper binary is missing or corrupted
2. The helper doesn't have proper permissions
3. The helper's backend storage is inaccessible
4. Docker Desktop was uninstalled but config remains

## Alternative Solutions

### Solution 1: Reinstall Docker Desktop

If you're using Docker Desktop, try reinstalling it:
- **macOS/Windows**: Download latest from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**:
  ```bash
  sudo apt-get update
  sudo apt-get install --reinstall docker-ce docker-ce-cli
  ```

### Solution 2: Use Different Credential Store

Edit `~/.docker/config.json`:

```json
{
  "credStore": "pass",
  "auths": {}
}
```

Requires `docker-credential-pass` to be installed:
```bash
# Ubuntu/Debian
sudo apt-get install pass docker-credential-pass

# macOS
brew install docker-credential-helper
```

### Solution 3: Run with Sudo (Linux only)

If running as non-root user:
```bash
sudo docker compose up -d
```

**Note**: This is not recommended for security reasons. Better to fix permissions:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again for changes to take effect
```

## Verify the Fix

After applying any solution, verify it works:

```bash
# Test pulling an image
docker pull hello-world

# Check Docker info
docker info

# Start your services
docker compose up -d

# Check service status
docker compose ps
```

## Still Having Issues?

If none of the above works:

1. **Check Docker daemon logs**:
   ```bash
   # Linux
   sudo journalctl -u docker.service -f

   # macOS/Docker Desktop
   # Click Docker icon → Troubleshoot → View logs
   ```

2. **Check system compatibility**:
   ```bash
   docker --version
   docker compose version
   uname -a
   ```

3. **Try a fresh Docker installation**:
   ```bash
   # Complete removal and reinstall (CAUTION: removes all containers/images)
   sudo apt-get purge docker-ce docker-ce-cli containerd.io
   sudo rm -rf /var/lib/docker
   # Then reinstall Docker following official docs
   ```

4. **Check for proxy/firewall issues**:
   ```bash
   # Test connection to Docker Hub
   curl -I https://hub.docker.com

   # If behind proxy, configure Docker:
   sudo mkdir -p /etc/systemd/system/docker.service.d
   sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
   ```

## Get Help

If you're still stuck:
1. Check the main [DOCKER.md](./DOCKER.md) troubleshooting section
2. Open an issue with:
   - Your operating system: `uname -a`
   - Docker version: `docker --version`
   - Full error message
   - Contents of `~/.docker/config.json` (remove any sensitive data)
