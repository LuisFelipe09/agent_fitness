"""
Additional auth DTO for password setup.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class SetPassword(BaseModel):
    """Set password for Telegram users."""
    email: Optional[EmailStr] = None
    password: str


class RoleAssignmentRequest(BaseModel):
    """Request to assign a role to a user."""
    role: str


class ProfessionalAssignmentRequest(BaseModel):
    """Request to assign a professional to a client."""
    professional_id: str


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data embedded in the token."""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request."""
    username: str
    password: str
    email: Optional[EmailStr] = None
