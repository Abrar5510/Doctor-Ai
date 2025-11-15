"""
Authentication and user management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.auth import AuthService, get_current_user
from src.models.database import User, UserRole
from src.utils.password import default_validator


# Pydantic models for request/response
class UserRegister(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=12)
    full_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """User login request."""

    username: str
    password: str


class PasswordChange(BaseModel):
    """Password change request."""

    old_password: str
    new_password: str = Field(..., min_length=12)


class PasswordStrength(BaseModel):
    """Password strength check request."""

    password: str


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str
    expires_at: str
    expires_in: int
    user: UserResponse


class PasswordStrengthResponse(BaseModel):
    """Password strength response."""

    strength: str
    is_valid: bool
    errors: list[str]


# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Creates a new user account with password validation.
    Returns access token upon successful registration.
    """
    auth_service = AuthService(db)

    # Create user
    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    # Create access token
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    token_data = auth_service.create_access_token(user, ip_address, user_agent)

    # Build response
    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_at=token_data["expires_at"],
        expires_in=token_data["expires_in"],
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return access token.

    Login with username/email and password.
    """
    auth_service = AuthService(db)

    # Authenticate user
    ip_address = request.client.host if request.client else None
    user = auth_service.authenticate_user(
        credentials.username,
        credentials.password,
        ip_address,
    )

    # Create access token
    user_agent = request.headers.get("User-Agent")
    token_data = auth_service.create_access_token(user, ip_address, user_agent)

    # Build response
    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_at=token_data["expires_at"],
        expires_in=token_data["expires_in"],
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Requires valid JWT token.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change user password.

    Requires current password and validates new password strength.
    """
    auth_service = AuthService(db)

    # Change password
    auth_service.change_password(
        current_user,
        password_data.old_password,
        password_data.new_password,
    )

    return {"message": "Password changed successfully. All sessions have been revoked."}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking all tokens.

    Invalidates all active sessions for the user.
    """
    auth_service = AuthService(db)

    # Revoke all user tokens
    count = auth_service.revoke_all_user_tokens(current_user.id)

    return {"message": f"Logged out successfully. {count} session(s) revoked."}


@router.post("/check-password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(password_data: PasswordStrength):
    """
    Check password strength without creating an account.

    Useful for client-side password validation.
    """
    is_valid, errors = default_validator.validate(password_data.password)
    strength = default_validator.get_password_strength(password_data.password)

    return PasswordStrengthResponse(
        strength=strength,
        is_valid=is_valid,
        errors=errors if not is_valid else [],
    )
