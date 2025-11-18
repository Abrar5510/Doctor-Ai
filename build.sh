#!/bin/bash
# Build script for deployments (Vercel, Docker, etc.)

set -e

echo "=== Doctor-AI Build Script ==="

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install dependencies (setuptools>=70.0.0 is in requirements.txt)
pip3 install -r requirements.txt

echo "=== Build completed successfully! ==="
