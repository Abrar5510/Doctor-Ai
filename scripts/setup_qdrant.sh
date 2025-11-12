#!/bin/bash
# Qdrant Setup Script for Doctor-AI
# This script helps you set up Qdrant vector database

set -e

echo "================================================"
echo "  Qdrant Setup for Doctor-AI"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: Install Python dependencies
echo "Step 1: Installing Python dependencies..."
if pip install qdrant-client==1.7.0; then
    print_success "qdrant-client installed successfully"
else
    print_error "Failed to install qdrant-client"
    exit 1
fi

# Step 2: Check Docker availability
echo ""
echo "Step 2: Checking Docker availability..."
if command_exists docker; then
    print_success "Docker is installed"

    echo ""
    echo "Would you like to start Qdrant using Docker? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Starting Qdrant with Docker Compose..."
        if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
            if [ -f "docker-compose.yml" ]; then
                # Try docker compose (newer) first, then docker-compose (older)
                if docker compose up -d qdrant 2>/dev/null || docker-compose up -d qdrant; then
                    print_success "Qdrant started successfully with Docker"
                    echo ""
                    echo "Qdrant is running at:"
                    echo "  - HTTP API: http://localhost:6333"
                    echo "  - gRPC API: http://localhost:6334"
                    echo "  - Web UI: http://localhost:6333/dashboard"
                else
                    print_error "Failed to start Qdrant with Docker Compose"
                fi
            else
                print_error "docker-compose.yml not found"
            fi
        else
            print_warning "docker-compose not found. Install it from: https://docs.docker.com/compose/install/"
        fi
    fi
else
    print_warning "Docker is not installed"
    echo ""
    echo "You have several options to run Qdrant:"
    echo ""
    echo "Option 1: Install Docker"
    echo "  Visit: https://docs.docker.com/get-docker/"
    echo ""
    echo "Option 2: Run Qdrant locally (binary)"
    echo "  Download from: https://github.com/qdrant/qdrant/releases"
    echo "  Run: ./qdrant"
    echo ""
    echo "Option 3: Use Qdrant Cloud (free tier available)"
    echo "  Sign up at: https://cloud.qdrant.io/"
    echo "  Then update your .env file with:"
    echo "    QDRANT_HOST=your-cluster-url.cloud.qdrant.io"
    echo "    QDRANT_API_KEY=your-api-key"
    echo ""
    echo "Option 4: Use embedded Qdrant (for development/testing only)"
    echo "  Set in your .env:"
    echo "    USE_EMBEDDED_QDRANT=true"
    echo ""
fi

# Step 3: Test connection (if Qdrant is running)
echo ""
echo "Step 3: Testing Qdrant connection..."
python3 << 'EOF'
import sys
try:
    from qdrant_client import QdrantClient

    # Try to connect to local Qdrant
    try:
        client = QdrantClient(host="localhost", port=6333, timeout=3)
        collections = client.get_collections()
        print("✓ Successfully connected to Qdrant at localhost:6333")
        print(f"  Found {len(collections.collections)} collection(s)")
        sys.exit(0)
    except Exception as e:
        print(f"⚠ Could not connect to Qdrant at localhost:6333")
        print(f"  Error: {str(e)}")
        print("")
        print("If Qdrant is not running, please start it using one of the options above.")
        sys.exit(1)

except ImportError:
    print("✗ qdrant-client not installed properly")
    sys.exit(1)
EOF

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Ensure Qdrant is running"
echo "  2. Copy .env.example to .env: cp .env.example .env"
echo "  3. Update .env with your Qdrant connection details"
echo "  4. Run the seeding script: python scripts/seed_data.py"
echo "  5. Start the API: python -m uvicorn src.main:app --reload"
echo ""
