#!/bin/bash
# Custom Vercel build script to use pip3 instead of pip3.12

set -e

# Add current directory to PATH so pip3.12 wrapper is found first
export PATH="/vercel/path0/api:$PATH"

# Use pip3 explicitly instead of pip3.12
if [ -f "requirements.txt" ]; then
    pip3 install --disable-pip-version-check --no-compile --no-cache-dir --upgrade -r requirements.txt
fi
