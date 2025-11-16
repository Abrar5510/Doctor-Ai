#!/usr/bin/env python3
"""
Initialize the database with tables and seed data.

Usage:
    python scripts/init_db.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import init_db, SessionLocal
from src.models.database import User, UserRole, UserStatus
from src.utils.password import hash_password
from datetime import datetime, timezone
from loguru import logger


def create_default_admin():
    """Create default admin user if not exists."""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@doctor-ai.local",
            hashed_password=hash_password("ChangeMe123!@#"),  # MUST be changed
            full_name="System Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            password_changed_at=datetime.now(timezone.utc),
        )

        db.add(admin)
        db.commit()
        logger.success("Admin user created successfully")
        logger.warning("⚠️  Default admin password is 'ChangeMe123!@#' - CHANGE IT IMMEDIATELY!")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function."""
    logger.info("Initializing database...")

    try:
        # Create tables
        init_db()
        logger.success("Database tables created successfully")

        # Create default admin
        create_default_admin()

        logger.success("Database initialization complete!")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
