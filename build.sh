#!/bin/bash
# Build script for deployments (Vercel, Docker, etc.)
# Ensures setuptools>=70.0.0 is installed before other dependencies

set -e

echo "=== Doctor-AI Build Script ==="
echo "Fixing distutils compatibility for Python 3.12+..."

# Determine pip command (prefer pip3 over pip3.12)
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "Error: pip not found"
    exit 1
fi

echo "Using pip command: $PIP_CMD"

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install setuptools first to avoid distutils errors
echo "Installing modern setuptools..."
$PIP_CMD install "setuptools>=70.0.0"

# Install requirements with constraints
echo "Installing project dependencies..."
$PIP_CMD install -r requirements.txt -c constraints.txt

echo "=== Build completed successfully! ==="
