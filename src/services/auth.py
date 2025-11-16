"""
Authentication and authorization service.

This module provides JWT-based authentication, user management,
and role-based access control for the Doctor-AI application.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config import get_settings
from src.models.database import User, UserSession, UserRole, UserStatus
from src.utils.password import hash_password, verify_password, default_validator


settings = get_settings()
security = HTTPBearer()


class AuthService:
    """Authentication service for user management and JWT operations."""

    def __init__(self, db: Session):
        """
        Initialize auth service.

        Args:
            db: Database session
        """
        self.db = db
        self.password_validator = default_validator

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.API_USER,
    ) -> User:
        """
        Create a new user with password validation.

        Args:
            username: Username
            email: Email address
            password: Plain text password
            full_name: Full name
            role: User role

        Returns:
            Created user object

        Raises:
            HTTPException: If username/email exists or password is weak
        """
        # Check if user exists
        if self.db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        if self.db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Validate password
        is_valid, errors = self.password_validator.validate(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "errors": errors},
            )

        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,  # Set to False if email verification is required
            password_changed_at=datetime.now(timezone.utc),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(
        self, username: str, password: str, ip_address: Optional[str] = None
    ) -> User:
        """
        Authenticate user with username and password.

        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address for audit

        Returns:
            Authenticated user object

        Raises:
            HTTPException: If authentication fails
        """
        # Find user by username or email
        user = (
            self.db.query(User)
            .filter((User.username == username) | (User.email == username))
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is locked until {user.locked_until.isoformat()}",
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)

            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is active
        if not user.is_active or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active",
            )

        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

        return user

    def create_access_token(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create JWT access token for user.

        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Dictionary with token and expiration info
        """
        # Generate unique token ID
        jti = secrets.token_urlsafe(32)

        # Calculate expiration
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.now(timezone.utc) + expires_delta

        # Create token payload
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "jti": jti,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc),
        }

        # Encode token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Create session record
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        self.db.add(session)
        self.db.commit()

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at.isoformat(),
            "expires_in": int(expires_delta.total_seconds()),
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Check if session is still valid
            jti = payload.get("jti")
            if jti:
                session = (
                    self.db.query(UserSession)
                    .filter(UserSession.token_jti == jti)
                    .first()
                )

                if not session or not session.is_active or session.revoked_at:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Update last activity
                session.last_activity_at = datetime.now(timezone.utc)
                self.db.commit()

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_user(self, token_payload: Dict[str, Any]) -> User:
        """
        Get current user from token payload.

        Args:
            token_payload: Decoded JWT payload

        Returns:
            User object

        Raises:
            HTTPException: If user not found or inactive
        """
        user_id = token_payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return user

    def revoke_token(self, jti: str) -> bool:
        """
        Revoke a token by its JTI.

        Args:
            jti: JWT token ID

        Returns:
            True if revoked successfully
        """
        session = (
            self.db.query(UserSession).filter(UserSession.token_jti == jti).first()
        )

        if session:
            session.is_active = False
            session.revoked_at = datetime.now(timezone.utc)
            self.db.commit()
            return True

        return False

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revoke all active tokens for a user.

        Args:
            user_id: User ID

        Returns:
            Number of tokens revoked
        """
        sessions = (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id, UserSession.is_active == True)
            .all()
        )

        count = 0
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.now(timezone.utc)
            count += 1

        self.db.commit()
        return count

    def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            user: User object
            old_password: Current password
            new_password: New password

        Returns:
            True if changed successfully

        Raises:
            HTTPException: If old password is incorrect or new password is weak
        """
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )

        # Validate new password
        is_valid, errors = self.password_validator.validate(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "New password does not meet requirements", "errors": errors},
            )

        # Update password
        user.hashed_password = hash_password(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        self.db.commit()

        # Revoke all existing tokens
        self.revoke_all_user_tokens(user.id)

        return True


# Import database dependency
from src.database import get_db


# Dependency for getting current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency for getting current authenticated user.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current user object
    """
    auth_service = AuthService(db)
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    return auth_service.get_current_user(payload)


# Dependency for role-based access control
class RoleChecker:
    """Dependency class for checking user roles."""

    def __init__(self, allowed_roles: list[UserRole]):
        """
        Initialize role checker.

        Args:
            allowed_roles: List of allowed roles
        """
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """
        Check if user has required role.

        Args:
            user: Current user

        Returns:
            User object if authorized

        Raises:
            HTTPException: If user doesn't have required role
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


# Convenience functions for common role checks
require_admin = RoleChecker([UserRole.ADMIN])
require_physician = RoleChecker([UserRole.ADMIN, UserRole.PHYSICIAN])
require_medical_staff = RoleChecker([UserRole.ADMIN, UserRole.PHYSICIAN, UserRole.NURSE])
