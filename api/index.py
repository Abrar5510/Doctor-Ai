"""
Vercel serverless function entry point for Doctor AI Backend API

This file wraps the FastAPI application to work with Vercel's serverless functions.

IMPORTANT NOTES:
- Vercel serverless functions have execution time limits (10s Hobby, 60s Pro)
- ML models may cause cold start delays
- Consider using external services for ML model hosting if needed
- This is best suited for lightweight API endpoints

For production with ML models, consider:
- Deploying backend to Railway, Fly.io, or Google Cloud Run
- Using this Vercel deployment only for non-ML endpoints
- Or upgrading to Vercel Pro and optimizing model loading
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app

# Export the FastAPI app for Vercel
# Vercel will handle the ASGI server
handler = app
