#!/bin/bash
# Vercel build script to ensure proper setuptools version
# This script runs during Vercel deployment to fix distutils compatibility

set -e

echo "Installing setuptools>=70.0.0 to fix distutils compatibility..."

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install setuptools explicitly before other packages
python3 -m pip install "setuptools>=70.0.0"

# Install requirements with constraints
python3 -m pip install -r requirements.txt -c constraints.txt

echo "Dependencies installed successfully!"
