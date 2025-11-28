"""
Additional auth DTO for password setup.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class SetPassword(BaseModel):
    """Set password for Telegram users."""
    email: Optional[EmailStr] = None
    password: str
