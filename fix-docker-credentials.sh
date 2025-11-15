#!/bin/bash
# Script to fix Docker credential helper issues
# This resolves "error getting credentials - err: exit status 1" errors

set -e

echo "========================================"
echo "Docker Credential Helper Fix Script"
echo "========================================"
echo ""

DOCKER_CONFIG="$HOME/.docker/config.json"
BACKUP_CONFIG="$HOME/.docker/config.json.backup.$(date +%Y%m%d_%H%M%S)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

echo "Step 1: Backing up Docker config..."
if [ -f "$DOCKER_CONFIG" ]; then
    cp "$DOCKER_CONFIG" "$BACKUP_CONFIG"
    echo "✓ Backup created: $BACKUP_CONFIG"
else
    echo "! No existing Docker config found at $DOCKER_CONFIG"
fi

echo ""
echo "Step 2: Fixing Docker credential store..."

# Create .docker directory if it doesn't exist
mkdir -p "$HOME/.docker"

# Create a clean config without credential helpers
cat > "$DOCKER_CONFIG" << 'EOF'
{
  "auths": {}
}
EOF

echo "✓ Docker config updated (removed credential helper)"

echo ""
echo "Step 3: Logging out of Docker (clearing any cached credentials)..."
docker logout 2>/dev/null || echo "! Already logged out or no credentials to clear"

echo ""
echo "Step 4: Testing Docker pull..."
echo "Attempting to pull Qdrant image..."

if docker pull qdrant/qdrant:v1.7.4; then
    echo "✓ Successfully pulled Qdrant image!"
    echo ""
    echo "========================================"
    echo "SUCCESS! Docker credentials are fixed."
    echo "========================================"
    echo ""
    echo "You can now run:"
    echo "  docker compose up -d"
    echo "or:"
    echo "  make docker-up"
else
    echo ""
    echo "========================================"
    echo "Pull failed. Additional troubleshooting needed."
    echo "========================================"
    echo ""
    echo "Please try:"
    echo "1. Check your internet connection"
    echo "2. Check if you're behind a proxy: docker info | grep -i proxy"
    echo "3. Try with sudo: sudo docker pull qdrant/qdrant:v1.7.4"
    echo "4. Check Docker daemon status: systemctl status docker"
    echo ""
    echo "If the issue persists, check DOCKER.md for more solutions."
    exit 1
fi

# Also pull other required images
echo ""
echo "Step 5: Pre-pulling other required images..."
docker pull postgres:15-alpine
docker pull redis:7-alpine

echo ""
echo "✓ All images pulled successfully!"
echo ""
echo "Next steps:"
echo "1. Start services: docker compose up -d"
echo "2. Check status: docker compose ps"
echo "3. View logs: docker compose logs -f"
