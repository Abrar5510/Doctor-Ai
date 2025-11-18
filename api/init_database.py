"""
One-time database initialization endpoint for Vercel deployment.

IMPORTANT: Delete this file after running it once, or protect it with authentication!

Usage:
1. Deploy to Vercel
2. Visit: https://your-app.vercel.app/api/init_database
3. Delete this file and redeploy for security

This endpoint will:
- Create all database tables
- Create default admin user
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.database import init_db, SessionLocal
from src.models.database import User, UserRole, UserStatus
from src.utils.password import hash_password
from datetime import datetime
from loguru import logger

app = FastAPI()


@app.get("/")
async def initialize_database():
    """
    Initialize database tables and create default admin user.

    ⚠️ SECURITY WARNING: This endpoint should be removed after first use!
    """
    try:
        # Create tables
        logger.info("Creating database tables...")
        init_db()
        logger.success("Database tables created successfully")

        # Create default admin user
        db = SessionLocal()
        try:
            # Check if admin exists
            admin = db.query(User).filter(User.username == "admin").first()
            if admin:
                return JSONResponse(
                    content={
                        "status": "already_initialized",
                        "message": "Database tables exist and admin user already created",
                        "warning": "⚠️ This endpoint should be DELETED for security!"
                    }
                )

            # Create admin user
            admin = User(
                username="admin",
                email="admin@doctor-ai.local",
                hashed_password=hash_password("ChangeMe123!@#"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True,
                password_changed_at=datetime.utcnow(),
            )

            db.add(admin)
            db.commit()
            logger.success("Admin user created successfully")

            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Database initialized successfully!",
                    "admin_credentials": {
                        "username": "admin",
                        "password": "ChangeMe123!@#",
                        "warning": "⚠️ CHANGE THIS PASSWORD IMMEDIATELY!"
                    },
                    "next_steps": [
                        "1. Change the admin password immediately",
                        "2. DELETE this api/init_database.py file",
                        "3. Redeploy your application"
                    ]
                }
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating admin user: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create admin user: {str(e)}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database initialization failed: {str(e)}"
        )


# Export the FastAPI app for Vercel
handler = app
